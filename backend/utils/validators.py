import re


def normalize_test_name(test_name: str) -> str:
    """Normalize test name for lookup."""
    normalized = test_name.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def normalize_unit(unit: str) -> str:
    """Normalize unit string for comparison."""
    return unit.strip().lower().replace("µ", "u")


def validate_lab_fields(test_name: str, value: float | None, unit: str) -> tuple[bool, str | None]:
    """Validate basic lab result fields."""
    if not test_name or not test_name.strip():
        return False, "Test name is required."
    if value is None:
        return False, "Value is required."
    if not isinstance(value, (int, float)):
        return False, "Value must be numeric."
    if not unit or not unit.strip():
        return False, "Unit is required."
    return True, None
