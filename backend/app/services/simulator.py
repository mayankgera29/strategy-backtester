from typing import Dict, Any, Optional
import pandas as pd
from dataclasses import dataclass
import os
import asyncio

@dataclass
class Trade:
    entry_time: str
    exit_time: str
    entry_price: float
    exit_price: float
    qty: float
    pnl: float
    exit_reason: Optional[str] = None

def load_ohlcv_from_csv(symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
    path = os.path.join("backend", "data", f"{symbol}_{timeframe}.csv")
    if not os.path.exists(path):
        alt = os.path.join("data", f"{symbol}_{timeframe}.csv")
        if os.path.exists(alt):
            path = alt
        else:
            raise FileNotFoundError(f"Historical data not found: {path} or {alt}")
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df = df.set_index("timestamp").sort_index()
    if start:
        df = df.loc[start:]
    if end:
        df = df.loc[:end]
    return df

def run_sma_crossover(
    df: pd.DataFrame,
    fast: int = 20,
    slow: int = 50,
    force_close: bool = True,
    sl_pct: Optional[float] = None,
    tp_pct: Optional[float] = None,
):
    """
    Simple SMA crossover with optional percent-based stop-loss and take-profit.
    sl_pct/tp_pct are fractional (e.g. 0.03 for 3%).
    Exits are checked on each bar's close price.
    """
    df = df.copy()
    df["sma_fast"] = df["close"].rolling(window=fast, min_periods=1).mean()
    df["sma_slow"] = df["close"].rolling(window=slow, min_periods=1).mean()

    position = 0
    entry_price = None
    entry_time = None
    trades = []

    for t, row in df.iterrows():
        price = float(row["close"])

        # entry signal
        if position == 0 and row["sma_fast"] > row["sma_slow"]:
            position = 1
            entry_price = price
            entry_time = t.isoformat()
            continue

        # if in position, check exit conditions in order:
        if position == 1:
            # 1) TP
            if tp_pct is not None:
                ret = (price - entry_price) / entry_price
                if ret >= tp_pct:
                    exit_price = price
                    exit_time = t.isoformat()
                    pnl = exit_price - entry_price
                    trades.append(Trade(entry_time=entry_time, exit_time=exit_time,
                                        entry_price=entry_price, exit_price=exit_price,
                                        qty=1, pnl=pnl, exit_reason="tp").__dict__)
                    position = 0
                    entry_price = None
                    entry_time = None
                    continue

            # 2) SL
            if sl_pct is not None:
                ret = (price - entry_price) / entry_price
                if ret <= -abs(sl_pct):
                    exit_price = price
                    exit_time = t.isoformat()
                    pnl = exit_price - entry_price
                    trades.append(Trade(entry_time=entry_time, exit_time=exit_time,
                                        entry_price=entry_price, exit_price=exit_price,
                                        qty=1, pnl=pnl, exit_reason="sl").__dict__)
                    position = 0
                    entry_price = None
                    entry_time = None
                    continue

            # 3) SMA cross-down normal exit
            if row["sma_fast"] < row["sma_slow"]:
                exit_price = price
                exit_time = t.isoformat()
                pnl = exit_price - entry_price
                trades.append(Trade(entry_time=entry_time, exit_time=exit_time,
                                    entry_price=entry_price, exit_price=exit_price,
                                    qty=1, pnl=pnl, exit_reason="sma_cross").__dict__)
                position = 0
                entry_price = None
                entry_time = None
                continue

    # Force-close any open position at the last available bar's close if requested
    if force_close and position == 1 and entry_price is not None:
        last_idx = df.index[-1]
        last_close = float(df.iloc[-1]["close"])
        exit_time = last_idx.isoformat()
        pnl = last_close - entry_price
        trades.append(Trade(entry_time=entry_time, exit_time=exit_time,
                            entry_price=entry_price, exit_price=last_close,
                            qty=1, pnl=pnl, exit_reason="force_close").__dict__)
    return trades

def compute_metrics(trades: list) -> Dict[str, Any]:
    total_pnl = sum(t["pnl"] for t in trades)
    wins = [t for t in trades if t["pnl"] > 0]
    win_rate = len(wins) / len(trades) if trades else None
    avg_pnl = total_pnl / len(trades) if trades else None
    return {"total_pnl": total_pnl, "trades_count": len(trades), "win_rate": win_rate, "avg_pnl": avg_pnl}

async def run_backtest_simulation(payload: Dict[str, Any]) -> Dict[str, Any]:
    def _run():
        symbol = payload.get("symbol")
        timeframe = payload.get("timeframe", "1m")
        start = payload.get("start")
        end = payload.get("end")
        params = payload.get("params", {}) or {}
        fast = int(params.get("fast", 20))
        slow = int(params.get("slow", 50))
        sl = params.get("sl", None)
        tp = params.get("tp", None)
        sl_pct = float(sl) if sl is not None else None
        tp_pct = float(tp) if tp is not None else None
        force_close = bool(payload.get("force_close", True))
        df = load_ohlcv_from_csv(symbol, timeframe, start, end)
        trades = run_sma_crossover(df, fast=fast, slow=slow, force_close=force_close, sl_pct=sl_pct, tp_pct=tp_pct)
        metrics = compute_metrics(trades)
        return {"trades": trades, "metrics": metrics}
    result = await asyncio.to_thread(_run)
    return result
