"""Unified data management for monitoring - combines caching and fetching."""

import logging
import time
from typing import TYPE_CHECKING, Any, Dict, Optional

from ai_usage_monitor.data.analysis import analyze_usage
from ai_usage_monitor.error_handling import report_error

if TYPE_CHECKING:
    from ai_usage_monitor.adapters.base import ToolAdapter

logger = logging.getLogger(__name__)


class DataManager:
    """Manages data fetching and caching for monitoring."""

    def __init__(
        self,
        cache_ttl: int = 30,
        hours_back: int = 192,
        data_path: Optional[str] = None,
        adapter: Optional["ToolAdapter"] = None,
        use_incremental: bool = True,
    ) -> None:
        """Initialize data manager with cache and fetch settings.

        Args:
            cache_ttl: Cache time-to-live in seconds
            hours_back: Hours of historical data to fetch
            data_path: Path to data directory (legacy, use adapter instead)
            adapter: Optional ToolAdapter instance for loading data (recommended)
            use_incremental: Enable incremental loading for performance (legacy reader only)
        """
        self.cache_ttl: int = cache_ttl
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[float] = None

        self.hours_back: int = hours_back
        self.data_path: Optional[str] = data_path
        self.adapter: Optional["ToolAdapter"] = adapter
        self.use_incremental: bool = use_incremental
        self._file_tracker: Optional["FileStateTracker"] = None
        self._last_error: Optional[str] = None
        self._last_successful_fetch: Optional[float] = None

        # Initialize file tracker if incremental mode enabled
        if self.use_incremental and not self.adapter:
            from ai_usage_monitor.monitoring.file_tracker import FileStateTracker

            self._file_tracker = FileStateTracker()

    def get_data(self, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """Get monitoring data with caching and error handling.

        Args:
            force_refresh: Force refresh ignoring cache

        Returns:
            Usage data dictionary or None if fetch fails
        """
        from ai_usage_monitor.telemetry import get_logfire_manager

        lf = get_logfire_manager()

        if not force_refresh and self._is_cache_valid():
            cache_age: float = time.time() - self._cache_timestamp  # type: ignore
            logger.debug(f"Using cached data (age: {cache_age:.1f}s)")
            lf.log_metric("monitoring.cache_hit", 1, cache_age_seconds=cache_age)
            return self._cache

        lf.log_metric("monitoring.cache_miss", 1, force_refresh=force_refresh)

        # Check if we can use incremental loading (legacy reader only)
        if self._should_use_incremental():
            files_changed = self._check_files_changed()
            if not files_changed:
                logger.debug("No files changed, skipping data fetch (incremental)")
                return self._cache

            lf.log_metric("monitoring.incremental_refresh", 1, files_changed=True)

        max_retries: int = 3
        for attempt in range(max_retries):
            try:
                logger.debug(
                    f"Fetching fresh usage data (attempt {attempt + 1}/{max_retries})"
                )
                data: Optional[Dict[str, Any]] = analyze_usage(
                    hours_back=self.hours_back,
                    quick_start=False,
                    use_cache=False,
                    data_path=self.data_path,
                    adapter=self.adapter,  # Pass adapter if available
                )

                if data is not None:
                    self._set_cache(data)
                    self._last_successful_fetch = time.time()
                    self._last_error = None

                    # Update file tracker after successful fetch (for incremental mode)
                    if self._should_use_incremental():
                        self._update_file_tracker()

                    return data

                logger.warning("No data returned from analyze_usage")
                break

            except (FileNotFoundError, PermissionError, OSError) as e:
                logger.exception(f"Data access error (attempt {attempt + 1}): {e}")
                self._last_error = str(e)
                report_error(
                    exception=e, component="data_manager", context_name="access_error"
                )
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (2**attempt))
                    continue

            except (ValueError, TypeError, KeyError) as e:
                logger.exception(f"Data format error: {e}")
                self._last_error = str(e)
                report_error(
                    exception=e, component="data_manager", context_name="format_error"
                )
                break

            except Exception as e:
                logger.exception(f"Unexpected error (attempt {attempt + 1}): {e}")
                self._last_error = str(e)
                report_error(
                    exception=e,
                    component="data_manager",
                    context_name="unexpected_error",
                )
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (2**attempt))
                    continue
                break

        if self._is_cache_valid():
            logger.info("Using cached data due to fetch error")
            return self._cache

        logger.error("Failed to get usage data - no cache fallback available")
        return None

    def invalidate_cache(self) -> None:
        """Invalidate the cache."""
        self._cache = None
        self._cache_timestamp = None

        # Also clear file tracker on cache invalidation
        if self._file_tracker:
            self._file_tracker.clear()

        logger.debug("Cache invalidated")

    def _should_use_incremental(self) -> bool:
        """Check if incremental loading should be used.

        Returns:
            True if incremental mode is enabled and available
        """
        # Only use incremental for legacy reader (not adapters)
        return (
            self.use_incremental
            and self._file_tracker is not None
            and self.data_path is not None
            and self.adapter is None
        )

    def _check_files_changed(self) -> bool:
        """Check if any files have changed since last read.

        Returns:
            True if files have changed, False otherwise
        """
        if not self._file_tracker or not self.data_path:
            return True  # Default to changed if no tracker

        try:
            from pathlib import Path

            from ai_usage_monitor.data.reader import _find_jsonl_files

            data_path = Path(self.data_path).expanduser()
            jsonl_files = _find_jsonl_files(data_path)

            if not jsonl_files:
                logger.debug("No JSONL files found, skipping incremental check")
                return False

            # Get files that need to be read
            files_to_read = self._file_tracker.get_files_to_read(jsonl_files)

            # If there are files to read, files have changed
            files_changed = len(files_to_read) > 0

            if files_changed:
                logger.debug(
                    f"{len(files_to_read)} files changed (incremental check)"
                )
            else:
                logger.debug("No files changed (incremental check)")

            return files_changed

        except Exception as e:
            logger.warning(f"Error checking file changes: {e}")
            return True  # Default to changed on error

    def _update_file_tracker(self) -> None:
        """Update file tracker with current file states after successful read.

        This ensures the tracker stays synchronized with the actual file system
        state after a data fetch completes successfully.
        """
        if not self._file_tracker or not self.data_path:
            return

        try:
            from pathlib import Path

            from ai_usage_monitor.data.reader import _find_jsonl_files

            data_path = Path(self.data_path).expanduser()
            jsonl_files = _find_jsonl_files(data_path)

            if not jsonl_files:
                logger.debug("No JSONL files found, skipping file tracker update")
                return

            # Update tracker with current state of all files
            for file_path in jsonl_files:
                try:
                    # Get file size to use as "final offset" (entire file read)
                    file_size = file_path.stat().st_size
                    self._file_tracker.update_file_state(file_path, file_size)
                except (FileNotFoundError, PermissionError, OSError) as e:
                    logger.debug(f"Skipping file tracker update for {file_path}: {e}")
                    continue

            logger.debug(
                f"Updated file tracker for {len(jsonl_files)} files (incremental)"
            )

        except Exception as e:
            logger.warning(f"Error updating file tracker: {e}")
            # Non-critical error, don't fail the entire operation

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if self._cache is None or self._cache_timestamp is None:
            return False

        cache_age = time.time() - self._cache_timestamp
        return cache_age <= self.cache_ttl

    def _set_cache(self, data: Dict[str, Any]) -> None:
        """Set cache with current timestamp."""
        self._cache = data
        self._cache_timestamp = time.time()

    @property
    def cache_age(self) -> float:
        """Get age of cached data in seconds."""
        if self._cache_timestamp is None:
            return float("inf")
        return time.time() - self._cache_timestamp

    @property
    def last_error(self) -> Optional[str]:
        """Get last error message."""
        return self._last_error

    @property
    def last_successful_fetch_time(self) -> Optional[float]:
        """Get timestamp of last successful fetch."""
        return self._last_successful_fetch
