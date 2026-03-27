from __future__ import annotations

import numpy as np
import pandas as pd


def _max_drawdown(returns: pd.Series) -> float:
    cumulative = (1.0 + returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative / peak) - 1.0
    return float(drawdown.min())


def _scenario_stats(name: str, base_returns: pd.Series, scenario_returns: pd.Series) -> dict[str, float]:
    base_pnl = float((1.0 + base_returns).prod() - 1.0)
    scenario_pnl = float((1.0 + scenario_returns).prod() - 1.0)
    return {
        "mean_return": float(scenario_returns.mean()),
        "pnl_delta": scenario_pnl - base_pnl,
        "max_drawdown": _max_drawdown(scenario_returns),
    }


def compute_scenarios(returns_df: pd.DataFrame, weights: np.ndarray) -> dict[str, dict[str, float]]:
    if returns_df.empty:
        raise ValueError("returns_df cannot be empty")

    base_returns = returns_df.mul(weights, axis=1).sum(axis=1)

    worst_day = float(base_returns.min())
    worst_week_returns = base_returns.rolling(5, min_periods=5).sum().dropna()
    worst_week = float(worst_week_returns.min()) if not worst_week_returns.empty else worst_day
    historical_replay = pd.Series([worst_day / 5.0] * 5 + [worst_week / 5.0] * 5)

    volatility_shock = (base_returns * 1.5) - 0.001

    corr = returns_df.corr().fillna(0.0).to_numpy()
    vols = returns_df.std(ddof=1).fillna(0.0).to_numpy()
    shocked_corr = corr.copy()
    for i in range(shocked_corr.shape[0]):
        for j in range(shocked_corr.shape[1]):
            if i != j:
                shocked_corr[i, j] = max(shocked_corr[i, j], 0.8)
    shocked_cov = np.outer(vols, vols) * shocked_corr
    shocked_mean = returns_df.mean().to_numpy() - 0.0005
    rng = np.random.default_rng(42)
    simulated = rng.multivariate_normal(shocked_mean, shocked_cov, size=len(returns_df))
    correlation_shock = pd.DataFrame(simulated, columns=returns_df.columns).mul(weights, axis=1).sum(axis=1)

    return {
        "historical_worst_day_week_replay": {
            **_scenario_stats("historical_worst_day_week_replay", base_returns, historical_replay),
            "worst_day_return": worst_day,
            "worst_week_return": worst_week,
        },
        "volatility_spike_negative_drift": {
            **_scenario_stats("volatility_spike_negative_drift", base_returns, volatility_shock),
            "volatility_multiplier": 1.5,
            "daily_drift_shift": -0.001,
        },
        "correlation_increase_covariance_reestimate": {
            **_scenario_stats("correlation_increase_covariance_reestimate", base_returns, correlation_shock),
            "off_diag_correlation_floor": 0.8,
        },
    }
