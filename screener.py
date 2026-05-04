from config import (
    TICKERS, ETF_TICKERS,
    RULES_FUNDAMENTAL, RULES_TECHNICAL,
    PASS_THRESHOLD, ETF_PASS_THRESHOLD
)
from data_fetcher import get_fundamentals, get_price_history
from fundamental_rules import run_fundamental_checks, get_fundamental_values
from technical_rules import run_technical_checks, get_technical_values


def score_stock(
    ticker: str,
    etf_mode: bool = False,
    fund_rules: dict = None,
    tech_rules: dict = None,
    threshold: float = None,
) -> dict | None:
    if fund_rules is None:
        fund_rules = RULES_FUNDAMENTAL
    if tech_rules is None:
        tech_rules = RULES_TECHNICAL
    if threshold is None:
        threshold = ETF_PASS_THRESHOLD if etf_mode else PASS_THRESHOLD

    print(f"  Analyzing {ticker}...")

    price_history = get_price_history(ticker)
    if price_history is None:
        return None

    technical_results = run_technical_checks(price_history, tech_rules)
    technical_values  = get_technical_values(price_history, tech_rules)

    if etf_mode:
        all_results       = technical_results
        raw_values        = {"technical": technical_values, "fundamental": {}}
        name              = ticker
        sector            = "ETF"
        price             = float(price_history["Close"].iloc[-1])
    else:
        fundamentals = get_fundamentals(ticker)
        if fundamentals is None:
            return None
        fundamental_results = run_fundamental_checks(fundamentals, fund_rules)
        fundamental_values  = get_fundamental_values(fundamentals, fund_rules)
        all_results         = {**fundamental_results, **technical_results}
        raw_values          = {"fundamental": fundamental_values, "technical": technical_values}
        name                = fundamentals.get("name", ticker)
        sector              = fundamentals.get("sector", "N/A")
        price               = fundamentals.get("price") or float(price_history["Close"].iloc[-1])

    total_rules  = len(all_results)
    rules_passed = sum(1 for v in all_results.values() if v)
    score        = rules_passed / total_rules if total_rules > 0 else 0

    return {
        "ticker":       ticker,
        "name":         name,
        "sector":       sector,
        "price":        price,
        "score":        score,
        "rules_passed": rules_passed,
        "total_rules":  total_rules,
        "passed":       score >= threshold,
        "rule_details": all_results,
        "raw_values":   raw_values,
    }


def run_screener(
    tickers: list = None,
    etf_tickers: list = None,
    fund_rules: dict = None,
    tech_rules: dict = None,
    stock_threshold: float = None,
    etf_threshold: float = None,
) -> list:
    if tickers is None:
        tickers = TICKERS
    if etf_tickers is None:
        etf_tickers = ETF_TICKERS

    results = []

    for ticker in tickers:
        result = score_stock(ticker, etf_mode=False,
                             fund_rules=fund_rules, tech_rules=tech_rules,
                             threshold=stock_threshold)
        if result:
            results.append(result)

    for ticker in etf_tickers:
        result = score_stock(ticker, etf_mode=True,
                             fund_rules=fund_rules, tech_rules=tech_rules,
                             threshold=etf_threshold)
        if result:
            results.append(result)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results