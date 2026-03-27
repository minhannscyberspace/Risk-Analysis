from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    dataset_id: str
    rows: int
    columns: list[str]


class AnalysisRunRequest(BaseModel):
    dataset_id: str = Field(min_length=1)
    confidence_level: float = Field(default=0.95, gt=0.5, lt=0.999)
    weights: list[float] = Field(default_factory=list)


class AnalysisRunResponse(BaseModel):
    analysis_id: str
    status: str


class AnalysisSummaryResponse(BaseModel):
    analysis_id: str
    dataset_id: str
    status: str
    summary: dict[str, object]


class ScenarioRunRequest(BaseModel):
    analysis_id: str = Field(min_length=1)


class ScenarioRunResponse(BaseModel):
    scenario_id: str
    status: str


class ReportGenerateRequest(BaseModel):
    analysis_id: str = Field(min_length=1)


class ReportGenerateResponse(BaseModel):
    report_id: str
    status: str
