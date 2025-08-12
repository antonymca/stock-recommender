"""Decision engine for exiting option positions."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional, Dict, Any

import numpy as np
import pandas as pd
import yfinance as yf

from .analysis import fetch_history, compute_core_indicators


class PositionType(str, Enum):
    """Supported position types."""

    LONG_PUT = "LONG_PUT"
    LONG_CALL = "LONG_CALL"
    DEBIT_SPREAD_CALL = "DEBIT_SPREAD_CALL"
    DEBIT_SPREAD_PUT = "DEBIT_SPREAD_PUT"


@dataclass
class Position:
    ticker: str
    expiry: date
    type: PositionType
    long_strike: float
    short_strike: Optional[float] = None
    entry_price: float = 0.0
    entry_date: date = date.today()
    quantity: int = 1


@dataclass
class SellConfig:
    stop_loss_pct: float = 0.40
    take_profit_pct: float = 0.50
    trail_pct: float = 0.35
    time_stop_days: int = 5
    breakeven_buffer: float = 2.0


# store in-session peaks for trailing stop
_PEAK_CACHE: Dict[str, float] = {}


def _pos_key(pos: Position) -> str:
    return f"{pos.ticker}-{pos.expiry}-{pos.type}-{pos.long_strike}-{pos.short_strike}"


def calc_spread_mark(long_last: float, short_last: float) -> float:
    """Return mark for debit spreads."""
    return float(long_last) - float(short_last)


def get_live_snapshot(position: Position) -> Dict[str, Any]:
    """Fetch live data for the position and underlying indicators."""
    ind = compute_core_indicators(position.ticker)
    t = yf.Ticker(position.ticker)
    expiry_str = position.expiry.isoformat()
    try:
        chain = t.option_chain(expiry_str)
    except Exception as exc:  # pragma: no cover - network/invalid
        raise ValueError(f"Option chain fetch failed: {exc}")

    side = "puts" if position.type in {PositionType.LONG_PUT, PositionType.DEBIT_SPREAD_PUT} else "calls"
    df_long = getattr(chain, side)
    long_row = df_long[df_long["strike"] == position.long_strike]
    if long_row.empty:
        raise ValueError("Long leg not found in chain")
    bid = float(long_row["bid"].iloc[0])
    ask = float(long_row["ask"].iloc[0])
    last = float(long_row.get("lastPrice", long_row.get("last", pd.Series([np.nan]))).iloc[0])
    if not np.isnan(bid) and not np.isnan(ask) and bid > 0 and ask > 0:
        long_last = (bid + ask) / 2
    else:
        long_last = last

    short_last = None
    if position.type in {PositionType.DEBIT_SPREAD_CALL, PositionType.DEBIT_SPREAD_PUT}:
        df_short = getattr(chain, side)
        short_row = df_short[df_short["strike"] == position.short_strike]
        if short_row.empty:
            raise ValueError("Short leg not found in chain")
        bid = float(short_row["bid"].iloc[0])
        ask = float(short_row["ask"].iloc[0])
        last = float(short_row.get("lastPrice", short_row.get("last", pd.Series([np.nan]))).iloc[0])
        if not np.isnan(bid) and not np.isnan(ask) and bid > 0 and ask > 0:
            short_last = (bid + ask) / 2
        else:
            short_last = last
        spread_mark = calc_spread_mark(long_last, short_last)
    else:
        spread_mark = None

    dte = (position.expiry - date.today()).days
    breakeven = position.long_strike
    if position.type in {PositionType.LONG_CALL, PositionType.DEBIT_SPREAD_CALL}:
        breakeven += position.entry_price
    else:
        breakeven -= position.entry_price

    hist = fetch_history(position.ticker, period="6mo")
    above_bk_days = 0
    below_bk_days = 0
    if not hist.empty:
        closes = hist["Close"]
        above_bk_days = int((closes > breakeven).tail(2).sum())
        below_bk_days = int((closes < breakeven).tail(2).sum())

    snapshot: Dict[str, Any] = {
        "underlying": ind["price"],
        "option_last": None if spread_mark is not None else long_last,
        "spread_mark": spread_mark,
        "dte": dte,
        "rsi14": ind["rsi14"],
        "sma20": ind["sma20"],
        "sma50": ind["sma50"],
        "sma200": ind["sma200"],
        "macd": ind["macd"],
        "macd_signal": ind["macd_signal"],
        "atr14": ind["atr14"],
        "breakeven": breakeven,
        "above_breakeven_days": above_bk_days,
        "below_breakeven_days": below_bk_days,
    }

    try:  # optional earnings info
        earn_df = t.get_earnings_dates(limit=1)
        if not earn_df.empty:
            next_earn = earn_df.index[0].date()
            snapshot["earnings_in"] = (next_earn - date.today()).days
    except Exception:  # pragma: no cover - optional
        pass

    return snapshot


def decide_sell(
    position: Position,
    cfg: SellConfig,
    prev_peak: Optional[float] = None,
    snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Decide whether to exit the option position."""
    snap = snapshot or get_live_snapshot(position)
    price = snap.get("option_last") or snap.get("spread_mark")

    key = _pos_key(position)
    peak = prev_peak if prev_peak is not None else _PEAK_CACHE.get(key, price)
    if price is not None and price > (peak or 0):
        peak = price
    _PEAK_CACHE[key] = peak if peak is not None else price

    reasons = []
    action = "HOLD"

    stop_loss_at = position.entry_price * (1 - cfg.stop_loss_pct)
    take_profit_at = position.entry_price * (1 + cfg.take_profit_pct)
    full_tp = position.entry_price * 2

    # A. hard risk controls
    if price is not None and price <= stop_loss_at:
        return {
            "action": "SELL_NOW",
            "snapshot": snap,
            "rationale": ["Hit stop loss"],
            "limits": {
                "entry_price": position.entry_price,
                "take_profit_at": take_profit_at,
                "stop_loss_at": stop_loss_at,
                "trail_from_peak": cfg.trail_pct * 100,
            },
            "notes": "Estimates only; option last used as proxy for mid.",
        }

    dte = snap["dte"]
    breakeven = snap["breakeven"]
    underlying = snap["underlying"]
    profitable = price > position.entry_price if price is not None else False
    if position.type in {PositionType.LONG_PUT, PositionType.DEBIT_SPREAD_PUT}:
        profitable = underlying < breakeven - cfg.breakeven_buffer
    elif position.type in {PositionType.LONG_CALL, PositionType.DEBIT_SPREAD_CALL}:
        profitable = underlying > breakeven + cfg.breakeven_buffer

    if dte <= cfg.time_stop_days and not profitable:
        return {
            "action": "SELL_NOW",
            "snapshot": snap,
            "rationale": ["Time stop: close to expiry and not profitable"],
            "limits": {
                "entry_price": position.entry_price,
                "take_profit_at": take_profit_at,
                "stop_loss_at": stop_loss_at,
                "trail_from_peak": cfg.trail_pct * 100,
            },
            "notes": "Estimates only; option last used as proxy for mid.",
        }

    # B. profit taking
    if price is not None and price >= full_tp:
        action = "SELL_NOW"
        reasons.append("≥100% gain")
    elif price is not None and price >= take_profit_at:
        action = "PARTIAL_SELL"
        reasons.append("Hit profit target")

    # trailing stop
    if action == "HOLD" and price is not None and peak is not None:
        if price <= peak * (1 - cfg.trail_pct):
            action = "SELL_NOW"
            reasons.append("Trailing stop hit")

    # C. technical invalidation
    if action == "HOLD" and position.type == PositionType.LONG_PUT:
        if (
            underlying > snap["sma20"]
            and snap["macd"] >= snap["macd_signal"]
            and snap["rsi14"] > 50
        ):
            action = "SELL_NOW"
            reasons.append("Momentum flipped against put")
        elif snap.get("above_breakeven_days", 0) >= 2:
            action = "SELL_NOW"
            reasons.append("Underlying above breakeven for 2 days")
    if action == "HOLD" and position.type == PositionType.LONG_CALL:
        if (
            underlying < snap["sma20"]
            and snap["macd"] <= snap["macd_signal"]
            and snap["rsi14"] < 50
        ):
            action = "SELL_NOW"
            reasons.append("Momentum flipped against call")
        elif snap.get("below_breakeven_days", 0) >= 2:
            action = "SELL_NOW"
            reasons.append("Underlying below breakeven for 2 days")

    # D. breakeven logic
    if action == "HOLD":
        if position.type in {PositionType.LONG_PUT, PositionType.DEBIT_SPREAD_PUT}:
            if underlying > breakeven + cfg.breakeven_buffer:
                if dte > 20 and snap["macd"] < snap["macd_signal"]:
                    reasons.append("Above breakeven but momentum bearish")
                else:
                    action = "SELL_NOW"
                    reasons.append("Underlying above breakeven + buffer")
        else:
            if underlying < breakeven - cfg.breakeven_buffer:
                if dte > 20 and snap["macd"] > snap["macd_signal"]:
                    reasons.append("Below breakeven but momentum bullish")
                else:
                    action = "SELL_NOW"
                    reasons.append("Underlying below breakeven - buffer")

    # E. earnings heuristic
    if action != "SELL_NOW" and snap.get("earnings_in") is not None:
        if 0 <= snap["earnings_in"] <= 2 and price is not None and price > position.entry_price:
            if action == "HOLD":
                action = "PARTIAL_SELL"
            reasons.append("Earnings soon; consider reducing")

    if not reasons:
        reasons.append("No sell triggers hit")

    return {
        "action": action,
        "snapshot": snap,
        "rationale": reasons,
        "limits": {
            "entry_price": position.entry_price,
            "take_profit_at": take_profit_at,
            "stop_loss_at": stop_loss_at,
            "trail_from_peak": cfg.trail_pct * 100,
        },
        "notes": "Estimates only; option last used as proxy for mid.",
    }
