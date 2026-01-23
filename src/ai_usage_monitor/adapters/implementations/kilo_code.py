"""Kilo Code adapter for AI Usage Monitor.

Kilo Code stores task history in JSON format within VS Code globalStorage.
"""

import json
import logging
from datetime import datetime, timedelta
from datetime import timezone as tz
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ai_usage_monitor.adapters.base import ToolAdapter, ToolMetadata
from ai_usage_monitor.adapters.registry import AdapterRegistry
from ai_usage_monitor.core.models import UsageEntry

logger = logging.getLogger(__name__)


@AdapterRegistry.register
class KiloCodeAdapter(ToolAdapter):
    """Adapter for Kilo Code VS Code extension usage data.

    Kilo Code stores task history in JSON format within
    VS Code's globalStorage directory.
    """

    @property
    def metadata(self) -> ToolMetadata:
        """Return metadata about Kilo Code adapter."""
        return ToolMetadata(
            name="kilo-code",
            display_name="Kilo Code",
            data_format="json",
            default_paths=[
                "~/.vscode/globalStorage/kilocode.kilo-code",
                "~/.config/Code/User/globalStorage/kilocode.kilo-code",
                "~/Library/Application Support/Code/User/globalStorage/kilocode.kilo-code",
            ],
            supported_features=["tokens", "sessions", "models", "cost"],
            pricing_available=True,
            version="1.0.0",
            description="Kilo Code VS Code extension usage tracking",
        )

    def discover_data_paths(
        self, custom_paths: Optional[List[str]] = None
    ) -> List[Path]:
        """Discover Kilo Code data directories."""
        paths_to_check = (
            [str(p) for p in custom_paths]
            if custom_paths
            else self.metadata.default_paths
        )

        discovered = []
        for path_str in paths_to_check:
            path = Path(path_str).expanduser().resolve()
            if path.exists() and path.is_dir():
                discovered.append(path)

        return discovered

    def load_usage_entries(
        self,
        data_path: Optional[str] = None,
        hours_back: Optional[int] = None,
        include_raw: bool = False,
    ) -> Tuple[List[UsageEntry], Optional[List[Dict[str, Any]]]]:
        """Load usage entries from Kilo Code data files."""
        if data_path:
            paths = [Path(data_path).expanduser()]
        else:
            paths = self.discover_data_paths()

        if not paths:
            return [], None

        cutoff_time = None
        if hours_back:
            cutoff_time = datetime.now(tz.utc) - timedelta(hours=hours_back)

        entries: List[UsageEntry] = []
        raw_entries: Optional[List[Dict[str, Any]]] = [] if include_raw else None
        processed_ids: Set[str] = set()

        for base_path in paths:
            # Look for task_history.json or similar files
            for json_file in base_path.rglob("*.json"):
                file_entries, file_raw = self._process_file(
                    json_file, cutoff_time, processed_ids, include_raw
                )
                entries.extend(file_entries)
                if include_raw and file_raw:
                    raw_entries.extend(file_raw)

        entries.sort(key=lambda e: e.timestamp)
        return entries, raw_entries

    def _process_file(
        self,
        file_path: Path,
        cutoff_time: Optional[datetime],
        processed_ids: Set[str],
        include_raw: bool,
    ) -> Tuple[List[UsageEntry], Optional[List[Dict[str, Any]]]]:
        """Process a single JSON file."""
        entries: List[UsageEntry] = []
        raw_data: Optional[List[Dict[str, Any]]] = [] if include_raw else None

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Handle task_history format
            if "taskHistory" in data or "task_history" in data:
                tasks = data.get("taskHistory", data.get("task_history", []))
                for task in tasks:
                    task_entries = self._parse_task(task, cutoff_time, processed_ids)
                    entries.extend(task_entries)
                    if include_raw:
                        raw_data.append(task)

            # Handle array of entries
            elif isinstance(data, list):
                for item in data:
                    entry_id = item.get("id", "")
                    if entry_id and entry_id in processed_ids:
                        continue

                    entry = self._parse_entry(item, cutoff_time)
                    if entry:
                        entries.append(entry)
                        if entry_id:
                            processed_ids.add(entry_id)

                    if include_raw:
                        raw_data.append(item)

            # Handle single entry
            elif isinstance(data, dict):
                entry = self._parse_entry(data, cutoff_time)
                if entry:
                    entries.append(entry)
                if include_raw:
                    raw_data.append(data)

        except json.JSONDecodeError:
            logger.debug(f"Invalid JSON in {file_path}")
        except Exception as e:
            logger.debug(f"Failed to read Kilo Code file {file_path}: {e}")

        return entries, raw_data

    def _parse_task(
        self,
        task: Dict[str, Any],
        cutoff_time: Optional[datetime],
        processed_ids: Set[str],
    ) -> List[UsageEntry]:
        """Parse a task entry into UsageEntry objects."""
        entries = []

        task_id = task.get("id", "")
        if task_id in processed_ids:
            return entries

        # Extract API usage from task
        api_usage = task.get("apiUsage", task.get("usage", {}))
        if not api_usage:
            return entries

        # Parse timestamp
        timestamp_str = task.get("timestamp") or task.get("createdAt")
        if not timestamp_str:
            return entries

        try:
            if isinstance(timestamp_str, (int, float)):
                # Handle milliseconds
                if timestamp_str > 1e12:
                    timestamp_str = timestamp_str / 1000
                timestamp = datetime.fromtimestamp(timestamp_str, tz=tz.utc)
            else:
                timestamp = datetime.fromisoformat(
                    str(timestamp_str).replace("Z", "+00:00")
                )

            if cutoff_time and timestamp < cutoff_time:
                return entries

            input_tokens = api_usage.get("inputTokens", 0)
            output_tokens = api_usage.get("outputTokens", 0)
            cache_write = api_usage.get("cacheWriteTokens", 0)
            cache_read = api_usage.get("cacheReadTokens", 0)
            cost = api_usage.get("cost", 0.0)

            if input_tokens or output_tokens:
                entries.append(
                    UsageEntry(
                        timestamp=timestamp,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        cache_creation_tokens=cache_write,
                        cache_read_tokens=cache_read,
                        cost_usd=cost,
                        model=task.get("model", ""),
                        request_id=task_id,
                        tool_name="kilo-code",
                        session_id=task.get("sessionId", ""),
                    )
                )
                processed_ids.add(task_id)

        except Exception as e:
            logger.debug(f"Failed to parse Kilo Code task: {e}")

        return entries

    def _parse_entry(
        self, data: Dict[str, Any], cutoff_time: Optional[datetime]
    ) -> Optional[UsageEntry]:
        """Parse a single data entry into UsageEntry."""
        try:
            # Parse timestamp
            timestamp_str = data.get("timestamp") or data.get("createdAt")
            if not timestamp_str:
                return None

            if isinstance(timestamp_str, (int, float)):
                if timestamp_str > 1e12:
                    timestamp_str = timestamp_str / 1000
                timestamp = datetime.fromtimestamp(timestamp_str, tz=tz.utc)
            else:
                timestamp = datetime.fromisoformat(
                    str(timestamp_str).replace("Z", "+00:00")
                )

            if cutoff_time and timestamp < cutoff_time:
                return None

            # Extract tokens
            usage = data.get("usage", data.get("apiUsage", {}))
            input_tokens = (
                usage.get("inputTokens")
                or usage.get("input_tokens")
                or data.get("inputTokens", 0)
            )
            output_tokens = (
                usage.get("outputTokens")
                or usage.get("output_tokens")
                or data.get("outputTokens", 0)
            )
            cache_write = usage.get("cacheWriteTokens", 0)
            cache_read = usage.get("cacheReadTokens", 0)
            cost = usage.get("cost", data.get("cost", 0.0))

            if not (input_tokens or output_tokens):
                return None

            return UsageEntry(
                timestamp=timestamp,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_creation_tokens=cache_write,
                cache_read_tokens=cache_read,
                cost_usd=cost,
                model=data.get("model", ""),
                request_id=data.get("id", ""),
                tool_name="kilo-code",
                session_id=data.get("sessionId", ""),
            )

        except Exception as e:
            logger.debug(f"Failed to parse Kilo Code entry: {e}")
            return None

    def calculate_cost(self, entry: UsageEntry) -> float:
        """Calculate cost for a Kilo Code entry using Claude pricing."""
        from ai_usage_monitor.core.pricing import PricingCalculator

        calculator = PricingCalculator()
        return calculator.calculate_cost(
            model=entry.model,
            input_tokens=entry.input_tokens,
            output_tokens=entry.output_tokens,
            cache_creation_tokens=entry.cache_creation_tokens,
            cache_read_tokens=entry.cache_read_tokens,
        )
