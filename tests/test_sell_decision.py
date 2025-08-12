from datetime import date

from signals.sell_decision import (
    Position,
    PositionType,
    SellConfig,
    decide_sell,
    calc_spread_mark,
)


def make_position() -> Position:
    return Position(
        ticker="TEST",
        expiry=date.today(),
        type=PositionType.LONG_PUT,
        long_strike=100,
        entry_price=10.0,
        entry_date=date.today(),
    )


def test_stop_loss_and_profit_target():
    pos = make_position()
    cfg = SellConfig()
    snap = {
        "option_last": 5.0,
        "underlying": 80.0,
        "dte": 30,
        "rsi14": 40.0,
        "sma20": 90.0,
        "sma50": 95.0,
        "sma200": 100.0,
        "macd": -1.0,
        "macd_signal": 0.0,
        "atr14": 5.0,
        "breakeven": 90.0,
    }
    dec = decide_sell(pos, cfg, snapshot=snap)
    assert dec["action"] == "SELL_NOW"

    snap["option_last"] = 15.0
    dec = decide_sell(pos, cfg, snapshot=snap)
    assert dec["action"] == "PARTIAL_SELL"

    snap["option_last"] = 20.0
    dec = decide_sell(pos, cfg, snapshot=snap)
    assert dec["action"] == "SELL_NOW"


def test_trailing_stop():
    pos = make_position()
    cfg = SellConfig()
    snap = {
        "option_last": 12.0,
        "underlying": 80.0,
        "dte": 30,
        "rsi14": 40.0,
        "sma20": 90.0,
        "sma50": 95.0,
        "sma200": 100.0,
        "macd": -1.0,
        "macd_signal": 0.0,
        "atr14": 5.0,
        "breakeven": 90.0,
    }
    dec = decide_sell(pos, cfg, prev_peak=20.0, snapshot=snap)
    assert dec["action"] == "SELL_NOW"


def test_breakeven_buffer_exit():
    pos = make_position()
    cfg = SellConfig()
    snap = {
        "option_last": 9.0,
        "underlying": 93.0,
        "dte": 10,
        "rsi14": 60.0,
        "sma20": 92.0,
        "sma50": 95.0,
        "sma200": 100.0,
        "macd": 1.0,
        "macd_signal": 0.5,
        "atr14": 5.0,
        "breakeven": 90.0,
    }
    dec = decide_sell(pos, cfg, snapshot=snap)
    assert dec["action"] == "SELL_NOW"


def test_spread_mark_calc():
    assert calc_spread_mark(5.5, 2.0) == 3.5
