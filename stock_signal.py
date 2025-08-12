"""
Stock signal and option strategy utilities.

This module fetches technical indicators using yfinance, evaluates simple
buy-timing rules, and suggests conservative option strategies. It exposes a
`summarize` function returning a JSON-serialisable dictionary that can be
consumed by UIs or other services.

Example
-------
>>> import json
>>> from stock_signal import summarize
>>> print(json.dumps(summarize("QQQ", iv_rank=8.0), indent=2))
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import datetime as dt


import pandas as pd
import yfinance as yf



@dataclass
class Config:
    """Configuration thresholds for signal generation."""

    rsi_overbought: float = 68.0
    rsi_entry_band: tuple = (50.0, 65.0)
    min_price: float = 5.0
    min_avg_dollar_vol: float = 5_000_000
    default_dte_days: int = 35
    bull_call_width: float = 20.0
    bull_put_width: float = 10.0
    csp_otm_pct: float = 0.07  # 7%
    covered_call_otm_pct: float = 0.05  # 5%


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss.replace({0: pd.NA})
    return 100 - (100 / (1 + rs))


def _macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line


def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()


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


def fetch_indicators(ticker: str, period: str = "1y") -> Dict[str, Any]:
    """Fetch price history and compute indicators for *ticker*.

    Returns a dictionary with the latest indicator values.
    """

    if pd is None or yf is None:  # pragma: no cover - requires optional deps
        raise ImportError("pandas and yfinance are required for fetch_indicators")



    data = yf.download(ticker, period=period, progress=False, auto_adjust=True)
    if data.empty:
        raise ValueError("No price data returned")

    close = data["Close"]
    price = float(close.iloc[-1])

    indicators = {
        "price": price,
        "sma20": float(close.rolling(20).mean().iloc[-1]),
        "sma50": float(close.rolling(50).mean().iloc[-1]),
        "sma200": float(close.rolling(200).mean().iloc[-1]),
        "rsi14": float(_rsi(close, 14).iloc[-1]),
    }

    macd_line, macd_signal = _macd(close, 12, 26, 9)
    indicators["macd"] = float(macd_line.iloc[-1])
    indicators["macd_signal"] = float(macd_signal.iloc[-1])

    atr14 = _atr(data, 14)
    indicators["atr14"] = float(atr14.iloc[-1])

    dollar_vol = (data["Close"] * data["Volume"]).rolling(20).mean()
    indicators["avg_dollar_vol"] = float(dollar_vol.iloc[-1])
    return indicators


def compute_buy_timing(ind: Dict[str, Any], cfg: Config) -> Dict[str, Any]:
    """Determine buy timing based on indicator dictionary and config."""

    rationale: List[str] = []
    trend = ind["price"] > ind["sma200"]
    if trend:
        rationale.append("Price > SMA200 (uptrend)")

    momentum = ind["macd"] > ind["macd_signal"] or ind["sma20"] > ind["sma50"]
    if ind["macd"] > ind["macd_signal"]:
        rationale.append("MACD bullish")
    elif ind["sma20"] > ind["sma50"]:
        rationale.append("SMA20 > SMA50 (bullish momentum)")

    not_overbought = ind["rsi14"] < cfg.rsi_overbought
    rationale.append(
        f"RSI {ind['rsi14']:.1f} (<{cfg.rsi_overbought})"
        if not_overbought
        else f"RSI {ind['rsi14']:.1f} (≥{cfg.rsi_overbought})"
    )

    buy_signal = trend and momentum and not_overbought
    if buy_signal:
        if cfg.rsi_entry_band[0] <= ind["rsi14"] <= cfg.rsi_entry_band[1]:
            timing_note = f"Scale-in 50% now; add on pullback to SMA20 (~{ind['sma20']:.2f})."
        else:
            timing_note = "Scale-in now (50%)."
    else:
        timing_note = "No entry."

    return {"buy_signal": buy_signal, "timing_note": timing_note, "rationale": rationale}


def _bull_call(px: float, cfg: Config) -> Dict[str, Any]:
    buy = round(px)
    sell = buy + cfg.bull_call_width
    net_debit = cfg.bull_call_width * 0.25
    max_profit = cfg.bull_call_width - net_debit
    breakeven = buy + net_debit
    return {
        "name": "Bull Call Debit Spread",
        "expiry": _nearest_monthly_expiry(cfg.default_dte_days).isoformat(),
        "legs": [
            {"type": "CALL", "side": "LONG", "strike": buy},
            {"type": "CALL", "side": "SHORT", "strike": sell},
        ],
        "estimates": {
            "net_debit": round(net_debit, 2),
            "max_profit": round(max_profit, 2),
            "max_loss": round(net_debit, 2),
            "breakeven": round(breakeven, 2),
        },
        "why": ["Low IV", "Defined risk", "Moderately bullish"],
    }


def _bull_put(px: float, cfg: Config) -> Dict[str, Any]:
    short = round(px * (1 - 0.07))
    long = short - cfg.bull_put_width
    net_credit = cfg.bull_put_width * 0.25
    max_loss = cfg.bull_put_width - net_credit
    breakeven = short - net_credit
    return {
        "name": "Bull Put Credit Spread",
        "expiry": _nearest_monthly_expiry(cfg.default_dte_days).isoformat(),
        "legs": [
            {"type": "PUT", "side": "SHORT", "strike": short},
            {"type": "PUT", "side": "LONG", "strike": long},
        ],
        "estimates": {
            "net_credit": round(net_credit, 2),
            "max_profit": round(net_credit, 2),
            "max_loss": round(max_loss, 2),
            "breakeven": round(breakeven, 2),
        },
        "why": ["High IV", "Defined risk", "Bullish"],
    }


def _cash_secured_put(px: float, cfg: Config) -> Dict[str, Any]:
    strike = round(px * (1 - cfg.csp_otm_pct))
    credit = strike * 0.01
    return {
        "name": "Cash-Secured Put",
        "expiry": _nearest_monthly_expiry(cfg.default_dte_days).isoformat(),
        "legs": [{"type": "PUT", "side": "SHORT", "strike": strike}],
        "estimates": {"credit": round(credit, 2), "max_loss": round(strike - credit, 2)},
        "why": ["High IV", "Willing to own shares"],
    }


def _covered_call(px: float, cfg: Config) -> Dict[str, Any]:
    strike = round(px * (1 + cfg.covered_call_otm_pct))
    credit = strike * 0.01
    return {
        "name": "Covered Call",
        "precondition": "Own ≥100 shares",
        "expiry": _nearest_monthly_expiry(cfg.default_dte_days).isoformat(),
        "legs": [{"type": "CALL", "side": "SHORT", "strike": strike}],
        "estimates": {"credit": round(credit, 2), "capped_upside": True},
        "why": ["Income", "Mild upside expected"],
    }


def _iron_condor(px: float, cfg: Config) -> Dict[str, Any]:
    width = cfg.bull_put_width
    lower_short = round(px * (1 - 0.07))
    lower_long = lower_short - width
    upper_short = round(px * (1 + 0.07))
    upper_long = upper_short + width
    net_credit = width * 0.25
    max_loss = width - net_credit
    return {
        "name": "Iron Condor",
        "expiry": _nearest_monthly_expiry(cfg.default_dte_days).isoformat(),
        "legs": [
            {"type": "PUT", "side": "LONG", "strike": lower_long},
            {"type": "PUT", "side": "SHORT", "strike": lower_short},
            {"type": "CALL", "side": "SHORT", "strike": upper_short},
            {"type": "CALL", "side": "LONG", "strike": upper_long},
        ],
        "estimates": {
            "net_credit": round(net_credit, 2),
            "max_profit": round(net_credit, 2),
            "max_loss": round(max_loss, 2),
        },
        "why": ["High IV", "Range-bound outlook"],
    }


def pick_strategies(px: float, iv_rank: Optional[float], holding_shares: int, cfg: Config) -> List[Dict[str, Any]]:
    """Select low-risk strategies given price and volatility regime."""

    strategies: List[Dict[str, Any]] = []
    high_iv = iv_rank is not None and iv_rank >= 30

    if not high_iv:
        strategies.append(_bull_call(px, cfg))
    else:
        strategies.append(_bull_put(px, cfg))
        strategies.append(_cash_secured_put(px, cfg))

    if holding_shares >= 100:
        strategies.append(_covered_call(px, cfg))

    return strategies


def summarize(
    ticker: str,
    iv_rank: Optional[float] = None,
    holding_shares: int = 0,
    cfg: Optional[Config] = None,
) -> Dict[str, Any]:
    """High level summary for *ticker* with indicators and strategies."""

    cfg = cfg or Config()
    ind = fetch_indicators(ticker)
    px = ind["price"]

    indicators = {
        k: ind[k]
        for k in [
            "price",
            "rsi14",
            "sma20",
            "sma50",
            "sma200",
            "macd",
            "macd_signal",
            "atr14",
        ]
    }

    if px < cfg.min_price or ind["avg_dollar_vol"] < cfg.min_avg_dollar_vol:
        timing_note = "Filtered: price/volume below minimums"
        return {
            "ticker": ticker,
            "buy_signal": False,
            "timing_note": timing_note,
            "rationale": [],
            "indicators": indicators,
            "selected_strategies": [],
            "disclaimer": "Educational only, not financial advice. Estimates based on models, not live option quotes.",
        }

    timing = compute_buy_timing(ind, cfg)

    strategies: List[Dict[str, Any]]
    if timing["buy_signal"]:
        strategies = pick_strategies(px, iv_rank, holding_shares, cfg)
    else:
        strategies = []
        if iv_rank is not None and iv_rank >= 30:
            strategies.append(_iron_condor(px, cfg))

    return {
        "ticker": ticker,
        "buy_signal": timing["buy_signal"],
        "timing_note": timing["timing_note"],
        "rationale": timing["rationale"],
        "indicators": indicators,
        "selected_strategies": strategies,
        "disclaimer": "Educational only, not financial advice. Estimates based on models, not live option quotes.",
    }
