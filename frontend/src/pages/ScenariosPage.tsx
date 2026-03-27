import { type Dispatch, type SetStateAction, useState } from "react";
import axios from "axios";

import { API_BASE } from "../lib/api";
import { type AppState, type ScenarioRunResponse } from "../types/app";

export default function ScenariosPage({
  state,
  setState,
}: {
  state: AppState;
  setState: Dispatch<SetStateAction<AppState>>;
}) {
  const [message, setMessage] = useState("Run scenarios once analysis is ready.");

  const runScenarios = async () => {
    if (!state.analysisId) {
      setMessage("Create an analysis first.");
      return;
    }
    try {
      const run = await axios.post<ScenarioRunResponse>(`${API_BASE}/scenarios/run`, {
        analysis_id: state.analysisId,
      });
      const result = await axios.get(`${API_BASE}/scenarios/${run.data.scenario_id}`);
      setState((prev) => ({
        ...prev,
        scenarioId: run.data.scenario_id,
        scenarios: result.data.scenarios,
      }));
      setMessage("Scenario simulation complete.");
    } catch (error) {
      setMessage(`Scenario run failed: ${String(error)}`);
    }
  };

  return (
    <section className="card">
      <h2>Scenario Analysis</h2>
      <button onClick={runScenarios}>Run Scenarios</button>
      <p>{message}</p>
      <p>Scenario ID: {state.scenarioId || "-"}</p>
      <pre>{state.scenarios ? JSON.stringify(state.scenarios, null, 2) : "No scenario output yet."}</pre>
    </section>
  );
}
