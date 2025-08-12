# Stock Recommender

Utilities for generating technical analysis signals, buy timing guidance and simple option strategy ideas using free `yfinance` data.

## CLI
```bash
python cli/ai_signal_bot.py --tickers AAPL,MSFT
```
Additional options allow including timing and option strategy columns or exporting CSV.

## API
```bash
uvicorn signals.api:app --reload
```
Health check at `/health` and analysis endpoint `/analyze`.

## Streamlit UI
```bash
streamlit run ui/streamlit_app.py
```
Enter tickers and view signals, timing notes, and strategy ideas.

## Tests
```bash
pytest
```
