import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.classification_service import classify_lab_value


class TestClassification:
    def test_normal_low_boundary(self):
        result, _ = classify_lab_value(12.0, 12.0, 17.5, 7.0, 20.0)
        assert result == "NORMAL"

    def test_normal_high_boundary(self):
        result, _ = classify_lab_value(17.5, 12.0, 17.5, 7.0, 20.0)
        assert result == "NORMAL"

    def test_normal_mid_range(self):
        result, _ = classify_lab_value(14.5, 12.0, 17.5, 7.0, 20.0)
        assert result == "NORMAL"

    def test_warning_low(self):
        result, _ = classify_lab_value(10.5, 12.0, 17.5, 7.0, 20.0)
        assert result == "WARNING"

    def test_warning_high(self):
        result, _ = classify_lab_value(18.0, 12.0, 17.5, 7.0, 20.0)
        assert result == "WARNING"

    def test_critical_low(self):
        result, _ = classify_lab_value(6.5, 12.0, 17.5, 7.0, 20.0)
        assert result == "CRITICAL"

    def test_critical_high(self):
        result, _ = classify_lab_value(20.0, 12.0, 17.5, 7.0, 20.0)
        assert result == "CRITICAL"

    def test_critical_at_threshold(self):
        result, _ = classify_lab_value(7.0, 12.0, 17.5, 7.0, 20.0)
        assert result == "CRITICAL"

    def test_deviation_strategy_low(self):
        result, _ = classify_lab_value(8.0, 12.0, 17.5, None, None)
        assert result == "CRITICAL"

    def test_deviation_strategy_high(self):
        result, _ = classify_lab_value(22.0, 12.0, 17.5, None, None)
        assert result == "CRITICAL"
