export type AppState = {
  datasetId: string;
  analysisId: string;
  scenarioId: string;
  reportId: string;
  pca: { explained_variance_ratio: number[] } | null;
  risk: Record<string, number> | null;
  metrics: Record<string, number> | null;
  scenarios: Record<string, Record<string, number>> | null;
  report: { highlights?: string[] } | null;
};

export type UploadResponse = { dataset_id: string; rows: number; columns: string[] };
export type AnalysisRunResponse = { analysis_id: string; status: string };
export type ScenarioRunResponse = { scenario_id: string; status: string };
export type ReportGenerateResponse = { report_id: string; status: string };
