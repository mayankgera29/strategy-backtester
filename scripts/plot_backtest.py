import sys
import json
from datetime import datetime
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/plot_backtest.py <backtest_json_file>")
        sys.exit(1)

    fn = sys.argv[1]
    with open(fn) as f:
        data = json.load(f)

    trades = data.get("result", {}).get("trades", []) if "result" in data else data.get("trades", [])
    metrics = data.get("result", {}).get("metrics", {}) if "result" in data else data.get("metrics", {})

    print("METRICS:")
    if metrics:
        for k, v in metrics.items():
            print(f"  {k}: {v}")
    else:
        print("  (no metrics found)")

    # build equity (cumulative pnl) over trade exit times
    if trades:
        trades_sorted = sorted(trades, key=lambda t: t["exit_time"])
        times = [datetime.fromisoformat(t["exit_time"]) for t in trades_sorted]
        pnls = [t["pnl"] for t in trades_sorted]
        cum = []
        s = 0.0
        for p in pnls:
            s += p
            cum.append(s)

        plt.plot(times, cum, marker='o')
        plt.title("Equity curve (trade-based)")
        plt.xlabel("Exit time")
        plt.ylabel("Cumulative PnL")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    else:
        print("No trades to plot.")

if __name__ == '__main__':
    main()
