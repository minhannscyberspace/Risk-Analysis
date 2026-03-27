from __future__ import annotations

import numpy as np
import pandas as pd


def _max_drawdown(portfolio_returns: pd.Series) -> float:
    cumulative = (1 + portfolio_returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative / peak) - 1.0
    return float(drawdown.min())


def compute_performance_metrics(portfolio_returns: pd.Series, risk_free_rate: float = 0.0) -> dict[str, float]:
    if portfolio_returns.empty:
        raise ValueError("portfolio_returns cannot be empty")

    excess = portfolio_returns - risk_free_rate / 252.0
    mean_excess = float(excess.mean())
    volatility = float(portfolio_returns.std(ddof=1))

    downside = portfolio_returns[portfolio_returns < 0]
    downside_vol = float(downside.std(ddof=1)) if not downside.empty else 0.0

    sharpe = mean_excess / volatility if volatility > 0 else 0.0
    sortino = mean_excess / downside_vol if downside_vol > 0 else 0.0

    rolling_vol = portfolio_returns.rolling(5, min_periods=5).std(ddof=1).dropna()
    rolling_vol_mean = float(rolling_vol.mean()) if not rolling_vol.empty else volatility

    return {
        "mean_return": float(portfolio_returns.mean()),
        "volatility": volatility,
        "sharpe": float(sharpe),
        "sortino": float(sortino),
        "max_drawdown": _max_drawdown(portfolio_returns),
        "rolling_volatility": rolling_vol_mean,
    }
