"""Tests for TOML configuration wiring in discovery and tool selection."""

import tempfile
from pathlib import Path
from typing import List
from unittest.mock import Mock, patch

import pytest

from ai_usage_monitor.cli.main import discover_data_paths_for_tool
from ai_usage_monitor.core.config import AppConfig, ToolConfig


class TestTOMLConfigWiring:
    """Test that TOML tool configuration is properly wired into discovery."""

    def test_discover_uses_configured_data_path(self) -> None:
        """Test that configured data_path is used for discovery."""
        # Create config with custom data path
        config = AppConfig(
            tools={
                "claude-code": ToolConfig(
                    name="claude-code",
                    enabled=True,
                    data_path="~/custom/claude/data",
                )
            }
        )

        # Mock the adapter to verify custom path is passed
        with patch("ai_usage_monitor.cli.main.AdapterRegistry.get_adapter") as mock_get:
            mock_adapter = Mock()
            mock_adapter.discover_data_paths.return_value = [Path("/fake/path")]
            mock_get.return_value = mock_adapter

            # Call discovery with config
            paths = discover_data_paths_for_tool("claude-code", config=config)

            # Verify custom path was passed to adapter
            mock_adapter.discover_data_paths.assert_called_once_with(
                ["~/custom/claude/data"]
            )
            assert len(paths) == 1

    def test_discover_uses_defaults_when_no_config(self) -> None:
        """Test that default discovery is used when no config provided."""
        # Create config without data_path
        config = AppConfig(
            tools={"claude-code": ToolConfig(name="claude-code", enabled=True)}
        )

        with patch("ai_usage_monitor.cli.main.AdapterRegistry.get_adapter") as mock_get:
            mock_adapter = Mock()
            mock_adapter.discover_data_paths.return_value = [Path("/default/path")]
            mock_get.return_value = mock_adapter

            # Call discovery with config (but no data_path set)
            paths = discover_data_paths_for_tool("claude-code", config=config)

            # Verify None was passed (use defaults)
            mock_adapter.discover_data_paths.assert_called_once_with(None)
            assert len(paths) == 1

    def test_discover_uses_defaults_when_no_config_object(self) -> None:
        """Test that default discovery is used when config=None."""
        with patch("ai_usage_monitor.cli.main.AdapterRegistry.get_adapter") as mock_get:
            mock_adapter = Mock()
            mock_adapter.discover_data_paths.return_value = [Path("/default/path")]
            mock_get.return_value = mock_adapter

            # Call discovery without config
            paths = discover_data_paths_for_tool("claude-code", config=None)

            # Verify None was passed (use defaults)
            mock_adapter.discover_data_paths.assert_called_once_with(None)
            assert len(paths) == 1

    def test_custom_paths_override_config(self) -> None:
        """Test that custom_paths parameter takes priority over config."""
        # Create config with data_path
        config = AppConfig(
            tools={
                "claude-code": ToolConfig(
                    name="claude-code",
                    enabled=True,
                    data_path="~/config/path",
                )
            }
        )

        custom_paths = ["~/custom/override"]

        with patch("ai_usage_monitor.cli.main.AdapterRegistry.get_adapter") as mock_get:
            mock_adapter = Mock()
            mock_adapter.discover_data_paths.return_value = [Path("/custom/path")]
            mock_get.return_value = mock_adapter

            # Call with both custom_paths and config
            paths = discover_data_paths_for_tool(
                "claude-code", custom_paths=custom_paths, config=config
            )

            # Verify custom_paths was used, not config
            mock_adapter.discover_data_paths.assert_called_once_with(custom_paths)
            assert len(paths) == 1

    def test_get_tool_data_path_returns_configured_path(self) -> None:
        """Test AppConfig.get_tool_data_path() returns configured path."""
        config = AppConfig(
            tools={
                "claude-code": ToolConfig(
                    name="claude-code",
                    enabled=True,
                    data_path="~/my/custom/path",
                )
            }
        )

        path = config.get_tool_data_path("claude-code")
        assert path == "~/my/custom/path"

    def test_get_tool_data_path_returns_none_when_not_configured(self) -> None:
        """Test AppConfig.get_tool_data_path() returns None for unconfigured tool."""
        config = AppConfig(tools={"claude-code": ToolConfig(name="claude-code")})

        path = config.get_tool_data_path("claude-code")
        assert path is None

    def test_get_tool_data_path_returns_none_for_unknown_tool(self) -> None:
        """Test AppConfig.get_tool_data_path() returns None for unknown tool."""
        config = AppConfig(tools={})

        path = config.get_tool_data_path("unknown-tool")
        assert path is None

    def test_get_enabled_tools_filters_correctly(self) -> None:
        """Test AppConfig.get_enabled_tools() returns only enabled tools."""
        config = AppConfig(
            tools={
                "claude-code": ToolConfig(name="claude-code", enabled=True),
                "codex-cli": ToolConfig(name="codex-cli", enabled=False),
                "cline": ToolConfig(name="cline", enabled=True),
            }
        )

        enabled = config.get_enabled_tools()
        assert set(enabled) == {"claude-code", "cline"}
        assert "codex-cli" not in enabled

    def test_discover_no_adapter_returns_empty_list(self) -> None:
        """Test discovery returns empty list when no adapter found."""
        with patch("ai_usage_monitor.cli.main.AdapterRegistry.get_adapter") as mock_get:
            mock_get.return_value = None

            paths = discover_data_paths_for_tool("unknown-tool")

            assert paths == []

    def test_discover_logs_when_using_configured_path(self) -> None:
        """Test that using configured path is logged."""
        config = AppConfig(
            tools={
                "claude-code": ToolConfig(
                    name="claude-code",
                    enabled=True,
                    data_path="~/custom/path",
                )
            }
        )

        with patch("ai_usage_monitor.cli.main.AdapterRegistry.get_adapter") as mock_get:
            mock_adapter = Mock()
            mock_adapter.discover_data_paths.return_value = []
            mock_get.return_value = mock_adapter

            # Patch logging.getLogger to verify log was called
            with patch("ai_usage_monitor.cli.main.logging.getLogger") as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger

                discover_data_paths_for_tool("claude-code", config=config)

                # Verify info log was called
                mock_logger.info.assert_called_once()
                log_message = mock_logger.info.call_args[0][0]
                assert "configured data path" in log_message.lower()
                assert "claude-code" in log_message
                assert "~/custom/path" in log_message
