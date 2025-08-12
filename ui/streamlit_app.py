"""Streamlit UI for signal analysis."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Ensure the repository root is on sys.path when running via `streamlit run`
sys.path.append(str(Path(__file__).resolve().parents[1]))

from signals import (
    Config,
    analyze_ticker,
    compute_core_indicators,
    compute_buy_timing,
    pick_strategies,
)
from signals.analysis import fetch_history

cfg = Config()

st.set_page_config(page_title="Stock Signal", page_icon="📈")
st.title("📈 Stock Signal & Option Ideas")

with st.sidebar:
    tickers_input = st.text_input("Tickers", value="AAPL")
    min_price = st.number_input("Min price", value=cfg.min_price)
    min_vol = st.number_input("Min avg $ volume", value=cfg.min_avg_dollar_vol)
    show_timing = st.checkbox("Show Buy Timing", value=True)
    show_opts = st.checkbox("Show Options Strategies", value=True)
    run_btn = st.button("Run", type="primary")

if run_btn:
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    rows = []
    for t in tickers:
        row = analyze_ticker(t, min_price, min_vol)
        if show_timing or show_opts:
            try:
                ind = compute_core_indicators(t)
                timing = compute_buy_timing(ind, cfg)
            except Exception as exc:  # pragma: no cover - UI fallback
                timing = {"buy_signal": False, "timing_note": str(exc), "rationale": []}
                ind = None
            if show_timing:
                row["BuySignal"] = timing["buy_signal"]
                row["TimingNote"] = timing["timing_note"]
            if show_opts:
                strategies = pick_strategies(ind["price"], None, 0, cfg) if timing["buy_signal"] and ind else []
                row["Strategies"] = strategies
        rows.append(row)

    df = pd.DataFrame(rows)
    table_cols = ["Ticker", "Recommendation", "Reasons"]
    if show_timing:
        table_cols += ["BuySignal", "TimingNote"]
    st.dataframe(df[table_cols])

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name="signals.csv", mime="text/csv")

    if tickers:
        hist = fetch_history(tickers[0])
        if not hist.empty:
            chart_df = pd.DataFrame(
                {
                    "Close": hist["Close"],
                    "SMA20": hist["Close"].rolling(20).mean(),
                    "SMA50": hist["Close"].rolling(50).mean(),
                    "SMA200": hist["Close"].rolling(200).mean(),
                }
            )
            st.line_chart(chart_df)

    if show_opts:
        for r in rows:
            if r.get("Strategies"):
                with st.expander(f"Strategies for {r['Ticker']}"):
                    for strat in r["Strategies"]:
                        st.write(f"**{strat['name']}** (exp {strat['expiry']})")
                        st.write(strat["legs"])
                        st.write(strat["estimates"])
        st.caption("Estimates (model). Not live quotes.")
else:
    st.info("Enter tickers and press Run to view signals.")
