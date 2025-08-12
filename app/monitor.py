"""Background scheduler to monitor positions."""
from __future__ import annotations

import datetime as dt
import json
import os
import time
from typing import Any, Dict, List, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from signals.sell_decision import (
    Position,
    PositionType,
    SellConfig,
    get_live_snapshot,
    decide_sell,
)
from automation.notifier import send_slack, send_email, send_telegram
from .store import (
    list_positions,
    get_settings,
    PositionOut,
)

scheduler: Optional[BackgroundScheduler] = None
JOB_ID = "position-monitor"


def _build_position(p: PositionOut) -> Position:
    entry_date = (
        dt.date.fromisoformat(p.entry_date) if p.entry_date else dt.date.today()
    )
    pos = Position(
        ticker=p.ticker,
        type=PositionType[p.type],
        expiry=dt.date.fromisoformat(p.expiry),
        long_strike=p.long_strike,
        short_strike=p.short_strike,
        entry_price=p.entry_price,
        entry_date=entry_date,
        quantity=p.quantity,
    )
    return pos


def run_monitor_once() -> List[Dict[str, Any]]:
    """Evaluate all enabled positions once."""
    settings = get_settings()
    positions = [p for p in list_positions() if p.enabled]
    results: List[Dict[str, Any]] = []
    for p in positions:
        pos = _build_position(p)
        snap = get_live_snapshot(pos)
        decision = decide_sell(pos, SellConfig(), prev_peak=p.previous_peak)
        payload = {
            "position_id": p.id,
            "ticker": pos.ticker,
            "decision": decision["action"],
            "snapshot": decision["snapshot"],
            "rationale": decision.get("rationale", []),
            "ts": dt.datetime.utcnow().isoformat(),
        }
        results.append(payload)
        if decision["action"] == "SELL_NOW":
            title = f"SELL_NOW: {pos.ticker} {p.type} {p.long_strike} {p.expiry}"
            if settings.notify_slack:
                send_slack(title)
            if settings.notify_email:
                send_email(title, json.dumps(payload, indent=2))
            if settings.notify_telegram:
                send_telegram(f"{title}\n{json.dumps(payload, indent=2)}")
    os.makedirs("logs/sell_decisions", exist_ok=True)
    stamp = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    with open(f"logs/sell_decisions/run_{stamp}.json", "w") as f:
        json.dump(results, f, indent=2)
    return results


def start_monitor() -> Dict[str, Any]:
    """Start or reschedule the background monitor."""
    global scheduler
    settings = get_settings()
    interval = settings.poll_minutes
    if scheduler and scheduler.get_job(JOB_ID):
        scheduler.reschedule_job(JOB_ID, trigger="interval", minutes=interval)
    else:
        if scheduler and scheduler.running:
            scheduler.shutdown(wait=False)
        scheduler = BackgroundScheduler()
        scheduler.add_job(run_monitor_once, IntervalTrigger(minutes=interval), id=JOB_ID)
        scheduler.start()
    return {"running": True, "interval": interval}


def stop_monitor() -> Dict[str, Any]:
    """Stop the scheduler."""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.remove_all_jobs()
        scheduler.shutdown(wait=False)
        scheduler = None
    return {"running": False}


def status_monitor() -> Dict[str, Any]:
    """Return running state and next run time."""
    if scheduler and scheduler.running:
        job = scheduler.get_job(JOB_ID)
        next_run = job.next_run_time.isoformat() if job else None
        interval = (
            int(job.trigger.interval.total_seconds() // 60) if job else None
        )
        return {"running": job is not None, "interval": interval, "next_run": next_run}
    return {"running": False, "interval": None, "next_run": None}


if __name__ == "__main__":  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(description="Position monitor CLI")
    parser.add_argument(
        "command",
        choices=["start", "stop", "run-once", "status"],
        help="Control the scheduler",
    )
    args = parser.parse_args()
    if args.command == "start":
        start_monitor()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_monitor()
    elif args.command == "stop":
        stop_monitor()
    elif args.command == "run-once":
        print(json.dumps(run_monitor_once(), indent=2))
    else:
        print(json.dumps(status_monitor(), indent=2))
