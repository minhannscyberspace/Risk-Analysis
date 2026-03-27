from __future__ import annotations


def generate_report_payload(analysis: dict[str, object]) -> dict[str, object]:
    risk = analysis["risk"]
    metrics = analysis["metrics"]
    pca = analysis["pca"]
    summary = analysis["summary"]
    scenarios = analysis.get("scenarios", {}) or {}

    scenario_lines: list[str] = []
    if isinstance(scenarios, dict):
        for scenario_name, scenario_stats in scenarios.items():
            if not isinstance(scenario_stats, dict):
                continue
            pnl_delta = scenario_stats.get("pnl_delta", None)
            max_dd = scenario_stats.get("max_drawdown", None)
            if isinstance(pnl_delta, (int, float)) and isinstance(max_dd, (int, float)):
                scenario_lines.append(
                    f"Scenario {scenario_name}: PnL delta {pnl_delta:.6f}, max drawdown {max_dd:.6f}"
                )

    return {
        "title": "Risk-Analysis Summary Report",
        "highlights": [
            f"Annualized return: {metrics['annualized_return']:.4%}",
            f"Annualized volatility: {metrics['annualized_volatility']:.4%}",
            f"Annualized Sharpe: {metrics['annualized_sharpe']:.3f}",
            f"Annualized Sortino: {metrics['annualized_sortino']:.3f}",
            f"Historical VaR: {risk['historical_var']:.6f}",
            f"CVaR: {risk['cvar']:.6f}",
            f"Backtest breaches (expected vs actual): {risk['expected_breach_rate']:.2%} vs {risk['actual_breach_rate']:.2%}",
            f"Benchmark ({summary['benchmark_ticker']}) Sharpe: {metrics['benchmark_sharpe']:.3f}",
            *(scenario_lines[:6]),
        ],
        "interpretation": {
            "risk_driver_hint": (
                "PC1 dominates risk contribution."
                if pca["explained_variance_ratio"] and pca["explained_variance_ratio"][0] > 0.5
                else "Risk appears distributed across factors."
            ),
            "tail_risk_hint": (
                "Tail risk is elevated; CVaR is materially below VaR."
                if risk["cvar"] < risk["historical_var"]
                else "Tail risk profile appears moderate."
            ),
            "period_hint": f"Analysis window: {summary['test_period_start']} to {summary['test_period_end']}.",
        },
        "raw": {
            "summary": summary,
            "pca": pca,
            "risk": risk,
            "metrics": metrics,
            "scenarios": analysis.get("scenarios", {}),
        },
    }
