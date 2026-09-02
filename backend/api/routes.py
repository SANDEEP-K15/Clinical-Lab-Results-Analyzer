import logging

from fastapi import APIRouter, HTTPException

from models.schemas import AnalyzeLabsRequest, AnalyzeLabsResponse, HealthResponse
from services.analysis_service import analyze_labs
from services.dataset_service import dataset_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")


@router.get("/dataset/info")
async def dataset_info():
    """Return Kaggle dataset metadata and inspection summary."""
    return dataset_service.get_dataset_info()


@router.get("/dataset/tests")
async def dataset_tests():
    """Return unique tests discovered in the Kaggle dataset."""
    return {"tests": dataset_service.get_known_tests()}


@router.get("/dataset/sample")
async def dataset_sample():
    """Return mappable lab results from the Kaggle dataset."""
    return {"labs": dataset_service.get_sample_labs()}


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
