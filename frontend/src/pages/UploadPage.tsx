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

  const onFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const upload = await axios.post<UploadResponse>(`${API_BASE}/upload/file`, formData);
      const run = await axios.post<AnalysisRunResponse>(`${API_BASE}/analysis/run`, {
        dataset_id: upload.data.dataset_id,
        confidence_level: 0.95,
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
      <input type="file" accept=".csv,text/csv" onChange={onFileChange} />
      <p>{message}</p>
      <p>Dataset ID: {state.datasetId || "-"}</p>
      <p>Analysis ID: {state.analysisId || "-"}</p>
    </section>
  );
}
