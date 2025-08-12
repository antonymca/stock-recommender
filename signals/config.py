from dataclasses import dataclass
from typing import Tuple


@dataclass
class Config:
    """Configuration thresholds for signal generation."""

    rsi_overbought: float = 68.0
    rsi_entry_band: Tuple[float, float] = (50.0, 65.0)
    min_price: float = 5.0
    min_avg_dollar_vol: float = 5_000_000
    default_dte_days: int = 35
    bull_call_width: float = 20.0
    bull_put_width: float = 10.0
    csp_otm_pct: float = 0.07  # 7% OTM
    covered_call_otm_pct: float = 0.05  # 5% OTM
