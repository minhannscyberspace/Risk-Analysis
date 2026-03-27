from __future__ import annotations

from io import StringIO

import pandas as pd

from app.core.metrics_engine import compute_performance_metrics
from app.core.pca_engine import compute_pca
from app.core.risk_engine import compute_risk_metrics
from app.services.analysis_store import store


def parse_returns_csv(content: bytes) -> pd.DataFrame:
    if not content:
        raise ValueError("uploaded file is empty")

    frame = pd.read_csv(StringIO(content.decode("utf-8")))
    if frame.empty:
        raise ValueError("uploaded dataset is empty")

    numeric = frame.select_dtypes(include=["number"])
    if numeric.empty:
        raise ValueError("dataset must include numeric return columns")

    cleaned = numeric.dropna()
    if cleaned.empty:
        raise ValueError("dataset has no valid numeric rows after cleaning")

    return cleaned


def run_initial_analysis(dataset_id: str, confidence_level: float) -> str:
    returns_df = store.get_dataset(dataset_id)
    portfolio_returns = returns_df.mean(axis=1)

    pca_results = compute_pca(returns_df)
    risk_results = compute_risk_metrics(portfolio_returns, confidence_level=confidence_level)
    metrics_results = compute_performance_metrics(portfolio_returns)

    summary = {
        "mean_return": metrics_results["mean_return"],
        "volatility": metrics_results["volatility"],
        "historical_var": risk_results["historical_var"],
        "cvar": risk_results["cvar"],
    }
    return store.save_analysis(
        dataset_id=dataset_id,
        summary=summary,
        pca=pca_results,
        risk=risk_results,
        metrics=metrics_results,
    )
