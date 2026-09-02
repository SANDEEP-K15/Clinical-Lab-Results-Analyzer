import logging

from services.classification_service import classify_lab_value
from services.reference_service import reference_service
from utils.validators import validate_lab_fields

logger = logging.getLogger(__name__)


def reference_range_lookup(test_name: str, unit: str, value: float | None = None) -> dict:
    """MCP tool: Look up reference range for a lab test."""
    return reference_service.lookup(test_name, unit, value=value)


def validate_lab_result(test_name: str, value: float, unit: str) -> dict:
    """MCP tool: Validate a lab result."""
    valid, error = validate_lab_fields(test_name, value, unit)
    if not valid:
      return {"valid": False, "test_name": test_name, "message": error}

    ref = reference_service.lookup(test_name, unit, value=value)
    if not ref.get("found"):
      if ref.get("unit_mismatch"):
        return {"valid": False, "test_name": test_name, "message": ref["message"]}
      return {
        "valid": True,
        "test_name": test_name,
        "value": value,
        "unit": unit,
        "reference_available": False,
      }

    return {
      "valid": True,
      "test_name": test_name,
      "value": value,
      "unit": unit,
      "reference_available": True,
    }


def classify_lab_result(
    test_name: str,
    value: float,
    unit: str,
    reference_low: float,
    reference_high: float,
    critical_low: float | None = None,
    critical_high: float | None = None,
) -> dict:
    """MCP tool: Classify a lab result deterministically."""
    classification, reason = classify_lab_value(
      value, reference_low, reference_high, critical_low, critical_high
    )
    return {"classification": classification, "reason": reason}
