import csv
from tabulate import tabulate
from config import PASS_THRESHOLD


def print_results(results: list):
    watchlist = [r for r in results if r["passed"]]
    others    = [r for r in results if not r["passed"]]

    print("\n" + "═" * 70)
    print(f"  STOCK SCREENER RESULTS  |  Pass Threshold: {int(PASS_THRESHOLD*100)}%")
    print("═" * 70)

    if watchlist:
        print(f"\n✅  WATCHLIST ({len(watchlist)} stocks)\n")
        table_data = []
        for r in watchlist:
            table_data.append([
                r["ticker"],
                r["name"][:25],
                r["sector"][:20],
                f"${r['price']:.2f}" if r["price"] else "N/A",
                f"{r['rules_passed']}/{r['total_rules']}",
                f"{r['score']*100:.0f}%",
            ])
        print(tabulate(table_data,
                       headers=["Ticker", "Name", "Sector", "Price", "Rules", "Score"],
                       tablefmt="rounded_outline"))
    else:
        print("\n  No stocks passed all criteria.")

    print(f"\n📊  ALL STOCKS (sorted by score)\n")
    table_all = []
    for r in results:
        flag = "✅" if r["passed"] else "❌"
        table_all.append([
            flag,
            r["ticker"],
            f"{r['rules_passed']}/{r['total_rules']}",
            f"{r['score']*100:.0f}%",
        ])
    print(tabulate(table_all,
                   headers=["", "Ticker", "Rules Passed", "Score"],
                   tablefmt="simple"))

    if watchlist:
        print("\n" + "─" * 70)
        print("  RULE BREAKDOWN (Watchlist stocks)")
        print("─" * 70)
        for r in watchlist:
            print(f"\n  {r['ticker']} — {r['name']}")
            for rule, passed in r["rule_details"].items():
                icon = "  ✅" if passed else "  ❌"
                print(f"    {icon}  {rule.replace('_', ' ').title()}")


def save_results_csv(results: list, filename: str = "screener_results.csv"):
    if not results:
        return
    fieldnames = ["ticker", "name", "sector", "price", "score", "rules_passed",
                  "total_rules", "passed"] + list(results[0]["rule_details"].keys())
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            row = {k: r[k] for k in ["ticker", "name", "sector", "price",
                                      "score", "rules_passed", "total_rules", "passed"]}
            row.update(r["rule_details"])
            writer.writerow(row)
    print(f"\n💾  Results saved to {filename}")