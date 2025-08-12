# AI Signal Bot (Free, yfinance)
Quick CLI + Streamlit UI for BUY/SELL/HOLD signals from RSI, SMA crossovers, and MACD.

## Install
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements_signal_bot.txt
```

## CLI
```bash
python ai_signal_bot.py --tickers AAPL,MSFT,NVDA
python ai_signal_bot.py --tickers-file tickers.txt --output signals.csv
```

## UI
```bash
streamlit run streamlit_app.py
```

Educational use only. Not investment advice.



This is an AI Signal Bot that provides BUY/SELL/HOLD trading recommendations using technical analysis indicators:

Core Features:

Technical Indicators: RSI, SMA crossovers (20/50/200), and MACD
Risk Filters: Minimum price and dollar volume thresholds
Data Source: Free market data via `yfinance`
Interfaces:

CLI: `ai_signal_bot.py` - analyze tickers from command line or file
Web UI: `streamlit_app.py` - interactive dashboard with charts
Key Logic:

BUY signals: RSI<30 in uptrend, SMA20 crosses above SMA50, MACD bullish crossover
SELL signals: RSI>70 in downtrend, SMA20 crosses below SMA50, MACD bearish crossover
Results sorted by recommendation priority and RSI levels
Usage:

python ai_signal_bot.py --tickers AAPL,MSFT,NVDA
streamlit run streamlit_app.py
Educational tool only - not investment advice.
