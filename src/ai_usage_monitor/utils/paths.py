"""Path utilities for config and data directories."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Standard config directory
CONFIG_DIR = Path.home() / ".ai-usage-monitor"


def get_config_dir() -> Path:
    """Get application config directory.

    Returns:
        Path to ~/.ai-usage-monitor
    """
    config_dir = CONFIG_DIR
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get TOML config file path.

    Returns:
        Path to ~/.ai-usage-monitor.toml (note: in home dir, not config dir)
    """
    return Path.home() / ".ai-usage-monitor.toml"


def get_last_used_file() -> Path:
    """Get last used params file path.

    Returns:
        Path to ~/.ai-usage-monitor/last_used.json
    """
    return get_config_dir() / "last_used.json"


def get_notifications_file() -> Path:
    """Get notifications state file path.

    Returns:
        Path to ~/.ai-usage-monitor/notifications.json
    """
    return get_config_dir() / "notifications.json"
