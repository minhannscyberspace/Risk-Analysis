import { type Dispatch, type SetStateAction, useState } from "react";
import axios from "axios";

import { API_BASE } from "../lib/api";
import { type AppState, type ReportGenerateResponse } from "../types/app";

export default function ReportPage({
  state,
  setState,
}: {
  state: AppState;
  setState: Dispatch<SetStateAction<AppState>>;
}) {
  const [message, setMessage] = useState("Generate a structured report after analysis.");

  const generateReport = async () => {
    if (!state.analysisId) {
      setMessage("Create an analysis first.");
      return;
    }
    try {
      const generated = await axios.post<ReportGenerateResponse>(`${API_BASE}/reports/generate`, {
        analysis_id: state.analysisId,
      });
      const report = await axios.get(`${API_BASE}/reports/${generated.data.report_id}`);
      setState((prev) => ({
        ...prev,
        reportId: generated.data.report_id,
        report: report.data.report,
      }));
      setMessage("Report generated.");
    } catch (error) {
      setMessage(`Report generation failed: ${String(error)}`);
    }
  };

  return (
    <section className="card">
      <h2>Summary Report</h2>
      <button onClick={generateReport}>Generate Report</button>
      <p>{message}</p>
      <p>Report ID: {state.reportId || "-"}</p>
      <ul>
        {(state.report?.highlights ?? []).map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <p>{state.report?.interpretation?.risk_driver_hint ?? ""}</p>
      <p>{state.report?.interpretation?.tail_risk_hint ?? ""}</p>
      <p>{state.report?.interpretation?.period_hint ?? ""}</p>
    </section>
  );
}
