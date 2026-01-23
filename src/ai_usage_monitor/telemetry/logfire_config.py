"""Logfire telemetry configuration and management.

This module provides optional Logfire integration for telemetry and monitoring.
Logfire is gracefully degraded when not installed, making it completely optional.
"""

import logging
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional

logger = logging.getLogger(__name__)

# Try to import logfire, but gracefully degrade if not installed
try:
    import logfire

    LOGFIRE_AVAILABLE = True
except ImportError:
    LOGFIRE_AVAILABLE = False
    logfire = None  # type: ignore


class LogfireManager:
    """Manages Logfire telemetry with graceful degradation.

    Features:
    - Optional dependency (works without logfire installed)
    - Context manager `span()` for tracing (no-op if disabled)
    - `log_metric()` for measurements
    - Global singleton pattern
    - Disabled by default for privacy

    Example:
        >>> from ai_usage_monitor.telemetry import get_logfire_manager
        >>> lf = get_logfire_manager()
        >>> with lf.span("operation.name", param1="value1") as span:
        ...     result = do_operation()
        ...     lf.log_metric("operation.count", 1, status="success")
    """

    def __init__(
        self,
        enabled: bool = False,
        token: Optional[str] = None,
        sample_rate: float = 1.0,
    ) -> None:
        """Initialize Logfire manager.

        Args:
            enabled: Whether telemetry is enabled (default: False)
            token: Logfire API token (optional)
            sample_rate: Sampling rate for telemetry (0.0 to 1.0, default: 1.0)
        """
        self.enabled = enabled and LOGFIRE_AVAILABLE
        self.token = token
        self.sample_rate = sample_rate
        self._initialized = False

        if enabled and not LOGFIRE_AVAILABLE:
            logger.warning(
                "Logfire telemetry requested but logfire not installed. "
                "Install with: pip install ai-usage-monitor[logfire]"
            )

        if self.enabled:
            self._initialize_logfire()

    def _initialize_logfire(self) -> None:
        """Initialize Logfire SDK."""
        if self._initialized or not LOGFIRE_AVAILABLE:
            return

        try:
            if logfire is not None:
                # Configure logfire
                logfire.configure(
                    token=self.token,
                    # Use console output if no token provided (local development)
                    send_to_logfire=bool(self.token),
                )

                self._initialized = True
                logger.info("Logfire telemetry initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Logfire: {e}")
            self.enabled = False

    @contextmanager
    def span(
        self, operation_name: str, **attributes: Any
    ) -> Generator[Any, None, None]:
        """Create a tracing span (no-op if disabled).

        Args:
            operation_name: Name of the operation being traced
            **attributes: Additional attributes to attach to the span

        Yields:
            Span object (or None if disabled)

        Example:
            >>> with lf.span("data.load", tool="claude-code") as span:
            ...     entries = load_entries()
            ...     if span:
            ...         span.set_attribute("entries_count", len(entries))
        """
        if not self.enabled or logfire is None:
            # No-op context manager
            yield None
            return

        try:
            with logfire.span(operation_name, **attributes) as span:
                yield span
        except Exception as e:
            logger.debug(f"Error in Logfire span: {e}")
            yield None

    def log_metric(
        self, metric_name: str, value: Any, **attributes: Any
    ) -> None:
        """Log a metric value (no-op if disabled).

        Args:
            metric_name: Name of the metric
            value: Metric value
            **attributes: Additional attributes/tags

        Example:
            >>> lf.log_metric("adapter.load_time", 2.5, tool="claude-code")
            >>> lf.log_metric("error.count", 1, error_type="FileNotFound")
        """
        if not self.enabled or logfire is None:
            return

        try:
            logfire.info(
                f"metric.{metric_name}",
                value=value,
                **attributes,
            )
        except Exception as e:
            logger.debug(f"Error logging metric: {e}")

    def log_event(
        self, event_name: str, **attributes: Any
    ) -> None:
        """Log an event (no-op if disabled).

        Args:
            event_name: Name of the event
            **attributes: Event attributes/properties

        Example:
            >>> lf.log_event("view.changed", from_view="realtime", to_view="daily")
            >>> lf.log_event("tool.selected", tool="codex-cli", mode="auto")
        """
        if not self.enabled or logfire is None:
            return

        try:
            logfire.info(event_name, **attributes)
        except Exception as e:
            logger.debug(f"Error logging event: {e}")


# Global singleton instance
_logfire_manager: Optional[LogfireManager] = None


def initialize_logfire(
    enabled: bool = False,
    token: Optional[str] = None,
    sample_rate: float = 1.0,
) -> LogfireManager:
    """Initialize the global Logfire manager.

    Args:
        enabled: Whether telemetry is enabled
        token: Logfire API token (optional)
        sample_rate: Sampling rate (0.0 to 1.0)

    Returns:
        LogfireManager instance
    """
    global _logfire_manager

    _logfire_manager = LogfireManager(
        enabled=enabled,
        token=token,
        sample_rate=sample_rate,
    )

    return _logfire_manager


def get_logfire_manager() -> LogfireManager:
    """Get the global Logfire manager instance.

    Returns:
        LogfireManager instance (creates one if needed)
    """
    global _logfire_manager

    if _logfire_manager is None:
        # Create disabled instance by default
        _logfire_manager = LogfireManager(enabled=False)

    return _logfire_manager
