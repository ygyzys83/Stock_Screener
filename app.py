import streamlit as st
import pandas as pd
from screener import score_stock
from config import (
    TICKERS, ETF_TICKERS,
    RULES_FUNDAMENTAL, RULES_TECHNICAL,
    PASS_THRESHOLD, ETF_PASS_THRESHOLD,
)

st.set_page_config(page_title="Stock Screener", layout="wide")
st.title("Stock Screener")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Configuration")

    st.subheader("Tickers")
    stock_input = st.text_area("Stocks (comma-separated)", value=", ".join(TICKERS), height=80)
    etf_input   = st.text_area("ETFs (comma-separated)",   value=", ".join(ETF_TICKERS), height=60)
    tickers     = [t.strip().upper() for t in stock_input.split(",") if t.strip()]
    etf_tickers = [t.strip().upper() for t in etf_input.split(",")   if t.strip()]

    st.divider()

    st.subheader("Pass threshold")
    pass_pct     = st.slider("Stocks — must pass X% of rules", 20, 100, int(PASS_THRESHOLD * 100),     step=5)
    etf_pass_pct = st.slider("ETFs — must pass X% of rules",   20, 100, int(ETF_PASS_THRESHOLD * 100), step=5)

    st.divider()

    st.subheader("Fundamental rules")
    pe_on  = st.toggle("P/E ratio",  value=RULES_FUNDAMENTAL["pe_ratio"]["enabled"])
    pe_max = st.slider("Max P/E",    1.0, 60.0, float(RULES_FUNDAMENTAL["pe_ratio"]["max"]),          step=1.0,  disabled=not pe_on)

    pb_on  = st.toggle("P/B ratio",  value=RULES_FUNDAMENTAL["pb_ratio"]["enabled"])
    pb_max = st.slider("Max P/B",    0.5, 10.0, float(RULES_FUNDAMENTAL["pb_ratio"]["max"]),          step=0.5,  disabled=not pb_on)

    peg_on  = st.toggle("PEG ratio", value=RULES_FUNDAMENTAL["peg_ratio"]["enabled"])
    peg_max = st.slider("Max PEG",   0.1, 10.0,  float(RULES_FUNDAMENTAL["peg_ratio"]["max"]),         step=0.1,  disabled=not peg_on)

    fcf_on  = st.toggle("FCF yield", value=RULES_FUNDAMENTAL["fcf_yield"]["enabled"])
    fcf_min = st.slider("Min FCF yield %", 1, 15, int(RULES_FUNDAMENTAL["fcf_yield"]["min"] * 100),   step=1,    disabled=not fcf_on)

    de_on  = st.toggle("D/E ratio",  value=RULES_FUNDAMENTAL["de_ratio"]["enabled"])
    de_max = st.slider("Max D/E",    0.0, 5.0,  float(RULES_FUNDAMENTAL["de_ratio"]["max"]),          step=0.1,  disabled=not de_on)

    st.divider()

    st.subheader("Technical rules")
    rsi_on  = st.toggle("RSI breakout",      value=RULES_TECHNICAL["rsi_breakout"]["enabled"])
    rsi_min = st.slider("RSI min", 0, 70,   RULES_TECHNICAL["rsi_breakout"]["min"],                  step=1,    disabled=not rsi_on)
    rsi_max_val = st.slider("RSI max", 0, 100, RULES_TECHNICAL["rsi_breakout"]["max"],                step=1,    disabled=not rsi_on)

    macd_on  = st.toggle("MACD crossover",    value=RULES_TECHNICAL["macd_crossover"]["enabled"])
    bb_on    = st.toggle("Bollinger squeeze", value=RULES_TECHNICAL["bb_squeeze"]["enabled"])
    ma_on    = st.toggle("MA confluence",     value=RULES_TECHNICAL["ma_confluence"]["enabled"])

    rvol_on  = st.toggle("Relative volume",   value=RULES_TECHNICAL["rel_volume_surge"]["enabled"])
    rvol_min = st.slider("Min volume multiplier", 0.5, 10.0,
                         float(RULES_TECHNICAL["rel_volume_surge"]["min_multiplier"]),
                         step=0.1, disabled=not rvol_on)

    st.divider()
    run = st.button("Run Screener", type="primary", use_container_width=True)

# ── Runtime rule dicts ────────────────────────────────────────────────────────
runtime_fundamental = {
    "pe_ratio":  {"max": pe_max,        "enabled": pe_on},
    "pb_ratio":  {"max": pb_max,        "enabled": pb_on},
    "peg_ratio": {"max": peg_max,       "enabled": peg_on},
    "fcf_yield": {"min": fcf_min / 100, "enabled": fcf_on},
    "de_ratio":  {"max": de_max,        "enabled": de_on},
}
runtime_technical = {
    "rsi_breakout":     {"min": rsi_min, "max": rsi_max_val, "enabled": rsi_on},
    "macd_crossover":   {"enabled": macd_on},
    "bb_squeeze":       {"enabled": bb_on},
    "ma_confluence":    {"enabled": ma_on},
    "rel_volume_surge": {"min_multiplier": rvol_min, "enabled": rvol_on},
}

# ── Helper: render detail expander for one stock ──────────────────────────────
def render_detail_expander(r: dict):
    label = f"🔍  {r['ticker']} — {r.get('name', r['ticker'])}  ({r['rules_passed']}/{r['total_rules']} rules passed)"
    with st.expander(label):
        fund_vals = r["raw_values"].get("fundamental", {})
        tech_vals = r["raw_values"].get("technical",   {})

        if fund_vals:
            st.markdown("**Fundamental indicators**")
            fund_rows = []
            for key, v in fund_vals.items():
                if not v["enabled"]:
                    continue
                fund_rows.append({
                    "Indicator": v["label"],
                    "Current value": v["display"],
                    "Threshold": v["threshold"],
                    "Result": "✅ Pass" if v["passed"] else "❌ Fail",
                })
            if fund_rows:
                st.dataframe(pd.DataFrame(fund_rows), use_container_width=True, hide_index=True)

        if tech_vals:
            st.markdown("**Technical indicators**")
            tech_rows = []
            for key, v in tech_vals.items():
                if not v["enabled"]:
                    continue
                tech_rows.append({
                    "Indicator": v["label"],
                    "Current value": v["display"],
                    "Threshold": v["threshold"],
                    "Result": "✅ Pass" if v["passed"] else "❌ Fail",
                })
            if tech_rows:
                st.dataframe(pd.DataFrame(tech_rows), use_container_width=True, hide_index=True)

# ── Main panel ────────────────────────────────────────────────────────────────
if not run:
    st.info("Configure your rules in the sidebar, then click **Run Screener**.")
    st.stop()

results = []
all_tickers_list = [(t, False) for t in tickers] + [(t, True) for t in etf_tickers]
progress = st.progress(0, text="Starting...")

for i, (ticker, is_etf) in enumerate(all_tickers_list):
    progress.progress((i + 1) / len(all_tickers_list), text=f"Analyzing {ticker}...")
    result = score_stock(
        ticker,
        etf_mode=is_etf,
        fund_rules=runtime_fundamental,
        tech_rules=runtime_technical,
        threshold=etf_pass_pct / 100 if is_etf else pass_pct / 100,
    )
    if result:
        results.append(result)

progress.empty()
results.sort(key=lambda x: x["score"], reverse=True)

if not results:
    st.warning("No results returned. Check your tickers.")
    st.stop()

# ── Summary metrics ───────────────────────────────────────────────────────────
passed = [r for r in results if r["passed"]]
failed = [r for r in results if not r["passed"]]

col1, col2, col3 = st.columns(3)
col1.metric("Screened", len(results))
col2.metric("Passed",   len(passed))
col3.metric("Failed",   len(failed))

st.divider()

# ── Results table + expanders ─────────────────────────────────────────────────
def build_table(result_list):
    rows = []
    for r in result_list:
        rows.append({
            "Ticker":  r["ticker"],
            "Name":    r.get("name", r["ticker"]),
            "Sector":  r.get("sector", "N/A"),
            "Price":   f"${r['price']:.2f}" if r.get("price") else "N/A",
            "Score":   f"{r['score']*100:.0f}%",
            "Rules":   f"{r['rules_passed']}/{r['total_rules']}",
        })
    return pd.DataFrame(rows)

if passed:
    st.subheader(f"✅ Watchlist ({len(passed)} stocks)")
    st.dataframe(build_table(passed), use_container_width=True, hide_index=True)
    st.markdown("**Expand a stock to see full indicator details:**")
    for r in passed:
        render_detail_expander(r)

st.divider()

if failed:
    st.subheader(f"❌ Did not pass ({len(failed)} stocks)")
    st.dataframe(build_table(failed), use_container_width=True, hide_index=True)
    st.markdown("**Expand a stock to see full indicator details:**")
    for r in failed:
        render_detail_expander(r)

# ── Export ────────────────────────────────────────────────────────────────────
st.divider()
csv = build_table(results).to_csv(index=False)
st.download_button("Download results as CSV", csv, "screener_results.csv", "text/csv")