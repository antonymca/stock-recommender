import pandas as pd
from fastapi.testclient import TestClient

from backend.core.signals.qvm import QVMWeights, compute_qvm_scores
from backend.apps.api.main import app


def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["A", "B", "C", "D"],
            "sector": ["Tech", "Tech", "Health", "Health"],
            "quality": [1.0, 2.0, 3.0, 4.0],
            "value": [4.0, 3.0, 2.0, 1.0],
            "momentum": [1.0, 2.0, 3.0, 4.0],
        }
    )


def test_compute_qvm_scores_basic():
    df = sample_df()
    result = compute_qvm_scores(df, weights=QVMWeights())
    assert "qvm_score" in result.columns
    assert result.loc[result["ticker"] == "B", "qvm_score"].iloc[0] > result.loc[
        result["ticker"] == "A", "qvm_score"
    ].iloc[0]


def test_screen_endpoint():
    client = TestClient(app)
    payload = sample_df().to_dict(orient="records")
    response = client.post("/screen", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    assert {"qvm_score", "quality_z", "value_z", "momentum_z"}.issubset(data[0].keys())
