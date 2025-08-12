from datetime import date
import os
import yaml

from signals.sell_decision import Position, PositionType, SellConfig, decide_sell
import signals.sell_decision as sd
from automation import runner


def make_snapshot(**overrides):
    snap = {
        "option_last": 10.0,
        "underlying": 95.0,
        "dte": 30,
        "rsi14": 40.0,
        "sma20": 90.0,
        "sma50": 95.0,
        "sma200": 100.0,
        "macd": -1.0,
        "macd_signal": 0.0,
        "atr14": 5.0,
        "breakeven": 90.0,
        "above_breakeven_days": 0,
        "below_breakeven_days": 0,
    }
    snap.update(overrides)
    return snap


def test_sell_now_on_above_breakeven(monkeypatch):
    pos = Position(
        ticker="TEST",
        expiry=date.today(),
        type=PositionType.LONG_PUT,
        long_strike=100,
        entry_price=10.0,
    )
    cfg = SellConfig()
    snap = make_snapshot(underlying=95.0, breakeven=90.0, above_breakeven_days=2)
    monkeypatch.setattr(sd, "get_live_snapshot", lambda _pos: snap)
    dec = decide_sell(pos, cfg)
    assert dec["action"] == "SELL_NOW"


def test_hold_when_below_breakeven(monkeypatch):
    pos = Position(
        ticker="TEST",
        expiry=date.today(),
        type=PositionType.LONG_PUT,
        long_strike=100,
        entry_price=10.0,
    )
    cfg = SellConfig()
    snap = make_snapshot(underlying=80.0, breakeven=90.0, option_last=10.0)
    monkeypatch.setattr(sd, "get_live_snapshot", lambda _pos: snap)
    dec = decide_sell(pos, cfg)
    assert dec["action"] == "HOLD"


def test_runner_notifies_only_sell_now(monkeypatch, tmp_path):
    positions = [
        {
            "ticker": "AAA",
            "type": "LONG_PUT",
            "expiry": "2025-01-01",
            "long_strike": 100,
            "entry_price": 10.0,
            "entry_date": "2024-01-01",
            "quantity": 1,
        },
        {
            "ticker": "BBB",
            "type": "LONG_PUT",
            "expiry": "2025-01-01",
            "long_strike": 100,
            "entry_price": 10.0,
            "entry_date": "2024-01-01",
            "quantity": 1,
        },
    ]
    yaml_path = tmp_path / "positions.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(positions, f)

    monkeypatch.setattr(runner, "get_live_snapshot", lambda pos: make_snapshot())

    def fake_decide_sell(pos, cfg, prev_peak=None):
        if pos.ticker == "AAA":
            return {"action": "SELL_NOW", "snapshot": {}, "rationale": []}
        return {"action": "HOLD", "snapshot": {}, "rationale": []}

    monkeypatch.setattr(runner, "decide_sell", fake_decide_sell)
    calls = []
    monkeypatch.setattr(runner, "notify", lambda title, payload: calls.append(title))

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        runner.run_once(str(yaml_path))
    finally:
        os.chdir(cwd)
    assert calls == ["SELL_NOW: AAA PositionType.LONG_PUT 100 2025-01-01"]
