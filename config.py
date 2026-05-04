TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "TSLA", "NVDA", "JPM", "JNJ", "V",
    "UNH", "PG", "HD", "MA", "BAC",
]

ETF_TICKERS = ["SPY", "QQQ", "VTI", "SCHD"]

PASS_THRESHOLD = 0.80
ETF_PASS_THRESHOLD = 0.80

RULES_FUNDAMENTAL = {
    "pe_ratio":  {"max": 15,   "enabled": True},
    "pb_ratio":  {"max": 2,    "enabled": True},
    "peg_ratio": {"max": 1.0,    "enabled": True},
    "fcf_yield": {"min": 0.07, "enabled": True},
    "de_ratio":  {"max": 1,    "enabled": True},
}

RULES_TECHNICAL = {
    "rsi_breakout":     {"min": 0, "max": 50, "enabled": True},
    "macd_crossover":   {"enabled": True},
    "bb_squeeze":       {"enabled": True},
    "ma_confluence":    {"enabled": True},
    "rel_volume_surge": {"min_multiplier": 1.5, "enabled": True},
}