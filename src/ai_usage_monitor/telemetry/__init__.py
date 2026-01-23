"""Telemetry and monitoring integration for AI Usage Monitor.

This module provides optional telemetry via Logfire. All telemetry is:
- Opt-in (disabled by default)
- Gracefully degraded (works without logfire installed)
- Privacy-respecting (no sensitive data)

Usage:
    from ai_usage_monitor.telemetry import get_logfire_manager

    lf = get_logfire_manager()
    with lf.span("operation.name") as span:
        result = do_work()
        lf.log_metric("operation.duration", 1.5)
"""

from ai_usage_monitor.telemetry.logfire_config import (
    LOGFIRE_AVAILABLE,
    LogfireManager,
    get_logfire_manager,
    initialize_logfire,
)

__all__ = [
    "LOGFIRE_AVAILABLE",
    "LogfireManager",
    "get_logfire_manager",
    "initialize_logfire",
]
