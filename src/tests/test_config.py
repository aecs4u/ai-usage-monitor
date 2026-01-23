"""Tests for TOML configuration module."""

import tempfile
from pathlib import Path

import pytest

from ai_usage_monitor.core.config import (
    AppConfig,
    CloudConfig,
    GeneralConfig,
    ToolConfig,
    create_default_config,
    load_config,
    save_config,
)


class TestAppConfig:
    """Test suite for AppConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = AppConfig()

        assert config.general.default_tool == "auto"
        assert config.general.theme == "auto"
        assert config.cloud.url is None
        assert config.cloud.auto_upload is False
        assert len(config.tools) == 0

    def test_get_enabled_tools_empty(self) -> None:
        """Test get_enabled_tools with no tools configured."""
        config = AppConfig()

        assert config.get_enabled_tools() == []

    def test_get_enabled_tools(self) -> None:
        """Test get_enabled_tools with configured tools."""
        config = AppConfig()
        config.tools["claude-code"] = ToolConfig(name="claude-code", enabled=True)
        config.tools["codex-cli"] = ToolConfig(name="codex-cli", enabled=False)
        config.tools["gemini-cli"] = ToolConfig(name="gemini-cli", enabled=True)

        enabled = config.get_enabled_tools()

        assert "claude-code" in enabled
        assert "gemini-cli" in enabled
        assert "codex-cli" not in enabled

    def test_get_tool_data_path(self) -> None:
        """Test get_tool_data_path method."""
        config = AppConfig()
        config.tools["claude-code"] = ToolConfig(
            name="claude-code",
            enabled=True,
            data_path="~/.custom/claude",
        )

        assert config.get_tool_data_path("claude-code") == "~/.custom/claude"
        assert config.get_tool_data_path("unknown-tool") is None


class TestLoadConfig:
    """Test suite for load_config function."""

    def test_load_nonexistent_config(self) -> None:
        """Test loading a non-existent config file returns defaults."""
        config = load_config(Path("/tmp/nonexistent-config-xyz.toml"))

        assert config.general.default_tool == "auto"
        assert len(config.tools) == 0

    def test_load_valid_config(self) -> None:
        """Test loading a valid TOML config file."""
        toml_content = """
[general]
default_tool = "claude-code"
theme = "dark"
timezone = "America/New_York"

[cloud]
url = "https://api.example.com"
auto_upload = true

[tools.claude-code]
enabled = true
data_path = "~/.custom/claude"

[tools.codex-cli]
enabled = false
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as f:
            f.write(toml_content)
            tmp_path = Path(f.name)

        try:
            config = load_config(tmp_path)

            assert config.general.default_tool == "claude-code"
            assert config.general.theme == "dark"
            assert config.general.timezone == "America/New_York"
            assert config.cloud.url == "https://api.example.com"
            assert config.cloud.auto_upload is True
            assert "claude-code" in config.tools
            assert config.tools["claude-code"].enabled is True
            assert config.tools["claude-code"].data_path == "~/.custom/claude"
            assert "codex-cli" in config.tools
            assert config.tools["codex-cli"].enabled is False
        finally:
            tmp_path.unlink()


class TestSaveConfig:
    """Test suite for save_config function."""

    def test_save_and_reload_config(self) -> None:
        """Test saving and reloading a config preserves values."""
        config = AppConfig()
        config.general = GeneralConfig(
            default_tool="gemini-cli",
            theme="light",
            timezone="Europe/London",
        )
        config.cloud = CloudConfig(
            url="https://test.example.com",
            api_key="test-key",
            auto_upload=True,
        )
        config.tools["claude-code"] = ToolConfig(
            name="claude-code",
            enabled=True,
            data_path="~/.test/claude",
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as f:
            tmp_path = Path(f.name)

        try:
            # Save
            result = save_config(config, tmp_path)
            assert result is True

            # Reload
            loaded = load_config(tmp_path)

            assert loaded.general.default_tool == "gemini-cli"
            assert loaded.general.theme == "light"
            assert loaded.general.timezone == "Europe/London"
            assert loaded.cloud.url == "https://test.example.com"
            assert loaded.cloud.api_key == "test-key"
            assert loaded.cloud.auto_upload is True
            assert loaded.tools["claude-code"].enabled is True
            assert loaded.tools["claude-code"].data_path == "~/.test/claude"
        finally:
            tmp_path.unlink()


class TestCreateDefaultConfig:
    """Test suite for create_default_config function."""

    def test_create_default_config(self) -> None:
        """Test creating a default configuration file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as f:
            tmp_path = Path(f.name)

        try:
            config = create_default_config(tmp_path)

            # Should have claude-code enabled by default
            assert "claude-code" in config.tools
            assert config.tools["claude-code"].enabled is True

            # Other tools should be disabled by default
            assert "codex-cli" in config.tools
            assert config.tools["codex-cli"].enabled is False

            # File should exist
            assert tmp_path.exists()

            # Should be reloadable
            loaded = load_config(tmp_path)
            assert loaded.tools["claude-code"].enabled is True
        finally:
            tmp_path.unlink()
