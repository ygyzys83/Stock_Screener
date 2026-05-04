import yfinance as yf
import pandas as pd


def get_fundamentals(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        market_cap = info.get("marketCap", None)
        free_cashflow = info.get("freeCashflow", None)
        fcf_yield = None
        if free_cashflow and market_cap and market_cap > 0:
            fcf_yield = free_cashflow / market_cap
        return {
            "ticker":   ticker,
            "pe_ratio": info.get("trailingPE", None),
            "pb_ratio": info.get("priceToBook", None),
            "peg_ratio":info.get("pegRatio", None),
            "fcf_yield":fcf_yield,
            "de_ratio": info.get("debtToEquity", None),
            "name":     info.get("shortName", ticker),
            "sector":   info.get("sector", "N/A"),
            "price":    info.get("currentPrice", None),
        }
    except Exception as e:
        print(f"  [!] Could not fetch fundamentals for {ticker}: {e}")
        return None


def get_price_history(ticker: str, period: str = "6mo") -> pd.DataFrame:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            print(f"  [!] No price history for {ticker}")
            return None
        return df
    except Exception as e:
        print(f"  [!] Could not fetch price history for {ticker}: {e}")
        return None