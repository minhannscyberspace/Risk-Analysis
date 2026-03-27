from __future__ import annotations

from io import StringIO

import numpy as np
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

    if "Date" in frame.columns:
        frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
        frame = frame.dropna(subset=["Date"]).set_index("Date")

    numeric = frame.select_dtypes(include=["number"])
    if numeric.empty:
        raise ValueError("dataset must include numeric return columns")

    missing_count = int(numeric.isna().sum().sum())
    cleaned = numeric.dropna()
    if cleaned.empty:
        raise ValueError("dataset has no valid numeric rows after cleaning")

    return cleaned.sort_index()


def run_initial_analysis(dataset_id: str, confidence_level: float, weights: list[float] | None = None) -> str:
    returns_df = store.get_dataset(dataset_id)
    if returns_df.empty:
        raise ValueError("dataset is empty")

    n_assets = returns_df.shape[1]
    if weights is None or len(weights) == 0:
        weights_arr = np.ones(n_assets) / n_assets
    else:
        if len(weights) != n_assets:
            raise ValueError(f"weights length must match number of assets ({n_assets})")
        weights_arr = np.array(weights, dtype=float)
        if float(weights_arr.sum()) <= 0:
            raise ValueError("weights sum must be positive")
        weights_arr = weights_arr / weights_arr.sum()

    portfolio_returns = returns_df.mul(weights_arr, axis=1).sum(axis=1)
    benchmark_col = "SPY" if "SPY" in returns_df.columns else returns_df.columns[0]
    benchmark_returns = returns_df[benchmark_col]

    pca_results = compute_pca(returns_df)
    risk_results = compute_risk_metrics(portfolio_returns, confidence_level=confidence_level)
    metrics_results = compute_performance_metrics(portfolio_returns, benchmark_returns=benchmark_returns)

    warnings: list[str] = []
    if len(returns_df) < 252:
        warnings.append("Short history (<252 rows): annualized metrics may be noisy.")
    zscores = ((returns_df - returns_df.mean()) / returns_df.std(ddof=1)).abs()
    if (zscores > 5).any().any():
        warnings.append("Extreme outliers detected (|z| > 5).")

    summary = {
        "mean_return_daily": metrics_results["mean_return"],
        "volatility_daily": metrics_results["volatility"],
        "mean_return_annualized": metrics_results["annualized_return"],
        "volatility_annualized": metrics_results["annualized_volatility"],
        "historical_var": risk_results["historical_var"],
        "cvar": risk_results["cvar"],
        "benchmark_ticker": benchmark_col,
        "test_period_start": str(returns_df.index.min().date()) if hasattr(returns_df.index.min(), "date") else "n/a",
        "test_period_end": str(returns_df.index.max().date()) if hasattr(returns_df.index.max(), "date") else "n/a",
        "warnings": warnings,
        "weights": {col: float(weights_arr[idx]) for idx, col in enumerate(returns_df.columns)},
    }
    return store.save_analysis(
        dataset_id=dataset_id,
        summary=summary,
        pca=pca_results,
        risk=risk_results,
        metrics=metrics_results,
    )
