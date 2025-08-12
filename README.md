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

## Sell Decision Notifier
Monitor open option positions and receive push alerts when the sell engine signals `SELL_NOW`.

Add positions in `automation/positions.yaml`:

```yaml
- ticker: NVDA
  type: LONG_PUT
  expiry: 2025-09-19
  long_strike: 195
  entry_price: 16.05
  entry_date: 2025-08-12
  quantity: 1
  previous_peak: null
```

Run once or start the scheduler:

```bash
python -m automation.runner        # single evaluation
python -m automation.schedule      # every 10m during market hours

# optional CLI wrapper
python cli/app_cli.py sell-watch --once
python cli/app_cli.py sell-watch --schedule
```

Configure Slack, email, or Telegram in `.env`:

```
SLACK_WEBHOOK_URL=
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
EMAIL_TO=
TG_BOT_TOKEN=
TG_CHAT_ID=
```

Educational only; not financial advice.

## Tests
```bash
pytest
```
