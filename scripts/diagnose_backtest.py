import pandas as pd
from pathlib import Path
from datetime import datetime

def load_df():
    p1 = Path("backend/data/BTCUSD_1m.csv")
    p2 = Path("data/BTCUSD_1m.csv")
    if p1.exists():
        path = p1
    elif p2.exists():
        path = p2
    else:
        raise FileNotFoundError(f"CSV not found at {p1} or {p2}")
    df = pd.read_csv(path, parse_dates=["timestamp"]).set_index("timestamp").sort_index()
    return df

def compute_smas(df, fast, slow):
    d = df.copy()
    d["sma_fast"] = d["close"].rolling(window=fast, min_periods=1).mean()
    d["sma_slow"] = d["close"].rolling(window=slow, min_periods=1).mean()
    d["fast_gt_slow"] = d["sma_fast"] > d["sma_slow"]
    d["signal"] = d["fast_gt_slow"].astype(int).diff().fillna(0).astype(int)
    return d

def find_trades_from_df(d):
    position = 0
    trades = []
    entry_price = None
    entry_time = None
    for t, row in d.iterrows():
        if position == 0 and row["sma_fast"] > row["sma_slow"]:
            position = 1
            entry_price = float(row["close"])
            entry_time = t
        elif position == 1 and row["sma_fast"] < row["sma_slow"]:
            exit_price = float(row["close"])
            exit_time = t
            pnl = exit_price - entry_price
            trades.append({
                "entry_time": entry_time.isoformat(),
                "exit_time": exit_time.isoformat(),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "pnl": pnl
            })
            position = 0
    return trades

def try_params(df, param_list):
    for fast, slow in param_list:
        print(f"\\n=== params fast={fast} slow={slow} ===")
        d = compute_smas(df, fast, slow)
        print("\\nLast 8 rows (timestamp, close, sma_fast, sma_slow, signal):")
        print(d[["close","sma_fast","sma_slow","signal"]].tail(8).to_string())
        crosses = d[d["signal"] == 1]
        if not crosses.empty:
            print("\\nCross-up events (fast crossed above slow):")
            print(crosses[["close","sma_fast","sma_slow","signal"]])
        else:
            print("\\nNo cross-up events detected for these params.")
        trades = find_trades_from_df(d)
        print(f"\\nTrades found: {len(trades)}")
        for tr in trades:
            print(" ", tr)
    print("\\nDone parameter sweep.")

def main():
    df = load_df()
    print("Loaded rows:", len(df))
    print(df.head().to_string())
    params = [(2,3),(2,4),(3,5),(5,8),(10,20),(2,50)]
    try_params(df, params)

if __name__ == '__main__':
    main()
