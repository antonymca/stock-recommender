"""Options strategy selector and estimators."""
from __future__ import annotations
from typing import List, Dict, Optional, Any
import datetime as dt

from .config import Config


def _nearest_monthly_expiry(days: int) -> dt.date:
    target = dt.date.today() + dt.timedelta(days=days)
    year, month = target.year, target.month
    while True:
        first = dt.date(year, month, 1)
        first_friday = first + dt.timedelta(days=(4 - first.weekday()) % 7)
        third_friday = first_friday + dt.timedelta(weeks=2)
        if third_friday >= target:
            return third_friday
        month += 1
        if month > 12:
            month = 1
            year += 1


def _bull_call(px: float, cfg: Config) -> Dict[str, Any]:
    long_strike = round(px)
    short_strike = long_strike + cfg.bull_call_width
    width = short_strike - long_strike
    net_debit = round(width * 0.25, 2)
    max_profit = round(width - net_debit, 2)
    breakeven = round(long_strike + net_debit, 2)
    return {
        "name": "Bull Call Debit Spread",
        "type": "Bullish",
        "expiry": _nearest_monthly_expiry(cfg.default_dte_days).isoformat(),
        "legs": [
            {"type": "CALL", "side": "LONG", "strike": long_strike},
            {"type": "CALL", "side": "SHORT", "strike": short_strike},
        ],
        "estimates": {
            "net_debit": net_debit,
            "max_profit": max_profit,
            "max_loss": net_debit,
            "breakeven": breakeven,
        },
        "why": ["Low IV", "Defined risk", "Moderately bullish"],
        "disclaimer": "Estimates (model), not live quotes",
    }


def _bull_put(px: float, cfg: Config) -> Dict[str, Any]:
    short_strike = round(px * (1 - cfg.csp_otm_pct))
    long_strike = short_strike - cfg.bull_put_width
    width = short_strike - long_strike
    net_credit = round(width * 0.3, 2)
    max_loss = round(width - net_credit, 2)
    breakeven = round(short_strike - net_credit, 2)
    return {
        "name": "Bull Put Credit Spread",
        "type": "Bullish",
        "expiry": _nearest_monthly_expiry(cfg.default_dte_days).isoformat(),
        "legs": [
            {"type": "PUT", "side": "SHORT", "strike": short_strike},
            {"type": "PUT", "side": "LONG", "strike": long_strike},
        ],
        "estimates": {
            "net_credit": net_credit,
            "max_profit": net_credit,
            "max_loss": max_loss,
            "breakeven": breakeven,
        },
        "why": ["High IV", "Defined risk", "Bullish"],
        "disclaimer": "Estimates (model), not live quotes",
    }


def _cash_secured_put(px: float, cfg: Config) -> Dict[str, Any]:
    strike = round(px * (1 - cfg.csp_otm_pct))
    credit = round(strike * 0.1, 2)
    basis = round(strike - credit, 2)
    return {
        "name": "Cash-Secured Put",
        "type": "Income",
        "expiry": _nearest_monthly_expiry(cfg.default_dte_days).isoformat(),
        "legs": [{"type": "PUT", "side": "SHORT", "strike": strike}],
        "estimates": {"credit": credit, "assigned_basis": basis},
        "why": ["High IV", "Willing to own shares"],
        "disclaimer": "Estimates (model), not live quotes",
    }


def _covered_call(px: float, cfg: Config) -> Dict[str, Any]:
    strike = round(px * (1 + cfg.covered_call_otm_pct))
    credit = round(strike * 0.02, 2)
    return {
        "name": "Covered Call",
        "precondition": "Own ≥100 shares",
        "type": "Income",
        "expiry": _nearest_monthly_expiry(cfg.default_dte_days).isoformat(),
        "legs": [{"type": "CALL", "side": "SHORT", "strike": strike}],
        "estimates": {"credit": credit, "capped_upside": True},
        "why": ["Income", "Mild upside expected"],
        "disclaimer": "Estimates (model), not live quotes",
    }


def _protective_put(px: float, cfg: Config) -> Dict[str, Any]:
    strike = round(px * 0.95)
    cost = round(px * 0.02, 2)
    return {
        "name": "Protective Put",
        "type": "Defensive",
        "expiry": _nearest_monthly_expiry(cfg.default_dte_days).isoformat(),
        "legs": [{"type": "PUT", "side": "LONG", "strike": strike}],
        "estimates": {"cost": cost, "floor": strike},
        "why": ["Downside hedge"],
        "disclaimer": "Estimates (model), not live quotes",
    }


def _iron_condor(px: float, cfg: Config) -> Dict[str, Any]:
    width = cfg.bull_put_width
    short_put = round(px * 0.95)
    long_put = short_put - width
    short_call = round(px * 1.05)
    long_call = short_call + width
    credit = round(width * 0.5, 2)
    return {
        "name": "Iron Condor",
        "type": "Income",
        "expiry": _nearest_monthly_expiry(cfg.default_dte_days).isoformat(),
        "legs": [
            {"type": "PUT", "side": "LONG", "strike": long_put},
            {"type": "PUT", "side": "SHORT", "strike": short_put},
            {"type": "CALL", "side": "SHORT", "strike": short_call},
            {"type": "CALL", "side": "LONG", "strike": long_call},
        ],
        "estimates": {"net_credit": credit, "max_profit": credit, "max_loss": round(width - credit, 2)},
        "why": ["Range-bound", "Income"],
        "disclaimer": "Estimates (model), not live quotes",
    }


def pick_strategies(px: float, iv_rank: Optional[float], holding_shares: int, cfg: Config, bullish: bool = True) -> List[Dict[str, Any]]:
    """Select strategies given price, volatility and bias."""
    strategies: List[Dict[str, Any]] = []
    high_iv = iv_rank is not None and iv_rank >= 30

    if bullish:
        if not high_iv:
            strategies.append(_bull_call(px, cfg))
        else:
            strategies.append(_bull_put(px, cfg))
            strategies.append(_cash_secured_put(px, cfg))
        if holding_shares >= 100:
            strategies.append(_covered_call(px, cfg))
    else:
        strategies.append(_protective_put(px, cfg))
        strategies.append(_iron_condor(px, cfg))

    return strategies
