from __future__ import annotations

import pandas as pd


def compute_scenarios(portfolio_returns: pd.Series) -> dict[str, dict[str, float]]:
    if portfolio_returns.empty:
        raise ValueError("portfolio_returns cannot be empty")

    base_mean = float(portfolio_returns.mean())
    base_vol = float(portfolio_returns.std(ddof=1))

    historical_crisis = portfolio_returns.nsmallest(max(1, len(portfolio_returns) // 10))
    historical_mean = float(historical_crisis.mean())

    volatility_shock = portfolio_returns * 1.5
    volatility_mean = float(volatility_shock.mean())

    correlation_shock = portfolio_returns * 0.75
    correlation_mean = float(correlation_shock.mean())

    return {
        "historical_crisis": {
            "mean_return": historical_mean,
            "delta_vs_base": historical_mean - base_mean,
        },
        "volatility_shock": {
            "mean_return": volatility_mean,
            "delta_vs_base": volatility_mean - base_mean,
            "volatility_proxy": base_vol * 1.5,
        },
        "correlation_shock": {
            "mean_return": correlation_mean,
            "delta_vs_base": correlation_mean - base_mean,
        },
    }
