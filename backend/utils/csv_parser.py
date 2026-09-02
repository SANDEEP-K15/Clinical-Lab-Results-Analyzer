"""Parse and validate CSV lab result data."""

import csv
import io
from typing import Any


REQUIRED_COLUMNS = {"test_name", "value", "unit"}


def parse_csv_content(content: str) -> dict[str, Any]:
    """Parse CSV string into valid and invalid rows."""
    reader = csv.DictReader(io.StringIO(content))
    fieldnames = {f.strip().lower() for f in (reader.fieldnames or [])}

    if not REQUIRED_COLUMNS.issubset(fieldnames):
        missing = REQUIRED_COLUMNS - fieldnames
        return {
            "valid": False,
            "error": f"Missing required columns: {', '.join(missing)}",
            "valid_rows": [],
            "invalid_rows": [],
        }

    valid_rows = []
    invalid_rows = []

    for i, row in enumerate(reader, start=2):
        test_name = (row.get("test_name") or row.get("Test Name") or "").strip()
        value_str = (row.get("value") or row.get("Value") or "").strip()
        unit = (row.get("unit") or row.get("Unit") or "").strip()

        errors = []
        if not test_name:
            errors.append("Missing test name")
        if not value_str:
            errors.append("Missing value")
        else:
            try:
                float(value_str)
            except ValueError:
                errors.append("Invalid numeric value")
        if not unit:
            errors.append("Missing unit")

        if errors:
            invalid_rows.append({"row": i, "data": row, "errors": errors})
        else:
            valid_rows.append({
                "test_name": test_name,
                "value": float(value_str),
                "unit": unit,
            })

    return {
        "valid": True,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
    }
