import os
from app import store, monitor


def setup_function(_):
    if os.path.exists(store.DB_PATH):
        os.remove(store.DB_PATH)
    store.Base.metadata.create_all(store.engine)


def test_run_once_triggers_notifier(monkeypatch):
    store.create_position(
        {
            "ticker": "AAPL",
            "type": "LONG_CALL",
            "expiry": "2030-01-01",
            "long_strike": 100.0,
            "entry_price": 1.0,
        }
    )
    store.update_settings(poll_minutes=5, notify_slack=1)

    monkeypatch.setattr(monitor, "get_live_snapshot", lambda pos: {})
    monkeypatch.setattr(
        monitor,
        "decide_sell",
        lambda pos, cfg, prev_peak=None: {"action": "SELL_NOW", "snapshot": {}},
    )
    calls = []
    monkeypatch.setattr(monitor, "send_slack", lambda msg: calls.append(msg))
    res = monitor.run_monitor_once()
    assert res[0]["decision"] == "SELL_NOW"
    assert calls
