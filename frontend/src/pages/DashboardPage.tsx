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

  const loadData = async () => {
    if (!state.analysisId) {
      setMessage("Create an analysis first on Upload page.");
      return;
    }
    try {
      const [pca, risk, metrics] = await Promise.all([
        axios.get(`${API_BASE}/analysis/${state.analysisId}/pca`),
        axios.get(`${API_BASE}/analysis/${state.analysisId}/risk`),
        axios.get(`${API_BASE}/analysis/${state.analysisId}/metrics`),
      ]);
      setState((prev) => ({ ...prev, pca: pca.data, risk: risk.data, metrics: metrics.data }));
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
        <div>Historical VaR: {state.risk?.historical_var?.toFixed(6) ?? "-"}</div>
        <div>CVaR: {state.risk?.cvar?.toFixed(6) ?? "-"}</div>
        <div>Sharpe: {state.metrics?.sharpe?.toFixed(4) ?? "-"}</div>
        <div>Sortino: {state.metrics?.sortino?.toFixed(4) ?? "-"}</div>
      </div>
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
    </section>
  );
}
