import json
import logging
from pathlib import Path

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

  def lookup(self, test_name: str, unit: str) -> dict:
    """Look up reference range for a test."""
    normalized = normalize_test_name(test_name)
    entry = self._ranges.get(normalized)

    if not entry:
      logger.info("Reference lookup: test '%s' not found", test_name)
      return {
        "found": False,
        "test_name": test_name,
        "message": "Reference range not found",
      }

    expected_unit = entry["unit"]
    if unit.strip().lower() != expected_unit.lower():
      logger.info(
        "Reference lookup: unit mismatch for '%s' - expected %s, got %s",
        test_name,
        expected_unit,
        unit,
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
    }


reference_service = ReferenceService()
