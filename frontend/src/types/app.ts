export type AppState = {
  datasetId: string;
  analysisId: string;
  scenarioId: string;
  reportId: string;
  confidenceLevel: number;
  weightsInput: string;
  pca: { explained_variance_ratio: number[] } | null;
  risk: Record<string, unknown> | null;
  metrics: Record<string, unknown> | null;
  scenarios: Record<string, Record<string, number>> | null;
  summary: Record<string, unknown> | null;
  report: { highlights?: string[]; interpretation?: Record<string, string> } | null;
};

export type UploadResponse = { dataset_id: string; rows: number; columns: string[] };
export type AnalysisRunResponse = { analysis_id: string; status: string };
export type ScenarioRunResponse = { scenario_id: string; status: string };
export type ReportGenerateResponse = { report_id: string; status: string };
