"""Indicator computation and core analysis functions."""
from __future__ import annotations

from typing import Dict, Any
import math

import numpy as np
import pandas as pd
import yfinance as yf

from .indicators import rsi, sma, macd, atr


def fetch_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLCV history from yfinance."""
    df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=False)
    if df.empty:
        return df
    return df


def compute_core_indicators(ticker: str) -> Dict[str, float]:
    """Compute core indicator set for *ticker*."""
    df = fetch_history(ticker)
    if df.empty or len(df) < 60:
        raise ValueError("No/insufficient data")
    close = df["Close"]
    price = float(close.iloc[-1])
    indicators = {
        "price": price,
        "sma20": float(sma(close, 20).iloc[-1]),
        "sma50": float(sma(close, 50).iloc[-1]),
        "sma200": float(sma(close, 200).iloc[-1]),
        "rsi14": float(rsi(close, 14).iloc[-1]),
    }
    macd_line, macd_signal = macd(close, 12, 26, 9)
    indicators["macd"] = float(macd_line.iloc[-1])
    indicators["macd_signal"] = float(macd_signal.iloc[-1])
    indicators["atr14"] = float(atr(df, 14).iloc[-1])
    dollar_vol = (close * df["Volume"]).rolling(20).mean()
    indicators["avg_dollar_vol"] = float(dollar_vol.iloc[-1])
    return indicators


def _crossover(series_a: pd.Series, series_b: pd.Series) -> pd.Series:
    prev = series_a.shift(1) - series_b.shift(1)
    curr = series_a - series_b
    return (prev <= 0) & (curr > 0)


def _crossunder(series_a: pd.Series, series_b: pd.Series) -> pd.Series:
    prev = series_a.shift(1) - series_b.shift(1)
    curr = series_a - series_b
    return (prev >= 0) & (curr < 0)


def analyze_ticker(ticker: str, min_price: float, min_dollar_vol: float) -> Dict[str, Any]:
    """Analyze *ticker* and produce signal summary for CLI/API."""
    df = fetch_history(ticker)
    if df.empty or len(df) < 60:
        return {"Ticker": ticker, "Error": "No/insufficient data"}

    close = df["Close"]
    volume = df["Volume"]
    price = float(close.iloc[-1])

    sma20 = sma(close, 20)
    sma50 = sma(close, 50)
    sma200 = sma(close, 200)
    rsi14 = rsi(close, 14)
    macd_line, macd_sig = macd(close, 12, 26, 9)
    atr14 = atr(df, 14)

    dollar_vol_20 = (close * volume).rolling(20).mean()
    avg_dollar_vol = float(dollar_vol_20.iloc[-1]) if not dollar_vol_20.isna().iloc[-1] else np.nan

    passes_price = price >= min_price
    passes_liquidity = (not math.isnan(avg_dollar_vol)) and (avg_dollar_vol >= min_dollar_vol)
    risk_ok = passes_price and passes_liquidity

    reasons, signals = [], []
    uptrend = price > (sma200.iloc[-1] if not np.isnan(sma200.iloc[-1]) else -np.inf)
    downtrend = price < (sma200.iloc[-1] if not np.isnan(sma200.iloc[-1]) else np.inf)
    rsi_now = float(rsi14.iloc[-1])

    if rsi_now < 30 and uptrend:
        signals.append("BUY"); reasons.append("RSI<30 in uptrend (SMA200)")
    elif rsi_now > 70 and downtrend:
        signals.append("SELL"); reasons.append("RSI>70 in downtrend (SMA200)")

    if _crossover(sma20, sma50).iloc[-1]:
        signals.append("BUY"); reasons.append("SMA20 crossed above SMA50")
    if _crossunder(sma20, sma50).iloc[-1]:
        signals.append("SELL"); reasons.append("SMA20 crossed below SMA50")
    if _crossover(macd_line, macd_sig).iloc[-1]:
        signals.append("BUY"); reasons.append("MACD crossed above signal")
    if _crossunder(macd_line, macd_sig).iloc[-1]:
        signals.append("SELL"); reasons.append("MACD crossed below signal")

    buy_votes = signals.count("BUY"); sell_votes = signals.count("SELL")
    if not risk_ok:
        recommendation = "HOLD"
        if not passes_price:
            reasons.append(f"Filtered: price < ${min_price:.2f}")
        if not passes_liquidity:
            reasons.append(f"Filtered: avg $ vol < {min_dollar_vol:,.0f}")
    elif buy_votes > sell_votes and buy_votes >= 1:
        recommendation = "BUY"
    elif sell_votes > buy_votes and sell_votes >= 1:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"
        if not reasons:
            reasons.append("No strong signals")

    return {
        "Ticker": ticker,
        "Price": round(price, 4),
        "RSI14": round(rsi_now, 2),
        "SMA20": float(sma20.iloc[-1]) if not np.isnan(sma20.iloc[-1]) else None,
        "SMA50": float(sma50.iloc[-1]) if not np.isnan(sma50.iloc[-1]) else None,
        "SMA200": float(sma200.iloc[-1]) if not np.isnan(sma200.iloc[-1]) else None,
        "MACD": float(macd_line.iloc[-1]) if not np.isnan(macd_line.iloc[-1]) else None,
        "MACDSignal": float(macd_sig.iloc[-1]) if not np.isnan(macd_sig.iloc[-1]) else None,
        "ATR14": float(atr14.iloc[-1]) if not np.isnan(atr14.iloc[-1]) else None,
        "AvgDollarVol20D": round(avg_dollar_vol, 2) if not math.isnan(avg_dollar_vol) else None,
        "Signals": ", ".join(signals) if signals else "None",
        "Recommendation": recommendation,
        "Reasons": " | ".join(reasons) if reasons else "None",
    }
