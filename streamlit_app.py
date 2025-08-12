import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

try:
    import sys, os
    sys.path.append(os.path.dirname(__file__))
    from ai_signal_bot import analyze_ticker
except Exception as e:
    st.error(f"Import error: {e}")
    analyze_ticker = None

st.set_page_config(page_title="AI Signal Bot (Free)", page_icon="📈", layout="wide")
st.title("📈 AI Signal Bot — Free (yfinance)")
st.caption("RSI • SMA20/50 • MACD • Risk filters")

with st.sidebar:
    st.header("Settings")
    tickers_text = st.text_area("Tickers (comma separated)", value="AAPL,MSFT,NVDA,SPY,QQQ", height=100)
    min_price = st.number_input("Min Price", min_value=0.0, value=5.0, step=0.5)
    min_dollar_vol = st.number_input("Min 20D Avg $ Volume", min_value=0.0, value=5_000_000.0, step=500_000.0, format="%.0f")
    run_btn = st.button("Run Analysis", type="primary")

def run_analysis(tickers, min_price, min_dollar_vol):
    rows = []
    for t in tickers:
        t = t.strip().upper()
        if not t: continue
        try:
            rows.append(analyze_ticker(t, min_price, min_dollar_vol))
        except Exception as e:
            rows.append({"Ticker": t, "Error": str(e)})
    import pandas as pd
    df = pd.DataFrame(rows)
    cols = ["Ticker","Price","RSI14","SMA20","SMA50","SMA200","MACD","MACDSignal","ATR14","AvgDollarVol20D","Signals","Recommendation","Reasons","Error"]
    for c in cols:
        if c not in df.columns: df[c] = None
    df = df[cols]
    rec_order = {"BUY":0, "SELL":1, "HOLD":2}
    df["rec_rank"] = df["Recommendation"].map(rec_order).fillna(3)
    df["rsi_rank"] = df["RSI14"].fillna(100)
    df = df.sort_values(by=["rec_rank","rsi_rank"], ascending=[True, True]).drop(columns=["rec_rank","rsi_rank"])
    return df

if run_btn and analyze_ticker is None:
    st.stop()

if run_btn:
    tickers = [t.strip() for t in tickers_text.split(",") if t.strip()]
    if not tickers:
        st.warning("Enter at least one ticker."); st.stop()
    df = run_analysis(tickers, min_price, min_dollar_vol)
    st.session_state.analysis_results = df

# Display results if they exist in session state
if 'analysis_results' in st.session_state:
    df = st.session_state.analysis_results
    st.subheader("Results")
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name="signals.csv", mime="text/csv")

    st.markdown("### Chart")
    selected = st.selectbox("Select a ticker to chart", options=df["Ticker"].dropna().tolist())
    if selected:
        try:
            hist = yf.Ticker(selected).history(period="6mo", interval="1d", auto_adjust=False)
            if not hist.empty:
                close = hist["Close"]; sma20 = close.rolling(20).mean(); sma50 = close.rolling(50).mean()
                fig, ax = plt.subplots()
                ax.plot(close.index, close.values, label="Close")
                ax.plot(sma20.index, sma20.values, label="SMA20")
                ax.plot(sma50.index, sma50.values, label="SMA50")
                ax.legend(); ax.set_title(f"{selected} — Price with SMA20/50")
                st.pyplot(fig)
        except Exception as e:
            st.info(f"Could not chart {selected}: {e}")
else:
    st.info("Use the sidebar to run an analysis.")
