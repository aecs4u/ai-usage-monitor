"""Simplified settings management with CLI and last used params only."""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

import pytz
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ai_usage_monitor import __version__

logger = logging.getLogger(__name__)

# Valid tool identifiers
VALID_TOOLS = ["claude-code", "codex-cli", "gemini-cli", "cline", "roo-code",
               "kilo-code", "github-copilot", "opencode", "pi-agent"]
TOOL_SELECTION_OPTIONS = ["auto", "all"] + VALID_TOOLS


class LastUsedParams:
    """Manages last used parameters persistence (moved from last_used.py)."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialize with config directory."""
        self.config_dir = config_dir or Path.home() / ".ai-usage-monitor"
        self.params_file = self.config_dir / "last_used.json"

    def save(self, settings: "Settings") -> None:
        """Save current settings as last used."""
        try:
            params = {
                "theme": settings.theme,
                "timezone": settings.timezone,
                "time_format": settings.time_format,
                "refresh_rate": settings.refresh_rate,
                "reset_hour": settings.reset_hour,
                "view": settings.view,
                "tool": settings.tool,
                "timestamp": datetime.now().isoformat(),
            }

            if settings.custom_limit_tokens:
                params["custom_limit_tokens"] = settings.custom_limit_tokens
            if settings.enabled_tools:
                params["enabled_tools"] = settings.enabled_tools

            self.config_dir.mkdir(parents=True, exist_ok=True)

            temp_file = self.params_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(params, f, indent=2)
            temp_file.replace(self.params_file)

            logger.debug(f"Saved last used params to {self.params_file}")

        except Exception as e:
            logger.warning(f"Failed to save last used params: {e}")

    def load(self) -> Dict[str, Any]:
        """Load last used parameters."""
        if not self.params_file.exists():
            return {}

        try:
            with open(self.params_file) as f:
                params = json.load(f)

            params.pop("timestamp", None)

            logger.debug(f"Loaded last used params from {self.params_file}")
            return params

        except Exception as e:
            logger.warning(f"Failed to load last used params: {e}")
            return {}

    def clear(self) -> None:
        """Clear last used parameters."""
        try:
            if self.params_file.exists():
                self.params_file.unlink()
                logger.debug("Cleared last used params")
        except Exception as e:
            logger.warning(f"Failed to clear last used params: {e}")

    def exists(self) -> bool:
        """Check if last used params exist."""
        return self.params_file.exists()


class Settings(BaseSettings):
    """ai-usage-monitor - Real-time token usage monitoring for AI coding tools"""

    model_config = SettingsConfigDict(
        env_file=None,
        env_prefix="",
        case_sensitive=False,
        validate_default=True,
        extra="ignore",
        cli_parse_args=True,
        cli_prog_name="ai-usage-monitor",
        cli_kebab_case=True,
        cli_implicit_flags=True,
    )

    # Multi-tool selection
    tool: str = Field(
        default="auto",
        description="Tool to monitor (auto, all, claude-code, codex-cli, gemini-cli, cline, roo-code, kilo-code, github-copilot, opencode, pi-agent)",
    )

    enabled_tools: List[str] = Field(
        default_factory=list,
        description="List of enabled tools when using --tool all",
    )

    plan: Literal["pro", "max5", "max20", "custom"] = Field(
        default="custom",
        description="Plan type (pro, max5, max20, custom)",
    )

    view: Literal["realtime", "daily", "monthly", "session"] = Field(
        default="realtime",
        description="View mode (realtime, daily, monthly, session)",
    )

    # Date range filtering
    from_date: Optional[str] = Field(
        default=None,
        description="Start date for data range (YYYY-MM-DD format)",
    )

    to_date: Optional[str] = Field(
        default=None,
        description="End date for data range (YYYY-MM-DD format)",
    )

    # Cloud sync settings (Phase 4 - prepared for future use)
    cloud_url: Optional[str] = Field(
        default=None,
        description="Cloud server URL for syncing usage data",
    )

    cloud_api_key: Optional[str] = Field(
        default=None,
        description="API key for cloud sync authentication",
    )

    auto_upload: bool = Field(
        default=False,
        description="Automatically upload usage data to cloud",
    )

    @staticmethod
    def _get_system_timezone() -> str:
        """Lazy import to avoid circular dependencies."""
        from ai_usage_monitor.utils.time_utils import get_system_timezone

        return get_system_timezone()

    @staticmethod
    def _get_system_time_format() -> str:
        """Lazy import to avoid circular dependencies."""
        from ai_usage_monitor.utils.time_utils import get_system_time_format

        return get_system_time_format()

    timezone: str = Field(
        default="auto",
        description="Timezone for display (auto-detected from system). Examples: UTC, America/New_York, Europe/London, Europe/Warsaw, Asia/Tokyo, Australia/Sydney",
    )

    time_format: str = Field(
        default="auto",
        description="Time format (12h or 24h, auto-detected from system)",
    )

    theme: Literal["light", "dark", "classic", "auto"] = Field(
        default="auto",
        description="Display theme (light, dark, classic, auto)",
    )

    custom_limit_tokens: Optional[int] = Field(
        default=None, gt=0, description="Token limit for custom plan"
    )

    refresh_rate: int = Field(
        default=10, ge=1, le=60, description="Refresh rate in seconds"
    )

    refresh_per_second: float = Field(
        default=0.75,
        ge=0.1,
        le=20.0,
        description="Display refresh rate per second (0.1-20 Hz). Higher values use more CPU",
    )

    reset_hour: Optional[int] = Field(
        default=None, ge=0, le=23, description="Reset hour for daily limits (0-23)"
    )

    log_level: str = Field(default="INFO", description="Logging level")

    log_file: Optional[Path] = Field(default=None, description="Log file path")

    debug: bool = Field(
        default=False,
        description="Enable debug logging (equivalent to --log-level DEBUG)",
    )

    version: bool = Field(default=False, description="Show version information")

    clear: bool = Field(default=False, description="Clear saved configuration")

    @field_validator("plan", mode="before")
    @classmethod
    def validate_plan(cls, v: Any) -> str:
        """Validate and normalize plan value."""
        if isinstance(v, str):
            v_lower = v.lower()
            valid_plans = ["pro", "max5", "max20", "custom"]
            if v_lower in valid_plans:
                return v_lower
            raise ValueError(
                f"Invalid plan: {v}. Must be one of: {', '.join(valid_plans)}"
            )
        return v

    @field_validator("view", mode="before")
    @classmethod
    def validate_view(cls, v: Any) -> str:
        """Validate and normalize view value."""
        if isinstance(v, str):
            v_lower = v.lower()
            valid_views = ["realtime", "daily", "monthly", "session"]
            if v_lower in valid_views:
                return v_lower
            raise ValueError(
                f"Invalid view: {v}. Must be one of: {', '.join(valid_views)}"
            )
        return v

    @field_validator("tool", mode="before")
    @classmethod
    def validate_tool(cls, v: Any) -> str:
        """Validate and normalize tool value."""
        if isinstance(v, str):
            v_lower = v.lower()
            if v_lower in TOOL_SELECTION_OPTIONS:
                return v_lower
            raise ValueError(
                f"Invalid tool: {v}. Must be one of: {', '.join(TOOL_SELECTION_OPTIONS)}"
            )
        return v

    @field_validator("enabled_tools", mode="before")
    @classmethod
    def validate_enabled_tools(cls, v: Any) -> List[str]:
        """Validate enabled tools list."""
        if v is None:
            return []
        if isinstance(v, str):
            # Handle comma-separated string from CLI
            tools = [t.strip().lower() for t in v.split(",") if t.strip()]
        elif isinstance(v, list):
            tools = [t.lower() for t in v]
        else:
            return []

        invalid = [t for t in tools if t not in VALID_TOOLS]
        if invalid:
            raise ValueError(
                f"Invalid tools: {', '.join(invalid)}. Valid tools: {', '.join(VALID_TOOLS)}"
            )
        return tools

    @field_validator("theme", mode="before")
    @classmethod
    def validate_theme(cls, v: Any) -> str:
        """Validate and normalize theme value."""
        if isinstance(v, str):
            v_lower = v.lower()
            valid_themes = ["light", "dark", "classic", "auto"]
            if v_lower in valid_themes:
                return v_lower
            raise ValueError(
                f"Invalid theme: {v}. Must be one of: {', '.join(valid_themes)}"
            )
        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Validate timezone."""
        if v not in ["local", "auto"] and v not in pytz.all_timezones:
            raise ValueError(f"Invalid timezone: {v}")
        return v

    @field_validator("time_format")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate time format."""
        if v not in ["12h", "24h", "auto"]:
            raise ValueError(
                f"Invalid time format: {v}. Must be '12h', '24h', or 'auto'"
            )
        return v

    @field_validator("from_date", "to_date", mode="before")
    @classmethod
    def validate_date(cls, v: Any) -> Optional[str]:
        """Validate date format (YYYY-MM-DD)."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                datetime.strptime(v, "%Y-%m-%d")
                return v
            except ValueError:
                raise ValueError(
                    f"Invalid date format: {v}. Must be YYYY-MM-DD (e.g., 2025-01-01)"
                )
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v_upper

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Any,
        init_settings: Any,
        env_settings: Any,
        dotenv_settings: Any,
        file_secret_settings: Any,
    ) -> Tuple[Any, ...]:
        """Custom sources - only init and last used."""
        _ = (
            settings_cls,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
        return (init_settings,)

    @classmethod
    def load_with_last_used(cls, argv: Optional[List[str]] = None) -> "Settings":
        """Load settings with last used params support (default behavior).

        Priority order (highest to lowest):
        1. CLI arguments
        2. Last used params
        3. TOML config file (~/.ai-usage-monitor.toml)
        4. Built-in defaults
        """
        if argv and "--version" in argv:
            print(f"ai-usage-monitor {__version__}")
            import sys

            sys.exit(0)

        clear_config = argv and "--clear" in argv

        # Load TOML config as base
        from ai_usage_monitor.core.config import load_config

        toml_config = load_config()

        if clear_config:
            last_used = LastUsedParams()
            last_used.clear()
            settings = cls(_cli_parse_args=argv)
        else:
            last_used = LastUsedParams()
            last_params = last_used.load()

            settings = cls(_cli_parse_args=argv)

            cli_provided_fields = set()
            if argv:
                for _i, arg in enumerate(argv):
                    if arg.startswith("--"):
                        field_name = arg[2:].replace("-", "_")
                        if field_name in cls.model_fields:
                            cli_provided_fields.add(field_name)

            # Apply TOML config for fields not provided via CLI or last_used
            toml_field_map = {
                "tool": toml_config.general.default_tool,
                "theme": toml_config.general.theme,
                "timezone": toml_config.general.timezone,
                "time_format": toml_config.general.time_format,
                "refresh_rate": toml_config.general.refresh_rate,
                "plan": toml_config.general.plan,
                "view": toml_config.general.view,
                "cloud_url": toml_config.cloud.url,
                "cloud_api_key": toml_config.cloud.api_key,
                "auto_upload": toml_config.cloud.auto_upload,
            }

            # Get enabled tools from TOML if configured
            if toml_config.tools and "enabled_tools" not in cli_provided_fields:
                enabled_from_toml = toml_config.get_enabled_tools()
                if enabled_from_toml:
                    settings.enabled_tools = enabled_from_toml

            for key, toml_value in toml_field_map.items():
                if (
                    key not in cli_provided_fields
                    and key not in last_params
                    and toml_value is not None
                ):
                    setattr(settings, key, toml_value)

            for key, value in last_params.items():
                if key == "plan":
                    continue
                if not hasattr(settings, key):
                    continue
                if key not in cli_provided_fields:
                    setattr(settings, key, value)

            if (
                "plan" in cli_provided_fields
                and settings.plan == "custom"
                and "custom_limit_tokens" not in cli_provided_fields
            ):
                settings.custom_limit_tokens = None

        if settings.timezone == "auto":
            settings.timezone = cls._get_system_timezone()
        if settings.time_format == "auto":
            settings.time_format = cls._get_system_time_format()

        if settings.debug:
            settings.log_level = "DEBUG"

        if settings.theme == "auto" or (
            "theme" not in cli_provided_fields and not clear_config
        ):
            from ai_usage_monitor.terminal.themes import (
                BackgroundDetector,
                BackgroundType,
            )

            detector = BackgroundDetector()
            detected_bg = detector.detect_background()

            if detected_bg == BackgroundType.LIGHT:
                settings.theme = "light"
            elif detected_bg == BackgroundType.DARK:
                settings.theme = "dark"
            else:
                settings.theme = "auto"

        if not clear_config:
            last_used = LastUsedParams()
            last_used.save(settings)

        return settings

    def to_namespace(self) -> argparse.Namespace:
        """Convert to argparse.Namespace for compatibility."""
        args = argparse.Namespace()

        args.tool = self.tool
        args.enabled_tools = self.enabled_tools
        args.plan = self.plan
        args.view = self.view
        args.timezone = self.timezone
        args.theme = self.theme
        args.refresh_rate = self.refresh_rate
        args.refresh_per_second = self.refresh_per_second
        args.reset_hour = self.reset_hour
        args.custom_limit_tokens = self.custom_limit_tokens
        args.time_format = self.time_format
        args.log_level = self.log_level
        args.log_file = str(self.log_file) if self.log_file else None
        args.version = self.version
        args.cloud_url = self.cloud_url
        args.cloud_api_key = self.cloud_api_key
        args.auto_upload = self.auto_upload
        args.from_date = self.from_date
        args.to_date = self.to_date

        return args
