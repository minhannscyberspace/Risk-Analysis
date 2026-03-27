from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm


def compute_risk_metrics(portfolio_returns: pd.Series, confidence_level: float) -> dict[str, object]:
    if portfolio_returns.empty:
        raise ValueError("portfolio_returns cannot be empty")

    alpha_tail = 1.0 - confidence_level
    series = portfolio_returns.to_numpy(dtype=float)

    historical_var = float(np.quantile(series, alpha_tail))
    cvar = float(series[series <= historical_var].mean())

    mu = float(np.mean(series))
    sigma = float(np.std(series, ddof=1))
    z = float(norm.ppf(alpha_tail))
    parametric_var = float(mu + z * sigma)

    breaches = float(np.mean(series <= historical_var))
    expected_breach_rate = alpha_tail

    rolling_var = portfolio_returns.rolling(250, min_periods=250).quantile(alpha_tail).dropna()
    aligned_returns = portfolio_returns.reindex(rolling_var.index)
    rolling_breaches = (aligned_returns <= rolling_var).astype(int)
    actual_breach_rate = float(rolling_breaches.mean()) if not rolling_breaches.empty else breaches

    backtest_points = [
        {
            "date": str(idx.date()) if hasattr(idx, "date") else str(idx),
            "return": float(ret),
            "var": float(var),
            "breach": int(br),
        }
        for idx, ret, var, br in zip(
            rolling_var.index[-120:],
            aligned_returns.iloc[-120:],
            rolling_var.iloc[-120:],
            rolling_breaches.iloc[-120:],
        )
    ]

    return {
        "historical_var": historical_var,
        "parametric_var": parametric_var,
        "cvar": cvar,
        "breach_frequency": breaches,
        "confidence_level": confidence_level,
        "expected_breach_rate": expected_breach_rate,
        "actual_breach_rate": actual_breach_rate,
        "rolling_var_250_last": float(rolling_var.iloc[-1]) if not rolling_var.empty else historical_var,
        "backtest_points": backtest_points,
    }
