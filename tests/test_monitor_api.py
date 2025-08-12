import os
from fastapi.testclient import TestClient

from app.api import app
from app import store, monitor


def setup_function(_):
    if os.path.exists(store.DB_PATH):
        os.remove(store.DB_PATH)
    store.Base.metadata.create_all(store.engine)
    monitor.stop_monitor()


def test_api_crud_and_schedule(monkeypatch):
    client = TestClient(app)
    monkeypatch.setattr(monitor, "run_monitor_once", lambda: [])

    pos_payload = {
        "ticker": "AAPL",
        "type": "LONG_CALL",
        "expiry": "2030-01-01",
        "long_strike": 100.0,
        "entry_price": 1.0,
    }
    resp = client.post("/positions", json=pos_payload)
    assert resp.status_code == 200
    pid = resp.json()["id"]

    resp = client.get("/positions")
    assert len(resp.json()) == 1

    resp = client.post(f"/positions/{pid}/toggle")
    assert resp.json()["enabled"] == 0

    resp = client.put(
        "/settings",
        json={
            "poll_minutes": 5,
            "notify_slack": 0,
            "notify_email": 0,
            "notify_telegram": 0,
        },
    )
    assert resp.json()["poll_minutes"] == 5

    resp = client.post("/monitor/start")
    assert resp.json()["running"]
    status = client.get("/monitor/status").json()
    assert status["running"]
    client.post("/monitor/stop")

    client.delete(f"/positions/{pid}")
    assert client.get("/positions").json() == []
