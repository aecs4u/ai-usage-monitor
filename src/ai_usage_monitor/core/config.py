"""TOML configuration file support for AI Usage Monitor.

Loads configuration from ~/.ai-usage-monitor.toml with the following structure:

    [general]
    default_tool = "auto"
    theme = "dark"
    timezone = "UTC"
    time_format = "24h"

    [cloud]
    url = "https://api.ai-usage-monitor.dev"
    api_key = "sk_..."
    auto_upload = true

    [tools.claude-code]
    enabled = true
    data_path = "~/.claude/projects"

    [tools.codex-cli]
    enabled = true

    [tools.cline]
    enabled = false
"""

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None  # type: ignore

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path.home() / ".ai-usage-monitor.toml"


@dataclass
class ToolConfig:
    """Configuration for a specific tool."""

    name: str
    enabled: bool = True
    data_path: Optional[str] = None
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CloudConfig:
    """Cloud sync configuration."""

    url: Optional[str] = None
    api_key: Optional[str] = None
    auto_upload: bool = False


@dataclass
class GeneralConfig:
    """General application configuration."""

    default_tool: str = "auto"
    theme: str = "auto"
    timezone: str = "auto"
    time_format: str = "auto"
    refresh_rate: int = 10
    plan: str = "custom"
    view: str = "realtime"


@dataclass
class AppConfig:
    """Complete application configuration from TOML file."""

    general: GeneralConfig = field(default_factory=GeneralConfig)
    cloud: CloudConfig = field(default_factory=CloudConfig)
    tools: Dict[str, ToolConfig] = field(default_factory=dict)
    config_path: Optional[Path] = None

    def get_enabled_tools(self) -> List[str]:
        """Get list of enabled tool names."""
        return [name for name, cfg in self.tools.items() if cfg.enabled]

    def get_tool_data_path(self, tool_name: str) -> Optional[str]:
        """Get custom data path for a tool if configured."""
        if tool_name in self.tools:
            return self.tools[tool_name].data_path
        return None


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """Load configuration from TOML file.

    Args:
        config_path: Path to config file. Defaults to ~/.ai-usage-monitor.toml

    Returns:
        AppConfig with loaded settings, or defaults if file doesn't exist.
    """
    path = config_path or DEFAULT_CONFIG_PATH

    if not path.exists():
        logger.debug(f"Config file not found at {path}, using defaults")
        return AppConfig()

    if tomllib is None:
        logger.warning("tomli not installed, cannot read TOML config")
        return AppConfig()

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)

        return _parse_config(data, path)

    except Exception as e:
        logger.warning(f"Failed to load config from {path}: {e}")
        return AppConfig()


def _parse_config(data: Dict[str, Any], config_path: Path) -> AppConfig:
    """Parse raw TOML data into AppConfig."""
    config = AppConfig(config_path=config_path)

    # Parse [general] section
    if "general" in data:
        general_data = data["general"]
        config.general = GeneralConfig(
            default_tool=general_data.get("default_tool", "auto"),
            theme=general_data.get("theme", "auto"),
            timezone=general_data.get("timezone", "auto"),
            time_format=general_data.get("time_format", "auto"),
            refresh_rate=general_data.get("refresh_rate", 10),
            plan=general_data.get("plan", "custom"),
            view=general_data.get("view", "realtime"),
        )

    # Parse [cloud] section
    if "cloud" in data:
        cloud_data = data["cloud"]
        config.cloud = CloudConfig(
            url=cloud_data.get("url"),
            api_key=cloud_data.get("api_key"),
            auto_upload=cloud_data.get("auto_upload", False),
        )

    # Parse [tools.*] sections
    if "tools" in data:
        for tool_name, tool_data in data["tools"].items():
            if isinstance(tool_data, dict):
                # Extract known fields, put rest in custom_settings
                known_keys = {"enabled", "data_path"}
                custom = {k: v for k, v in tool_data.items() if k not in known_keys}

                config.tools[tool_name] = ToolConfig(
                    name=tool_name,
                    enabled=tool_data.get("enabled", True),
                    data_path=tool_data.get("data_path"),
                    custom_settings=custom,
                )
            else:
                # Simple enabled = true/false
                config.tools[tool_name] = ToolConfig(
                    name=tool_name,
                    enabled=bool(tool_data),
                )

    return config


def save_config(config: AppConfig, config_path: Optional[Path] = None) -> bool:
    """Save configuration to TOML file.

    Args:
        config: AppConfig to save
        config_path: Path to save to. Defaults to ~/.ai-usage-monitor.toml

    Returns:
        True if saved successfully.
    """
    path = config_path or DEFAULT_CONFIG_PATH

    try:
        # Build TOML content manually (toml writing is simpler than parsing)
        lines = []

        # [general] section
        lines.append("[general]")
        lines.append(f'default_tool = "{config.general.default_tool}"')
        lines.append(f'theme = "{config.general.theme}"')
        lines.append(f'timezone = "{config.general.timezone}"')
        lines.append(f'time_format = "{config.general.time_format}"')
        lines.append(f"refresh_rate = {config.general.refresh_rate}")
        lines.append(f'plan = "{config.general.plan}"')
        lines.append(f'view = "{config.general.view}"')
        lines.append("")

        # [cloud] section
        lines.append("[cloud]")
        if config.cloud.url:
            lines.append(f'url = "{config.cloud.url}"')
        if config.cloud.api_key:
            lines.append(f'api_key = "{config.cloud.api_key}"')
        lines.append(f"auto_upload = {'true' if config.cloud.auto_upload else 'false'}")
        lines.append("")

        # [tools.*] sections
        for tool_name, tool_cfg in config.tools.items():
            lines.append(f"[tools.{tool_name}]")
            lines.append(
                f"enabled = {'true' if tool_cfg.enabled else 'false'}"
            )
            if tool_cfg.data_path:
                lines.append(f'data_path = "{tool_cfg.data_path}"')
            for key, value in tool_cfg.custom_settings.items():
                if isinstance(value, str):
                    lines.append(f'{key} = "{value}"')
                elif isinstance(value, bool):
                    lines.append(f"{key} = {'true' if value else 'false'}")
                else:
                    lines.append(f"{key} = {value}")
            lines.append("")

        # Write to file
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write("\n".join(lines))

        logger.info(f"Saved config to {path}")
        return True

    except Exception as e:
        logger.error(f"Failed to save config to {path}: {e}")
        return False


def create_default_config(config_path: Optional[Path] = None) -> AppConfig:
    """Create a default configuration file.

    Args:
        config_path: Path to create config at. Defaults to ~/.ai-usage-monitor.toml

    Returns:
        The created AppConfig.
    """
    from ai_usage_monitor.core.settings import VALID_TOOLS

    config = AppConfig(config_path=config_path or DEFAULT_CONFIG_PATH)

    # Set up default tools
    for tool_name in VALID_TOOLS:
        config.tools[tool_name] = ToolConfig(
            name=tool_name,
            enabled=tool_name == "claude-code",  # Only claude-code enabled by default
        )

    save_config(config, config_path)
    return config
