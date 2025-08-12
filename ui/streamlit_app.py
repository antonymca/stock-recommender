"""Streamlit UI for signal analysis."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from datetime import date
import requests

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
from signals.sell_decision import (
    Position,
    PositionType,
    SellConfig,
    decide_sell,
)

cfg = Config()

st.set_page_config(page_title="Stock Signal", page_icon="📈")
st.title("📈 Stock Signal & Option Ideas")
tab_scan, tab_monitor = st.tabs(["Signals", "Positions Monitor"])

with st.sidebar:
    st.header("Scan")
    tickers_input = st.text_input("Tickers", value="AAPL")
    min_price = st.number_input("Min price", value=cfg.min_price)
    min_vol = st.number_input("Min avg $ volume", value=cfg.min_avg_dollar_vol)
    show_timing = st.checkbox("Show Buy Timing", value=True)
    show_opts = st.checkbox("Show Options Strategies", value=True)
    run_btn = st.button("Run", type="primary")
    st.divider()
    st.header("Positions")
    pos_ticker = st.text_input("Ticker", value="")
    pos_type = st.selectbox("Type", [p.value for p in PositionType])
    pos_expiry = st.date_input("Expiry", value=date.today())
    pos_long = st.number_input("Long strike", value=0.0)
    pos_short = st.number_input("Short strike", value=0.0)
    pos_entry = st.number_input("Entry price", value=0.0)
    pos_entry_date = st.date_input("Entry date", value=date.today())
    pos_qty = st.number_input("Quantity", value=1, step=1)
    pos_peak = st.number_input("Prior peak", value=0.0)
    sell_btn = st.button("Check Sell Decision")
def render_scan_tab():
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
                    row["NoBuyReason"] = timing.get("no_buy_reason")
                    if not timing["buy_signal"] and timing.get("no_buy_reason"):
                        row["Reasons"] = timing["no_buy_reason"]
                if show_opts:
                    strategies = pick_strategies(
                        ind["price"], None, 0, cfg, timing["buy_signal"]
                    ) if ind else []
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
                            prefix = (
                                "⚠ Not a buy — Defensive strategy idea: "
                                if not r.get("BuySignal")
                                else ""
                            )
                            st.write(f"{prefix}**{strat['name']}** (exp {strat['expiry']})")
                            st.write(strat["legs"])
                            st.write(strat["estimates"])
            st.caption("Estimates (model). Not live quotes.")
    else:
        st.info("Enter tickers and press Run to view signals.")

    if sell_btn and pos_ticker:
        pos = Position(
            ticker=pos_ticker.upper(),
            expiry=pos_expiry,
            type=PositionType[pos_type],
            long_strike=pos_long,
            short_strike=pos_short if pos_short else None,
            entry_price=pos_entry,
            entry_date=pos_entry_date,
            quantity=int(pos_qty),
        )
        dec = decide_sell(pos, SellConfig(), prev_peak=pos_peak if pos_peak else None)
        st.subheader(f"Decision: {dec['action']}")
        st.table(pd.DataFrame([dec["snapshot"]]))
        price = dec["snapshot"].get("option_last") or dec["snapshot"].get("spread_mark")
        cfg_s = SellConfig()
        cols = st.columns(4)
        cols[0].metric(
            "Profit Target",
            f"{dec['limits']['take_profit_at']:.2f}",
            "Hit" if price and price >= dec["limits"]["take_profit_at"] else "Not hit",
        )
        cols[1].metric(
            "Stop Loss",
            f"{dec['limits']['stop_loss_at']:.2f}",
            "Hit" if price and price <= dec["limits"]["stop_loss_at"] else "Not hit",
        )
        trail_hit = False
        if pos_peak and price:
            trail_hit = price <= pos_peak * (1 - cfg_s.trail_pct)
        cols[2].metric(
            "Trailing",
            f"{cfg_s.trail_pct*100:.0f}%",
            "Hit" if trail_hit else "Not hit",
        )
        if pos_type in {PositionType.LONG_PUT.value, PositionType.DEBIT_SPREAD_PUT.value}:
            breakeven_hit = dec["snapshot"]["underlying"] > dec["snapshot"]["breakeven"] + cfg_s.breakeven_buffer
        else:
            breakeven_hit = dec["snapshot"]["underlying"] < dec["snapshot"]["breakeven"] - cfg_s.breakeven_buffer
        cols[3].metric(
            "Breakeven",
            f"{dec['snapshot']['breakeven']:.2f}",
            "Hit" if breakeven_hit else "Not hit",
        )
        st.write("**Rationale**")
        for r in dec["rationale"]:
            st.write(f"- {r}")


def render_monitor_tab():
    base = st.secrets.get("api_url", "http://localhost:8000")
    if "edit_id" not in st.session_state:
        st.session_state["edit_id"] = None

    st.subheader("Positions")
    positions = requests.get(f"{base}/positions").json()
    if positions:
        st.dataframe(pd.DataFrame(positions))
        for p in positions:
            cols = st.columns(3)
            if cols[0].button("Edit", key=f"e{p['id']}"):
                st.session_state["edit_id"] = p["id"]
            if cols[1].button("Delete", key=f"d{p['id']}"):
                requests.delete(f"{base}/positions/{p['id']}")
                st.experimental_rerun()
            if cols[2].button("Toggle", key=f"t{p['id']}"):
                requests.post(f"{base}/positions/{p['id']}/toggle")
                st.experimental_rerun()
    else:
        st.write("No positions")

    data = {}
    if st.session_state["edit_id"]:
        data = next((p for p in positions if p["id"] == st.session_state["edit_id"]), {})

    with st.form("pos_form"):
        ticker = st.text_input("Ticker", value=data.get("ticker", ""))
        ptype = st.selectbox(
            "Type", [p.value for p in PositionType], index=
            [p.value for p in PositionType].index(data.get("type", PositionType.LONG_CALL.value))
        )
        expiry = st.date_input(
            "Expiry", value=date.fromisoformat(data["expiry"]) if data.get("expiry") else date.today()
        )
        long_strike = st.number_input("Long Strike", value=float(data.get("long_strike", 0)))
        short_strike = st.number_input(
            "Short Strike", value=float(data.get("short_strike", 0) or 0)
        )
        entry_price = st.number_input("Entry Price", value=float(data.get("entry_price", 0)))
        entry_date = st.date_input(
            "Entry Date", value=date.fromisoformat(data["entry_date"]) if data.get("entry_date") else date.today()
        )
        quantity = st.number_input("Quantity", value=int(data.get("quantity", 1)), step=1)
        previous_peak = st.number_input("Previous Peak", value=float(data.get("previous_peak", 0)))
        submitted = st.form_submit_button("Save")
        cancel = st.form_submit_button("Cancel")
    if submitted:
        payload = {
            "ticker": ticker,
            "type": ptype,
            "expiry": expiry.isoformat(),
            "long_strike": long_strike,
            "short_strike": short_strike or None,
            "entry_price": entry_price,
            "entry_date": entry_date.isoformat(),
            "quantity": int(quantity),
            "previous_peak": previous_peak or None,
        }
        if st.session_state["edit_id"]:
            requests.put(f"{base}/positions/{st.session_state['edit_id']}", json=payload)
        else:
            requests.post(f"{base}/positions", json=payload)
        st.session_state["edit_id"] = None
        st.experimental_rerun()
    if cancel:
        st.session_state["edit_id"] = None

    st.subheader("Settings")
    settings = requests.get(f"{base}/settings").json()
    poll = st.number_input("Polling Minutes", value=settings["poll_minutes"], step=1)
    slack = st.checkbox("Notify Slack", value=bool(settings["notify_slack"]))
    email = st.checkbox("Notify Email", value=bool(settings["notify_email"]))
    telegram = st.checkbox("Notify Telegram", value=bool(settings["notify_telegram"]))
    if st.button("Save Settings"):
        requests.put(
            f"{base}/settings",
            json={
                "poll_minutes": int(poll),
                "notify_slack": int(slack),
                "notify_email": int(email),
                "notify_telegram": int(telegram),
            },
        )
        requests.post(f"{base}/monitor/start")

    cols = st.columns(3)
    if cols[0].button("Start Monitor"):
        requests.post(f"{base}/monitor/start")
    if cols[1].button("Stop Monitor"):
        requests.post(f"{base}/monitor/stop")
    if cols[2].button("Run Once Now"):
        st.session_state["last_results"] = requests.post(
            f"{base}/monitor/run-once"
        ).json().get("results", [])

    status = requests.get(f"{base}/monitor/status").json()
    st.write(f"Running: {status['running']} Next: {status['next_run']}")

    recent = st.session_state.get("last_results") or requests.get(
        f"{base}/decisions/recent?limit=20"
    ).json()
    if recent:
        df_r = pd.DataFrame(recent)
        def highlight(row):
            color = "salmon" if row.get("decision") == "SELL_NOW" else ""
            return [f"background-color: {color}"] * len(row)

        st.dataframe(df_r.style.apply(highlight, axis=1))


with tab_scan:
    render_scan_tab()
with tab_monitor:
    render_monitor_tab()
