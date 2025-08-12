#!/usr/bin/env python3
# (same content as earlier message — full bot logic)
# To keep this cell short, we'll embed the full previously provided script again.
# --- BEGIN SCRIPT ---
import argparse
import sys
import math
from typing import List, Dict
import numpy as np
import pandas as pd
import yfinance as yf

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss.replace({0: np.nan})
    rsi = 100 - (100 / (1 + rs))
    return rsi

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def crossover(series_a: pd.Series, series_b: pd.Series) -> pd.Series:
    prev = series_a.shift(1) - series_b.shift(1)
    curr = series_a - series_b
    return (prev <= 0) & (curr > 0)

def crossunder(series_a: pd.Series, series_b: pd.Series) -> pd.Series:
    prev = series_a.shift(1) - series_b.shift(1)
    curr = series_a - series_b
    return (prev >= 0) & (curr < 0)

def fetch_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=False)
    if df.empty:
        return df
    df = df.rename(columns={"Open":"Open","High":"High","Low":"Low","Close":"Close","Volume":"Volume"})
    return df

def analyze_ticker(ticker: str, min_price: float, min_dollar_vol: float) -> Dict:
    df = fetch_history(ticker)
    if df.empty or len(df) < 60:
        return {"Ticker": ticker, "Error": "No/insufficient data"}
    close = df["Close"]
    volume = df["Volume"]
    price = float(close.iloc[-1])
    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    rsi14 = rsi(close, 14)
    macd_line, macd_sig, macd_hist = macd(close, 12, 26, 9)
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
    if crossover(sma20, sma50).iloc[-1]:
        signals.append("BUY"); reasons.append("SMA20 crossed above SMA50")
    if crossunder(sma20, sma50).iloc[-1]:
        signals.append("SELL"); reasons.append("SMA20 crossed below SMA50")
    if crossover(macd_line, macd_sig).iloc[-1]:
        signals.append("BUY"); reasons.append("MACD crossed above signal")
    if crossunder(macd_line, macd_sig).iloc[-1]:
        signals.append("SELL"); reasons.append("MACD crossed below signal")
    buy_votes = signals.count("BUY"); sell_votes = signals.count("SELL")
    if not risk_ok:
        recommendation = "HOLD"
        if not passes_price: reasons.append(f"Filtered: price < ${min_price:.2f}")
        if not passes_liquidity: reasons.append(f"Filtered: avg $ vol < {min_dollar_vol:,.0f}")
    elif buy_votes > sell_votes and buy_votes >= 1:
        recommendation = "BUY"
    elif sell_votes > buy_votes and sell_votes >= 1:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"; 
        if not reasons: reasons.append("No strong signals")
    return {
        "Ticker": ticker, "Price": round(price, 4), "RSI14": round(rsi_now, 2),
        "SMA20": float(sma20.iloc[-1]) if not np.isnan(sma20.iloc[-1]) else None,
        "SMA50": float(sma50.iloc[-1]) if not np.isnan(sma50.iloc[-1]) else None,
        "SMA200": float(sma200.iloc[-1]) if not np.isnan(sma200.iloc[-1]) else None,
        "MACD": float(macd_line.iloc[-1]) if not np.isnan(macd_line.iloc[-1]) else None,
        "MACDSignal": float(macd_sig.iloc[-1]) if not np.isnan(macd_sig.iloc[-1]) else None,
        "ATR14": float(atr14.iloc[-1]) if not np.isnan(atr14.iloc[-1]) else None,
        "AvgDollarVol20D": round(avg_dollar_vol, 2) if not math.isnan(avg_dollar_vol) else None,
        "Signals": ", ".join(signals) if signals else "None",
        "Recommendation": recommendation, "Reasons": " | ".join(reasons) if reasons else "None",
    }

def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="AI Signal Bot (free data via yfinance)")
    p.add_argument("--tickers", type=str, default="")
    p.add_argument("--tickers-file", type=str, default="")
    p.add_argument("--min-price", type=float, default=5.0)
    p.add_argument("--min-dollar-vol", type=float, default=5_000_000)
    p.add_argument("--output", type=str, default="")
    return p.parse_args()

def load_universe(args) -> List[str]:
    tickers = []
    if args.tickers: tickers += [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    if args.tickers_file:
        with open(args.tickers_file, "r") as f:
            for line in f:
                sym = line.strip().upper()
                if sym: tickers.append(sym)
    return sorted(list(set(tickers)))

def main():
    args = parse_args()
    universe = load_universe(args)
    if not universe:
        print("No tickers provided. Use --tickers or --tickers-file."); sys.exit(1)
    rows = []
    for t in universe:
        try: rows.append(analyze_ticker(t, args.min_price, args.min_dollar_vol))
        except Exception as e: rows.append({"Ticker": t, "Error": str(e)})
    df = pd.DataFrame(rows)
    cols = ["Ticker","Price","RSI14","SMA20","SMA50","SMA200","MACD","MACDSignal","ATR14","AvgDollarVol20D","Signals","Recommendation","Reasons","Error"]
    for c in cols:
        if c not in df.columns: df[c] = None
    df = df[cols]
    rec_order = {"BUY":0, "SELL":1, "HOLD":2}
    df["rec_rank"] = df["Recommendation"].map(rec_order).fillna(3)
    df["rsi_rank"] = df["RSI14"].fillna(100)
    df = df.sort_values(by=["rec_rank","rsi_rank"], ascending=[True, True]).drop(columns=["rec_rank","rsi_rank"])
    print(df.to_string(index=False))
    if args.output:
        df.to_csv(args.output, index=False); print(f"\nSaved to {args.output}")

if __name__ == "__main__":
    main()
# --- END SCRIPT ---
