"""MCP Server implementation for AI Usage Monitor.

This module provides MCP tools for accessing AI tool usage data,
including daily stats, model usage, cost breakdowns, and tool comparisons.

Usage:
    # Start the MCP server
    python -m ai_usage_monitor.mcp

    # Or use the entry point
    ai-usage-monitor-mcp
"""

import asyncio
import logging
from datetime import datetime, timedelta
from datetime import timezone as tz
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Check if mcp is available
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP package not installed. Install with: pip install mcp")


def _get_usage_data(
    tool_name: Optional[str] = None,
    hours_back: int = 168,
) -> Dict[str, Any]:
    """Get usage data from adapters.

    Args:
        tool_name: Specific tool to get data for, or None for auto-detect
        hours_back: Number of hours to look back

    Returns:
        Dictionary with usage entries and metadata
    """
    from ai_usage_monitor.adapters.registry import AdapterRegistry
    from ai_usage_monitor.core.models import UsageEntry

    entries: List[UsageEntry] = []

    if tool_name and tool_name != "all":
        # Get data from specific tool
        adapter = AdapterRegistry.get_adapter(tool_name)
        if adapter and adapter.is_available():
            tool_entries, _ = adapter.load_usage_entries(hours_back=hours_back)
            entries.extend(tool_entries)
    else:
        # Get data from all available tools
        for tool_meta in AdapterRegistry.get_available_tools():
            adapter = AdapterRegistry.get_adapter(tool_meta.name)
            if adapter:
                try:
                    tool_entries, _ = adapter.load_usage_entries(hours_back=hours_back)
                    entries.extend(tool_entries)
                except Exception as e:
                    logger.warning(f"Failed to load data from {tool_meta.name}: {e}")

    return {
        "entries": entries,
        "count": len(entries),
        "hours_back": hours_back,
        "tool_name": tool_name or "all",
    }


def _aggregate_daily_stats(
    entries: List[Any], days_back: int = 7
) -> List[Dict[str, Any]]:
    """Aggregate entries into daily statistics.

    Args:
        entries: List of UsageEntry objects
        days_back: Number of days to include

    Returns:
        List of daily stat dictionaries
    """
    from collections import defaultdict

    cutoff = datetime.now(tz.utc) - timedelta(days=days_back)

    daily_stats: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "date": "",
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
            "models": set(),
            "tools": set(),
        }
    )

    for entry in entries:
        if entry.timestamp < cutoff:
            continue

        date_key = entry.timestamp.strftime("%Y-%m-%d")
        stats = daily_stats[date_key]
        stats["date"] = date_key
        stats["input_tokens"] += entry.input_tokens
        stats["output_tokens"] += entry.output_tokens
        stats["cache_tokens"] += entry.cache_creation_tokens + entry.cache_read_tokens
        stats["total_tokens"] += entry.total_tokens
        stats["cost_usd"] += entry.cost_usd
        stats["request_count"] += 1
        if entry.model:
            stats["models"].add(entry.model)
        stats["tools"].add(entry.tool_name)

    # Convert sets to lists for JSON serialization
    result = []
    for date_key in sorted(daily_stats.keys(), reverse=True):
        stats = daily_stats[date_key]
        stats["models"] = list(stats["models"])
        stats["tools"] = list(stats["tools"])
        result.append(stats)

    return result


def _aggregate_model_usage(entries: List[Any]) -> List[Dict[str, Any]]:
    """Aggregate entries by model.

    Args:
        entries: List of UsageEntry objects

    Returns:
        List of model usage dictionaries
    """
    from collections import defaultdict

    model_stats: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "model": "",
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
        }
    )

    for entry in entries:
        model = entry.model or "unknown"
        stats = model_stats[model]
        stats["model"] = model
        stats["input_tokens"] += entry.input_tokens
        stats["output_tokens"] += entry.output_tokens
        stats["total_tokens"] += entry.total_tokens
        stats["cost_usd"] += entry.cost_usd
        stats["request_count"] += 1

    return sorted(
        model_stats.values(), key=lambda x: x["total_tokens"], reverse=True
    )


def _aggregate_cost_breakdown(
    entries: List[Any], period: str = "weekly"
) -> Dict[str, Any]:
    """Aggregate cost breakdown.

    Args:
        entries: List of UsageEntry objects
        period: Period for breakdown (daily, weekly, monthly)

    Returns:
        Cost breakdown dictionary
    """
    total_cost = sum(e.cost_usd for e in entries)
    total_input = sum(e.input_tokens for e in entries)
    total_output = sum(e.output_tokens for e in entries)
    total_cache = sum(e.cache_creation_tokens + e.cache_read_tokens for e in entries)

    # Calculate average daily cost
    if entries:
        date_range = max(e.timestamp for e in entries) - min(e.timestamp for e in entries)
        days = max(date_range.days, 1)
        avg_daily = total_cost / days
    else:
        avg_daily = 0.0

    return {
        "period": period,
        "total_cost_usd": round(total_cost, 4),
        "average_daily_cost_usd": round(avg_daily, 4),
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_cache_tokens": total_cache,
        "request_count": len(entries),
    }


if MCP_AVAILABLE:
    # Create MCP server instance
    server = Server("ai-usage-monitor")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available MCP tools."""
        return [
            Tool(
                name="get_daily_stats",
                description="Get daily usage statistics for AI coding tools",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tool": {
                            "type": "string",
                            "description": "Tool to get stats for (claude-code, codex-cli, etc.) or 'all'",
                        },
                        "days_back": {
                            "type": "integer",
                            "description": "Number of days to look back (default: 7)",
                            "default": 7,
                        },
                    },
                },
            ),
            Tool(
                name="get_model_usage",
                description="Get usage statistics broken down by AI model",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tool": {
                            "type": "string",
                            "description": "Tool to get stats for or 'all'",
                        },
                        "hours_back": {
                            "type": "integer",
                            "description": "Number of hours to look back (default: 168 = 1 week)",
                            "default": 168,
                        },
                    },
                },
            ),
            Tool(
                name="get_cost_breakdown",
                description="Get cost breakdown for AI tool usage",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tool": {
                            "type": "string",
                            "description": "Tool to get costs for or 'all'",
                        },
                        "period": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly"],
                            "description": "Time period for breakdown",
                            "default": "weekly",
                        },
                    },
                },
            ),
            Tool(
                name="compare_tools",
                description="Compare usage across multiple AI coding tools",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tools": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of tools to compare",
                        },
                        "hours_back": {
                            "type": "integer",
                            "description": "Number of hours to look back",
                            "default": 168,
                        },
                    },
                    "required": ["tools"],
                },
            ),
            Tool(
                name="list_available_tools",
                description="List all AI coding tools that have data available",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls."""
        import json

        try:
            if name == "get_daily_stats":
                tool = arguments.get("tool")
                days_back = arguments.get("days_back", 7)
                hours_back = days_back * 24

                data = _get_usage_data(tool, hours_back)
                daily_stats = _aggregate_daily_stats(data["entries"], days_back)

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "tool": data["tool_name"],
                                "days_back": days_back,
                                "daily_stats": daily_stats,
                            },
                            indent=2,
                        ),
                    )
                ]

            elif name == "get_model_usage":
                tool = arguments.get("tool")
                hours_back = arguments.get("hours_back", 168)

                data = _get_usage_data(tool, hours_back)
                model_usage = _aggregate_model_usage(data["entries"])

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "tool": data["tool_name"],
                                "hours_back": hours_back,
                                "model_usage": model_usage,
                            },
                            indent=2,
                        ),
                    )
                ]

            elif name == "get_cost_breakdown":
                tool = arguments.get("tool")
                period = arguments.get("period", "weekly")

                # Map period to hours
                period_hours = {"daily": 24, "weekly": 168, "monthly": 720}
                hours_back = period_hours.get(period, 168)

                data = _get_usage_data(tool, hours_back)
                breakdown = _aggregate_cost_breakdown(data["entries"], period)

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "tool": data["tool_name"],
                                "breakdown": breakdown,
                            },
                            indent=2,
                        ),
                    )
                ]

            elif name == "compare_tools":
                tools = arguments.get("tools", [])
                hours_back = arguments.get("hours_back", 168)

                comparison = []
                for tool_name in tools:
                    data = _get_usage_data(tool_name, hours_back)
                    breakdown = _aggregate_cost_breakdown(data["entries"], "weekly")
                    comparison.append(
                        {
                            "tool": tool_name,
                            "total_tokens": breakdown["total_input_tokens"]
                            + breakdown["total_output_tokens"],
                            "total_cost_usd": breakdown["total_cost_usd"],
                            "request_count": breakdown["request_count"],
                        }
                    )

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "hours_back": hours_back,
                                "comparison": comparison,
                            },
                            indent=2,
                        ),
                    )
                ]

            elif name == "list_available_tools":
                from ai_usage_monitor.adapters.registry import AdapterRegistry

                available = AdapterRegistry.get_available_tools()
                tools_info = [
                    {
                        "name": t.name,
                        "display_name": t.display_name,
                        "data_format": t.data_format,
                        "features": t.supported_features,
                    }
                    for t in available
                ]

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "available_tools": tools_info,
                                "count": len(tools_info),
                            },
                            indent=2,
                        ),
                    )
                ]

            else:
                return [
                    TextContent(type="text", text=f"Unknown tool: {name}")
                ]

        except Exception as e:
            logger.exception(f"Error in tool {name}")
            return [
                TextContent(type="text", text=f"Error: {str(e)}")
            ]


async def serve() -> None:
    """Start the MCP server."""
    if not MCP_AVAILABLE:
        print("Error: MCP package is not installed.")
        print("Install it with: pip install mcp")
        return

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    """Main entry point for MCP server."""
    asyncio.run(serve())


if __name__ == "__main__":
    main()
