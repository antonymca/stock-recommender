"""Buy timing logic."""
from __future__ import annotations

from typing import Dict, Any, List

from .config import Config


def compute_buy_timing(ind: Dict[str, float], cfg: Config) -> Dict[str, Any]:
    """Determine buy timing and rationale based on indicators."""
    rationale: List[str] = []

    trend_ok = ind["price"] > ind["sma200"]
    rationale.append("Price > SMA200" if trend_ok else "Price ≤ SMA200")

    macd_bull = ind["macd"] > ind["macd_signal"]
    sma_bull = ind["sma20"] > ind["sma50"]
    momentum_ok = macd_bull or sma_bull
    if macd_bull:
        rationale.append("MACD bullish")
    elif sma_bull:
        rationale.append("SMA20 > SMA50")
    else:
        rationale.append("Momentum weak")

    rsi_ok = ind["rsi14"] < cfg.rsi_overbought
    rationale.append(
        f"RSI {ind['rsi14']:.0f} < {cfg.rsi_overbought}"
        if rsi_ok
        else f"RSI {ind['rsi14']:.0f} ≥ {cfg.rsi_overbought}"
    )

    buy_signal = trend_ok and momentum_ok and rsi_ok

    if not buy_signal:
        note = "Conditions not met"
    else:
        rsi_val = ind["rsi14"]
        low, high = cfg.rsi_entry_band
        if rsi_val < low:
            note = "Wait for momentum confirmation."
        elif low <= rsi_val <= high:
            note = f"Scale-in 50% now; add on pullback to SMA20 (~{ind['sma20']:.0f})."
        else:
            note = "Scale-in 50% now."

    return {"buy_signal": buy_signal, "timing_note": note, "rationale": rationale}
