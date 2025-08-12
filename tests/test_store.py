import os
from app import store


def setup_function(_):
    if os.path.exists(store.DB_PATH):
        os.remove(store.DB_PATH)
    store.Base.metadata.create_all(store.engine)


def test_store_crud_and_settings():
    p = store.create_position(
        {
            "ticker": "AAPL",
            "type": "LONG_CALL",
            "expiry": "2030-01-01",
            "long_strike": 100.0,
            "entry_price": 1.0,
        }
    )
    assert p.id > 0
    assert store.list_positions()[0].ticker == "AAPL"
    u = store.update_position(p.id, {"ticker": "MSFT"})
    assert u.ticker == "MSFT"
    t = store.toggle_position(p.id, 0)
    assert t.enabled == 0
    store.delete_position(p.id)
    assert store.list_positions() == []

    s = store.get_settings()
    assert s.poll_minutes == 10
    s2 = store.update_settings(poll_minutes=5, notify_slack=1)
    assert s2.poll_minutes == 5 and s2.notify_slack == 1
