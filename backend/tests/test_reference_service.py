import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.reference_service import ReferenceService


class TestReferenceService:
    def setup_method(self):
        self.service = ReferenceService()

    def test_lookup_hemoglobin(self):
        result = self.service.lookup("Hemoglobin", "g/dL")
        assert result["found"] is True
        assert result["low"] == 12.0
        assert result["high"] == 17.5
        assert result["unit"] == "g/dL"

    def test_lookup_normalized_name(self):
        result = self.service.lookup("  HEMOGLOBIN  ", "g/dL")
        assert result["found"] is True

    def test_lookup_unknown_test(self):
        result = self.service.lookup("Unknown Test", "mg/dL")
        assert result["found"] is False

    def test_unit_mismatch(self):
        result = self.service.lookup("Hemoglobin", "mg/dL")
        assert result["found"] is False
        assert "expects g/dL" in result["message"]

    def test_lookup_wbc(self):
        result = self.service.lookup("WBC", "cells/uL")
        assert result["found"] is True
        assert result["critical_low"] == 2000
