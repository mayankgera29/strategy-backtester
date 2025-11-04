import sys
import json
from datetime import datetime

def parse_time(s):
    # handles ISO timestamps produced by the simulator
    try:
        return datetime.fromisoformat(s)
    except Exception:
        # fallback: try removing timezone Z or fractions
        return datetime.fromisoformat(s.split('+')[0])

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/print_backtest.py <backtest_json_file>")
        sys.exit(1)

    fn = sys.argv[1]
    with open(fn) as f:
        data = json.load(f)

    # support both API-wrapped result and raw result object
    wrapper = "result" in data
    trades = data.get("result", {}).get("trades", []) if wrapper else data.get("trades", [])
    metrics = data.get("result", {}).get("metrics", {}) if wrapper else data.get("metrics", {})

    print("METRICS:")
    if metrics:
        for k, v in metrics.items():
            print(f"  {k}: {v}")
    else:
        print("  (no metrics found)")
    print(f"Number of trades: {len(trades)}\n")

    if not trades:
        print("No trades in this backtest.")
        return

    for i, t in enumerate(trades, 1):
        entry_time = t.get("entry_time")
        exit_time = t.get("exit_time")
        entry_price = t.get("entry_price")
        exit_price = t.get("exit_price")
        pnl = t.get("pnl")
        reason = t.get("exit_reason", "n/a")

        # duration in seconds and in bars (if timestamps parse)
        duration_sec = None
        duration_bars = None
        try:
            et = parse_time(entry_time)
            xt = parse_time(exit_time)
            duration_sec = (xt - et).total_seconds()
        except Exception:
            duration_sec = None

        # estimate bars if timestamps are evenly spaced: count bars between times in trades list not available here,
        # so show duration in seconds and leave bars None.
        print(f"Trade {i}: entry={entry_price} at {entry_time} | exit={exit_price} at {exit_time} | pnl={pnl} | reason={reason}")
        if duration_sec is not None:
            print(f"         duration: {duration_sec} seconds")
        print()

if __name__ == '__main__':
    main()
