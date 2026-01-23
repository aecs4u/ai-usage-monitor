"""Tests for configuration path consolidation and migration."""

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ai_usage_monitor.cli.migrate import (
    auto_migrate_if_needed,
    check_migration_needed,
    migrate_claude_config,
    migrate_config,
)
from ai_usage_monitor.core.settings import LastUsedParams
from ai_usage_monitor.utils.paths import (
    CONFIG_DIR,
    get_config_dir,
    get_config_file,
    get_last_used_file,
    get_notifications_file,
)


class TestConfigPaths:
    """Test that configuration paths are properly consolidated."""

    def test_config_dir_location(self) -> None:
        """Test that config directory is at ~/.ai-usage-monitor."""
        config_dir = get_config_dir()
        expected = Path.home() / ".ai-usage-monitor"

        assert config_dir == expected
        assert config_dir.exists()  # Should be created
        assert config_dir.is_dir()

    def test_config_file_location(self) -> None:
        """Test that config file is at ~/.ai-usage-monitor.toml."""
        config_file = get_config_file()
        expected = Path.home() / ".ai-usage-monitor.toml"

        assert config_file == expected

    def test_last_used_file_location(self) -> None:
        """Test that last_used.json is in config directory."""
        last_used_file = get_last_used_file()
        expected = get_config_dir() / "last_used.json"

        assert last_used_file == expected

    def test_notifications_file_location(self) -> None:
        """Test that notifications.json is in config directory."""
        notifications_file = get_notifications_file()
        expected = get_config_dir() / "notifications.json"

        assert notifications_file == expected

    def test_config_dir_constant(self) -> None:
        """Test CONFIG_DIR constant matches expected location."""
        assert CONFIG_DIR == Path.home() / ".ai-usage-monitor"

    def test_last_used_params_uses_config_dir(self) -> None:
        """Test that LastUsedParams defaults to centralized config dir."""
        params = LastUsedParams()

        assert params.config_dir == get_config_dir()
        assert params.params_file == get_last_used_file()

    def test_last_used_params_custom_dir(self) -> None:
        """Test that LastUsedParams can use custom directory."""
        custom_dir = Path(tempfile.mkdtemp())
        try:
            params = LastUsedParams(config_dir=custom_dir)

            assert params.config_dir == custom_dir
            assert params.params_file == custom_dir / "last_used.json"
        finally:
            shutil.rmtree(custom_dir)


class TestConfigMigration:
    """Test configuration migration from old directories."""

    def test_claude_config_migration(self, tmp_path: Path) -> None:
        """Test migration from ~/.claude/config to ~/.ai-usage-monitor."""
        # Create mock old directory
        old_claude_config = tmp_path / ".claude" / "config"
        old_claude_config.mkdir(parents=True)

        # Create test files
        (old_claude_config / "notifications.json").write_text(
            json.dumps({"test": "notifications"})
        )
        (old_claude_config / "last_used.json").write_text(
            json.dumps({"test": "last_used"})
        )

        # Mock the directories
        new_config = tmp_path / ".ai-usage-monitor"

        with patch("ai_usage_monitor.cli.migrate.Path.home", return_value=tmp_path):
            with patch(
                "ai_usage_monitor.cli.migrate.NEW_CONFIG_DIR", new_config
            ):
                result = migrate_claude_config()

                assert result is True
                assert (new_config / "notifications.json").exists()
                assert (new_config / "last_used.json").exists()

                # Verify content was copied
                notifications = json.loads(
                    (new_config / "notifications.json").read_text()
                )
                assert notifications == {"test": "notifications"}

    def test_claude_monitor_migration(self, tmp_path: Path) -> None:
        """Test migration from ~/.claude-monitor to ~/.ai-usage-monitor."""
        # Create mock old directory
        old_config = tmp_path / ".claude-monitor"
        old_config.mkdir(parents=True)

        # Create test file
        (old_config / "last_used.json").write_text(
            json.dumps({"theme": "dark", "view": "daily"})
        )

        # Mock the directories
        new_config = tmp_path / ".ai-usage-monitor"

        with patch("ai_usage_monitor.cli.migrate.OLD_CONFIG_DIR", old_config):
            with patch(
                "ai_usage_monitor.cli.migrate.NEW_CONFIG_DIR", new_config
            ):
                result = migrate_config()

                assert result is True
                assert (new_config / "last_used.json").exists()

                # Verify tool was added
                params = json.loads((new_config / "last_used.json").read_text())
                assert params["tool"] == "claude-code"
                assert params["theme"] == "dark"

    def test_check_migration_needed_no_old_config(self, tmp_path: Path) -> None:
        """Test check_migration_needed when no old config exists."""
        with patch(
            "ai_usage_monitor.cli.migrate.OLD_CONFIG_DIR",
            tmp_path / ".claude-monitor",
        ):
            assert check_migration_needed() is False

    def test_check_migration_needed_old_exists(self, tmp_path: Path) -> None:
        """Test check_migration_needed when old config exists."""
        old_config = tmp_path / ".claude-monitor"
        old_config.mkdir(parents=True)

        with patch("ai_usage_monitor.cli.migrate.OLD_CONFIG_DIR", old_config):
            with patch(
                "ai_usage_monitor.cli.migrate.NEW_CONFIG_DIR",
                tmp_path / ".ai-usage-monitor",
            ):
                assert check_migration_needed() is True

    def test_auto_migrate_claude_config_only(self, tmp_path: Path) -> None:
        """Test that auto_migrate_if_needed migrates from ~/.claude/config."""
        old_claude = tmp_path / ".claude" / "config"
        old_claude.mkdir(parents=True)
        (old_claude / "notifications.json").write_text(
            json.dumps({"test": "notifications"})
        )

        new_config = tmp_path / ".ai-usage-monitor"

        # No old monitor directory
        with patch("ai_usage_monitor.cli.migrate.Path.home", return_value=tmp_path):
            with patch(
                "ai_usage_monitor.cli.migrate.OLD_CONFIG_DIR",
                tmp_path / ".claude-monitor",
            ):
                with patch(
                    "ai_usage_monitor.cli.migrate.NEW_CONFIG_DIR", new_config
                ):
                    auto_migrate_if_needed()

                    # Claude config migration should have run
                    assert (new_config / "notifications.json").exists()
                    notifications = json.loads(
                        (new_config / "notifications.json").read_text()
                    )
                    assert notifications == {"test": "notifications"}

    def test_migration_preserves_existing_files(self, tmp_path: Path) -> None:
        """Test that migration doesn't overwrite existing files."""
        old_config = tmp_path / ".claude" / "config"
        old_config.mkdir(parents=True)
        (old_config / "notifications.json").write_text(
            json.dumps({"old": "data"})
        )

        new_config = tmp_path / ".ai-usage-monitor"
        new_config.mkdir(parents=True)
        (new_config / "notifications.json").write_text(
            json.dumps({"new": "data"})
        )

        with patch("ai_usage_monitor.cli.migrate.Path.home", return_value=tmp_path):
            with patch(
                "ai_usage_monitor.cli.migrate.NEW_CONFIG_DIR", new_config
            ):
                migrate_claude_config()

                # Existing file should not be overwritten
                notifications = json.loads(
                    (new_config / "notifications.json").read_text()
                )
                assert notifications == {"new": "data"}

    def test_migration_handles_missing_old_directory_gracefully(
        self, tmp_path: Path
    ) -> None:
        """Test that migration succeeds when old directory doesn't exist."""
        with patch(
            "ai_usage_monitor.cli.migrate.Path.home", return_value=tmp_path
        ):
            result = migrate_claude_config()
            assert result is True  # Should succeed without error


class TestNoHardcodedPaths:
    """Test that no hardcoded paths remain in key files."""

    def test_settings_uses_get_config_dir(self) -> None:
        """Test that settings.py imports get_config_dir."""
        from ai_usage_monitor.core import settings

        # Check that the file imports from utils.paths
        with open(settings.__file__) as f:
            content = f.read()
            assert "from ai_usage_monitor.utils.paths import get_config_dir" in content

    def test_config_uses_get_config_file(self) -> None:
        """Test that config.py imports get_config_file."""
        from ai_usage_monitor.core import config

        with open(config.__file__) as f:
            content = f.read()
            assert "from ai_usage_monitor.utils.paths import get_config_file" in content

    def test_display_controller_uses_get_config_dir(self) -> None:
        """Test that display_controller.py imports get_config_dir."""
        from ai_usage_monitor.ui import display_controller

        with open(display_controller.__file__) as f:
            content = f.read()
            assert "from ai_usage_monitor.utils.paths import get_config_dir" in content
