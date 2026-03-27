from __future__ import annotations


def generate_report_payload(analysis: dict[str, object]) -> dict[str, object]:
    risk = analysis["risk"]
    metrics = analysis["metrics"]
    pca = analysis["pca"]

    return {
        "title": "Risk-Analysis Summary Report",
        "highlights": [
            f"Mean return: {metrics['mean_return']:.6f}",
            f"Volatility: {metrics['volatility']:.6f}",
            f"Historical VaR: {risk['historical_var']:.6f}",
            f"CVaR: {risk['cvar']:.6f}",
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
        },
        "raw": {
            "summary": analysis["summary"],
            "pca": pca,
            "risk": risk,
            "metrics": metrics,
            "scenarios": analysis.get("scenarios", {}),
        },
    }
