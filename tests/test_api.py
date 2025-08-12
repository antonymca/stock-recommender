from fastapi.testclient import TestClient
import signals.api as api


def fake_core(_ticker):
    return {
        "price": 100.0,
        "rsi14": 55.0,
        "sma20": 95.0,
        "sma50": 90.0,
        "sma200": 80.0,
        "macd": 1.0,
        "macd_signal": 0.5,
        "atr14": 1.0,
        "avg_dollar_vol": 10_000_000.0,
    }


def fake_analyze(ticker, min_price, min_dollar_vol):
    return {
        "Ticker": ticker,
        "Price": 100.0,
        "RSI14": 55.0,
        "SMA20": 95.0,
        "SMA50": 90.0,
        "SMA200": 80.0,
        "MACD": 1.0,
        "MACDSignal": 0.5,
        "ATR14": 1.0,
        "AvgDollarVol20D": 10_000_000.0,
        "Signals": "BUY",
        "Recommendation": "BUY",
        "Reasons": "test",
    }


def test_analyze_endpoint(monkeypatch):
    monkeypatch.setattr(api, "compute_core_indicators", fake_core)
    monkeypatch.setattr(api, "analyze_ticker", fake_analyze)
    client = TestClient(api.app)
    resp = client.post("/analyze", json={"ticker": "TEST"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "TEST"
    assert data["buy_signal"] is True
    assert data.get("no_buy_reason") is None
    assert data["signals"]["raw"] == "BUY"
    assert "price" in data["indicators"]
