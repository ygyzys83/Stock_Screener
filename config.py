TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "TSLA", "NVDA", "JPM", "JNJ", "V",
    "UNH", "PG", "HD", "MA", "BAC",
    "SNDK", "SNAP", "NKE", "CRWV", "CAG",
    "KMB", "LULU", "MSTR",
]

ETF_TICKERS = ["SPY", "QQQ", "VTI", "SCHD", "XLE", "GLD", "USO",
]

PASS_THRESHOLD = 0.80
ETF_PASS_THRESHOLD = 0.80

RULES_FUNDAMENTAL = {
    "pe_ratio":  {"max": 25,   "enabled": True},
    "pb_ratio":  {"max": 2,    "enabled": True},
    "peg_ratio": {"max": 1.0,    "enabled": True},
    "fcf_yield": {"min": 0.03, "enabled": True},
    "de_ratio":  {"max": 1,    "enabled": True},
}

RULES_TECHNICAL = {
    "rsi_breakout":     {"min": 0, "max": 50, "enabled": True},
    "macd_crossover":   {"enabled": True},
    "bb_squeeze":       {
        "enabled":              True,
        "window":               60,
        "percentile_threshold": 0.20,
        "lookback_periods":     3,
    },
    "ma_confluence":    {"enabled": True},
    "rel_volume_surge": {"min_multiplier": 1.5, "enabled": True},
    "golden_cross":     {"lookback_days": 90, "enabled": True},
    "death_cross":      {"lookback_days": 90, "enabled": False},  # disabled by default — bearish signal
}