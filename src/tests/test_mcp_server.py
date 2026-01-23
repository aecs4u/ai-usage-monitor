"""Tests for MCP server module."""

import pytest

from ai_usage_monitor.mcp.server import (
    MCP_AVAILABLE,
    _aggregate_cost_breakdown,
    _aggregate_daily_stats,
    _aggregate_model_usage,
    _get_usage_data,
)


class TestMCPHelpers:
    """Test MCP server helper functions."""

    def test_mcp_available(self) -> None:
        """Test MCP availability check."""
        # MCP should be available if installed
        assert isinstance(MCP_AVAILABLE, bool)

    def test_get_usage_data_returns_dict(self) -> None:
        """Test _get_usage_data returns correct structure."""
        data = _get_usage_data(tool_name="claude-code", hours_back=1)

        assert isinstance(data, dict)
        assert "entries" in data
        assert "count" in data
        assert "hours_back" in data
        assert "tool_name" in data
        assert data["hours_back"] == 1
        assert data["tool_name"] == "claude-code"

    def test_get_usage_data_all_tools(self) -> None:
        """Test _get_usage_data with all tools."""
        data = _get_usage_data(tool_name=None, hours_back=1)

        assert data["tool_name"] == "all"

    def test_aggregate_daily_stats_empty(self) -> None:
        """Test _aggregate_daily_stats with empty entries."""
        result = _aggregate_daily_stats([], days_back=7)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_aggregate_daily_stats_structure(self) -> None:
        """Test _aggregate_daily_stats returns correct structure."""
        # Get some real data
        data = _get_usage_data(tool_name="claude-code", hours_back=24)
        result = _aggregate_daily_stats(data["entries"], days_back=1)

        assert isinstance(result, list)
        if result:  # If there's data
            day = result[0]
            assert "date" in day
            assert "input_tokens" in day
            assert "output_tokens" in day
            assert "total_tokens" in day
            assert "cost_usd" in day
            assert "request_count" in day
            assert "models" in day
            assert "tools" in day

    def test_aggregate_model_usage_empty(self) -> None:
        """Test _aggregate_model_usage with empty entries."""
        result = _aggregate_model_usage([])

        assert isinstance(result, list)
        assert len(result) == 0

    def test_aggregate_model_usage_structure(self) -> None:
        """Test _aggregate_model_usage returns correct structure."""
        data = _get_usage_data(tool_name="claude-code", hours_back=24)
        result = _aggregate_model_usage(data["entries"])

        assert isinstance(result, list)
        if result:  # If there's data
            model = result[0]
            assert "model" in model
            assert "input_tokens" in model
            assert "output_tokens" in model
            assert "total_tokens" in model
            assert "cost_usd" in model
            assert "request_count" in model

    def test_aggregate_cost_breakdown_empty(self) -> None:
        """Test _aggregate_cost_breakdown with empty entries."""
        result = _aggregate_cost_breakdown([], period="weekly")

        assert isinstance(result, dict)
        assert result["period"] == "weekly"
        assert result["total_cost_usd"] == 0
        assert result["request_count"] == 0

    def test_aggregate_cost_breakdown_structure(self) -> None:
        """Test _aggregate_cost_breakdown returns correct structure."""
        data = _get_usage_data(tool_name="claude-code", hours_back=24)
        result = _aggregate_cost_breakdown(data["entries"], period="daily")

        assert isinstance(result, dict)
        assert "period" in result
        assert "total_cost_usd" in result
        assert "average_daily_cost_usd" in result
        assert "total_input_tokens" in result
        assert "total_output_tokens" in result
        assert "total_cache_tokens" in result
        assert "request_count" in result
        assert result["period"] == "daily"


@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP package not installed")
class TestMCPServer:
    """Test MCP server when available."""

    def test_server_instance_exists(self) -> None:
        """Test that server instance is created."""
        from ai_usage_monitor.mcp.server import server

        assert server is not None
        assert server.name == "ai-usage-monitor"

    @pytest.mark.asyncio
    async def test_list_tools(self) -> None:
        """Test list_tools returns expected tools."""
        from ai_usage_monitor.mcp.server import list_tools

        tools = await list_tools()

        assert isinstance(tools, list)
        assert len(tools) == 5

        tool_names = [t.name for t in tools]
        assert "get_daily_stats" in tool_names
        assert "get_model_usage" in tool_names
        assert "get_cost_breakdown" in tool_names
        assert "compare_tools" in tool_names
        assert "list_available_tools" in tool_names

    @pytest.mark.asyncio
    async def test_call_tool_list_available_tools(self) -> None:
        """Test calling list_available_tools tool."""
        from ai_usage_monitor.mcp.server import call_tool

        result = await call_tool("list_available_tools", {})

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"

        import json
        data = json.loads(result[0].text)
        assert "available_tools" in data
        assert "count" in data

    @pytest.mark.asyncio
    async def test_call_tool_get_daily_stats(self) -> None:
        """Test calling get_daily_stats tool."""
        from ai_usage_monitor.mcp.server import call_tool

        result = await call_tool("get_daily_stats", {"days_back": 1})

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"

        import json
        data = json.loads(result[0].text)
        assert "daily_stats" in data
        assert "days_back" in data

    @pytest.mark.asyncio
    async def test_call_tool_get_cost_breakdown(self) -> None:
        """Test calling get_cost_breakdown tool."""
        from ai_usage_monitor.mcp.server import call_tool

        result = await call_tool("get_cost_breakdown", {"period": "weekly"})

        assert isinstance(result, list)
        assert len(result) == 1

        import json
        data = json.loads(result[0].text)
        assert "breakdown" in data

    @pytest.mark.asyncio
    async def test_call_tool_unknown(self) -> None:
        """Test calling unknown tool."""
        from ai_usage_monitor.mcp.server import call_tool

        result = await call_tool("unknown_tool", {})

        assert isinstance(result, list)
        assert "Unknown tool" in result[0].text
