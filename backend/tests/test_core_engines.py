import pandas as pd

from app.core.metrics_engine import compute_performance_metrics
from app.core.pca_engine import compute_pca
from app.core.risk_engine import compute_risk_metrics


def _sample_returns() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "asset_a": [0.01, -0.02, 0.015, 0.012, -0.01, 0.007],
            "asset_b": [0.008, -0.01, 0.011, 0.009, -0.006, 0.005],
            "asset_c": [0.012, -0.018, 0.014, 0.01, -0.009, 0.006],
        }
    )


def test_pca_output_shape() -> None:
    returns_df = _sample_returns()
    results = compute_pca(returns_df)
    assert results["feature_names"] == ["asset_a", "asset_b", "asset_c"]
    assert len(results["explained_variance_ratio"]) == 3


def test_risk_and_metrics_outputs() -> None:
    portfolio_returns = _sample_returns().mean(axis=1)
    risk = compute_risk_metrics(portfolio_returns, confidence_level=0.95)
    metrics = compute_performance_metrics(portfolio_returns)

    assert risk["cvar"] <= risk["historical_var"]
    assert 0 <= risk["breach_frequency"] <= 1
    assert "sharpe" in metrics
    assert "max_drawdown" in metrics
