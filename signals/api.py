"""FastAPI endpoints wrapping analysis and strategy logic."""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import Config
from .analysis import compute_core_indicators, analyze_ticker
from .timing import compute_buy_timing
from .options import pick_strategies
from .sell_decision import PositionType, Position, SellConfig, decide_sell

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
    type: str


class AnalyzeResponse(BaseModel):
    ticker: str
    buy_signal: bool
    no_buy_reason: Optional[str] = None
    timing_note: str
    rationale: List[str]
    indicators: IndicatorResp
    signals: SignalsResp
    selected_strategies: List[StrategyResp]


class PositionModel(BaseModel):
    ticker: str
    type: PositionType
    expiry: date
    long_strike: float
    short_strike: Optional[float] = None
    entry_price: float
    entry_date: date
    quantity: int = 1


class SellConfigModel(BaseModel):
    stop_loss_pct: float = 0.40
    take_profit_pct: float = 0.50
    trail_pct: float = 0.35
    time_stop_days: int = 5
    breakeven_buffer: float = 2.0


class SellDecisionRequest(BaseModel):
    position: PositionModel
    config: SellConfigModel = SellConfigModel()
    prev_peak: Optional[float] = None


@app.get("/health")
def health() -> Dict[str, bool]:
    return {"ok": True}


def _analyze_one(req: AnalyzeRequest) -> AnalyzeResponse:
    ind = compute_core_indicators(req.ticker)
    timing = compute_buy_timing(ind, cfg)
    base = analyze_ticker(req.ticker, cfg.min_price, cfg.min_avg_dollar_vol)
    strategies = pick_strategies(
        ind["price"], req.iv_rank, req.holding_shares, cfg, timing["buy_signal"]
    )
    signal_obj = {
        "raw": base.get("Recommendation", "HOLD"),
        "reasons": base.get("Reasons", "").split(" | ") if base.get("Reasons") else [],
    }
    resp_dict = {
        "ticker": req.ticker,
        "buy_signal": timing["buy_signal"],
        "no_buy_reason": timing.get("no_buy_reason"),
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


@app.post("/sell-decision")
def sell_decision_endpoint(req: SellDecisionRequest) -> Dict[str, Any]:
    pos = Position(**req.position.dict())
    cfg_obj = SellConfig(**req.config.dict())
    decision = decide_sell(pos, cfg_obj, prev_peak=req.prev_peak)
    return decision
