"""Simplified CLI entry point using pydantic-settings."""

import argparse
import contextlib
import logging
import signal
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, NoReturn, Optional, Union

if TYPE_CHECKING:
    from ai_usage_monitor.core.config import AppConfig

from rich.console import Console

from ai_usage_monitor import __version__
from ai_usage_monitor.adapters.registry import AdapterRegistry
from ai_usage_monitor.cli.bootstrap import (
    ensure_directories,
    init_timezone,
    setup_environment,
    setup_logging,
)
from ai_usage_monitor.core.plans import Plans, PlanType, get_token_limit
from ai_usage_monitor.core.settings import Settings
from ai_usage_monitor.data.aggregator import UsageAggregator
from ai_usage_monitor.data.analysis import analyze_usage
from ai_usage_monitor.error_handling import report_error
from ai_usage_monitor.monitoring.orchestrator import MonitoringOrchestrator
from ai_usage_monitor.terminal.manager import (
    enter_alternate_screen,
    handle_cleanup_and_exit,
    handle_error_and_exit,
    restore_terminal,
    setup_terminal,
)
from ai_usage_monitor.terminal.themes import get_themed_console, print_themed
from ai_usage_monitor.ui.display_controller import DisplayController
from ai_usage_monitor.ui.table_views import TableViewsController

# Type aliases for CLI callbacks
DataUpdateCallback = Callable[[Dict[str, Any]], None]
SessionChangeCallback = Callable[[str, str, Optional[Dict[str, Any]]], None]


def get_standard_claude_paths() -> List[str]:
    """Get list of standard Claude data directory paths to check."""
    return ["~/.claude/projects", "~/.config/claude/projects"]


def discover_data_paths_for_tool(
    tool_name: str,
    custom_paths: Optional[List[str]] = None,
    config: Optional["AppConfig"] = None,
) -> List[Path]:
    """Discover data directories for a specific tool using the adapter system.

    Args:
        tool_name: Tool identifier (e.g., 'claude-code', 'codex-cli')
        custom_paths: Optional list of custom paths to check
        config: Optional AppConfig to read tool configuration from

    Returns:
        List of Path objects for existing data directories
    """
    logger = logging.getLogger(__name__)

    adapter = AdapterRegistry.get_adapter(tool_name)
    if not adapter:
        # Fallback for tools without adapters
        logger.warning(f"No adapter found for tool: {tool_name}")
        return []

    # Priority: custom_paths > config data_path > defaults
    paths_to_check = custom_paths

    if paths_to_check is None and config:
        config_data_path = config.get_tool_data_path(tool_name)
        if config_data_path:
            paths_to_check = [config_data_path]
            logger.info(f"Using configured data path for {tool_name}: {config_data_path}")

    return adapter.discover_data_paths(paths_to_check)


def load_entries_from_all_tools():
    """Load usage entries from all available tools.

    Returns:
        Combined list of UsageEntry objects from all available tools.
    """
    from ai_usage_monitor.core.models import UsageEntry

    logger = logging.getLogger(__name__)
    all_entries: List[UsageEntry] = []
    available_tools = AdapterRegistry.get_available_tools()

    if not available_tools:
        logger.warning("No tools with data available")
        return all_entries

    for tool_meta in available_tools:
        adapter = AdapterRegistry.get_adapter(tool_meta.name)
        if adapter:
            try:
                entries, _ = adapter.load_usage_entries()
                if entries:
                    # Calculate cost for each entry if not already set
                    for entry in entries:
                        if entry.cost_usd == 0.0:
                            entry.cost_usd = adapter.calculate_cost(entry)
                    logger.info(f"Loaded {len(entries)} entries from {tool_meta.display_name}")
                    all_entries.extend(entries)
            except Exception as e:
                logger.warning(f"Failed to load entries from {tool_meta.name}: {e}")

    # Sort all entries by timestamp
    all_entries.sort(key=lambda e: e.timestamp)
    logger.info(f"Total entries loaded from all tools: {len(all_entries)}")
    return all_entries


def discover_claude_data_paths(
    custom_paths: Optional[List[str]] = None, config: Optional["AppConfig"] = None
) -> List[Path]:
    """Discover all available Claude data directories (legacy compatibility).

    Args:
        custom_paths: Optional list of custom paths to check instead of standard ones
        config: Optional AppConfig to read tool configuration from

    Returns:
        List of Path objects for existing Claude data directories
    """
    return discover_data_paths_for_tool("claude-code", custom_paths, config)


def get_active_tool(settings: Settings) -> str:
    """Determine which tool to use based on settings.

    Args:
        settings: Application settings with tool configuration

    Returns:
        Tool identifier to use
    """
    tool = settings.tool

    if tool == "auto":
        # Auto-detect: use first available tool
        available = AdapterRegistry.get_available_tools()
        if available:
            return available[0].name
        return "claude-code"  # Default fallback

    if tool == "all":
        # Multi-tool mode - return special marker
        return "all"

    return tool


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point with direct pydantic-settings integration."""
    if argv is None:
        argv = sys.argv[1:]

    if "--version" in argv or "-v" in argv:
        print(f"ai-usage-monitor {__version__}")
        return 0

    try:
        settings = Settings.load_with_last_used(argv)

        setup_environment()
        ensure_directories()

        if settings.log_file:
            setup_logging(settings.log_level, settings.log_file, disable_console=True)
        else:
            setup_logging(settings.log_level, disable_console=True)

        init_timezone(settings.timezone)

        # Load TOML config
        from ai_usage_monitor.core.config import load_config

        config = load_config()

        # Determine active tool
        active_tool = get_active_tool(settings)
        logger = logging.getLogger(__name__)
        logger.info(f"Active tool: {active_tool}")

        args = settings.to_namespace()
        args.active_tool = active_tool
        args.config = config  # Attach config for use in discovery

        _run_monitoring(args)

        return 0

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
        return 0
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Monitor failed: {e}", exc_info=True)
        traceback.print_exc()
        return 1


def _run_monitoring(args: argparse.Namespace) -> None:
    """Main monitoring implementation without facade."""
    view_mode = getattr(args, "view", "realtime")

    if hasattr(args, "theme") and args.theme:
        console = get_themed_console(force_theme=args.theme.lower())
    else:
        console = get_themed_console()

    old_terminal_settings = setup_terminal()
    live_display_active: bool = False

    try:
        # Get active tool from args
        active_tool: str = getattr(args, "active_tool", "claude-code")
        logger = logging.getLogger(__name__)

        # Handle "all" mode for daily/monthly views
        if active_tool == "all" and view_mode in ["daily", "monthly"]:
            available_tools = AdapterRegistry.get_available_tools()
            if not available_tools:
                print_themed("No tools with data available", style="error")
                return
            tool_names = [t.display_name for t in available_tools]
            print_themed(f"Loading data from: {', '.join(tool_names)}", style="info")
            _run_multi_tool_table_view(args, view_mode, console)
            return

        # Check for multi-tool mode in realtime view (not supported)
        if active_tool == "all" and view_mode == "realtime":
            print_themed(
                "Multi-tool mode (--tool all) is not supported in realtime view.\n"
                "Use --view daily or --view monthly for multi-tool reports.",
                style="error"
            )
            return

        # Get adapter for single tool
        adapter = AdapterRegistry.get_adapter(active_tool)
        if not adapter or not adapter.is_available():
            tool_display = adapter.metadata.display_name if adapter else active_tool
            print_themed(f"No data available for {tool_display}", style="error")
            return

        logger.info(f"Using adapter for {active_tool}: {adapter.metadata.display_name}")

        # Handle different view modes
        if view_mode in ["daily", "monthly"]:
            _run_table_view(args, adapter, view_mode, console)
            return

        token_limit: int = _get_initial_token_limit(args, adapter)

        display_controller = DisplayController()
        display_controller.live_manager._console = console

        refresh_per_second: float = getattr(args, "refresh_per_second", 0.75)
        logger.info(
            f"Display refresh rate: {refresh_per_second} Hz ({1000 / refresh_per_second:.0f}ms)"
        )
        logger.info(f"Data refresh rate: {args.refresh_rate} seconds")

        live_display = display_controller.live_manager.create_live_display(
            auto_refresh=True, console=console, refresh_per_second=refresh_per_second
        )

        loading_display = display_controller.create_loading_display(
            args.plan, args.timezone
        )

        enter_alternate_screen()

        live_display_active = False

        try:
            # Enter live context and show loading screen immediately
            live_display.__enter__()
            live_display_active = True
            live_display.update(loading_display)

            orchestrator = MonitoringOrchestrator(
                update_interval=(
                    args.refresh_rate if hasattr(args, "refresh_rate") else 10
                ),
                data_path=None,  # Not needed with adapter
                adapter=adapter,  # Use adapter instead of data_path
            )
            orchestrator.set_args(args)

            # Setup monitoring callback
            def on_data_update(monitoring_data: Dict[str, Any]) -> None:
                """Handle data updates from orchestrator."""
                try:
                    data: Dict[str, Any] = monitoring_data.get("data", {})
                    blocks: List[Dict[str, Any]] = data.get("blocks", [])

                    logger.debug(f"Display data has {len(blocks)} blocks")
                    if blocks:
                        active_blocks: List[Dict[str, Any]] = [
                            b for b in blocks if b.get("isActive")
                        ]
                        logger.debug(f"Active blocks: {len(active_blocks)}")
                        if active_blocks:
                            total_tokens: int = active_blocks[0].get("totalTokens", 0)
                            logger.debug(f"Active block tokens: {total_tokens}")

                    renderable = display_controller.create_data_display(
                        data, args, monitoring_data.get("token_limit", token_limit)
                    )

                    if live_display:
                        live_display.update(renderable)

                except Exception as e:
                    logger.error(f"Display update error: {e}", exc_info=True)
                    report_error(
                        exception=e,
                        component="cli_main",
                        context_name="display_update_error",
                    )

            # Register callbacks
            orchestrator.register_update_callback(on_data_update)

            # Optional: Register session change callback
            def on_session_change(
                event_type: str, session_id: str, session_data: Optional[Dict[str, Any]]
            ) -> None:
                """Handle session changes."""
                if event_type == "session_start":
                    logger.info(f"New session detected: {session_id}")
                elif event_type == "session_end":
                    logger.info(f"Session ended: {session_id}")

            orchestrator.register_session_callback(on_session_change)

            # Start monitoring
            orchestrator.start()

            # Wait for initial data
            logger.info("Waiting for initial data...")
            if not orchestrator.wait_for_initial_data(timeout=10.0):
                logger.warning("Timeout waiting for initial data")

            # Main loop - live display is already active
            # Use signal.pause() for more efficient waiting
            try:
                signal.pause()
            except AttributeError:
                # Fallback for Windows which doesn't support signal.pause()
                while True:
                    time.sleep(1)
        finally:
            # Stop monitoring first
            if "orchestrator" in locals():
                orchestrator.stop()

            # Exit live display context if it was activated
            if live_display_active:
                with contextlib.suppress(Exception):
                    live_display.__exit__(None, None, None)

    except KeyboardInterrupt:
        # Clean exit from live display if it's active
        if "live_display" in locals():
            with contextlib.suppress(Exception):
                live_display.__exit__(None, None, None)
        handle_cleanup_and_exit(old_terminal_settings)
    except Exception as e:
        # Clean exit from live display if it's active
        if "live_display" in locals():
            with contextlib.suppress(Exception):
                live_display.__exit__(None, None, None)
        handle_error_and_exit(old_terminal_settings, e)
    finally:
        restore_terminal(old_terminal_settings)


def _get_initial_token_limit(
    args: argparse.Namespace, adapter
) -> int:
    """Get initial token limit for the plan using adapter.

    Args:
        args: Command line arguments
        adapter: ToolAdapter instance for loading data

    Returns:
        Token limit for the plan
    """
    logger = logging.getLogger(__name__)
    plan: str = getattr(args, "plan", PlanType.PRO.value)

    # For custom plans, check if custom_limit_tokens is provided first
    if plan == "custom":
        # If custom_limit_tokens is explicitly set, use it
        if hasattr(args, "custom_limit_tokens") and args.custom_limit_tokens:
            custom_limit = int(args.custom_limit_tokens)
            print_themed(
                f"Using custom token limit: {custom_limit:,} tokens",
                style="info",
            )
            return custom_limit

        # Otherwise, analyze usage data to calculate P90
        print_themed("Analyzing usage data to determine cost limits...", style="info")

        try:
            # Use adapter to analyze usage data
            usage_data: Optional[Dict[str, Any]] = analyze_usage(
                hours_back=96 * 2,
                quick_start=False,
                use_cache=False,
                adapter=adapter,  # Use adapter instead of data_path
            )

            if usage_data and "blocks" in usage_data:
                blocks: List[Dict[str, Any]] = usage_data["blocks"]
                token_limit: int = get_token_limit(plan, blocks)

                print_themed(
                    f"P90 session limit calculated: {token_limit:,} tokens",
                    style="info",
                )

                return token_limit

        except Exception as e:
            logger.warning(f"Failed to analyze usage data: {e}")

        # Fallback to default limit
        print_themed("Using default limit as fallback", style="warning")
        return Plans.DEFAULT_TOKEN_LIMIT

    # For standard plans, just get the limit
    return get_token_limit(plan)


def handle_application_error(
    exception: Exception,
    component: str = "cli_main",
    exit_code: int = 1,
) -> NoReturn:
    """Handle application-level errors with proper logging and exit.

    Args:
        exception: The exception that occurred
        component: Component where the error occurred
        exit_code: Exit code to use when terminating
    """
    logger = logging.getLogger(__name__)

    # Log the error with traceback
    logger.error(f"Application error in {component}: {exception}", exc_info=True)

    # Report to error handling system
    from ai_usage_monitor.error_handling import report_application_startup_error

    report_application_startup_error(
        exception=exception,
        component=component,
        additional_context={
            "exit_code": exit_code,
            "args": sys.argv,
        },
    )

    # Print user-friendly error message
    print(f"\nError: {exception}", file=sys.stderr)
    print("For more details, check the log files.", file=sys.stderr)

    sys.exit(exit_code)


def validate_cli_environment() -> Optional[str]:
    """Validate the CLI environment and return error message if invalid.

    Returns:
        Error message if validation fails, None if successful
    """
    try:
        # Check Python version compatibility
        if sys.version_info < (3, 8):
            return f"Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}"

        # Check for required dependencies
        required_modules = ["rich", "pydantic", "watchdog"]
        missing_modules: List[str] = []

        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)

        if missing_modules:
            return f"Missing required modules: {', '.join(missing_modules)}"

        return None

    except Exception as e:
        return f"Environment validation failed: {e}"


def _run_multi_tool_table_view(
    args: argparse.Namespace, view_mode: str, console: Console
) -> None:
    """Run table view mode for all available tools (daily/monthly)."""
    logger = logging.getLogger(__name__)

    try:
        # Parse date range if provided
        from_date = None
        to_date = None
        if hasattr(args, "from_date") and args.from_date:
            from_date = datetime.strptime(args.from_date, "%Y-%m-%d")
            from_date = from_date.replace(tzinfo=timezone.utc)
        if hasattr(args, "to_date") and args.to_date:
            to_date = datetime.strptime(args.to_date, "%Y-%m-%d")
            to_date = to_date.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)

        # Load entries from all tools
        all_entries = load_entries_from_all_tools()
        if not all_entries:
            print_themed(f"No usage data found for {view_mode} view", style="warning")
            return

        # Create aggregator for processing (use a dummy path since we have entries)
        from ai_usage_monitor.data.aggregator import UsageAggregator
        from ai_usage_monitor.utils.time_utils import TimezoneHandler

        timezone_handler = TimezoneHandler()

        # Apply timezone to entries
        for entry in all_entries:
            if entry.timestamp.tzinfo is None:
                entry.timestamp = timezone_handler.ensure_timezone(entry.timestamp)

        # Create a temporary aggregator just for aggregation functions
        aggregator = UsageAggregator(
            data_path="",  # Not used since we have entries
            aggregation_mode=view_mode,
            timezone=args.timezone,
            from_date=from_date,
            to_date=to_date,
        )

        # Aggregate the entries
        if view_mode == "daily":
            aggregated_data = aggregator.aggregate_daily(all_entries, from_date, to_date)
        else:
            aggregated_data = aggregator.aggregate_monthly(all_entries, from_date, to_date)

        if not aggregated_data:
            print_themed(f"No usage data found for {view_mode} view", style="warning")
            return

        # Create table controller
        controller = TableViewsController(console=console)

        # Get a default data path for token limit calculation (use claude-code if available)
        default_data_path = None
        config = getattr(args, "config", None)
        claude_paths = discover_data_paths_for_tool("claude-code", config=config)
        if claude_paths:
            default_data_path = claude_paths[0]

        # Display the table
        controller.display_aggregated_view(
            data=aggregated_data,
            view_mode=view_mode,
            timezone=args.timezone,
            plan=args.plan,
            token_limit=_get_initial_token_limit(args, default_data_path) if default_data_path else 19000,
        )

    except Exception as e:
        logger.error(f"Error in multi-tool table view: {e}", exc_info=True)
        print_themed(f"Error displaying {view_mode} view: {e}", style="error")


def _run_table_view(
    args: argparse.Namespace, adapter, view_mode: str, console: Console
) -> None:
    """Run table view mode (daily/monthly) using adapter.

    Args:
        args: Command line arguments
        adapter: ToolAdapter instance for loading data
        view_mode: View mode ('daily' or 'monthly')
        console: Rich console instance
    """
    logger = logging.getLogger(__name__)

    try:
        # Parse date range if provided
        from_date = None
        to_date = None
        if hasattr(args, "from_date") and args.from_date:
            from_date = datetime.strptime(args.from_date, "%Y-%m-%d")
            from_date = from_date.replace(tzinfo=timezone.utc)
        if hasattr(args, "to_date") and args.to_date:
            to_date = datetime.strptime(args.to_date, "%Y-%m-%d")
            to_date = to_date.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)

        # Load entries via adapter
        logger.info(f"Loading {view_mode} usage data via adapter...")
        entries, _ = adapter.load_usage_entries()

        if not entries:
            print_themed(f"No usage data found for {view_mode} view", style="warning")
            return

        # Create aggregator with entries
        aggregator = UsageAggregator(
            data_path="",  # Not used when entries provided
            aggregation_mode=view_mode,
            timezone=args.timezone,
            from_date=from_date,
            to_date=to_date,
        )

        # Aggregate the loaded entries
        if view_mode == "daily":
            aggregated_data = aggregator.aggregate_daily(entries, from_date, to_date)
        else:
            aggregated_data = aggregator.aggregate_monthly(entries, from_date, to_date)

        if not aggregated_data:
            print_themed(f"No usage data found for {view_mode} view", style="warning")
            return

        # Create table controller
        controller = TableViewsController(console=console)

        # Display the table
        controller.display_aggregated_view(
            data=aggregated_data,
            view_mode=view_mode,
            timezone=args.timezone,
            plan=args.plan,
            token_limit=_get_initial_token_limit(args, adapter),
        )

    except Exception as e:
        logger.error(f"Error in table view: {e}", exc_info=True)
        print_themed(f"Error displaying {view_mode} view: {e}", style="error")


if __name__ == "__main__":
    sys.exit(main())
