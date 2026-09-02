"""MCP server exposing laboratory analysis tools."""

import asyncio
import json
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp.tools import (
    classify_lab_result,
    reference_range_lookup,
    validate_lab_result,
)

logger = logging.getLogger(__name__)

server = Server("clinical-lab-analyzer")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="reference_range_lookup",
            description="Look up reference range for a laboratory test",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_name": {"type": "string", "description": "Name of the lab test"},
                    "unit": {"type": "string", "description": "Unit of measurement"},
                },
                "required": ["test_name", "unit"],
            },
        ),
        Tool(
            name="validate_lab_result",
            description="Validate a laboratory test result",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_name": {"type": "string"},
                    "value": {"type": "number"},
                    "unit": {"type": "string"},
                },
                "required": ["test_name", "value", "unit"],
            },
        ),
        Tool(
            name="classify_lab_result",
            description="Classify a lab result as NORMAL, WARNING, or CRITICAL",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_name": {"type": "string"},
                    "value": {"type": "number"},
                    "unit": {"type": "string"},
                    "reference_low": {"type": "number"},
                    "reference_high": {"type": "number"},
                    "critical_low": {"type": "number"},
                    "critical_high": {"type": "number"},
                },
                "required": ["test_name", "value", "unit", "reference_low", "reference_high"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info("MCP tool called: %s", name)

    if name == "reference_range_lookup":
        result = reference_range_lookup(arguments["test_name"], arguments["unit"])
    elif name == "validate_lab_result":
        result = validate_lab_result(
            arguments["test_name"], arguments["value"], arguments["unit"]
        )
    elif name == "classify_lab_result":
        result = classify_lab_result(
            arguments["test_name"],
            arguments["value"],
            arguments["unit"],
            arguments["reference_low"],
            arguments["reference_high"],
            arguments.get("critical_low"),
            arguments.get("critical_high"),
        )
    else:
        result = {"error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
