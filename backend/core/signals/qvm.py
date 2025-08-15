"""QVM (Quality, Value, Momentum) scoring utilities.

This module provides a small, testable implementation of a QVM scoring
engine.  Given a DataFrame with ``ticker``, ``sector`` and the three factor
columns (``quality``, ``value`` and ``momentum``) it returns sector
neutral z‑scores and a composite score using configurable weights.

The implementation is intentionally light‑weight and does not fetch data from
external services – callers are expected to supply the raw metrics.  The
weights roughly follow the spec in the project documentation (40% quality,
30% value and 30% momentum) but can be changed by passing a ``QVMWeights``
instance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


@dataclass
class QVMWeights:
    """Container for Q/V/M weights.

    The defaults mirror the initial configuration described in the project
    brief.  The dataclass makes it trivial for callers to persist or customise
    the blend.
    """

    quality: float = 0.4
    value: float = 0.3
    momentum: float = 0.3

    def to_series(self) -> pd.Series:
        return pd.Series(
            {"quality": self.quality, "value": self.value, "momentum": self.momentum}
        )


def _zscore_grouped(df: pd.DataFrame, cols: Iterable[str], group_col: str) -> pd.DataFrame:
    """Return z‑scores for ``cols`` grouped by ``group_col``.

    The calculation uses population standard deviation (``ddof=0``) to avoid
    division by zero errors when a group has only a single member.
    """

    return df.groupby(group_col)[list(cols)].transform(
        lambda s: (s - s.mean()) / s.std(ddof=0)
    )


def compute_qvm_scores(
    df: pd.DataFrame,
    weights: QVMWeights | None = None,
    group_col: str = "sector",
) -> pd.DataFrame:
    """Compute QVM scores for the provided ``df``.

    Parameters
    ----------
    df:
        DataFrame with columns ``ticker``, ``sector``, ``quality``, ``value`` and
        ``momentum``.  Extra columns are preserved.
    weights:
        Optional :class:`QVMWeights` instance to override the default blend.
    group_col:
        Column used for sector/industry grouping when normalising scores.

    Returns
    -------
    pd.DataFrame
        Original data with additional ``*_z`` columns and ``qvm_score`` sorted
        in descending order.
    """

    required = {"ticker", "sector", "quality", "value", "momentum"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    weights = weights or QVMWeights()
    zscores = _zscore_grouped(df, ["quality", "value", "momentum"], group_col)

    composite = (zscores * weights.to_series()).sum(axis=1)

    result = df.copy()
    result[["quality_z", "value_z", "momentum_z"]] = zscores
    result["qvm_score"] = composite

    return result.sort_values("qvm_score", ascending=False).reset_index(drop=True)
