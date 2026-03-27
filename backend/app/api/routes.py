from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas import (
    AnalysisRunRequest,
    AnalysisRunResponse,
    AnalysisSummaryResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
    ScenarioRunRequest,
    ScenarioRunResponse,
    UploadResponse,
)
from app.core.report_engine import generate_report_payload
from app.services.analysis_store import store
from app.core.scenario_engine import compute_scenarios
from app.services.orchestrator import parse_returns_csv, run_initial_analysis

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def readiness() -> dict[str, str]:
    if not store.ping():
        raise HTTPException(status_code=503, detail="database not ready")
    return {"status": "ready"}


@router.post("/upload/file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    content = await file.read()
    try:
        frame = parse_returns_csv(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    dataset_id = store.save_dataset(frame)
    return UploadResponse(dataset_id=dataset_id, rows=len(frame), columns=list(frame.columns))


@router.post("/analysis/run", response_model=AnalysisRunResponse)
def run_analysis(request: AnalysisRunRequest) -> AnalysisRunResponse:
    try:
        analysis_id = run_initial_analysis(request.dataset_id, confidence_level=request.confidence_level)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="dataset not found") from exc

    return AnalysisRunResponse(analysis_id=analysis_id, status="completed")


@router.get("/analysis/{analysis_id}", response_model=AnalysisSummaryResponse)
def get_analysis(analysis_id: str) -> AnalysisSummaryResponse:
    try:
        payload = store.get_analysis(analysis_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="analysis not found") from exc

    return AnalysisSummaryResponse(**payload)


@router.get("/analysis/{analysis_id}/pca")
def get_analysis_pca(analysis_id: str) -> dict[str, object]:
    try:
        payload = store.get_analysis(analysis_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="analysis not found") from exc
    return payload["pca"]


@router.get("/analysis/{analysis_id}/risk")
def get_analysis_risk(analysis_id: str) -> dict[str, float]:
    try:
        payload = store.get_analysis(analysis_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="analysis not found") from exc
    return payload["risk"]


@router.get("/analysis/{analysis_id}/metrics")
def get_analysis_metrics(analysis_id: str) -> dict[str, float]:
    try:
        payload = store.get_analysis(analysis_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="analysis not found") from exc
    return payload["metrics"]


@router.post("/scenarios/run", response_model=ScenarioRunResponse)
def run_scenarios(request: ScenarioRunRequest) -> ScenarioRunResponse:
    try:
        analysis = store.get_analysis(request.analysis_id)
        dataset = store.get_dataset(analysis["dataset_id"])
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="analysis not found") from exc

    portfolio_returns = dataset.mean(axis=1)
    scenarios = compute_scenarios(portfolio_returns)
    scenario_id = store.save_scenario_run(request.analysis_id, scenarios)
    return ScenarioRunResponse(scenario_id=scenario_id, status="completed")


@router.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str) -> dict[str, object]:
    try:
        return store.get_scenario_run(scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="scenario not found") from exc


@router.post("/reports/generate", response_model=ReportGenerateResponse)
def generate_report(request: ReportGenerateRequest) -> ReportGenerateResponse:
    try:
        analysis = store.get_analysis(request.analysis_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="analysis not found") from exc

    report_payload = generate_report_payload(analysis)
    report_id = store.save_report(request.analysis_id, report_payload)
    return ReportGenerateResponse(report_id=report_id, status="completed")


@router.get("/reports/{report_id}")
def get_report(report_id: str) -> dict[str, object]:
    try:
        return store.get_report(report_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="report not found") from exc
