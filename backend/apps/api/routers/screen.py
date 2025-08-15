"""Screening endpoint returning QVM scores for supplied tickers."""

from __future__ import annotations

from typing import List

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel

from ...core.signals.qvm import QVMWeights, compute_qvm_scores


class TickerIn(BaseModel):
    ticker: str
    sector: str
    quality: float
    value: float
    momentum: float


class TickerOut(BaseModel):
    ticker: str
    qvm_score: float
    quality_z: float
    value_z: float
    momentum_z: float


router = APIRouter()


@router.post("/screen", response_model=List[TickerOut])
def screen_endpoint(tickers: List[TickerIn]):
    """Rank the supplied universe using the QVM scoring model."""

    df = pd.DataFrame([t.dict() for t in tickers])
    result = compute_qvm_scores(df, weights=QVMWeights())
    return result[[
        "ticker",
        "qvm_score",
        "quality_z",
        "value_z",
        "momentum_z",
    ]].to_dict(orient="records")
