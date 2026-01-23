"""Simplified data reader for Claude Monitor.

Combines functionality from file_reader, filter, mapper, and processor
into a single cohesive module.
"""

import json
import logging
from datetime import datetime, timedelta
from datetime import timezone as tz
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ai_usage_monitor.core.data_processors import (
    DataConverter,
    TimestampProcessor,
    TokenExtractor,
)
from ai_usage_monitor.core.models import CostMode, UsageEntry
from ai_usage_monitor.core.pricing import PricingCalculator
from ai_usage_monitor.error_handling import report_file_error
from ai_usage_monitor.utils.time_utils import TimezoneHandler

FIELD_COST_USD = "cost_usd"
FIELD_MODEL = "model"
TOKEN_INPUT = "input_tokens"
TOKEN_OUTPUT = "output_tokens"

logger = logging.getLogger(__name__)


def load_usage_entries(
    data_path: Optional[str] = None,
    hours_back: Optional[int] = None,
    mode: CostMode = CostMode.AUTO,
    include_raw: bool = False,
    timezone: Optional[str] = None,
) -> Tuple[List[UsageEntry], Optional[List[Dict[str, Any]]]]:
    """Load and convert JSONL files to UsageEntry objects.

    .. deprecated:: 4.1.0
        Use ToolAdapter.load_usage_entries() instead.
        This function will be removed in v5.0.0.

    Args:
        data_path: Path to Claude data directory (defaults to ~/.claude/projects)
        hours_back: Only include entries from last N hours
        mode: Cost calculation mode
        include_raw: Whether to return raw JSON data alongside entries
        timezone: Optional timezone for timestamp normalization (defaults to UTC)

    Returns:
        Tuple of (usage_entries, raw_data) where raw_data is None unless include_raw=True
    """
    import warnings

    warnings.warn(
        "load_usage_entries() is deprecated and will be removed in v5.0.0. "
        "Use ToolAdapter.load_usage_entries() instead for multi-tool support.",
        DeprecationWarning,
        stacklevel=2,
    )

    data_path = Path(data_path if data_path else "~/.claude/projects").expanduser()
    timezone_handler = TimezoneHandler(default_tz=timezone or "UTC")
    pricing_calculator = PricingCalculator()

    cutoff_time = None
    if hours_back:
        cutoff_time = datetime.now(tz.utc) - timedelta(hours=hours_back)

    jsonl_files = _find_jsonl_files(data_path)
    if not jsonl_files:
        logger.warning("No JSONL files found in %s", data_path)
        return [], None

    all_entries: List[UsageEntry] = []
    raw_entries: Optional[List[Dict[str, Any]]] = [] if include_raw else None
    processed_hashes: Set[str] = set()

    for file_path in jsonl_files:
        entries, raw_data = _process_single_file(
            file_path,
            mode,
            cutoff_time,
            processed_hashes,
            include_raw,
            timezone_handler,
            pricing_calculator,
        )
        all_entries.extend(entries)
        if include_raw and raw_data:
            raw_entries.extend(raw_data)

    all_entries.sort(key=lambda e: e.timestamp)

    logger.info(f"Processed {len(all_entries)} entries from {len(jsonl_files)} files")

    return all_entries, raw_entries


def load_usage_entries_incremental(
    data_path: Optional[str] = None,
    file_tracker: Optional["FileStateTracker"] = None,
    hours_back: Optional[int] = None,
    mode: CostMode = CostMode.AUTO,
    timezone: Optional[str] = None,
) -> Tuple[List[UsageEntry], Optional["FileStateTracker"]]:
    """Load usage entries incrementally using file state tracking.

    This function only reads new or modified files since the last read,
    significantly improving performance during monitoring refreshes.

    Args:
        data_path: Path to data directory (defaults to ~/.claude/projects)
        file_tracker: Optional FileStateTracker for incremental loading
        hours_back: Only include entries from last N hours
        mode: Cost calculation mode
        timezone: Optional timezone for timestamp normalization

    Returns:
        Tuple of (new_entries, updated_file_tracker)
    """
    from ai_usage_monitor.monitoring.file_tracker import FileStateTracker

    data_path = Path(data_path if data_path else "~/.claude/projects").expanduser()
    timezone_handler = TimezoneHandler(default_tz=timezone or "UTC")
    pricing_calculator = PricingCalculator()

    cutoff_time = None
    if hours_back:
        cutoff_time = datetime.now(tz.utc) - timedelta(hours=hours_back)

    # Initialize or use provided tracker
    if file_tracker is None:
        file_tracker = FileStateTracker()

    jsonl_files = _find_jsonl_files(data_path)
    if not jsonl_files:
        logger.debug("No JSONL files found in %s", data_path)
        return [], file_tracker

    # Get list of files that need to be read
    files_to_read = file_tracker.get_files_to_read(jsonl_files)

    if not files_to_read:
        logger.debug("No changed files detected (incremental)")
        return [], file_tracker

    new_entries: List[UsageEntry] = []
    processed_hashes: Set[str] = set()

    logger.debug(f"Reading {len(files_to_read)} changed/new files incrementally")

    for file_path, start_offset in files_to_read:
        entries, final_offset = _read_file_from_offset(
            file_path,
            start_offset,
            mode,
            cutoff_time,
            processed_hashes,
            timezone_handler,
            pricing_calculator,
        )
        new_entries.extend(entries)

        # Update tracker with final offset
        file_tracker.update_file_state(file_path, final_offset)

    new_entries.sort(key=lambda e: e.timestamp)

    logger.info(
        f"Loaded {len(new_entries)} new entries from "
        f"{len(files_to_read)} changed files (incremental)"
    )

    return new_entries, file_tracker


def load_all_raw_entries(data_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load all raw JSONL entries without processing.

    .. deprecated:: 4.1.0
        Use ToolAdapter.load_usage_entries(include_raw=True) instead.
        This function will be removed in v5.0.0.

    Args:
        data_path: Path to Claude data directory

    Returns:
        List of raw JSON dictionaries
    """
    import warnings

    warnings.warn(
        "load_all_raw_entries() is deprecated and will be removed in v5.0.0. "
        "Use ToolAdapter.load_usage_entries(include_raw=True) instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    data_path = Path(data_path if data_path else "~/.claude/projects").expanduser()
    jsonl_files = _find_jsonl_files(data_path)

    all_raw_entries: List[Dict[str, Any]] = []
    for file_path in jsonl_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        all_raw_entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.exception(f"Error loading raw entries from {file_path}: {e}")

    return all_raw_entries


def _find_jsonl_files(data_path: Path) -> List[Path]:
    """Find all .jsonl files in the data directory."""
    if not data_path.exists():
        logger.warning("Data path does not exist: %s", data_path)
        return []
    return list(data_path.rglob("*.jsonl"))


def _process_single_file(
    file_path: Path,
    mode: CostMode,
    cutoff_time: Optional[datetime],
    processed_hashes: Set[str],
    include_raw: bool,
    timezone_handler: TimezoneHandler,
    pricing_calculator: PricingCalculator,
) -> Tuple[List[UsageEntry], Optional[List[Dict[str, Any]]]]:
    """Process a single JSONL file."""
    entries: List[UsageEntry] = []
    raw_data: Optional[List[Dict[str, Any]]] = [] if include_raw else None

    try:
        entries_read = 0
        entries_filtered = 0
        entries_mapped = 0

        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    entries_read += 1

                    if not _should_process_entry(
                        data, cutoff_time, processed_hashes, timezone_handler
                    ):
                        entries_filtered += 1
                        continue

                    entry = _map_to_usage_entry(
                        data, mode, timezone_handler, pricing_calculator
                    )
                    if entry:
                        entries_mapped += 1
                        entries.append(entry)
                        _update_processed_hashes(data, processed_hashes)

                    if include_raw:
                        raw_data.append(data)

                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse JSON line in {file_path}: {e}")
                    continue

        logger.debug(
            f"File {file_path.name}: {entries_read} read, "
            f"{entries_filtered} filtered out, {entries_mapped} successfully mapped"
        )

    except Exception as e:
        logger.warning("Failed to read file %s: %s", file_path, e)
        report_file_error(
            exception=e,
            file_path=str(file_path),
            operation="read",
            additional_context={"file_exists": file_path.exists()},
        )
        return [], None

    return entries, raw_data


def _read_file_from_offset(
    file_path: Path,
    start_offset: int,
    mode: CostMode,
    cutoff_time: Optional[datetime],
    processed_hashes: Set[str],
    timezone_handler: TimezoneHandler,
    pricing_calculator: PricingCalculator,
) -> Tuple[List[UsageEntry], int]:
    """Read JSONL file from a specific byte offset.

    Args:
        file_path: Path to the JSONL file
        start_offset: Byte offset to start reading from (0 for beginning)
        mode: Cost calculation mode
        cutoff_time: Optional cutoff time for filtering entries
        processed_hashes: Set of already processed entry hashes
        timezone_handler: Timezone handler for timestamp normalization
        pricing_calculator: Pricing calculator for cost calculation

    Returns:
        Tuple of (entries, final_offset) where final_offset is the byte
        position after reading all lines
    """
    entries: List[UsageEntry] = []
    final_offset = start_offset

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # Seek to the start offset
            f.seek(start_offset)

            # Read lines from this offset
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)

                    if not _should_process_entry(
                        data, cutoff_time, processed_hashes, timezone_handler
                    ):
                        continue

                    entry = _map_to_usage_entry(
                        data, mode, timezone_handler, pricing_calculator
                    )
                    if entry:
                        entries.append(entry)
                        _update_processed_hashes(data, processed_hashes)

                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse JSON line in {file_path}: {e}")
                    continue

            # Get final position
            final_offset = f.tell()

        if entries:
            logger.debug(
                f"Read {len(entries)} entries from {file_path.name} "
                f"(offset {start_offset} -> {final_offset})"
            )

    except (FileNotFoundError, PermissionError) as e:
        logger.warning(f"Cannot read file {file_path}: {e}")
        report_file_error(
            exception=e,
            file_path=str(file_path),
            operation="incremental_read",
        )
    except Exception as e:
        logger.exception(f"Unexpected error reading {file_path} from offset: {e}")
        report_file_error(
            exception=e,
            file_path=str(file_path),
            operation="incremental_read",
        )

    return entries, final_offset


def _should_process_entry(
    data: Dict[str, Any],
    cutoff_time: Optional[datetime],
    processed_hashes: Set[str],
    timezone_handler: TimezoneHandler,
) -> bool:
    """Check if entry should be processed based on time and uniqueness."""
    if cutoff_time:
        timestamp_str = data.get("timestamp")
        if timestamp_str:
            processor = TimestampProcessor(timezone_handler)
            timestamp = processor.parse_timestamp(timestamp_str)
            if timestamp and timestamp < cutoff_time:
                return False

    unique_hash = _create_unique_hash(data)
    return not (unique_hash and unique_hash in processed_hashes)


def _create_unique_hash(data: Dict[str, Any]) -> Optional[str]:
    """Create unique hash for deduplication."""
    message_id = data.get("message_id") or (
        data.get("message", {}).get("id")
        if isinstance(data.get("message"), dict)
        else None
    )
    request_id = data.get("requestId") or data.get("request_id")

    return f"{message_id}:{request_id}" if message_id and request_id else None


def _update_processed_hashes(data: Dict[str, Any], processed_hashes: Set[str]) -> None:
    """Update the processed hashes set with current entry's hash."""
    unique_hash = _create_unique_hash(data)
    if unique_hash:
        processed_hashes.add(unique_hash)


def _map_to_usage_entry(
    data: Dict[str, Any],
    mode: CostMode,
    timezone_handler: TimezoneHandler,
    pricing_calculator: PricingCalculator,
) -> Optional[UsageEntry]:
    """Map raw data to UsageEntry with proper cost calculation."""
    try:
        timestamp_processor = TimestampProcessor(timezone_handler)
        timestamp = timestamp_processor.parse_timestamp(data.get("timestamp", ""))
        if not timestamp:
            return None

        token_data = TokenExtractor.extract_tokens(data)
        if not any(v for k, v in token_data.items() if k != "total_tokens"):
            return None

        model = DataConverter.extract_model_name(data, default="unknown")

        entry_data: Dict[str, Any] = {
            FIELD_MODEL: model,
            TOKEN_INPUT: token_data["input_tokens"],
            TOKEN_OUTPUT: token_data["output_tokens"],
            "cache_creation_tokens": token_data.get("cache_creation_tokens", 0),
            "cache_read_tokens": token_data.get("cache_read_tokens", 0),
            FIELD_COST_USD: data.get("cost") or data.get(FIELD_COST_USD),
        }
        cost_usd = pricing_calculator.calculate_cost_for_entry(entry_data, mode)

        message = data.get("message", {})
        message_id = data.get("message_id") or message.get("id") or ""
        request_id = data.get("request_id") or data.get("requestId") or "unknown"

        return UsageEntry(
            timestamp=timestamp,
            input_tokens=token_data["input_tokens"],
            output_tokens=token_data["output_tokens"],
            cache_creation_tokens=token_data.get("cache_creation_tokens", 0),
            cache_read_tokens=token_data.get("cache_read_tokens", 0),
            cost_usd=cost_usd,
            model=model,
            message_id=message_id,
            request_id=request_id,
        )

    except (KeyError, ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Failed to map entry: {type(e).__name__}: {e}")
        return None


class UsageEntryMapper:
    """Compatibility wrapper for legacy UsageEntryMapper interface.

    This class provides backward compatibility for tests that expect
    the old UsageEntryMapper interface, wrapping the new functional
    approach in _map_to_usage_entry.
    """

    def __init__(
        self, pricing_calculator: PricingCalculator, timezone_handler: TimezoneHandler
    ):
        """Initialize with required components."""
        self.pricing_calculator = pricing_calculator
        self.timezone_handler = timezone_handler

    def map(self, data: Dict[str, Any], mode: CostMode) -> Optional[UsageEntry]:
        """Map raw data to UsageEntry - compatibility interface."""
        return _map_to_usage_entry(
            data, mode, self.timezone_handler, self.pricing_calculator
        )

    def _has_valid_tokens(self, tokens: Dict[str, int]) -> bool:
        """Check if tokens are valid (for test compatibility)."""
        return any(v > 0 for v in tokens.values())

    def _extract_timestamp(self, data: Dict[str, Any]) -> Optional[datetime]:
        """Extract timestamp (for test compatibility)."""
        if "timestamp" not in data:
            return None
        processor = TimestampProcessor(self.timezone_handler)
        return processor.parse_timestamp(data["timestamp"])

    def _extract_model(self, data: Dict[str, Any]) -> str:
        """Extract model name (for test compatibility)."""
        return DataConverter.extract_model_name(data, default="unknown")

    def _extract_metadata(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Extract metadata (for test compatibility)."""
        message = data.get("message", {})
        return {
            "message_id": data.get("message_id") or message.get("id", ""),
            "request_id": data.get("request_id") or data.get("requestId", "unknown"),
        }
