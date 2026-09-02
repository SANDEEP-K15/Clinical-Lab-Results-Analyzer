import logging

logger = logging.getLogger(__name__)

CRITICAL_DEVIATION_FACTOR = 0.75
CRITICAL_HIGH_DEVIATION_FACTOR = 1.25


def classify_lab_value(
    value: float,
    low: float,
    high: float,
    critical_low: float | None = None,
    critical_high: float | None = None,
) -> tuple[str, str]:
    """
    Deterministic classification of a lab value against reference ranges.
    Returns (classification, reason).
    """
    if critical_low is not None and value <= critical_low:
      reason = "The value is at or below the configured critical low threshold."
      logger.info("Classification: CRITICAL (low) - value=%s, critical_low=%s", value, critical_low)
      return "CRITICAL", reason

    if critical_high is not None and value >= critical_high:
      reason = "The value is at or above the configured critical high threshold."
      logger.info("Classification: CRITICAL (high) - value=%s, critical_high=%s", value, critical_high)
      return "CRITICAL", reason

    if low <= value <= high:
      reason = "The value falls within the configured reference range."
      logger.info("Classification: NORMAL - value=%s, range=[%s, %s]", value, low, high)
      return "NORMAL", reason

    if value < low:
      if critical_low is None and value < low * CRITICAL_DEVIATION_FACTOR:
        reason = (
          "The value is substantially below the configured reference range "
          "and exceeds the configured deviation threshold."
        )
        return "CRITICAL", reason
      reason = "The value is below the configured reference range but does not cross the critical threshold."
      logger.info("Classification: WARNING (low) - value=%s, low=%s", value, low)
      return "WARNING", reason

    if value > high:
      if critical_high is None and value > high * CRITICAL_HIGH_DEVIATION_FACTOR:
        reason = (
          "The value is substantially above the configured reference range "
          "and exceeds the configured deviation threshold."
        )
        return "CRITICAL", reason
      reason = "The value is above the configured reference range but does not cross the critical threshold."
      logger.info("Classification: WARNING (high) - value=%s, high=%s", value, high)
      return "WARNING", reason

    return "NORMAL", "The value falls within the configured reference range."
