"""Tests for Logfire telemetry integration."""

from unittest.mock import Mock, patch

import pytest

from ai_usage_monitor.telemetry import (
    LOGFIRE_AVAILABLE,
    LogfireManager,
    get_logfire_manager,
    initialize_logfire,
)


class TestLogfireAvailability:
    """Test Logfire availability detection."""

    def test_logfire_available_flag_is_boolean(self) -> None:
        """Test that LOGFIRE_AVAILABLE is a boolean."""
        assert isinstance(LOGFIRE_AVAILABLE, bool)

    @patch("ai_usage_monitor.telemetry.logfire_config.LOGFIRE_AVAILABLE", False)
    @patch("ai_usage_monitor.telemetry.logfire_config.logfire", None)
    def test_logfire_manager_disabled_when_not_available(self) -> None:
        """Test that LogfireManager is disabled when logfire not available."""
        manager = LogfireManager(enabled=True, token="test_token")

        assert manager.enabled is False
        assert manager._initialized is False

    def test_logfire_manager_disabled_by_default(self) -> None:
        """Test that LogfireManager is disabled by default."""
        manager = LogfireManager()

        assert manager.enabled is False
        assert manager._initialized is False


class TestLogfireManager:
    """Test LogfireManager functionality."""

    def test_init_default_values(self) -> None:
        """Test LogfireManager initialization with default values."""
        manager = LogfireManager()

        assert manager.enabled is False
        assert manager.token is None
        assert manager.sample_rate == 1.0
        assert manager._initialized is False

    def test_init_with_custom_values(self) -> None:
        """Test LogfireManager initialization with custom values."""
        with patch("ai_usage_monitor.telemetry.logfire_config.LOGFIRE_AVAILABLE", True):
            with patch("ai_usage_monitor.telemetry.logfire_config.logfire") as mock_lf:
                mock_lf.configure = Mock()
                manager = LogfireManager(
                    enabled=True, token="test_token", sample_rate=0.5
                )

                assert manager.token == "test_token"
                assert manager.sample_rate == 0.5

    def test_span_no_op_when_disabled(self) -> None:
        """Test that span() is a no-op when disabled."""
        manager = LogfireManager(enabled=False)

        with manager.span("test.operation", param1="value1") as span:
            assert span is None

    def test_log_metric_no_op_when_disabled(self) -> None:
        """Test that log_metric() is a no-op when disabled."""
        manager = LogfireManager(enabled=False)

        # Should not raise any exception
        manager.log_metric("test.metric", 42, tag="value")

    def test_log_event_no_op_when_disabled(self) -> None:
        """Test that log_event() is a no-op when disabled."""
        manager = LogfireManager(enabled=False)

        # Should not raise any exception
        manager.log_event("test.event", param="value")

    @patch("ai_usage_monitor.telemetry.logfire_config.LOGFIRE_AVAILABLE", True)
    @patch("ai_usage_monitor.telemetry.logfire_config.logfire")
    def test_span_calls_logfire_when_enabled(self, mock_logfire) -> None:
        """Test that span() calls logfire when enabled."""
        mock_logfire.configure = Mock()
        mock_logfire.span = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))

        manager = LogfireManager(enabled=True, token="test_token")

        with manager.span("test.operation", param1="value1"):
            pass

        mock_logfire.span.assert_called_once_with("test.operation", param1="value1")

    @patch("ai_usage_monitor.telemetry.logfire_config.LOGFIRE_AVAILABLE", True)
    @patch("ai_usage_monitor.telemetry.logfire_config.logfire")
    def test_log_metric_calls_logfire_when_enabled(self, mock_logfire) -> None:
        """Test that log_metric() calls logfire when enabled."""
        mock_logfire.configure = Mock()
        mock_logfire.info = Mock()

        manager = LogfireManager(enabled=True, token="test_token")
        manager.log_metric("test.metric", 42, tag="value")

        mock_logfire.info.assert_called_once_with(
            "metric.test.metric", value=42, tag="value"
        )

    @patch("ai_usage_monitor.telemetry.logfire_config.LOGFIRE_AVAILABLE", True)
    @patch("ai_usage_monitor.telemetry.logfire_config.logfire")
    def test_log_event_calls_logfire_when_enabled(self, mock_logfire) -> None:
        """Test that log_event() calls logfire when enabled."""
        mock_logfire.configure = Mock()
        mock_logfire.info = Mock()

        manager = LogfireManager(enabled=True, token="test_token")
        manager.log_event("test.event", param="value")

        mock_logfire.info.assert_called_once_with("test.event", param="value")

    @patch("ai_usage_monitor.telemetry.logfire_config.LOGFIRE_AVAILABLE", True)
    @patch("ai_usage_monitor.telemetry.logfire_config.logfire")
    def test_initialization_with_token(self, mock_logfire) -> None:
        """Test that logfire is configured with token when provided."""
        mock_logfire.configure = Mock()

        LogfireManager(enabled=True, token="my_token")

        mock_logfire.configure.assert_called_once()
        call_kwargs = mock_logfire.configure.call_args[1]
        assert call_kwargs["token"] == "my_token"
        assert call_kwargs["send_to_logfire"] is True

    @patch("ai_usage_monitor.telemetry.logfire_config.LOGFIRE_AVAILABLE", True)
    @patch("ai_usage_monitor.telemetry.logfire_config.logfire")
    def test_initialization_without_token(self, mock_logfire) -> None:
        """Test that logfire is configured for local when no token provided."""
        mock_logfire.configure = Mock()

        LogfireManager(enabled=True, token=None)

        mock_logfire.configure.assert_called_once()
        call_kwargs = mock_logfire.configure.call_args[1]
        assert call_kwargs["token"] is None
        assert call_kwargs["send_to_logfire"] is False


class TestGlobalSingleton:
    """Test global singleton pattern for LogfireManager."""

    def test_initialize_logfire_returns_manager(self) -> None:
        """Test that initialize_logfire returns a LogfireManager."""
        manager = initialize_logfire(enabled=False)

        assert isinstance(manager, LogfireManager)

    def test_get_logfire_manager_returns_manager(self) -> None:
        """Test that get_logfire_manager returns a LogfireManager."""
        manager = get_logfire_manager()

        assert isinstance(manager, LogfireManager)

    def test_get_logfire_manager_creates_disabled_by_default(self) -> None:
        """Test that get_logfire_manager creates disabled manager by default."""
        # Clear the global instance
        import ai_usage_monitor.telemetry.logfire_config as lf_config

        lf_config._logfire_manager = None

        manager = get_logfire_manager()

        assert manager.enabled is False

    def test_initialize_logfire_sets_global_instance(self) -> None:
        """Test that initialize_logfire sets the global instance."""
        manager1 = initialize_logfire(enabled=False, token="test")
        manager2 = get_logfire_manager()

        assert manager1 is manager2


class TestGracefulDegradation:
    """Test graceful degradation when logfire is not installed."""

    @patch("ai_usage_monitor.telemetry.logfire_config.LOGFIRE_AVAILABLE", False)
    @patch("ai_usage_monitor.telemetry.logfire_config.logfire", None)
    def test_span_works_without_logfire(self) -> None:
        """Test that span() works without logfire installed."""
        manager = LogfireManager(enabled=True)

        # Should not raise any exception
        with manager.span("test.operation") as span:
            assert span is None

    @patch("ai_usage_monitor.telemetry.logfire_config.LOGFIRE_AVAILABLE", False)
    @patch("ai_usage_monitor.telemetry.logfire_config.logfire", None)
    def test_log_metric_works_without_logfire(self) -> None:
        """Test that log_metric() works without logfire installed."""
        manager = LogfireManager(enabled=True)

        # Should not raise any exception
        manager.log_metric("test.metric", 42)

    @patch("ai_usage_monitor.telemetry.logfire_config.LOGFIRE_AVAILABLE", False)
    @patch("ai_usage_monitor.telemetry.logfire_config.logfire", None)
    def test_log_event_works_without_logfire(self) -> None:
        """Test that log_event() works without logfire installed."""
        manager = LogfireManager(enabled=True)

        # Should not raise any exception
        manager.log_event("test.event", param="value")


class TestErrorHandling:
    """Test error handling in LogfireManager."""

    @patch("ai_usage_monitor.telemetry.logfire_config.LOGFIRE_AVAILABLE", True)
    @patch("ai_usage_monitor.telemetry.logfire_config.logfire")
    def test_span_handles_errors_gracefully(self, mock_logfire) -> None:
        """Test that span() handles errors gracefully."""
        mock_logfire.configure = Mock()
        mock_logfire.span = Mock(side_effect=Exception("Test error"))

        manager = LogfireManager(enabled=True, token="test")

        # Should not raise exception, should yield None
        with manager.span("test.operation") as span:
            assert span is None

    @patch("ai_usage_monitor.telemetry.logfire_config.LOGFIRE_AVAILABLE", True)
    @patch("ai_usage_monitor.telemetry.logfire_config.logfire")
    def test_log_metric_handles_errors_gracefully(self, mock_logfire) -> None:
        """Test that log_metric() handles errors gracefully."""
        mock_logfire.configure = Mock()
        mock_logfire.info = Mock(side_effect=Exception("Test error"))

        manager = LogfireManager(enabled=True, token="test")

        # Should not raise exception
        manager.log_metric("test.metric", 42)

    @patch("ai_usage_monitor.telemetry.logfire_config.LOGFIRE_AVAILABLE", True)
    @patch("ai_usage_monitor.telemetry.logfire_config.logfire")
    def test_initialization_error_disables_manager(self, mock_logfire) -> None:
        """Test that initialization errors disable the manager."""
        mock_logfire.configure = Mock(side_effect=Exception("Init error"))

        manager = LogfireManager(enabled=True, token="test")

        # Manager should be disabled due to init error
        assert manager.enabled is False


class TestConfigurationIntegration:
    """Test integration with AppConfig."""

    def test_telemetry_config_defaults(self) -> None:
        """Test that TelemetryConfig has correct defaults."""
        from ai_usage_monitor.core.config import TelemetryConfig

        config = TelemetryConfig()

        assert config.enabled is False
        assert config.token is None
        assert config.sample_rate == 1.0

    def test_app_config_has_telemetry_field(self) -> None:
        """Test that AppConfig has telemetry field."""
        from ai_usage_monitor.core.config import AppConfig

        config = AppConfig()

        assert hasattr(config, "telemetry")
        assert config.telemetry.enabled is False
