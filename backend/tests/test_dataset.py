import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.dataset_service import DatasetService


class TestDatasetService:
    def setup_method(self):
        self.service = DatasetService()

    def test_dataset_available(self):
        info = self.service.get_dataset_info()
        assert info.get("available") is True or info.get("total_rows", 0) > 0

    def test_dataset_source_url(self):
        info = self.service.get_dataset_info()
        assert "pinuto/laboratory-test-results-anonymized-dataset" in info.get("source_url", "")

    def test_known_tests_from_kaggle(self):
        tests = self.service.get_known_tests()
        assert len(tests) > 0
        test_names = [t["test_name"] for t in tests]
        assert "hemoglobin" in test_names

    def test_resolve_hemoglobin_alias(self):
        assert self.service.resolve_test_alias("Hemoglobin") == "hemoglobin"

    def test_resolve_lokosit_alias(self):
        assert self.service.resolve_test_alias("Lökosit") == "wbc"

    def test_unit_conversion_wbc(self):
        value, unit = self.service.convert_unit_if_needed("wbc", 6.37, "10^3/uL")
        assert value == 6370.0
        assert unit == "cells/uL"

    def test_sample_labs_from_kaggle(self):
        labs = self.service.get_sample_labs()
        assert len(labs) >= 3
        assert all("test_name" in lab for lab in labs)
