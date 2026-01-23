"""Cline adapter for AI Usage Monitor.

Cline (formerly Claude Dev) stores conversation history in VS Code globalStorage
at ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/
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
class ClineAdapter(ToolAdapter):
    """Adapter for Cline (Claude Dev) VS Code extension usage data.

    Cline stores conversation history and task data in JSON format
    within VS Code's globalStorage directory.
    """

    @property
    def metadata(self) -> ToolMetadata:
        """Return metadata about Cline adapter."""
        return ToolMetadata(
            name="cline",
            display_name="Cline",
            data_format="json",
            default_paths=[
                "~/.config/Code/User/globalStorage/saoudrizwan.claude-dev",
                "~/.vscode/globalStorage/saoudrizwan.claude-dev",
                "~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev",
                "~/.config/Code - Insiders/User/globalStorage/saoudrizwan.claude-dev",
            ],
            supported_features=["tokens", "sessions", "models", "cost"],
            pricing_available=True,  # Uses Claude models with known pricing
            version="1.0.0",
            description="Cline (Claude Dev) VS Code extension usage tracking",
        )

    def discover_data_paths(
        self, custom_paths: Optional[List[str]] = None
    ) -> List[Path]:
        """Discover Cline data directories."""
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
        """Load usage entries from Cline data files."""
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
            # Look for task history and conversation files
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

            # Handle task history format
            if "taskHistory" in data:
                for task in data.get("taskHistory", []):
                    task_entries = self._parse_task(task, cutoff_time, processed_ids)
                    entries.extend(task_entries)
                    if include_raw:
                        raw_data.append(task)

            # Handle conversation history format
            elif "conversationHistory" in data or "messages" in data:
                conv_entries = self._parse_conversation(data, cutoff_time, processed_ids)
                entries.extend(conv_entries)
                if include_raw:
                    raw_data.append(data)

            # Handle API response log format
            elif "apiResponses" in data:
                for response in data.get("apiResponses", []):
                    entry = self._parse_api_response(response, cutoff_time, processed_ids)
                    if entry:
                        entries.append(entry)
                    if include_raw:
                        raw_data.append(response)

        except json.JSONDecodeError:
            logger.debug(f"Invalid JSON in {file_path}")
        except Exception as e:
            logger.debug(f"Failed to read Cline file {file_path}: {e}")

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
        api_usage = task.get("apiUsage", {})
        if not api_usage:
            return entries

        # Parse timestamp
        timestamp_str = task.get("timestamp") or task.get("createdAt")
        if not timestamp_str:
            return entries

        try:
            if isinstance(timestamp_str, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp_str / 1000, tz=tz.utc)
            else:
                timestamp = datetime.fromisoformat(
                    timestamp_str.replace("Z", "+00:00")
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
                        tool_name="cline",
                        session_id=task.get("sessionId", ""),
                    )
                )
                processed_ids.add(task_id)

        except Exception as e:
            logger.debug(f"Failed to parse Cline task: {e}")

        return entries

    def _parse_conversation(
        self,
        data: Dict[str, Any],
        cutoff_time: Optional[datetime],
        processed_ids: Set[str],
    ) -> List[UsageEntry]:
        """Parse conversation history into UsageEntry objects."""
        entries = []
        messages = data.get("conversationHistory", data.get("messages", []))

        for msg in messages:
            if msg.get("role") != "assistant":
                continue

            msg_id = msg.get("id", "")
            if msg_id in processed_ids:
                continue

            usage = msg.get("usage", {})
            if not usage:
                continue

            timestamp_str = msg.get("timestamp") or msg.get("createdAt")
            if not timestamp_str:
                continue

            try:
                if isinstance(timestamp_str, (int, float)):
                    timestamp = datetime.fromtimestamp(timestamp_str / 1000, tz=tz.utc)
                else:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )

                if cutoff_time and timestamp < cutoff_time:
                    continue

                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)

                if input_tokens or output_tokens:
                    entries.append(
                        UsageEntry(
                            timestamp=timestamp,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            model=msg.get("model", ""),
                            request_id=msg_id,
                            tool_name="cline",
                        )
                    )
                    if msg_id:
                        processed_ids.add(msg_id)

            except Exception as e:
                logger.debug(f"Failed to parse Cline message: {e}")

        return entries

    def _parse_api_response(
        self,
        response: Dict[str, Any],
        cutoff_time: Optional[datetime],
        processed_ids: Set[str],
    ) -> Optional[UsageEntry]:
        """Parse an API response entry."""
        response_id = response.get("id", "")
        if response_id in processed_ids:
            return None

        usage = response.get("usage", {})
        if not usage:
            return None

        timestamp_str = response.get("timestamp")
        if not timestamp_str:
            return None

        try:
            if isinstance(timestamp_str, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp_str / 1000, tz=tz.utc)
            else:
                timestamp = datetime.fromisoformat(
                    timestamp_str.replace("Z", "+00:00")
                )

            if cutoff_time and timestamp < cutoff_time:
                return None

            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)

            if not (input_tokens or output_tokens):
                return None

            if response_id:
                processed_ids.add(response_id)

            return UsageEntry(
                timestamp=timestamp,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=response.get("model", ""),
                request_id=response_id,
                tool_name="cline",
            )

        except Exception as e:
            logger.debug(f"Failed to parse Cline API response: {e}")
            return None

    def calculate_cost(self, entry: UsageEntry) -> float:
        """Calculate cost for a Cline entry using Claude pricing."""
        from ai_usage_monitor.core.pricing import PricingCalculator

        calculator = PricingCalculator()
        return calculator.calculate_cost(
            model=entry.model,
            input_tokens=entry.input_tokens,
            output_tokens=entry.output_tokens,
            cache_creation_tokens=entry.cache_creation_tokens,
            cache_read_tokens=entry.cache_read_tokens,
        )
