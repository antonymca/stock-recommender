"""FastAPI app combining analysis endpoints with position monitor."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from signals.api import app as signals_app
from .store import (
    list_positions,
    get_position,
    create_position,
    update_position,
    delete_position,
    toggle_position,
    get_settings,
    update_settings,
    PositionIn,
    PositionOut,
    SettingsOut,
)
from .monitor import (
    start_monitor,
    stop_monitor,
    status_monitor,
    run_monitor_once,
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(signals_app.router)


# Positions CRUD
@app.get("/positions", response_model=List[PositionOut])
def positions_list() -> List[PositionOut]:
    return list_positions()


@app.post("/positions", response_model=PositionOut)
def positions_create(p: PositionIn) -> PositionOut:
    return create_position(p.dict())


@app.put("/positions/{pid}", response_model=PositionOut)
def positions_update(pid: int, p: PositionIn) -> PositionOut:
    if not get_position(pid):
        raise HTTPException(status_code=404, detail="Not found")
    return update_position(pid, p.dict())


@app.delete("/positions/{pid}")
def positions_delete(pid: int) -> dict:
    delete_position(pid)
    return {"ok": True}


@app.post("/positions/{pid}/toggle", response_model=PositionOut)
def positions_toggle(pid: int) -> PositionOut:
    pos = get_position(pid)
    if not pos:
        raise HTTPException(status_code=404, detail="Not found")
    return toggle_position(pid, 0 if pos.enabled else 1)


# Settings
@app.get("/settings", response_model=SettingsOut)
def settings_get() -> SettingsOut:
    return get_settings()


@app.put("/settings", response_model=SettingsOut)
def settings_put(s: SettingsOut) -> SettingsOut:
    return update_settings(**s.dict())


# Monitor controls
@app.post("/monitor/start")
def monitor_start() -> dict:
    return start_monitor()


@app.post("/monitor/stop")
def monitor_stop() -> dict:
    return stop_monitor()


@app.get("/monitor/status")
def monitor_status() -> dict:
    return status_monitor()


@app.post("/monitor/run-once")
def monitor_run_once() -> dict:
    return {"results": run_monitor_once()}


# Decisions history
@app.get("/decisions/recent")
def decisions_recent(limit: int = 50) -> List[dict]:
    logs = Path("logs/sell_decisions")
    items: List[dict] = []
    if logs.exists():
        for file in sorted(logs.glob("run_*.json"), reverse=True):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    items.extend(data)
            except Exception:
                continue
            if len(items) >= limit:
                break
    return items[:limit]
