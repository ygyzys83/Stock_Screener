import pandas as pd
import numpy as np
from config import RULES_TECHNICAL as DEFAULT_RULES


def check_rsi_breakout(df: pd.DataFrame, rules: dict) -> bool:
    rule = rules["rsi_breakout"]
    close = df["Close"]
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]
    return rule["min"] <= current_rsi <= rule["max"]


def check_macd_crossover(df: pd.DataFrame, rules: dict) -> bool:
    close = df["Close"]
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    for i in range(-3, 0):
        if macd.iloc[i] > signal.iloc[i] and macd.iloc[i - 1] <= signal.iloc[i - 1]:
            return True
    return False


def _detect_volatility_squeeze(
    bandwidth: pd.Series,
    window: int = 60,
    percentile_threshold: float = 0.20,
    lookback_periods: int = 3,
) -> pd.Series:
    """
    Returns a boolean Series. True means a confirmed squeeze is active
    (bandwidth has been at or below the rolling percentile threshold
    for at least `lookback_periods` consecutive bars).

    Parameters:
    -----------
    bandwidth         : Bollinger Band width series ( (upper - lower) / mid )
    window            : lookback window for the rolling percentile calculation
    percentile_threshold : percentile level that defines "tight" (e.g. 0.20 = 20th)
    lookback_periods  : number of consecutive bars that must be tight to confirm a squeeze
    """
    rolling_percentile = bandwidth.rolling(window=window).apply(
        lambda x: np.percentile(x, percentile_threshold * 100),
        raw=True,
    )
    is_at_threshold = bandwidth <= rolling_percentile
    is_confirmed_squeeze = (
        is_at_threshold.rolling(window=lookback_periods).sum() == lookback_periods
    )
    return is_confirmed_squeeze


def check_bb_squeeze(df: pd.DataFrame, rules: dict) -> bool:
    """
    Returns True if a confirmed Bollinger Band squeeze is active on the most
    recent bar. Uses a rolling percentile threshold and requires the squeeze
    to have persisted for multiple consecutive bars to filter out noise.
    """
    rule = rules["bb_squeeze"]
    close = df["Close"]
    sma20 = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    upper = sma20 + (2 * std20)
    lower = sma20 - (2 * std20)
    bandwidth = (upper - lower) / sma20

    squeeze_series = _detect_volatility_squeeze(
        bandwidth,
        window=rule.get("window", 60),
        percentile_threshold=rule.get("percentile_threshold", 0.20),
        lookback_periods=rule.get("lookback_periods", 3),
    )
    return bool(squeeze_series.iloc[-1])


def check_ma_confluence(df: pd.DataFrame, rules: dict) -> bool:
    close = df["Close"]
    ma50  = close.rolling(window=50).mean().iloc[-1]
    ma200 = close.rolling(window=200).mean().iloc[-1]
    price = close.iloc[-1]
    return price > ma50 and price > ma200


def check_rel_volume_surge(df: pd.DataFrame, rules: dict) -> bool:
    rule = rules["rel_volume_surge"]
    avg_vol   = df["Volume"].iloc[-21:-1].mean()
    today_vol = df["Volume"].iloc[-1]
    if avg_vol == 0:
        return False
    return (today_vol / avg_vol) >= rule["min_multiplier"]


def run_technical_checks(df: pd.DataFrame, rules: dict = None) -> dict:
    if rules is None:
        rules = DEFAULT_RULES
    df = df.copy()
    results = {}
    rule_map = {
        "rsi_breakout":     check_rsi_breakout,
        "macd_crossover":   check_macd_crossover,
        "bb_squeeze":       check_bb_squeeze,
        "ma_confluence":    check_ma_confluence,
        "rel_volume_surge": check_rel_volume_surge,
    }
    for rule_name, check_fn in rule_map.items():
        if rules[rule_name]["enabled"]:
            try:
                results[rule_name] = check_fn(df, rules)
            except Exception as e:
                print(f"    [!] Error in {rule_name}: {e}")
                results[rule_name] = False
    return results


def get_technical_values(df: pd.DataFrame, rules: dict = None) -> dict:
    """Calculates and returns the actual current technical indicator values for display."""
    if rules is None:
        rules = DEFAULT_RULES
    df = df.copy()

    # ── RSI ──────────────────────────────────────────────────────────────────
    try:
        close = df["Close"]
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi_series = 100 - (100 / (1 + rs))
        rsi_val = round(float(rsi_series.iloc[-1]), 2)
        rsi_min = rules["rsi_breakout"]["min"]
        rsi_max = rules["rsi_breakout"]["max"]
        rsi_passed = rsi_min <= rsi_val <= rsi_max
        rsi_display   = f"{rsi_val}"
        rsi_threshold = f"between {rsi_min} and {rsi_max}"
    except Exception:
        rsi_val, rsi_display, rsi_passed, rsi_threshold = None, "N/A", False, "N/A"

    # ── MACD ─────────────────────────────────────────────────────────────────
    try:
        close  = df["Close"]
        ema12  = close.ewm(span=12, adjust=False).mean()
        ema26  = close.ewm(span=26, adjust=False).mean()
        macd   = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_val   = round(float(macd.iloc[-1]), 4)
        signal_val = round(float(signal.iloc[-1]), 4)
        hist_val   = round(macd_val - signal_val, 4)
        crossed = any(
            macd.iloc[i] > signal.iloc[i] and macd.iloc[i - 1] <= signal.iloc[i - 1]
            for i in range(-3, 0)
        )
        macd_display   = f"MACD {macd_val}  |  Signal {signal_val}  |  Hist {hist_val}"
        macd_threshold = "MACD crossed above signal in last 3 bars"
        macd_passed    = crossed
    except Exception:
        macd_display, macd_threshold, macd_passed = "N/A", "N/A", False

    # ── Bollinger Band Squeeze ────────────────────────────────────────────────
    try:
        close     = df["Close"]
        sma20     = close.rolling(window=20).mean()
        std20     = close.rolling(window=20).std()
        upper     = sma20 + (2 * std20)
        lower     = sma20 - (2 * std20)
        bandwidth = (upper - lower) / sma20

        bb_window      = rules["bb_squeeze"].get("window", 60)
        bb_pct         = rules["bb_squeeze"].get("percentile_threshold", 0.20)
        bb_lookback    = rules["bb_squeeze"].get("lookback_periods", 3)

        squeeze_series  = _detect_volatility_squeeze(bandwidth, bb_window, bb_pct, bb_lookback)
        bb_passed       = bool(squeeze_series.iloc[-1])

        current_bw      = round(float(bandwidth.iloc[-1]), 4)
        rolling_pct_val = round(float(
            bandwidth.rolling(window=bb_window).apply(
                lambda x: np.percentile(x, bb_pct * 100), raw=True
            ).iloc[-1]
        ), 4)

        bb_display   = (
            f"Bandwidth {current_bw}  |  "
            f"{int(bb_pct*100)}th percentile {rolling_pct_val}  |  "
            f"Squeeze confirmed for {bb_lookback} bars: {'Yes' if bb_passed else 'No'}"
        )
        bb_threshold = (
            f"Bandwidth ≤ {int(bb_pct*100)}th percentile "
            f"for {bb_lookback}+ consecutive bars"
        )
    except Exception:
        bb_display, bb_threshold, bb_passed = "N/A", "N/A", False

    # ── Moving Average Confluence ─────────────────────────────────────────────
    try:
        close  = df["Close"]
        price  = round(float(close.iloc[-1]), 2)
        ma50   = round(float(close.rolling(window=50).mean().iloc[-1]), 2)
        ma200  = round(float(close.rolling(window=200).mean().iloc[-1]), 2)
        ma_passed    = price > ma50 and price > ma200
        ma_display   = f"Price {price}  |  50-day MA {ma50}  |  200-day MA {ma200}"
        ma_threshold = "Price above both 50-day and 200-day MA"
    except Exception:
        ma_display, ma_threshold, ma_passed = "N/A", "N/A", False

    # ── Relative Volume ───────────────────────────────────────────────────────
    try:
        avg_vol   = round(float(df["Volume"].iloc[-21:-1].mean()), 0)
        today_vol = round(float(df["Volume"].iloc[-1]), 0)
        ratio     = round(today_vol / avg_vol, 2) if avg_vol > 0 else 0
        min_mult  = rules["rel_volume_surge"]["min_multiplier"]
        rvol_passed    = ratio >= min_mult
        rvol_display   = f"{ratio}x  (today {int(today_vol):,}  |  20-day avg {int(avg_vol):,})"
        rvol_threshold = f"≥ {min_mult}x average volume"
    except Exception:
        rvol_display, rvol_threshold, rvol_passed = "N/A", "N/A", False

    return {
        "rsi_breakout": {
            "label":     "RSI (14)",
            "display":   rsi_display,
            "threshold": rsi_threshold,
            "passed":    rsi_passed,
            "enabled":   rules["rsi_breakout"]["enabled"],
        },
        "macd_crossover": {
            "label":     "MACD",
            "display":   macd_display,
            "threshold": macd_threshold,
            "passed":    macd_passed,
            "enabled":   rules["macd_crossover"]["enabled"],
        },
        "bb_squeeze": {
            "label":     "Bollinger Band Squeeze",
            "display":   bb_display,
            "threshold": bb_threshold,
            "passed":    bb_passed,
            "enabled":   rules["bb_squeeze"]["enabled"],
        },
        "ma_confluence": {
            "label":     "MA Confluence",
            "display":   ma_display,
            "threshold": ma_threshold,
            "passed":    ma_passed,
            "enabled":   rules["ma_confluence"]["enabled"],
        },
        "rel_volume_surge": {
            "label":     "Relative Volume",
            "display":   rvol_display,
            "threshold": rvol_threshold,
            "passed":    rvol_passed,
            "enabled":   rules["rel_volume_surge"]["enabled"],
        },
    }