import json
import logging
from pathlib import Path

from services.dataset_service import dataset_service
from utils.validators import normalize_test_name

logger = logging.getLogger(__name__)

REFERENCE_DATA_PATH = Path(__file__).parent.parent / "data" / "reference_ranges.json"


class ReferenceService:
    def __init__(self):
        self._ranges: dict = {}
        self._load_ranges()

    def _load_ranges(self) -> None:
        try:
            with open(REFERENCE_DATA_PATH, encoding="utf-8") as f:
                self._ranges = json.load(f)
            logger.info("Loaded %d reference ranges", len(self._ranges))
        except FileNotFoundError:
            logger.error("Reference ranges file not found: %s", REFERENCE_DATA_PATH)
            self._ranges = {}

    def _resolve_reference_key(self, test_name: str) -> str:
        """Resolve test name using Kaggle-derived aliases and direct lookup."""
        normalized = normalize_test_name(test_name)
        if normalized in self._ranges:
            return normalized

        alias_key = dataset_service.resolve_test_alias(test_name)
        if alias_key and alias_key in self._ranges:
            logger.info("Resolved '%s' to reference key '%s' via Kaggle alias", test_name, alias_key)
            return alias_key

        return normalized

    def lookup(self, test_name: str, unit: str, value: float | None = None) -> dict:
        """Look up reference range for a test."""
        ref_key = self._resolve_reference_key(test_name)
        entry = self._ranges.get(ref_key)

        if not entry:
            logger.info("Reference lookup: test '%s' not found", test_name)
            return {
                "found": False,
                "test_name": test_name,
                "message": "Reference range not found",
            }

        lookup_value = value
        lookup_unit = unit.strip()

        if value is not None:
            lookup_value, lookup_unit = dataset_service.convert_unit_if_needed(
                ref_key, value, unit
            )
            if lookup_unit != unit.strip():
                logger.info(
                    "Converted unit for '%s': %s %s -> %s %s",
                    test_name, value, unit, lookup_value, lookup_unit,
                )

        expected_unit = entry["unit"]
        if lookup_unit.lower() != expected_unit.lower():
            logger.info(
                "Reference lookup: unit mismatch for '%s' - expected %s, got %s",
                test_name, expected_unit, lookup_unit,
            )
            return {
                "found": False,
                "test_name": test_name,
                "message": f"{test_name} expects {expected_unit}. Received {unit}.",
                "unit_mismatch": True,
                "expected_unit": expected_unit,
                "received_unit": unit,
            }

        return {
            "found": True,
            "test_name": test_name,
            "unit": entry["unit"],
            "low": entry["low"],
            "high": entry["high"],
            "critical_low": entry.get("critical_low"),
            "critical_high": entry.get("critical_high"),
            "source": "local_reference_database",
            "resolved_key": ref_key,
            "converted_value": lookup_value,
        }


reference_service = ReferenceService()
