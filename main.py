from config import TICKERS, ETF_TICKERS
from screener import run_screener
from results import print_results, save_results_csv

if __name__ == "__main__":
    print("=" * 70)
    print("  STOCK SCREENER  — Starting analysis...")
    print(f"  Screening {len(TICKERS)} stocks and {len(ETF_TICKERS)} ETFs\n")

    results = run_screener()
    print_results(results)
    save_results_csv(results)