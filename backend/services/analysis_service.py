import logging

from agent.lab_agent import lab_agent
from models.schemas import AnalyzeLabsRequest, AnalyzeLabsResponse

logger = logging.getLogger(__name__)


async def analyze_labs(request: AnalyzeLabsRequest) -> AnalyzeLabsResponse:
    logger.info("Analysis service: received %d lab results", len(request.labs))
    return await lab_agent.analyze(request.labs)
