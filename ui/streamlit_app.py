"""Streamlit UI for signal analysis."""
from __future__ import annotations

import json
import sys
from pathlib import Path
import requests
from datetime import date

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

# Initialize session state for watchlist
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

def render_scan_tab():
    with st.sidebar:
        st.header("📊 Ticker Watchlist")
        
        # Watchlist management
        new_ticker = st.text_input("Add ticker", placeholder="e.g., AAPL")
        if st.button("➕", help="Add to watchlist") and new_ticker:
            ticker = new_ticker.strip().upper()
            if ticker and ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(ticker)
                st.rerun()
        
        # Display watchlist with selection
        if st.session_state.watchlist:
            selected_tickers = []
            for ticker in st.session_state.watchlist:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.checkbox(ticker, key=f"select_{ticker}"):
                        selected_tickers.append(ticker)
                with col2:
                    if st.button("🗑️", key=f"remove_{ticker}", help="Remove"):
                        st.session_state.watchlist.remove(ticker)
                        st.rerun()
        else:
            selected_tickers = []
        
        st.divider()
        
        # Manual input section
        st.header("📝 Manual Input")
        st.subheader("Tickers")
        manual_tickers = st.text_input("Tickers", value="AAPL,MSFT,GOOGL", key="manual_tickers")
        
        st.divider()
        
        # Settings
        st.header("⚙️ Settings")
        st.subheader("Min price")
        min_price = st.number_input("Min price", value=cfg.min_price, step=0.01)
        
        st.subheader("Min avg $ volume")
        min_vol = st.number_input("Min avg $ volume", value=cfg.min_avg_dollar_vol, step=1000000)
        
        show_timing = st.checkbox("Show Buy Timing", value=True)
        show_opts = st.checkbox("Show Options Strategies", value=True)
        
        st.divider()
        
        # Run buttons
        if selected_tickers:
            run_selected_btn = st.button(f"🏃 Run Selected ({len(selected_tickers)})", type="primary")
        else:
            run_selected_btn = False
            
        run_manual_btn = st.button("🏃 Run Manual Input")

    # Determine which tickers to analyze
    tickers_to_analyze = []
    analysis_source = ""
    
    if run_selected_btn and selected_tickers:
        tickers_to_analyze = selected_tickers
        analysis_source = f"Selected from watchlist ({len(selected_tickers)} tickers): {', '.join(selected_tickers)}"
    elif run_manual_btn and manual_tickers:
        tickers_to_analyze = [t.strip().upper() for t in manual_tickers.split(",") if t.strip()]
        analysis_source = f"Manual input: {', '.join(tickers_to_analyze)}"

    if tickers_to_analyze:
        st.success(f"🔍 {analysis_source}")
        
        # Run analysis
        rows = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, ticker in enumerate(tickers_to_analyze):
            status_text.text(f"Analyzing {ticker}...")
            progress_bar.progress((i + 1) / len(tickers_to_analyze))
            
            row = analyze_ticker(ticker, min_price, min_vol)
            
            if show_timing or show_opts:
                try:
                    ind = compute_core_indicators(ticker)
                    timing = compute_buy_timing(ind, cfg)
                except Exception as exc:
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
        
        status_text.empty()
        progress_bar.empty()
        
        # Display results
        df = pd.DataFrame(rows)
        table_cols = ["Ticker", "Recommendation", "Reasons"]
        if show_timing:
            table_cols += ["BuySignal", "TimingNote"]
        
        st.dataframe(df[table_cols])
        
        # Download CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="signals.csv", mime="text/csv")
        
        # Chart for first ticker
        if tickers_to_analyze:
            try:
                hist = fetch_history(tickers_to_analyze[0])
                if not hist.empty:
                    chart_df = pd.DataFrame({
                        "Close": hist["Close"],
                        "SMA20": hist["Close"].rolling(20).mean(),
                        "SMA50": hist["Close"].rolling(50).mean(),
                        "SMA200": hist["Close"].rolling(200).mean(),
                    })
                    st.line_chart(chart_df)
            except Exception as e:
                st.warning(f"Could not load chart for {tickers_to_analyze[0]}: {e}")
        
        # Options strategies
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

    # Sell Decision Feature
    st.divider()
    st.header("🔄 Position Management")

    with st.expander("Sell Decision Analysis"):
        col1, col2 = st.columns(2)
        with col1:
            pos_ticker = st.text_input("Position Ticker", placeholder="AAPL")
            pos_type = st.selectbox("Position Type", [e.value for e in PositionType])
            pos_long = st.number_input("Long Strike", value=0.0)
            pos_entry = st.number_input("Entry Price", value=0.0)
            pos_qty = st.number_input("Quantity", value=1)
        
        with col2:
            pos_expiry = st.date_input("Expiry Date", value=date.today())
            pos_short = st.number_input("Short Strike (optional)", value=0.0)
            pos_entry_date = st.date_input("Entry Date", value=date.today())
            pos_peak = st.number_input("Previous Peak (optional)", value=0.0)
        
        sell_btn = st.button("Analyze Sell Decision")

        if sell_btn and pos_ticker:
            try:
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
                    
            except Exception as e:
                st.error(f"Error analyzing sell decision: {e}")


def render_monitor_tab():
    st.header("📊 Positions Monitor")
    
    # Try to get API base URL from secrets, with fallback
    try:
        base_url = st.secrets.get("api_url", "http://localhost:8000")
    except Exception:
        base_url = "http://localhost:8000"
    
    st.info(f"API endpoint: {base_url}")
    
    # Add connection test button instead of automatic connection
    col1, col2 = st.columns([1, 3])
    with col1:
        test_connection = st.button("🔌 Test API Connection")
    with col2:
        refresh_positions = st.button("🔄 Refresh Positions")
    
    api_connected = False
    
    if test_connection:
        try:
            with st.spinner("Testing API connection..."):
                response = requests.get(f"{base_url}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ API Connected Successfully!")
                    api_connected = True
                else:
                    st.error(f"❌ API health check failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ API connection failed: {e}")
            st.info("💡 Make sure to start the API server with: `uvicorn app.api:app --reload`")
    
    # Fetch and display positions
    if refresh_positions or api_connected:
        try:
            with st.spinner("Fetching positions..."):
                positions_response = requests.get(f"{base_url}/positions", timeout=10)
                if positions_response.status_code == 200:
                    positions = positions_response.json()
                    
                    if positions:
                        st.subheader("Current Positions")
                        df = pd.DataFrame(positions)
                        st.dataframe(df, use_container_width=True)
                        
                        # Add delete buttons for each position
                        for pos in positions:
                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.write(f"{pos['ticker']} - {pos['type']} - {pos['expiry']}")
                            with col2:
                                if st.button(f"🔄 Toggle", key=f"toggle_{pos['id']}"):
                                    try:
                                        toggle_response = requests.post(f"{base_url}/positions/{pos['id']}/toggle", timeout=5)
                                        if toggle_response.status_code == 200:
                                            st.success("Position toggled!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to toggle position")
                                    except Exception as e:
                                        st.error(f"Error toggling position: {e}")
                            with col3:
                                if st.button(f"🗑️ Delete", key=f"delete_{pos['id']}"):
                                    try:
                                        delete_response = requests.delete(f"{base_url}/positions/{pos['id']}", timeout=5)
                                        if delete_response.status_code == 200:
                                            st.success("Position deleted!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to delete position")
                                    except Exception as e:
                                        st.error(f"Error deleting position: {e}")
                    else:
                        st.info("📭 No positions found")
                else:
                    st.error(f"Failed to fetch positions: {positions_response.status_code}")
                    
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching positions: {e}")
    
    # Manual position entry section
    st.divider()
    st.subheader("➕ Add New Position")
    
    with st.form("add_position"):
        col1, col2 = st.columns(2)
        
        with col1:
            ticker = st.text_input("Ticker *", placeholder="AAPL", help="Required field")
            ptype = st.selectbox("Position Type *", [p.value for p in PositionType], help="Required field")
            long_strike = st.number_input("Long Strike *", value=0.0, step=0.01, help="Required field")
            entry_price = st.number_input("Entry Price *", value=0.0, step=0.01, help="Required field")
            quantity = st.number_input("Quantity *", value=1, step=1, help="Required field")
            
        with col2:
            expiry = st.date_input("Expiry Date *", help="Required field")
            short_strike = st.number_input("Short Strike (optional)", value=0.0, step=0.01)
            entry_date = st.date_input("Entry Date *", value=date.today(), help="Required field")
            notes = st.text_area("Notes (optional)", placeholder="Additional notes...")
            
        col1, col2 = st.columns(2)
        with col1:
            add_via_api = st.form_submit_button("📡 Add via API", type="primary")
        with col2:
            analyze_only = st.form_submit_button("🔍 Analyze Only")
        
        if (add_via_api or analyze_only):
            # Validation
            errors = []
            if not ticker or ticker.strip() == "":
                errors.append("Ticker is required")
            if not ptype:
                errors.append("Position Type is required")
            if long_strike <= 0:
                errors.append("Long Strike must be greater than 0")
            if entry_price <= 0:
                errors.append("Entry Price must be greater than 0")
            if quantity <= 0:
                errors.append("Quantity must be greater than 0")
            if not expiry:
                errors.append("Expiry Date is required")
            if not entry_date:
                errors.append("Entry Date is required")
            
            if errors:
                st.error("❌ Please fix the following errors:")
                for error in errors:
                    st.error(f"• {error}")
                return
            
            try:
                position_data = {
                    "ticker": ticker.upper().strip(),
                    "expiry": expiry.isoformat(),
                    "type": ptype,
                    "long_strike": long_strike,
                    "short_strike": short_strike if short_strike > 0 else None,
                    "entry_price": entry_price,
                    "entry_date": entry_date.isoformat(),
                    "quantity": int(quantity),
                }
                
                if notes and notes.strip():
                    position_data["notes"] = notes.strip()
                
                if add_via_api:
                    # Try to add via API
                    try:
                        with st.spinner("Adding position via API..."):
                            response = requests.post(f"{base_url}/positions", json=position_data, timeout=10)
                            if response.status_code == 200:
                                st.success("✅ Position added successfully via API!")
                                st.balloons()
                                # Clear form by rerunning
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to add position via API: {response.status_code}")
                                if response.text:
                                    try:
                                        error_detail = response.json()
                                        st.error(f"Error details: {error_detail}")
                                    except:
                                        st.error(f"Error details: {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to API server")
                        st.info("💡 Start the API server with: `uvicorn app.api:app --reload`")
                        st.info("💡 Or use 'Analyze Only' mode which works without the API")
                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ API request failed: {e}")
                        st.info("💡 Try 'Analyze Only' mode or start the API server")
                
                # Always perform local analysis
                try:
                    pos = Position(
                        ticker=ticker.upper().strip(),
                        expiry=expiry,
                        type=PositionType[ptype],
                        long_strike=long_strike,
                        short_strike=short_strike if short_strike > 0 else None,
                        entry_price=entry_price,
                        entry_date=entry_date,
                        quantity=int(quantity),
                    )
                    
                    with st.spinner("Analyzing position..."):
                        dec = decide_sell(pos, SellConfig())
                        
                    st.subheader(f"📊 Analysis Result: {dec['action']}")
                    
                    # Display position snapshot
                    snapshot_df = pd.DataFrame([dec["snapshot"]])
                    st.dataframe(snapshot_df, use_container_width=True)
                    
                    # Display metrics
                    price = dec["snapshot"].get("option_last") or dec["snapshot"].get("spread_mark")
                    cfg_s = SellConfig()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        profit_hit = price and price >= dec["limits"]["take_profit_at"] if price else False
                        st.metric(
                            "🎯 Profit Target",
                            f"${dec['limits']['take_profit_at']:.2f}",
                            "Hit ✅" if profit_hit else "Not hit ⏳",
                            delta_color="normal" if profit_hit else "off"
                        )
                    
                    with col2:
                        stop_hit = price and price <= dec["limits"]["stop_loss_at"] if price else False
                        st.metric(
                            "🛑 Stop Loss",
                            f"${dec['limits']['stop_loss_at']:.2f}",
                            "Hit ⚠️" if stop_hit else "Safe ✅",
                            delta_color="inverse" if stop_hit else "normal"
                        )
                    
                    with col3:
                        st.metric(
                            "📈 Trailing Stop",
                            f"{cfg_s.trail_pct*100:.0f}%",
                            "Active 🔄"
                        )
                    
                    with col4:
                        breakeven = dec["snapshot"]["breakeven"]
                        current_underlying = dec["snapshot"]["underlying"]
                        st.metric(
                            "⚖️ Breakeven",
                            f"${breakeven:.2f}",
                            f"Current: ${current_underlying:.2f}"
                        )
                    
                    # Display rationale
                    st.subheader("🧠 Decision Rationale")
                    for i, reason in enumerate(dec["rationale"], 1):
                        st.write(f"{i}. {reason}")
                        
                except ValueError as ve:
                    if "Option chain fetch failed" in str(ve):
                        st.error("❌ **Option Chain Data Error**")
                        st.error(f"Could not fetch option data for {ticker.upper()} with expiry {expiry}")
                        st.info("💡 **Possible solutions:**")
                        st.info("• Check if the ticker symbol is correct")
                        st.info("• Verify the expiry date is a valid option expiration date")
                        st.info("• Try a different expiry date (usually Fridays)")
                        st.info("• The option might not be actively traded")
                    else:
                        st.error(f"❌ Validation Error: {ve}")
                except Exception as e:
                    st.error(f"❌ Error analyzing position: {e}")
                    st.info("💡 This might be due to:")
                    st.info("• Invalid ticker symbol")
                    st.info("• Network connectivity issues")
                    st.info("• Market data provider limitations")
                    with st.expander("🔍 Technical Details"):
                        st.exception(e)
                    
            except Exception as e:
                st.error(f"❌ Error processing position data: {e}")
                st.exception(e)
    
    # API Status footer
    st.divider()
    st.caption("💡 **Tip**: Start the API server with `uvicorn app.api:app --reload` to enable full position management features.")


# Render tabs
with tab_scan:
    render_scan_tab()
with tab_monitor:
    render_monitor_tab()
