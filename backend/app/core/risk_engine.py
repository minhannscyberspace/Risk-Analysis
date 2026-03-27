from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm


def compute_risk_metrics(portfolio_returns: pd.Series, confidence_level: float) -> dict[str, float]:
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

    return {
        "historical_var": historical_var,
        "parametric_var": parametric_var,
        "cvar": cvar,
        "breach_frequency": breaches,
        "confidence_level": confidence_level,
    }
