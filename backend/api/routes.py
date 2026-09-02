import logging

from fastapi import APIRouter, HTTPException

from models.schemas import AnalyzeLabsRequest, AnalyzeLabsResponse, HealthResponse
from services.analysis_service import analyze_labs

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")


@router.post("/analyze_labs", response_model=AnalyzeLabsResponse)
async def analyze_labs_endpoint(request: AnalyzeLabsRequest):
    logger.info("POST /analyze_labs - %d results", len(request.labs))
    try:
        for lab in request.labs:
            if not lab.test_name or not lab.test_name.strip():
                raise HTTPException(status_code=400, detail="Test name is required.")
            if lab.unit is None or not str(lab.unit).strip():
                raise HTTPException(status_code=400, detail="Unit is required.")

        return await analyze_labs(request)
    except ValueError as e:
        logger.warning("Validation error: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in analyze_labs")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.") from e
