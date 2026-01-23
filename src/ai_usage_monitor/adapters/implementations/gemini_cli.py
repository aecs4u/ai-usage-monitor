"""Gemini CLI adapter for AI Usage Monitor.

Gemini CLI stores session data in JSON format at ~/.gemini/
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
class GeminiCLIAdapter(ToolAdapter):
    """Adapter for Google Gemini CLI usage data.

    Gemini CLI stores session data in JSON format with fields:
    - tool_name, success, duration
    - prompt_tokens, completion_tokens
    """

    @property
    def metadata(self) -> ToolMetadata:
        """Return metadata about Gemini CLI adapter."""
        return ToolMetadata(
            name="gemini-cli",
            display_name="Gemini CLI",
            data_format="json",
            default_paths=["~/.gemini", "~/.config/gemini"],
            supported_features=["tokens", "sessions", "models"],
            pricing_available=False,
            version="1.0.0",
            description="Google Gemini CLI usage tracking",
        )

    def discover_data_paths(
        self, custom_paths: Optional[List[str]] = None
    ) -> List[Path]:
        """Discover Gemini CLI data directories."""
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
        """Load usage entries from Gemini CLI data files."""
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
            # Look for JSON files in sessions directory
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

            # Handle both single object and array formats
            items = data if isinstance(data, list) else [data]

            for item in items:
                entry_id = item.get("id") or item.get("request_id", "")
                if entry_id and entry_id in processed_ids:
                    continue

                entry = self._parse_entry(item, cutoff_time)
                if entry:
                    entries.append(entry)
                    if entry_id:
                        processed_ids.add(entry_id)

                if include_raw:
                    raw_data.append(item)

        except json.JSONDecodeError:
            logger.debug(f"Invalid JSON in {file_path}")
        except Exception as e:
            logger.warning(f"Failed to read Gemini file {file_path}: {e}")

        return entries, raw_data

    def _parse_entry(
        self, data: Dict[str, Any], cutoff_time: Optional[datetime]
    ) -> Optional[UsageEntry]:
        """Parse a single data entry into UsageEntry."""
        try:
            # Parse timestamp
            timestamp_str = data.get("timestamp") or data.get("created_at")
            if not timestamp_str:
                return None

            if isinstance(timestamp_str, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp_str, tz=tz.utc)
            else:
                timestamp = datetime.fromisoformat(
                    timestamp_str.replace("Z", "+00:00")
                )

            if cutoff_time and timestamp < cutoff_time:
                return None

            # Extract tokens from usage metadata
            usage = data.get("usage_metadata", data.get("usage", {}))
            input_tokens = (
                usage.get("prompt_token_count")
                or usage.get("prompt_tokens")
                or usage.get("input_tokens", 0)
            )
            output_tokens = (
                usage.get("candidates_token_count")
                or usage.get("completion_tokens")
                or usage.get("output_tokens", 0)
            )
            cached_tokens = usage.get("cached_content_token_count", 0)

            if not (input_tokens or output_tokens):
                return None

            return UsageEntry(
                timestamp=timestamp,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_read_tokens=cached_tokens,
                model=data.get("model", "gemini"),
                request_id=data.get("id") or data.get("request_id", ""),
                tool_name="gemini-cli",
                session_id=data.get("session_id", ""),
                duration_seconds=data.get("duration", 0.0),
                success=data.get("success", True),
            )

        except Exception as e:
            logger.debug(f"Failed to parse Gemini entry: {e}")
            return None

    def calculate_cost(self, entry: UsageEntry) -> float:
        """Calculate cost for a Gemini entry.

        Note: Google pricing varies by model. Returns 0 as we don't
        have definitive pricing for all Gemini models.
        """
        return 0.0
