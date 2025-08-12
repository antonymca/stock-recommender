from signals.timing import compute_buy_timing
from signals.config import Config


def test_buy_signal_band():
    ind = {
        "price": 110.0,
        "sma20": 105.0,
        "sma50": 102.0,
        "sma200": 100.0,
        "macd": 1.0,
        "macd_signal": 0.5,
        "rsi14": 55.0,
    }
    res = compute_buy_timing(ind, Config())
    assert res["buy_signal"] is True
    assert "Price > SMA200" in res["rationale"][0]


def test_overbought_no_buy():
    ind = {
        "price": 110.0,
        "sma20": 105.0,
        "sma50": 102.0,
        "sma200": 100.0,
        "macd": 1.0,
        "macd_signal": 0.5,
        "rsi14": 75.0,
    }
    cfg = Config(rsi_overbought=68.0)
    res = compute_buy_timing(ind, cfg)
    assert res["buy_signal"] is False
    assert "RSI overbought" in res["no_buy_reason"]
