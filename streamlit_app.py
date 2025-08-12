"""Streamlit interface for the stock signal summarizer."""

from __future__ import annotations

import json
import streamlit as st

from stock_signal import Config, summarize


st.set_page_config(page_title="Stock Signal", page_icon="📈")
st.title("📈 Stock Signal & Option Ideas")


with st.sidebar:
    st.header("Inputs")
    ticker = st.text_input("Ticker", value="AAPL").strip().upper()
    iv_rank = st.number_input("IV Rank", min_value=0.0, max_value=100.0, value=10.0)
    shares = st.number_input("Holding shares", min_value=0, step=100, value=0)
    run_btn = st.button("Analyze", type="primary")


if run_btn:
    try:
        result = summarize(ticker, iv_rank=iv_rank, holding_shares=shares, cfg=Config())
    except Exception as exc:  # pragma: no cover - UI feedback
        st.error(str(exc))
    else:
        st.subheader(f"Summary for {result['ticker']}")
        st.write("**Buy signal:**", result["buy_signal"])
        st.write(result["timing_note"])
        if result["rationale"]:
            st.write("### Rationale")
            for r in result["rationale"]:
                st.write(f"- {r}")
        st.write("### Indicators")
        st.json(result["indicators"])
        if result["selected_strategies"]:
            st.write("### Strategies")
            for strat in result["selected_strategies"]:
                st.write(f"**{strat['name']}**")
                st.json(strat)
        st.caption(result["disclaimer"])
else:
    st.info("Enter a ticker and press Analyze to view signals.")

