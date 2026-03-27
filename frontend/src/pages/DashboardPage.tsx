import { type Dispatch, type SetStateAction, useMemo, useState } from "react";
import axios from "axios";

import { API_BASE } from "../lib/api";
import { type AppState } from "../types/app";

export default function DashboardPage({
  state,
  setState,
}: {
  state: AppState;
  setState: Dispatch<SetStateAction<AppState>>;
}) {
  const [message, setMessage] = useState("Load analysis outputs after upload.");
  const asNumber = (value: unknown): number | null => (typeof value === "number" ? value : null);

  const loadData = async () => {
    if (!state.analysisId) {
      setMessage("Create an analysis first on Upload page.");
      return;
    }
    try {
      const [summary, pca, risk, metrics] = await Promise.all([
        axios.get(`${API_BASE}/analysis/${state.analysisId}`),
        axios.get(`${API_BASE}/analysis/${state.analysisId}/pca`),
        axios.get(`${API_BASE}/analysis/${state.analysisId}/risk`),
        axios.get(`${API_BASE}/analysis/${state.analysisId}/metrics`),
      ]);
      setState((prev) => ({
        ...prev,
        summary: summary.data.summary,
        pca: pca.data,
        risk: risk.data,
        metrics: metrics.data,
      }));
      setMessage("Dashboard data loaded.");
    } catch (error) {
      setMessage(`Failed to load dashboard data: ${String(error)}`);
    }
  };

  const varianceBars = useMemo(() => {
    const y = state.pca?.explained_variance_ratio ?? [];
    return y.map((value, index) => ({ component: `PC${index + 1}`, value }));
  }, [state.pca]);

  return (
    <section className="card">
      <h2>Risk Dashboard</h2>
      <button onClick={loadData}>Load Dashboard Data</button>
      <p>{message}</p>
      <div className="metrics">
        <div>Historical VaR: {asNumber(state.risk?.historical_var)?.toFixed(6) ?? "-"}</div>
        <div>CVaR: {asNumber(state.risk?.cvar)?.toFixed(6) ?? "-"}</div>
        <div>Sharpe (daily): {asNumber(state.metrics?.sharpe)?.toFixed(4) ?? "-"}</div>
        <div>Sortino (daily): {asNumber(state.metrics?.sortino)?.toFixed(4) ?? "-"}</div>
        <div>Annualized return: {(asNumber(state.metrics?.annualized_return) ?? 0).toFixed(4)}</div>
        <div>Annualized vol: {(asNumber(state.metrics?.annualized_volatility) ?? 0).toFixed(4)}</div>
        <div>Annualized Sharpe: {(asNumber(state.metrics?.annualized_sharpe) ?? 0).toFixed(4)}</div>
        <div>Benchmark Sharpe: {(asNumber(state.metrics?.benchmark_sharpe) ?? 0).toFixed(4)}</div>
        <div>Benchmark annualized return: {(asNumber(state.metrics?.benchmark_annualized_return) ?? 0).toFixed(4)}</div>
        <div>Benchmark annualized vol: {(asNumber(state.metrics?.benchmark_annualized_volatility) ?? 0).toFixed(4)}</div>
        <div>Benchmark max drawdown: {(asNumber(state.metrics?.benchmark_max_drawdown) ?? 0).toFixed(4)}</div>
        <div>Expected breach: {(100 * (asNumber(state.risk?.expected_breach_rate) ?? 0)).toFixed(2)}%</div>
        <div>Actual breach: {(100 * (asNumber(state.risk?.actual_breach_rate) ?? 0)).toFixed(2)}%</div>
      </div>
      <p>
        Period: {String(state.summary?.test_period_start ?? "-")} to {String(state.summary?.test_period_end ?? "-")}
      </p>
      <p>Benchmark: {String(state.summary?.benchmark_ticker ?? "-")}</p>
      <p>Warnings: {Array.isArray(state.summary?.warnings) ? state.summary?.warnings.join(" | ") : "None"}</p>
      <div className="bar-chart" aria-label="PCA explained variance bar chart">
        <h3>PCA Explained Variance</h3>
        {varianceBars.length === 0 ? (
          <p>No PCA data loaded yet.</p>
        ) : (
          varianceBars.map((bar) => (
            <div className="bar-row" key={bar.component}>
              <span className="bar-label">{bar.component}</span>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${Math.max(1, bar.value * 100)}%` }} />
              </div>
              <span className="bar-value">{(bar.value * 100).toFixed(2)}%</span>
            </div>
          ))
        )}
      </div>

      <div className="section">
        <h3>VaR Backtest (rolling 250d)</h3>
        <p>
          Expected breach rate: {(asNumber(state.risk?.expected_breach_rate) ?? 0).toFixed(2)}% · Actual:
          {(asNumber(state.risk?.actual_breach_rate) ?? 0).toFixed(2)}%
        </p>
        {Array.isArray(state.risk?.backtest_points) && state.risk?.backtest_points.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Return</th>
                <th>VaR</th>
                <th>Breach</th>
              </tr>
            </thead>
            <tbody>
              {state.risk.backtest_points.slice(-10).map((pt, idx) => {
                const p = pt as { date?: string; return?: number; var?: number; breach?: number };
                return (
                  <tr key={`${p.date ?? idx}-${idx}`}>
                    <td>{String(p.date ?? "-")}</td>
                    <td>{typeof p.return === "number" ? p.return.toFixed(5) : "-"}</td>
                    <td>{typeof p.var === "number" ? p.var.toFixed(5) : "-"}</td>
                    <td>{p.breach === 1 ? "Yes" : "No"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <p>No backtest points available.</p>
        )}
      </div>
    </section>
  );
}
