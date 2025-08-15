.PHONY: dev nightly intraday backtest

# Convenience targets for the new backend skeleton.

dev:
@echo "Starting API and web via docker-compose..."
docker compose up --build

nightly:
@echo "Running nightly job (placeholder)..."
python backend/jobs/nightly.py

intraday:
@echo "Running intraday explainer once (placeholder)..."
python backend/jobs/intraday_explainer.py

backtest:
@echo "Running demo QVM backtest (placeholder)..."
python backend/core/backtest/vectorbt_runs.py
