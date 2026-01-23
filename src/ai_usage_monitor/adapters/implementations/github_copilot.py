"""GitHub Copilot adapter for AI Usage Monitor.

GitHub Copilot stores usage data in SQLite format within VS Code workspaceStorage.
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
class GitHubCopilotAdapter(ToolAdapter):
    """Adapter for GitHub Copilot usage data.

    GitHub Copilot stores usage telemetry in SQLite format (state.vscdb)
    within VS Code's workspaceStorage directory.
    """

    @property
    def metadata(self) -> ToolMetadata:
        """Return metadata about GitHub Copilot adapter."""
        return ToolMetadata(
            name="github-copilot",
            display_name="GitHub Copilot",
            data_format="sqlite",
            default_paths=[
                "~/.config/Code/User/workspaceStorage",
                "~/.vscode/workspaceStorage",
                "~/Library/Application Support/Code/User/workspaceStorage",
                "~/.config/Code/User/globalStorage/github.copilot",
                "~/.config/Code/User/globalStorage/github.copilot-chat",
            ],
            supported_features=["tokens", "sessions", "models"],
            pricing_available=False,  # Copilot uses subscription pricing
            version="1.0.0",
            description="GitHub Copilot usage tracking",
        )

    def discover_data_paths(
        self, custom_paths: Optional[List[str]] = None
    ) -> List[Path]:
        """Discover GitHub Copilot data directories."""
        paths_to_check = (
            [str(p) for p in custom_paths]
            if custom_paths
            else self.metadata.default_paths
        )

        discovered = []
        for path_str in paths_to_check:
            path = Path(path_str).expanduser().resolve()
            if path.exists() and path.is_dir():
                # Check for Copilot-related files
                if "copilot" in path_str.lower():
                    discovered.append(path)
                else:
                    # Search for Copilot data in workspace storage
                    for subdir in path.iterdir():
                        if subdir.is_dir():
                            state_file = subdir / "state.vscdb"
                            if state_file.exists():
                                discovered.append(subdir)
                                break

        return discovered

    def load_usage_entries(
        self,
        data_path: Optional[str] = None,
        hours_back: Optional[int] = None,
        include_raw: bool = False,
    ) -> Tuple[List[UsageEntry], Optional[List[Dict[str, Any]]]]:
        """Load usage entries from GitHub Copilot data."""
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
            # Check for SQLite database
            for db_file in base_path.rglob("state.vscdb"):
                db_entries, db_raw = self._load_from_sqlite(
                    db_file, cutoff_time, include_raw
                )
                entries.extend(db_entries)
                if include_raw and db_raw:
                    raw_entries.extend(db_raw)

            # Also check for JSON telemetry files
            for json_file in base_path.rglob("*.json"):
                if "telemetry" in json_file.name.lower() or "usage" in json_file.name.lower():
                    json_entries, json_raw = self._load_from_json(
                        json_file, cutoff_time, include_raw
                    )
                    entries.extend(json_entries)
                    if include_raw and json_raw:
                        raw_entries.extend(json_raw)

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

            # Query for Copilot-related data
            cursor.execute(
                "SELECT key, value FROM ItemTable WHERE key LIKE '%copilot%' OR key LIKE '%completion%'"
            )

            for row in cursor.fetchall():
                try:
                    value = row["value"]
                    if not value:
                        continue

                    data = json.loads(value)

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
            logger.warning("sqlite3 not available for GitHub Copilot adapter")
        except Exception as e:
            logger.debug(f"Failed to read Copilot database {db_path}: {e}")

        return entries, raw_data

    def _load_from_json(
        self,
        json_path: Path,
        cutoff_time: Optional[datetime],
        include_raw: bool,
    ) -> Tuple[List[UsageEntry], Optional[List[Dict[str, Any]]]]:
        """Load entries from JSON telemetry file."""
        import json

        entries: List[UsageEntry] = []
        raw_data: Optional[List[Dict[str, Any]]] = [] if include_raw else None

        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)

            items = data if isinstance(data, list) else [data]

            for item in items:
                entry = self._parse_entry(item, cutoff_time)
                if entry:
                    entries.append(entry)
                if include_raw:
                    raw_data.append(item)

        except Exception as e:
            logger.debug(f"Failed to read Copilot JSON {json_path}: {e}")

        return entries, raw_data

    def _parse_entry(
        self, data: Dict[str, Any], cutoff_time: Optional[datetime]
    ) -> Optional[UsageEntry]:
        """Parse a single data entry into UsageEntry."""
        try:
            # Parse timestamp
            timestamp_str = (
                data.get("timestamp")
                or data.get("time")
                or data.get("created")
            )
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

            # Extract tokens (Copilot may track completions differently)
            usage = data.get("usage", {})
            input_tokens = (
                usage.get("prompt_tokens")
                or usage.get("input_tokens")
                or data.get("promptTokens", 0)
            )
            output_tokens = (
                usage.get("completion_tokens")
                or usage.get("output_tokens")
                or data.get("completionTokens", 0)
            )

            # Copilot might track by completions instead of tokens
            if not (input_tokens or output_tokens):
                completions = data.get("completions", 0)
                if completions:
                    # Estimate tokens based on completions
                    output_tokens = completions * 50  # Rough estimate

            if not (input_tokens or output_tokens):
                return None

            return UsageEntry(
                timestamp=timestamp,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=data.get("model", "copilot"),
                request_id=data.get("id", ""),
                tool_name="github-copilot",
                session_id=data.get("sessionId", ""),
            )

        except Exception as e:
            logger.debug(f"Failed to parse Copilot entry: {e}")
            return None

    def calculate_cost(self, entry: UsageEntry) -> float:
        """Calculate cost for a GitHub Copilot entry.

        Note: Copilot uses subscription pricing, not per-token pricing.
        Returns 0 as cost tracking is not applicable.
        """
        return 0.0
