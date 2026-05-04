# Stock Screener

A Python-based stock and ETF screening tool with a Streamlit web UI. Screen stocks against a configurable set of fundamental and technical rules, adjust thresholds in real time, and export results to CSV — no paid API required.

---

## Features

- Screen stocks and ETFs against up to 10 configurable rules
- Adjust rule thresholds (P/E, P/B, PEG, etc.) live in the UI without touching code
- Enable or disable individual rules per screening session
- Separate pass thresholds for stocks vs ETFs
- Expandable per-stock detail view showing actual current indicator values
- Export results to CSV
- Also runnable as a command-line script (`main.py`)

---

## Tech stack

- [yfinance](https://github.com/ranaroussi/yfinance) — market data (no API key required)
- [Streamlit](https://streamlit.io) — web UI
- [pandas](https://pandas.pydata.org) — data manipulation
- [tabulate](https://github.com/astanin/python-tabulate) — CLI results formatting

---

## Project structure

```
stock_screener/
├── app.py                  # Streamlit web app — main entry point
├── main.py                 # Command-line entry point
├── config.py               # Default tickers, rules, and thresholds
├── data_fetcher.py         # Pulls price history and fundamentals via yfinance
├── fundamental_rules.py    # P/E, P/B, PEG, FCF yield, D/E checks
├── technical_rules.py      # RSI, MACD, Bollinger Bands, MA, volume checks
├── screener.py             # Orchestrates data fetching, rule evaluation, scoring
├── results.py              # CLI results display and CSV export
├── requirements.txt        # Python dependencies
├── .env                    # API keys if added in future (never committed)
└── .gitignore
```

---

## Installation

**Requirements:** Python 3.12+

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/stock-screener.git
   cd stock-screener
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # macOS / Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Web app (recommended)

```bash
streamlit run app.py
```

Opens at `http://localhost:8501` in your browser.

### Command line

```bash
python main.py
```

Prints results to the terminal and saves a `screener_results.csv` file.

---

## Configuration

Default tickers, rule thresholds, and pass percentages are set in `config.py`. When using the web app, all of these can be adjusted live in the sidebar without editing any files.

### Default tickers

```python
TICKERS = ["AAPL", "MSFT", "GOOGL", ...]   # stocks
ETF_TICKERS = ["SPY", "QQQ", "VTI", ...]   # ETFs (technical rules only)
```

### Pass threshold

A stock must pass at least this percentage of enabled rules to be added to the watchlist. Default is 80%.

---

## Screening rules

### Fundamental rules (stocks only)

| Rule | Default threshold | Description |
|---|-------------------|---|
| P/E Ratio | < 15              | Price-to-earnings ratio |
| P/B Ratio | < 2.0             | Price-to-book ratio |
| PEG Ratio | < 1.0             | Price/earnings-to-growth ratio |
| FCF Yield | > 7%              | Free cash flow divided by market cap |
| D/E Ratio | < 1.0             | Total debt divided by shareholders' equity |

### Technical rules (stocks and ETFs)

| Rule | Description |
|---|---|
| RSI Breakout | 14-day RSI is in the momentum-building zone (default 50–70) |
| MACD Crossover | MACD line crossed above the signal line in the last 3 bars |
| Bollinger Band Squeeze | Band width is in the lowest 20% of the past 60 bars |
| MA Confluence | Price is above both the 50-day and 200-day simple moving averages |
| Relative Volume Surge | Today's volume is at least 1.5x the 20-day average |

> ETFs are evaluated on technical rules only, since metrics like P/E and FCF yield are not meaningful for funds.

---

## Data source

All data is fetched from Yahoo Finance via `yfinance`. This is free and requires no API key for personal use. Price history is used for technical indicators; fundamental data is pulled from Yahoo's company info endpoint.

Note: `yfinance` is an unofficial library — Yahoo Finance could change their API at any time. It is suitable for personal research and development but not recommended for production trading systems.

---

## Adding a paid API (optional)

If you later add a paid data provider (Finnhub, Twelve Data, Polygon, etc.), store your API key in a `.env` file and never commit it:

```
# .env
FINNHUB_API_KEY=your_key_here
```

Load it in code with:

```python
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("FINNHUB_API_KEY")
```

Install the helper: `pip install python-dotenv`

---

## Disclaimer

This tool is for research and educational purposes only. Nothing in this project constitutes financial advice. Always do your own research before making investment decisions.
