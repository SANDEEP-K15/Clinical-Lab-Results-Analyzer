"""MCP client for laboratory analysis tools.

Provides an abstraction layer so the agent communicates through MCP tools
rather than calling services directly.
"""

import json
import logging

from mcp.tools import (
    classify_lab_result,
    reference_range_lookup,
    validate_lab_result,
)

logger = logging.getLogger(__name__)


class LabMCPClient:
    """Client that invokes MCP laboratory tools."""

    async def reference_range_lookup(self, test_name: str, unit: str, value: float | None = None) -> dict:
        logger.info("MCP client: reference_range_lookup(%s, %s)", test_name, unit)
        return reference_range_lookup(test_name, unit, value=value)

    async def validate_lab_result(self, test_name: str, value: float, unit: str) -> dict:
        logger.info("MCP client: validate_lab_result(%s, %s, %s)", test_name, value, unit)
        return validate_lab_result(test_name, value, unit)

    async def classify_lab_result(
        self,
        test_name: str,
        value: float,
        unit: str,
        reference_low: float,
        reference_high: float,
        critical_low: float | None = None,
        critical_high: float | None = None,
    ) -> dict:
        logger.info("MCP client: classify_lab_result(%s)", test_name)
        return classify_lab_result(
            test_name, value, unit,
            reference_low, reference_high,
            critical_low, critical_high,
        )


mcp_client = LabMCPClient()
