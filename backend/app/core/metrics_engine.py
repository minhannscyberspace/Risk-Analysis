from __future__ import annotations

import numpy as np
import pandas as pd


def _max_drawdown(portfolio_returns: pd.Series) -> float:
    cumulative = (1 + portfolio_returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative / peak) - 1.0
    return float(drawdown.min())


def _safe_ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator > 0 else 0.0


def compute_performance_metrics(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    risk_free_rate: float = 0.0,
) -> dict[str, float]:
    if portfolio_returns.empty:
        raise ValueError("portfolio_returns cannot be empty")

    benchmark = benchmark_returns.reindex(portfolio_returns.index).dropna()
    aligned_portfolio = portfolio_returns.reindex(benchmark.index) if not benchmark.empty else portfolio_returns

    annualization = np.sqrt(252.0)
    excess = portfolio_returns - risk_free_rate / 252.0
    mean_excess = float(excess.mean())
    volatility = float(portfolio_returns.std(ddof=1))

    downside = portfolio_returns[portfolio_returns < 0]
    downside_vol = float(downside.std(ddof=1)) if not downside.empty else 0.0

    sharpe = _safe_ratio(mean_excess, volatility)
    sortino = _safe_ratio(mean_excess, downside_vol)

    rolling_vol = portfolio_returns.rolling(5, min_periods=5).std(ddof=1).dropna()
    rolling_vol_mean = float(rolling_vol.mean()) if not rolling_vol.empty else volatility

    benchmark_mean = float(aligned_portfolio.mean()) if benchmark.empty else float(benchmark.mean())
    benchmark_vol = float(aligned_portfolio.std(ddof=1)) if benchmark.empty else float(benchmark.std(ddof=1))
    benchmark_max_dd = _max_drawdown(aligned_portfolio) if benchmark.empty else _max_drawdown(benchmark)
    benchmark_sharpe = _safe_ratio(benchmark_mean - risk_free_rate / 252.0, benchmark_vol)

    annual_return = float(portfolio_returns.mean() * 252.0)
    annual_volatility = float(volatility * annualization)
    annual_sharpe = _safe_ratio(annual_return - risk_free_rate, annual_volatility)
    downside_sigma = float(portfolio_returns[portfolio_returns < 0].std(ddof=1))
    if np.isnan(downside_sigma):
        downside_sigma = 0.0
    annual_downside_vol = downside_sigma * annualization
    annual_sortino = _safe_ratio(annual_return - risk_free_rate, annual_downside_vol)

    benchmark_annualized_return = float(benchmark_mean * 252.0)
    benchmark_annualized_volatility = float(benchmark_vol * annualization)
    benchmark_annualized_sharpe = _safe_ratio(
        benchmark_annualized_return - risk_free_rate, benchmark_annualized_volatility
    )

    return {
        "mean_return": float(portfolio_returns.mean()),
        "volatility": volatility,
        "sharpe": float(sharpe),
        "sortino": float(sortino),
        "annualized_return": annual_return,
        "annualized_volatility": annual_volatility,
        "annualized_sharpe": annual_sharpe,
        "annualized_sortino": annual_sortino,
        "max_drawdown": _max_drawdown(portfolio_returns),
        "rolling_volatility": rolling_vol_mean,
        "benchmark_mean_return": benchmark_mean,
        "benchmark_volatility": benchmark_vol,
        "benchmark_max_drawdown": benchmark_max_dd,
        "benchmark_sharpe": benchmark_sharpe,
        "benchmark_annualized_return": benchmark_annualized_return,
        "benchmark_annualized_volatility": benchmark_annualized_volatility,
        "benchmark_annualized_sharpe": benchmark_annualized_sharpe,
    }
