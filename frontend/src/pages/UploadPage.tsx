import { type ChangeEvent, type Dispatch, type SetStateAction, useState } from "react";
import axios from "axios";

import { API_BASE } from "../lib/api";
import { type AnalysisRunResponse, type AppState, type UploadResponse } from "../types/app";

export default function UploadPage({
  state,
  setState,
}: {
  state: AppState;
  setState: Dispatch<SetStateAction<AppState>>;
}) {
  const [message, setMessage] = useState("Upload a CSV with numeric return columns.");

  const parseWeights = (): number[] => {
    if (!state.weightsInput.trim()) {
      return [];
    }
    return state.weightsInput
      .split(",")
      .map((part) => Number(part.trim()))
      .filter((value) => Number.isFinite(value));
  };

  const onFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const upload = await axios.post<UploadResponse>(`${API_BASE}/upload/file`, formData);
      const run = await axios.post<AnalysisRunResponse>(`${API_BASE}/analysis/run`, {
        dataset_id: upload.data.dataset_id,
        confidence_level: state.confidenceLevel,
        weights: parseWeights(),
      });

      setState((prev) => ({
        ...prev,
        datasetId: upload.data.dataset_id,
        analysisId: run.data.analysis_id,
      }));
      setMessage(`Uploaded ${upload.data.rows} rows. Analysis created.`);
    } catch (error) {
      setMessage(`Upload/analysis failed: ${String(error)}`);
    }
  };

  return (
    <section className="card">
      <h2>Portfolio Input</h2>
      <label htmlFor="confidence-level">Confidence level</label>
      <select
        id="confidence-level"
        value={state.confidenceLevel}
        onChange={(event) =>
          setState((prev) => ({
            ...prev,
            confidenceLevel: Number(event.target.value),
          }))
        }
      >
        <option value={0.95}>95%</option>
        <option value={0.99}>99%</option>
      </select>
      <label htmlFor="weights-input">Asset weights (comma separated, optional)</label>
      <input
        id="weights-input"
        type="text"
        placeholder="e.g. 0.4,0.3,0.2,0.1"
        value={state.weightsInput}
        onChange={(event) =>
          setState((prev) => ({
            ...prev,
            weightsInput: event.target.value,
          }))
        }
      />
      <input type="file" accept=".csv,text/csv" onChange={onFileChange} />
      <p>{message}</p>
      <p>Dataset ID: {state.datasetId || "-"}</p>
      <p>Analysis ID: {state.analysisId || "-"}</p>
    </section>
  );
}
