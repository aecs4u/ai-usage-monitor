"""Roo Code adapter for AI Usage Monitor.

Roo Code stores data in SQLite format within VS Code globalStorage.
"""

import logging
from datetime import datetime, timedelta
from datetime import timezone as tz
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ai_usage_monitor.adapters.base import ToolAdapter, ToolMetadata
from ai_usage_monitor.adapters.registry import AdapterRegistry
from ai_usage_monitor.core.models import UsageEntry

logger = logging.getLogger(__name__)


@AdapterRegistry.register
class RooCodeAdapter(ToolAdapter):
    """Adapter for Roo Code VS Code extension usage data.

    Roo Code stores data in SQLite format (state.vscdb) within
    VS Code's globalStorage directory.
    """

    @property
    def metadata(self) -> ToolMetadata:
        """Return metadata about Roo Code adapter."""
        return ToolMetadata(
            name="roo-code",
            display_name="Roo Code",
            data_format="sqlite",
            default_paths=[
                "~/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline",
                "~/.vscode/globalStorage/rooveterinaryinc.roo-cline",
                "~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline",
            ],
            supported_features=["tokens", "sessions", "models", "cost"],
            pricing_available=True,
            version="1.0.0",
            description="Roo Code VS Code extension usage tracking",
        )

    def discover_data_paths(
        self, custom_paths: Optional[List[str]] = None
    ) -> List[Path]:
        """Discover Roo Code data directories."""
        paths_to_check = (
            [str(p) for p in custom_paths]
            if custom_paths
            else self.metadata.default_paths
        )

        discovered = []
        for path_str in paths_to_check:
            path = Path(path_str).expanduser().resolve()
            if path.exists() and path.is_dir():
                # Check for state.vscdb file
                db_file = path / "state.vscdb"
                if db_file.exists():
                    discovered.append(path)

        return discovered

    def load_usage_entries(
        self,
        data_path: Optional[str] = None,
        hours_back: Optional[int] = None,
        include_raw: bool = False,
    ) -> Tuple[List[UsageEntry], Optional[List[Dict[str, Any]]]]:
        """Load usage entries from Roo Code SQLite database."""
        if data_path:
            paths = [Path(data_path).expanduser()]
        else:
            paths = self.discover_data_paths()

        if not paths:
            return [], None

        entries: List[UsageEntry] = []
        raw_entries: Optional[List[Dict[str, Any]]] = [] if include_raw else None

        cutoff_time = None
        if hours_back:
            cutoff_time = datetime.now(tz.utc) - timedelta(hours=hours_back)

        for base_path in paths:
            db_path = base_path / "state.vscdb"
            if db_path.exists():
                db_entries, db_raw = self._load_from_sqlite(
                    db_path, cutoff_time, include_raw
                )
                entries.extend(db_entries)
                if include_raw and db_raw:
                    raw_entries.extend(db_raw)

        entries.sort(key=lambda e: e.timestamp)
        return entries, raw_entries

    def _load_from_sqlite(
        self,
        db_path: Path,
        cutoff_time: Optional[datetime],
        include_raw: bool,
    ) -> Tuple[List[UsageEntry], Optional[List[Dict[str, Any]]]]:
        """Load entries from SQLite database."""
        entries: List[UsageEntry] = []
        raw_data: Optional[List[Dict[str, Any]]] = [] if include_raw else None

        try:
            import sqlite3
            import json

            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Query the ItemTable for task/usage data
            cursor.execute(
                "SELECT key, value FROM ItemTable WHERE key LIKE '%task%' OR key LIKE '%usage%'"
            )

            for row in cursor.fetchall():
                try:
                    key = row["key"]
                    value = row["value"]

                    if not value:
                        continue

                    data = json.loads(value)

                    # Handle different data formats
                    if isinstance(data, list):
                        for item in data:
                            entry = self._parse_entry(item, cutoff_time)
                            if entry:
                                entries.append(entry)
                            if include_raw:
                                raw_data.append(item)
                    elif isinstance(data, dict):
                        entry = self._parse_entry(data, cutoff_time)
                        if entry:
                            entries.append(entry)
                        if include_raw:
                            raw_data.append(data)

                except (json.JSONDecodeError, KeyError):
                    continue

            conn.close()

        except ImportError:
            logger.warning("sqlite3 not available for Roo Code adapter")
        except Exception as e:
            logger.warning(f"Failed to read Roo Code database {db_path}: {e}")

        return entries, raw_data

    def _parse_entry(
        self, data: Dict[str, Any], cutoff_time: Optional[datetime]
    ) -> Optional[UsageEntry]:
        """Parse a single data entry into UsageEntry."""
        try:
            # Look for API usage data
            api_usage = data.get("apiUsage", data.get("usage", {}))
            if not api_usage and "tokensIn" not in data and "inputTokens" not in data:
                return None

            # Parse timestamp
            timestamp_str = (
                data.get("timestamp")
                or data.get("ts")
                or data.get("createdAt")
            )
            if not timestamp_str:
                return None

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
                return None

            # Extract tokens
            input_tokens = (
                api_usage.get("inputTokens")
                or api_usage.get("tokensIn")
                or data.get("inputTokens")
                or data.get("tokensIn", 0)
            )
            output_tokens = (
                api_usage.get("outputTokens")
                or api_usage.get("tokensOut")
                or data.get("outputTokens")
                or data.get("tokensOut", 0)
            )
            cache_write = api_usage.get("cacheWriteTokens", 0)
            cache_read = api_usage.get("cacheReadTokens", 0)
            cost = api_usage.get("cost", data.get("cost", 0.0))

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
                tool_name="roo-code",
                session_id=data.get("taskId", ""),
            )

        except Exception as e:
            logger.debug(f"Failed to parse Roo Code entry: {e}")
            return None

    def calculate_cost(self, entry: UsageEntry) -> float:
        """Calculate cost for a Roo Code entry using Claude pricing."""
        from ai_usage_monitor.core.pricing import PricingCalculator

        calculator = PricingCalculator()
        return calculator.calculate_cost(
            model=entry.model,
            input_tokens=entry.input_tokens,
            output_tokens=entry.output_tokens,
            cache_creation_tokens=entry.cache_creation_tokens,
            cache_read_tokens=entry.cache_read_tokens,
        )
