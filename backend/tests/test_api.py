import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from models.schemas import Explanation

client = TestClient(app)

MOCK_EXPLANATION = Explanation(
    summary="Test summary",
    why_flagged="Test why flagged",
    clinical_significance="Test significance",
    next_step="Test next step",
    disclaimer="Test disclaimer",
)


class TestAPI:
    @pytest.fixture(autouse=True)
    def mock_llm(self):
        with patch("agent.lab_agent.llm_service") as mock:
            mock.generate_explanation.return_value = MOCK_EXPLANATION
            yield mock

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_analyze_all_normal(self):
        response = client.post("/analyze_labs", json={
            "labs": [
                {"test_name": "Hemoglobin", "value": 14.5, "unit": "g/dL"},
                {"test_name": "Glucose", "value": 90, "unit": "mg/dL"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["summary"]["normal"] == 2
        assert all(r["severity"] == "NORMAL" for r in data["results"])
        assert all("explanation" in r for r in data["results"])

    def test_analyze_mixed_severity(self):
        response = client.post("/analyze_labs", json={
            "labs": [
                {"test_name": "Glucose", "value": 90, "unit": "mg/dL"},
                {"test_name": "Hemoglobin", "value": 6.5, "unit": "g/dL"},
                {"test_name": "WBC", "value": 12500, "unit": "cells/uL"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        severities = [r["severity"] for r in data["results"]]
        assert severities[0] == "CRITICAL"
        assert "WARNING" in severities
        assert "NORMAL" in severities

    def test_analyze_unknown_test(self):
        response = client.post("/analyze_labs", json={
            "labs": [{"test_name": "Unknown Test", "value": 5.0, "unit": "mg/dL"}]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["results"][0]["severity"] == "UNKNOWN"
        assert data["results"][0]["reference_range"] is None

    def test_missing_test_name(self):
        response = client.post("/analyze_labs", json={
            "labs": [{"test_name": "", "value": 5.0, "unit": "g/dL"}]
        })
        assert response.status_code == 400

    def test_invalid_unit(self):
        response = client.post("/analyze_labs", json={
            "labs": [{"test_name": "Hemoglobin", "value": 14.5, "unit": "mg/dL"}]
        })
        assert response.status_code == 400

    def test_llm_failure_fallback(self):
        with patch("agent.lab_agent.llm_service") as mock:
            mock.generate_explanation.return_value = Explanation(
                summary="AI explanation is temporarily unavailable.",
                why_flagged="The result was classified using the configured reference range.",
                clinical_significance="Please review with a healthcare professional.",
                next_step="Clinical review is recommended.",
                disclaimer="AI explanation unavailable.",
            )
            response = client.post("/analyze_labs", json={
                "labs": [{"test_name": "Hemoglobin", "value": 14.5, "unit": "g/dL"}]
            })
            assert response.status_code == 200
            assert "temporarily unavailable" in response.json()["results"][0]["explanation"]["summary"]

    def test_severity_ordering(self):
        response = client.post("/analyze_labs", json={
            "labs": [
                {"test_name": "Glucose", "value": 90, "unit": "mg/dL"},
                {"test_name": "Hemoglobin", "value": 6.5, "unit": "g/dL"},
                {"test_name": "WBC", "value": 12500, "unit": "cells/uL"},
                {"test_name": "Hemoglobin", "value": 6.0, "unit": "g/dL"},
            ]
        })
        data = response.json()
        severities = [r["severity"] for r in data["results"]]
        critical_indices = [i for i, s in enumerate(severities) if s == "CRITICAL"]
        warning_indices = [i for i, s in enumerate(severities) if s == "WARNING"]
        normal_indices = [i for i, s in enumerate(severities) if s == "NORMAL"]
        if critical_indices and warning_indices:
            assert max(critical_indices) < min(warning_indices)
        if warning_indices and normal_indices:
            assert max(warning_indices) < min(normal_indices)
