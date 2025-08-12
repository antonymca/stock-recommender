import pandas as pd
from signals.indicators import rsi, macd


def test_rsi_smoothing():
    s = pd.Series([i for i in range(1, 30)])
    res = rsi(s, 14)
    assert len(res) == len(s)
    assert not pd.isna(res.iloc[-1])


def test_macd_direction():
    up = pd.Series([i for i in range(1, 30)])
    down = pd.Series([30 - i for i in range(1, 30)])
    macd_up, sig_up = macd(up, 3, 6, 3)
    macd_down, sig_down = macd(down, 3, 6, 3)
    assert macd_up.iloc[-1] > sig_up.iloc[-1]
    assert macd_down.iloc[-1] < sig_down.iloc[-1]
