import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from models.schemas import Explanation


@pytest.fixture
def mock_explanation():
    return Explanation(
        summary="Test summary",
        why_flagged="Test why flagged",
        clinical_significance="Test significance",
        next_step="Test next step",
        disclaimer="Test disclaimer",
    )


@pytest.fixture
def mock_llm_service(mock_explanation):
    with patch("agent.lab_agent.llm_service") as mock:
        mock.generate_explanation.return_value = mock_explanation
        yield mock
