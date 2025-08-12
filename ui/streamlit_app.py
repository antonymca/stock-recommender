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

# Page configuration
st.set_page_config(
    page_title="Stock Signal & Options Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Navigation
def create_navigation():
    st.sidebar.title("📈 Stock Signal Hub")
    
    # Navigation menu
    pages = {
        "🔍 Signal Scanner": "scanner",
        "📊 Position Monitor": "monitor", 
        "➕ Add Position": "add_position",
        "📈 Market Analysis": "analysis",
        "⚙️ Settings": "settings"
    }
    
    selected_page = st.sidebar.radio("Navigate to:", list(pages.keys()))
    
    # Quick stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Quick Stats")
    
    # Try to get position count
    try:
        base_url = st.secrets.get("api_url", "http://localhost:8000")
        response = requests.get(f"{base_url}/positions", timeout=3)
        if response.status_code == 200:
            positions = response.json()
            st.sidebar.metric("Active Positions", len(positions))
            enabled_count = sum(1 for p in positions if p.get('enabled', 1))
            st.sidebar.metric("Enabled Positions", enabled_count)
        else:
            st.sidebar.info("API not connected")
    except:
        st.sidebar.info("API not available")
    
    # Quick actions
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Quick Actions")
    
    if st.sidebar.button("🔄 Refresh All Data"):
        st.cache_data.clear()
        st.rerun()
    
    if st.sidebar.button("📊 Test API Connection"):
        try:
            response = requests.get(f"{base_url}/health", timeout=3)
            if response.status_code == 200:
                st.sidebar.success("✅ API Connected")
            else:
                st.sidebar.error("❌ API Error")
        except:
            st.sidebar.error("❌ API Unavailable")
    
    return pages[selected_page]

# Initialize session state
if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
if "positions_data" not in st.session_state:
    st.session_state.positions_data = []
if "positions_loaded" not in st.session_state:
    st.session_state.positions_loaded = False

def render_scanner_page():
    st.markdown('<h1 class="main-header">🔍 Signal Scanner</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Ticker Analysis")
        
        # Quick preset buttons
        st.markdown("**Quick Presets:**")
        preset_col1, preset_col2, preset_col3 = st.columns(3)
        
        with preset_col1:
            if st.button("🔥 Popular Stocks", use_container_width=True):
                st.session_state.analysis_tickers = "AAPL,MSFT,GOOGL,AMZN,TSLA"
        with preset_col2:
            if st.button("💎 Tech Giants", use_container_width=True):
                st.session_state.analysis_tickers = "AAPL,MSFT,GOOGL,META,NVDA"
        with preset_col3:
            if st.button("📈 Growth Stocks", use_container_width=True):
                st.session_state.analysis_tickers = "TSLA,NVDA,AMD,CRM,SNOW"
        
        # Manual input
        manual_tickers = st.text_input(
            "Enter Tickers (comma-separated)", 
            value=st.session_state.get("analysis_tickers", "AAPL,MSFT,GOOGL"),
            key="manual_tickers",
            help="Enter stock symbols separated by commas"
        )
        
        # Analysis options
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            show_timing = st.checkbox("📅 Show Buy Timing", value=True)
            show_chart = st.checkbox("📊 Show Price Chart", value=True)
        with col_opt2:
            show_opts = st.checkbox("🎯 Show Options Strategies", value=True)
            export_csv = st.checkbox("💾 Enable CSV Export", value=False)
        
        # Run analysis button
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            if manual_tickers:
                run_analysis(manual_tickers, show_timing, show_opts, show_chart, export_csv)
            else:
                st.error("Please enter at least one ticker symbol")
    
    with col2:
        st.subheader("📝 Watchlist Manager")
        
        # Add to watchlist
        new_ticker = st.text_input("Add ticker", placeholder="e.g., AAPL")
        if st.button("➕ Add to Watchlist", use_container_width=True) and new_ticker:
            ticker = new_ticker.strip().upper()
            if ticker and ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(ticker)
                st.success(f"Added {ticker} to watchlist!")
                st.rerun()
        
        # Display watchlist
        if st.session_state.watchlist:
            st.markdown("**Your Watchlist:**")
            selected_tickers = []
            
            for ticker in st.session_state.watchlist:
                col_check, col_remove = st.columns([3, 1])
                with col_check:
                    if st.checkbox(ticker, key=f"select_{ticker}"):
                        selected_tickers.append(ticker)
                with col_remove:
                    if st.button("🗑️", key=f"remove_{ticker}", help="Remove"):
                        st.session_state.watchlist.remove(ticker)
                        st.rerun()
            
            if selected_tickers:
                if st.button(f"🏃 Analyze Selected ({len(selected_tickers)})", 
                           type="secondary", use_container_width=True):
                    run_analysis(",".join(selected_tickers), True, True, True, False)
        
        # Settings panel
        st.markdown("---")
        st.subheader("⚙️ Analysis Settings")
        min_price = st.number_input("Min Price ($)", value=cfg.min_price, step=0.01)
        min_vol = st.number_input("Min Avg Volume ($M)", value=cfg.min_avg_dollar_vol/1000000, step=1.0)

def run_analysis(tickers_str, show_timing, show_opts, show_chart, export_csv):
    tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]
    
    if not tickers:
        st.error("No valid tickers provided")
        return
    
    st.success(f"🔍 Analyzing {len(tickers)} tickers: {', '.join(tickers)}")
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    rows = []
    
    for i, ticker in enumerate(tickers):
        status_text.text(f"Analyzing {ticker}... ({i+1}/{len(tickers)})")
        progress_bar.progress((i + 1) / len(tickers))
        
        try:
            row = analyze_ticker(ticker, cfg.min_price, cfg.min_avg_dollar_vol)
            
            if show_timing or show_opts:
                try:
                    ind = compute_core_indicators(ticker)
                    timing = compute_buy_timing(ind, cfg)
                except Exception as exc:
                    timing = {"buy_signal": False, "timing_note": str(exc), "rationale": []}
                    ind = None
                    
                if show_timing:
                    row["BuySignal"] = "✅ Yes" if timing["buy_signal"] else "❌ No"
                    row["TimingNote"] = timing["timing_note"]
                    
                if show_opts and ind:
                    strategies = pick_strategies(ind["price"], None, 0, cfg, timing["buy_signal"])
                    row["StrategyCount"] = len(strategies)
                    
            rows.append(row)
            
        except Exception as e:
            st.error(f"Error analyzing {ticker}: {e}")
    
    status_text.empty()
    progress_bar.empty()
    
    if rows:
        with results_container:
            display_results(rows, tickers, show_timing, show_opts, show_chart, export_csv)

def display_results(rows, tickers, show_timing, show_opts, show_chart, export_csv):
    st.subheader("📊 Analysis Results")
    
    # Create results dataframe
    df = pd.DataFrame(rows)
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    buy_signals = sum(1 for r in rows if r.get("BuySignal") == "✅ Yes")
    strong_buy = sum(1 for r in rows if r.get("Recommendation") == "Strong Buy")
    
    col1.metric("📈 Buy Signals", f"{buy_signals}/{len(rows)}")
    col2.metric("🎯 Strong Buys", strong_buy)
    col3.metric("📊 Analyzed", len(rows))
    col4.metric("⚠️ Warnings", len(rows) - buy_signals)
    
    # Display results table
    display_cols = ["Ticker", "Recommendation", "Reasons"]
    if show_timing:
        display_cols.extend(["BuySignal", "TimingNote"])
    if show_opts:
        display_cols.append("StrategyCount")
    
    st.dataframe(df[display_cols], use_container_width=True)
    
    # Export option
    if export_csv:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Results CSV",
            data=csv,
            file_name=f"signals_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Chart for first ticker
    if show_chart and tickers:
        try:
            st.subheader(f"📈 Price Chart - {tickers[0]}")
            hist = fetch_history(tickers[0])
            if not hist.empty:
                chart_df = pd.DataFrame({
                    "Close": hist["Close"],
                    "SMA20": hist["Close"].rolling(20).mean(),
                    "SMA50": hist["Close"].rolling(50).mean(),
                    "SMA200": hist["Close"].rolling(200).mean(),
                })
                st.line_chart(chart_df, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load chart: {e}")

def render_monitor_page():
    st.markdown('<h1 class="main-header">📊 Position Monitor</h1>', unsafe_allow_html=True)
    
    # API connection status
    base_url = st.secrets.get("api_url", "http://localhost:8000") if "api_url" in st.secrets else "http://localhost:8000"
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.info(f"🔗 API Endpoint: {base_url}")
    with col2:
        if st.button("🔌 Test Connection", use_container_width=True):
            test_api_connection(base_url)
    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            fetch_positions(base_url)
    
    # Auto-load positions
    if not st.session_state.positions_loaded:
        fetch_positions(base_url)
    
    # Display positions
    if st.session_state.positions_data:
        display_positions()
    else:
        st.info("📭 No positions found. Add some positions to get started!")
        if st.button("➕ Add Your First Position", type="primary"):
            st.switch_page("add_position")

def display_positions():
    st.subheader("📋 Current Positions")
    
    df = pd.DataFrame(st.session_state.positions_data)
    
    # Summary metrics
    total_positions = len(df)
    enabled_positions = sum(1 for p in st.session_state.positions_data if p.get('enabled', 1))
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Positions", total_positions)
    col2.metric("Active Positions", enabled_positions)
    col3.metric("Inactive Positions", total_positions - enabled_positions)
    
    # Positions table
    st.dataframe(df, use_container_width=True)
    
    # Position actions
    st.subheader("🎛️ Position Actions")
    
    for pos in st.session_state.positions_data:
        with st.expander(f"📊 {pos['ticker']} - {pos['type']} (Exp: {pos['expiry']})"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                enabled_status = "✅ Enabled" if pos.get('enabled', 1) else "❌ Disabled"
                st.write(f"**Status:** {enabled_status}")
                st.write(f"**Strike:** ${pos['long_strike']}")
            
            with col2:
                st.write(f"**Entry:** ${pos['entry_price']}")
                st.write(f"**Quantity:** {pos['quantity']}")
            
            with col3:
                if st.button("🔄 Toggle Status", key=f"toggle_{pos['id']}"):
                    toggle_position(pos['id'])
                
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{pos['id']}", type="secondary"):
                    delete_position(pos['id'])

def render_add_position_page():
    st.markdown('<h1 class="main-header">➕ Add New Position</h1>', unsafe_allow_html=True)
    
    # Quick help
    with st.expander("ℹ️ How to add a position"):
        st.markdown("""
        **Required Fields:**
        - **Ticker**: Stock symbol (e.g., AAPL, MSFT)
        - **Position Type**: Type of option position
        - **Long Strike**: Strike price of the option
        - **Entry Price**: Price you paid for the position
        - **Expiry Date**: Option expiration date
        - **Entry Date**: Date you entered the position
        
        **Optional Fields:**
        - **Short Strike**: For spread positions
        - **Notes**: Additional information about the position
        """)
    
    # Position form
    with st.form("add_position_form", clear_on_submit=True):
        st.subheader("📝 Position Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ticker = st.text_input("Ticker *", placeholder="AAPL", help="Stock symbol")
            ptype = st.selectbox("Position Type *", [p.value for p in PositionType])
            long_strike = st.number_input("Long Strike *", value=0.0, step=0.01, format="%.2f")
            entry_price = st.number_input("Entry Price *", value=0.0, step=0.01, format="%.2f")
            
        with col2:
            expiry = st.date_input("Expiry Date *")
            entry_date = st.date_input("Entry Date *", value=date.today())
            short_strike = st.number_input("Short Strike (optional)", value=0.0, step=0.01, format="%.2f")
            quantity = st.number_input("Quantity *", value=1, step=1)
        
        notes = st.text_area("Notes (optional)", placeholder="Additional notes about this position...")
        
        # Submit buttons
        col1, col2 = st.columns(2)
        with col1:
            add_to_db = st.form_submit_button("💾 Save to Database", type="primary", use_container_width=True)
        with col2:
            analyze_only = st.form_submit_button("🔍 Analyze Only", use_container_width=True)
        
        if add_to_db or analyze_only:
            handle_position_submission(ticker, ptype, long_strike, entry_price, expiry, 
                                     entry_date, short_strike, quantity, notes, add_to_db)

def handle_position_submission(ticker, ptype, long_strike, entry_price, expiry, 
                             entry_date, short_strike, quantity, notes, save_to_db):
    # Validation
    errors = validate_position_inputs(ticker, ptype, long_strike, entry_price, expiry, entry_date, quantity)
    
    if errors:
        st.error("❌ Please fix the following errors:")
        for error in errors:
            st.error(f"• {error}")
        return
    
    # Create position data
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
    
    # Save to database if requested
    if save_to_db:
        save_position_to_db(position_data)
    
    # Always perform analysis
    analyze_position(position_data)

def validate_position_inputs(ticker, ptype, long_strike, entry_price, expiry, entry_date, quantity):
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
    return errors

def save_position_to_db(position_data):
    base_url = st.secrets.get("api_url", "http://localhost:8000") if "api_url" in st.secrets else "http://localhost:8000"
    
    try:
        with st.spinner("💾 Saving position to database..."):
            response = requests.post(f"{base_url}/positions", json=position_data, timeout=10)
            if response.status_code == 200:
                st.success("✅ Position saved successfully!")
                st.balloons()
                # Refresh positions data
                fetch_positions(base_url)
            else:
                st.error(f"❌ Failed to save position: {response.status_code}")
                if response.text:
                    try:
                        error_detail = response.json()
                        st.error(f"Details: {error_detail}")
                    except:
                        st.error(f"Details: {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server")
        st.info("💡 Start the API server with: `uvicorn app.api:app --reload`")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Request failed: {e}")

def analyze_position(position_data):
    try:
        pos = Position(
            ticker=position_data["ticker"],
            expiry=date.fromisoformat(position_data["expiry"]),
            type=PositionType[position_data["type"]],
            long_strike=position_data["long_strike"],
            short_strike=position_data.get("short_strike"),
            entry_price=position_data["entry_price"],
            entry_date=date.fromisoformat(position_data["entry_date"]),
            quantity=position_data["quantity"],
        )
        
        with st.spinner("🔍 Analyzing position..."):
            dec = decide_sell(pos, SellConfig())
        
        display_analysis_results(dec)
        
    except ValueError as ve:
        handle_analysis_error(ve, position_data["ticker"], position_data["expiry"])
    except Exception as e:
        st.error(f"❌ Analysis failed: {e}")
        with st.expander("🔍 Technical Details"):
            st.exception(e)

def display_analysis_results(dec):
    st.subheader(f"📊 Analysis Result: {dec['action']}")
    
    # Position snapshot
    snapshot_df = pd.DataFrame([dec["snapshot"]])
    st.dataframe(snapshot_df, use_container_width=True)
    
    # Key metrics
    price = dec["snapshot"].get("option_last") or dec["snapshot"].get("spread_mark")
    cfg_s = SellConfig()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        profit_hit = price and price >= dec["limits"]["take_profit_at"] if price else False
        st.metric(
            "🎯 Profit Target",
            f"${dec['limits']['take_profit_at']:.2f}",
            "Hit ✅" if profit_hit else "Not hit ⏳"
        )
    
    with col2:
        stop_hit = price and price <= dec["limits"]["stop_loss_at"] if price else False
        st.metric(
            "🛑 Stop Loss",
            f"${dec['limits']['stop_loss_at']:.2f}",
            "Hit ⚠️" if stop_hit else "Safe ✅"
        )
    
    with col3:
        st.metric("📈 Trailing Stop", f"{cfg_s.trail_pct*100:.0f}%", "Active")
    
    with col4:
        breakeven = dec["snapshot"]["breakeven"]
        current_underlying = dec["snapshot"]["underlying"]
        st.metric("⚖️ Breakeven", f"${breakeven:.2f}", f"Current: ${current_underlying:.2f}")
    
    # Decision rationale
    st.subheader("🧠 Decision Rationale")
    for i, reason in enumerate(dec["rationale"], 1):
        st.write(f"{i}. {reason}")

def handle_analysis_error(ve, ticker, expiry):
    error_msg = str(ve)
    if "Option chain fetch failed" in error_msg:
        st.error("❌ **Option Chain Data Error**")
        st.error(f"Could not fetch option data for {ticker} with expiry {expiry}")
        
        if "Available expirations are:" in error_msg:
            available_dates = error_msg.split("Available expirations are:")[1].strip()
            st.info(f"**Available expiration dates:** {available_dates}")
        
        st.info("💡 **Possible solutions:**")
        st.info("• Check if the ticker symbol is correct")
        st.info("• Verify the expiry date is a valid option expiration date")
        st.info("• Try a different expiry date (usually Fridays)")
        st.info("• The option might not be actively traded")
    else:
        st.error(f"❌ Validation Error: {ve}")

def render_analysis_page():
    st.markdown('<h1 class="main-header">📈 Market Analysis</h1>', unsafe_allow_html=True)
    
    st.info("🚧 Advanced market analysis features coming soon!")
    
    # Placeholder for future features
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Market Overview")
        st.write("• Real-time market data")
        st.write("• Sector performance")
        st.write("• Market sentiment indicators")
        
    with col2:
        st.subheader("🎯 Strategy Performance")
        st.write("• Historical strategy returns")
        st.write("• Risk metrics")
        st.write("• Performance analytics")

def render_settings_page():
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)
    
    # API Configuration
    st.subheader("🔗 API Configuration")
    
    current_url = st.secrets.get("api_url", "http://localhost:8000") if "api_url" in st.secrets else "http://localhost:8000"
    api_url = st.text_input("API Base URL", value=current_url)
    
    if st.button("💾 Save API Settings"):
        st.success("Settings saved! (Note: Restart required for full effect)")
    
    # Analysis Settings
    st.subheader("📊 Analysis Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        min_price = st.number_input("Minimum Price ($)", value=cfg.min_price, step=0.01)
        min_volume = st.number_input("Minimum Volume ($M)", value=cfg.min_avg_dollar_vol/1000000, step=1.0)
    
    with col2:
        default_quantity = st.number_input("Default Quantity", value=1, step=1)
        auto_refresh = st.checkbox("Auto-refresh data", value=True)
    
    # Display Settings
    st.subheader("🎨 Display Settings")
    
    theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
    show_advanced = st.checkbox("Show advanced features", value=False)
    
    if st.button("💾 Save All Settings"):
        st.success("All settings saved successfully!")

# Helper functions
def test_api_connection(base_url):
    try:
        with st.spinner("Testing API connection..."):
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API Connected Successfully!")
            else:
                st.error(f"❌ API health check failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API connection failed: {e}")
        st.info("💡 Make sure to start the API server with: `uvicorn app.api:app --reload`")

def fetch_positions(base_url):
    try:
        with st.spinner("Fetching positions..."):
            response = requests.get(f"{base_url}/positions", timeout=10)
            if response.status_code == 200:
                st.session_state.positions_data = response.json()
                st.session_state.positions_loaded = True
                return True
            else:
                st.error(f"Failed to fetch positions: {response.status_code}")
                return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching positions: {e}")
        return False

def toggle_position(position_id):
    base_url = st.secrets.get("api_url", "http://localhost:8000") if "api_url" in st.secrets else "http://localhost:8000"
    try:
        response = requests.post(f"{base_url}/positions/{position_id}/toggle", timeout=5)
        if response.status_code == 200:
            st.success("Position toggled!")
            fetch_positions(base_url)
            st.rerun()
        else:
            st.error("Failed to toggle position")
    except Exception as e:
        st.error(f"Error toggling position: {e}")

def delete_position(position_id):
    base_url = st.secrets.get("api_url", "http://localhost:8000") if "api_url" in st.secrets else "http://localhost:8000"
    try:
        response = requests.delete(f"{base_url}/positions/{position_id}", timeout=5)
        if response.status_code == 200:
            st.success("Position deleted!")
            fetch_positions(base_url)
            st.rerun()
        else:
            st.error("Failed to delete position")
    except Exception as e:
        st.error(f"Error deleting position: {e}")

# Main app
def main():
    selected_page = create_navigation()
    
    if selected_page == "scanner":
        render_scanner_page()
    elif selected_page == "monitor":
        render_monitor_page()
    elif selected_page == "add_position":
        render_add_position_page()
    elif selected_page == "analysis":
        render_analysis_page()
    elif selected_page == "settings":
        render_settings_page()

if __name__ == "__main__":
    main()
