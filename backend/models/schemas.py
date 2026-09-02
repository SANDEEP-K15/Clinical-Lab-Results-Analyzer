from pydantic import BaseModel, Field


class LabResult(BaseModel):
    test_name: str
    value: float
    unit: str


class AnalyzeLabsRequest(BaseModel):
    labs: list[LabResult] = Field(..., min_length=1)


class ReferenceRange(BaseModel):
    low: float
    high: float
    unit: str
    source: str


class Explanation(BaseModel):
    summary: str
    why_flagged: str
    clinical_significance: str
    next_step: str
    disclaimer: str


class AnalysisResult(BaseModel):
    test_name: str
    value: float
    unit: str
    reference_range: ReferenceRange | None
    severity: str
    classification_reason: str
    explanation: Explanation


class SummaryCounts(BaseModel):
    critical: int = 0
    warning: int = 0
    normal: int = 0
    unknown: int = 0


class AnalyzeLabsResponse(BaseModel):
    success: bool
    total_results: int
    summary: SummaryCounts
    results: list[AnalysisResult]


class HealthResponse(BaseModel):
    status: str
