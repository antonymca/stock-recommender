"""Evaluate sell decisions for configured positions and send notifications."""
import os
import json
import datetime as dt
from typing import List, Dict

import yaml
from dotenv import load_dotenv

from signals.sell_decision import (
    Position,
    PositionType,
    SellConfig,
    get_live_snapshot,
    decide_sell,
)
from .notifier import notify

load_dotenv()

CFG = SellConfig()


def _parse_dates(p: Dict) -> Dict:
    p = dict(p)
    if isinstance(p.get("type"), str):
        p["type"] = PositionType[p["type"]]
    if isinstance(p.get("expiry"), str):
        p["expiry"] = dt.datetime.strptime(p["expiry"], "%Y-%m-%d").date()
    if p.get("entry_date") and isinstance(p["entry_date"], str):
        p["entry_date"] = dt.datetime.strptime(p["entry_date"], "%Y-%m-%d").date()
    return p


def run_once(yaml_path: str = "automation/positions.yaml") -> List[Dict]:
    with open(yaml_path, "r") as f:
        positions = yaml.safe_load(f) or []
    results: List[Dict] = []
    for p in positions:
        pos = Position(**_parse_dates(p))
        snap = get_live_snapshot(pos)
        decision = decide_sell(pos, CFG, prev_peak=p.get("previous_peak"))
        payload = {
            "ticker": pos.ticker,
            "decision": decision["action"],
            "snapshot": decision["snapshot"],
            "rationale": decision.get("rationale", []),
        }
        results.append(payload)
        if decision["action"] == "SELL_NOW":
            title = f"SELL_NOW: {pos.ticker} {pos.type} {pos.long_strike} {pos.expiry}"
            notify(title, payload)
    os.makedirs("logs/sell_decisions", exist_ok=True)
    stamp = dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    with open(f"logs/sell_decisions/run_{stamp}.json", "w") as f:
        json.dump(results, f, indent=2)
    return results


if __name__ == "__main__":  # pragma: no cover
    run_once()
