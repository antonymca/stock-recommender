#!/usr/bin/env python3
"""Command line interface for stock signals and option ideas."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Dict
import datetime as dt

import pandas as pd

from signals import (
    Config,
    analyze_ticker,
    compute_core_indicators,
    compute_buy_timing,
    pick_strategies,
)
from signals.sell_decision import Position, PositionType, SellConfig, decide_sell


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AI Signal Bot (free data via yfinance)")
    p.add_argument("--tickers", type=str, default="")
    p.add_argument("--tickers-file", type=str, default="")
    p.add_argument("--min-price", type=float, default=5.0)
    p.add_argument("--min-dollar-vol", type=float, default=5_000_000)
    p.add_argument("--output", type=str, default="")
    p.add_argument("--include-timing", dest="include_timing", action="store_true", default=True)
    p.add_argument("--no-include-timing", dest="include_timing", action="store_false")
    p.add_argument("--include-options", dest="include_options", action="store_true", default=True)
    p.add_argument("--no-include-options", dest="include_options", action="store_false")
    p.add_argument("--legacy-output", action="store_true", help="Hide new columns for backward compatibility")
    p.add_argument("--sell-decision", action="store_true", help="Run sell decision engine")
    p.add_argument("--ticker", type=str, default="")
    p.add_argument("--type", type=str, default="")
    p.add_argument("--expiry", type=str, default="")
    p.add_argument("--strike", type=float, default=0.0)
    p.add_argument("--short-strike", type=float, default=None)
    p.add_argument("--entry", type=float, default=0.0)
    p.add_argument("--entry-date", type=str, default="")
    p.add_argument("--qty", type=int, default=1)
    p.add_argument("--peak", type=float, default=None)
    return p.parse_args()


def load_universe(args: argparse.Namespace) -> List[str]:
    tickers: List[str] = []
    if args.tickers:
        tickers += [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    if args.tickers_file:
        with open(args.tickers_file, "r") as f:
            for line in f:
                sym = line.strip().upper()
                if sym:
                    tickers.append(sym)
    return sorted(list(set(tickers)))


def main() -> None:
    args = parse_args()
    if args.sell_decision:
        if not args.ticker or not args.type or not args.expiry or not args.strike or not args.entry:
            print("Missing required sell-decision parameters.")
            sys.exit(1)
        pos = Position(
            ticker=args.ticker.upper(),
            expiry=dt.datetime.strptime(args.expiry, "%Y-%m-%d").date(),
            type=PositionType[args.type],
            long_strike=args.strike,
            short_strike=args.short_strike,
            entry_price=args.entry,
            entry_date=dt.datetime.strptime(args.entry_date, "%Y-%m-%d").date()
            if args.entry_date
            else dt.date.today(),
            quantity=args.qty,
        )
        cfg = SellConfig()
        decision = decide_sell(pos, cfg, prev_peak=args.peak)
        print(json.dumps(decision, default=str))
        return

    universe = load_universe(args)
    if not universe:
        print("No tickers provided. Use --tickers or --tickers-file.")
        sys.exit(1)

    cfg = Config()
    rows: List[Dict] = []
    for t in universe:
        try:
            row = analyze_ticker(t, args.min_price, args.min_dollar_vol)
            if args.include_timing or args.include_options:
                ind = compute_core_indicators(t)
                timing = compute_buy_timing(ind, cfg)
                if args.include_timing:
                    row["BuySignal"] = timing["buy_signal"]
                    row["TimingNote"] = timing["timing_note"]
                    row["NoBuyReason"] = timing.get("no_buy_reason")
                if args.include_options:
                    strategies = pick_strategies(
                        ind["price"], None, 0, cfg, timing["buy_signal"]
                    )
                    row["OptionStrategiesJSON"] = json.dumps(strategies)
            rows.append(row)
        except Exception as exc:
            rows.append({"Ticker": t, "Error": str(exc)})

    df = pd.DataFrame(rows)
    base_cols = [
        "Ticker",
        "Price",
        "RSI14",
        "SMA20",
        "SMA50",
        "SMA200",
        "MACD",
        "MACDSignal",
        "ATR14",
        "AvgDollarVol20D",
        "Signals",
        "Recommendation",
        "Reasons",
        "Error",
    ]
    extra_cols = []
    if args.include_timing:
        extra_cols.extend(["BuySignal", "TimingNote", "NoBuyReason"])
    if args.include_options:
        extra_cols.append("OptionStrategiesJSON")
    cols = base_cols + ([] if args.legacy_output else extra_cols)
    for c in cols:
        if c not in df.columns:
            df[c] = None
    df = df[cols]

    rec_order = {"BUY": 0, "SELL": 1, "HOLD": 2}
    df["rec_rank"] = df["Recommendation"].map(rec_order).fillna(3)
    df["rsi_rank"] = df["RSI14"].fillna(100)
    df = df.sort_values(by=["rec_rank", "rsi_rank"], ascending=[True, True]).drop(columns=["rec_rank", "rsi_rank"])

    print(df.to_string(index=False))
    if args.output:
        df.to_csv(args.output, index=False)
        print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
