import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.csv_parser import parse_csv_content


class TestCSVParser:
    def test_valid_csv(self):
        content = "test_name,value,unit\nHemoglobin,14.5,g/dL\nWBC,7000,cells/uL\n"
        result = parse_csv_content(content)
        assert result["valid"] is True
        assert len(result["valid_rows"]) == 2

    def test_missing_columns(self):
        content = "name,val\nHemoglobin,14.5\n"
        result = parse_csv_content(content)
        assert result["valid"] is False

    def test_invalid_row(self):
        content = "test_name,value,unit\nHemoglobin,14.5,g/dL\n,abc,\n"
        result = parse_csv_content(content)
        assert len(result["invalid_rows"]) == 1

    def test_non_numeric_value(self):
        content = "test_name,value,unit\nHemoglobin,abc,g/dL\n"
        result = parse_csv_content(content)
        assert len(result["invalid_rows"]) == 1
        assert "Invalid numeric value" in result["invalid_rows"][0]["errors"][0]
