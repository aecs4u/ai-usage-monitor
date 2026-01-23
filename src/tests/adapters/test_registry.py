"""Tests for AdapterRegistry."""

import pytest

from ai_usage_monitor.adapters.base import ToolAdapter, ToolMetadata
from ai_usage_monitor.adapters.registry import AdapterRegistry


class TestAdapterRegistry:
    """Test suite for AdapterRegistry."""

    def test_all_expected_adapters_registered(self) -> None:
        """Test that all expected adapters are registered."""
        expected_adapters = [
            "claude-code",
            "codex-cli",
            "gemini-cli",
            "cline",
            "roo-code",
            "kilo-code",
            "github-copilot",
            "opencode",
            "pi-agent",
        ]

        registered = AdapterRegistry.get_tool_names()

        for adapter_name in expected_adapters:
            assert adapter_name in registered, f"Missing adapter: {adapter_name}"

    def test_get_adapter_returns_instance(self) -> None:
        """Test that get_adapter returns a valid adapter instance."""
        adapter = AdapterRegistry.get_adapter("claude-code")

        assert adapter is not None
        assert isinstance(adapter, ToolAdapter)
        assert adapter.metadata.name == "claude-code"

    def test_get_adapter_returns_same_instance(self) -> None:
        """Test that get_adapter returns the same instance on repeated calls."""
        adapter1 = AdapterRegistry.get_adapter("claude-code")
        adapter2 = AdapterRegistry.get_adapter("claude-code")

        assert adapter1 is adapter2

    def test_get_adapter_unknown_tool_returns_none(self) -> None:
        """Test that get_adapter returns None for unknown tools."""
        adapter = AdapterRegistry.get_adapter("unknown-tool-xyz")

        assert adapter is None

    def test_is_registered(self) -> None:
        """Test is_registered method."""
        assert AdapterRegistry.is_registered("claude-code") is True
        assert AdapterRegistry.is_registered("unknown-tool") is False

    def test_get_all_tools_returns_metadata(self) -> None:
        """Test get_all_tools returns ToolMetadata objects."""
        tools = AdapterRegistry.get_all_tools()

        assert len(tools) >= 9
        for tool in tools:
            assert isinstance(tool, ToolMetadata)
            assert tool.name
            assert tool.display_name
            assert tool.data_format

    def test_get_available_tools_subset_of_all(self) -> None:
        """Test that available tools is a subset of all tools."""
        all_tools = set(t.name for t in AdapterRegistry.get_all_tools())
        available_tools = set(t.name for t in AdapterRegistry.get_available_tools())

        assert available_tools.issubset(all_tools)


class TestClaudeCodeAdapter:
    """Test suite for ClaudeCodeAdapter."""

    def test_metadata(self) -> None:
        """Test adapter metadata."""
        adapter = AdapterRegistry.get_adapter("claude-code")

        assert adapter is not None
        assert adapter.metadata.name == "claude-code"
        assert adapter.metadata.display_name == "Claude Code"
        assert adapter.metadata.data_format == "jsonl"
        assert "tokens" in adapter.metadata.supported_features
        assert "cost" in adapter.metadata.supported_features
        assert adapter.metadata.pricing_available is True

    def test_discover_data_paths(self) -> None:
        """Test discover_data_paths method."""
        adapter = AdapterRegistry.get_adapter("claude-code")

        assert adapter is not None
        paths = adapter.discover_data_paths()

        # Should return a list (possibly empty if no data)
        assert isinstance(paths, list)

    def test_load_usage_entries_returns_tuple(self) -> None:
        """Test load_usage_entries returns correct tuple structure."""
        adapter = AdapterRegistry.get_adapter("claude-code")

        assert adapter is not None
        result = adapter.load_usage_entries(hours_back=1)

        assert isinstance(result, tuple)
        assert len(result) == 2
        entries, raw_data = result
        assert isinstance(entries, list)
        # raw_data should be None when include_raw=False
        assert raw_data is None

    def test_load_usage_entries_with_raw(self) -> None:
        """Test load_usage_entries with include_raw=True."""
        adapter = AdapterRegistry.get_adapter("claude-code")

        assert adapter is not None
        entries, raw_data = adapter.load_usage_entries(hours_back=1, include_raw=True)

        assert isinstance(entries, list)
        # raw_data should be a list when include_raw=True
        assert raw_data is None or isinstance(raw_data, list)


class TestAdapterInterface:
    """Test that all adapters implement the required interface."""

    @pytest.mark.parametrize(
        "adapter_name",
        [
            "claude-code",
            "codex-cli",
            "gemini-cli",
            "cline",
            "roo-code",
            "kilo-code",
            "github-copilot",
            "opencode",
            "pi-agent",
        ],
    )
    def test_adapter_has_required_methods(self, adapter_name: str) -> None:
        """Test that each adapter has all required methods."""
        adapter = AdapterRegistry.get_adapter(adapter_name)

        assert adapter is not None
        assert hasattr(adapter, "metadata")
        assert hasattr(adapter, "discover_data_paths")
        assert hasattr(adapter, "load_usage_entries")
        assert hasattr(adapter, "calculate_cost")
        assert hasattr(adapter, "is_available")

    @pytest.mark.parametrize(
        "adapter_name",
        [
            "claude-code",
            "codex-cli",
            "gemini-cli",
            "cline",
            "roo-code",
            "kilo-code",
            "github-copilot",
            "opencode",
            "pi-agent",
        ],
    )
    def test_adapter_metadata_valid(self, adapter_name: str) -> None:
        """Test that each adapter has valid metadata."""
        adapter = AdapterRegistry.get_adapter(adapter_name)

        assert adapter is not None
        meta = adapter.metadata

        assert meta.name == adapter_name
        assert len(meta.display_name) > 0
        assert meta.data_format in ["jsonl", "json", "sqlite", "txt"]
        assert len(meta.default_paths) > 0
        assert isinstance(meta.supported_features, list)
        assert isinstance(meta.pricing_available, bool)
