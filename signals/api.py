"""FastAPI endpoints wrapping analysis and strategy logic."""
from __future__ import annotations

from typing import List, Optional, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import Config
from .analysis import compute_core_indicators, analyze_ticker
from .timing import compute_buy_timing
from .options import pick_strategies

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cfg = Config()


class AnalyzeRequest(BaseModel):
    ticker: str
    iv_rank: Optional[float] = None
    holding_shares: int = 0


class IndicatorResp(BaseModel):
    price: float
    rsi14: float
    sma20: float
    sma50: float
    sma200: float
    macd: float
    macd_signal: float
    atr14: float


class SignalsResp(BaseModel):
    raw: str
    reasons: List[str]


class StrategyResp(BaseModel):
    name: str
    expiry: str
    legs: List[Dict[str, Any]]
    estimates: Dict[str, float]
    why: List[str]
    disclaimer: str
    precondition: Optional[str] = None


class AnalyzeResponse(BaseModel):
    ticker: str
    buy_signal: bool
    timing_note: str
    rationale: List[str]
    indicators: IndicatorResp
    signals: SignalsResp
    selected_strategies: List[StrategyResp]


@app.get("/health")
def health() -> Dict[str, bool]:
    return {"ok": True}


def _analyze_one(req: AnalyzeRequest) -> AnalyzeResponse:
    ind = compute_core_indicators(req.ticker)
    timing = compute_buy_timing(ind, cfg)
    base = analyze_ticker(req.ticker, cfg.min_price, cfg.min_avg_dollar_vol)
    strategies = pick_strategies(ind["price"], req.iv_rank, req.holding_shares, cfg) if timing["buy_signal"] else []
    signal_obj = {
        "raw": base.get("Recommendation", "HOLD"),
        "reasons": base.get("Reasons", "").split(" | ") if base.get("Reasons") else [],
    }
    resp_dict = {
        "ticker": req.ticker,
        "buy_signal": timing["buy_signal"],
        "timing_note": timing["timing_note"],
        "rationale": timing["rationale"],
        "indicators": ind,
        "signals": signal_obj,
        "selected_strategies": strategies,
    }
    return AnalyzeResponse(**resp_dict)


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    return _analyze_one(req)


class BatchRequest(BaseModel):
    items: List[AnalyzeRequest]


@app.post("/batch", response_model=List[AnalyzeResponse])
def batch(req: BatchRequest) -> List[AnalyzeResponse]:
    return [_analyze_one(item) for item in req.items]
