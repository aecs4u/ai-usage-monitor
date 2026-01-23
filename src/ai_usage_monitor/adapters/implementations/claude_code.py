"""Claude Code adapter for AI Usage Monitor.

This adapter reads usage data from Claude Code's JSONL files stored in
~/.claude/projects/ or ~/.config/claude/projects/.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ai_usage_monitor.adapters.base import ToolAdapter, ToolMetadata
from ai_usage_monitor.adapters.registry import AdapterRegistry
from ai_usage_monitor.core.models import CostMode, UsageEntry
from ai_usage_monitor.core.pricing import PricingCalculator
from ai_usage_monitor.data.reader import load_usage_entries as _load_usage_entries

logger = logging.getLogger(__name__)


@AdapterRegistry.register
class ClaudeCodeAdapter(ToolAdapter):
    """Adapter for Claude Code JSONL usage data.

    Claude Code stores usage data in JSONL files within the user's home
    directory. This adapter reads and parses that data.

    Data locations:
        - Primary: ~/.claude/projects/
        - Alternative: ~/.config/claude/projects/

    Data format: JSONL with fields:
        - timestamp: ISO format timestamp
        - inputTokens/input_tokens: Input token count
        - outputTokens/output_tokens: Output token count
        - cacheCreationInputTokens: Cache creation tokens
        - cacheReadInputTokens: Cache read tokens
        - message.model or model: Model name
        - cost or costUSD: Pre-calculated cost (optional)
    """

    def __init__(self) -> None:
        """Initialize the Claude Code adapter."""
        self._pricing_calculator = PricingCalculator()

    @property
    def metadata(self) -> ToolMetadata:
        """Return metadata about Claude Code."""
        return ToolMetadata(
            name="claude-code",
            display_name="Claude Code",
            data_format="jsonl",
            default_paths=[
                "~/.claude/projects",
                "~/.config/claude/projects",
            ],
            supported_features=[
                "tokens",
                "cost",
                "sessions",
                "models",
                "cache",
            ],
            pricing_available=True,
            version="1.0.0",
            description="Anthropic's Claude Code CLI tool for AI-assisted coding",
        )

    def discover_data_paths(
        self, custom_paths: Optional[List[str]] = None
    ) -> List[Path]:
        """Discover Claude Code data directories.

        Args:
            custom_paths: Optional custom paths to check.

        Returns:
            List of existing data directory paths.
        """
        paths_to_check = custom_paths if custom_paths else self.metadata.default_paths
        existing_paths: List[Path] = []

        for path_str in paths_to_check:
            path = Path(path_str).expanduser()
            if path.exists() and path.is_dir():
                existing_paths.append(path)
                logger.debug(f"Found Claude Code data at: {path}")

        return existing_paths

    def load_usage_entries(
        self,
        data_path: Optional[str] = None,
        hours_back: Optional[int] = None,
        include_raw: bool = False,
    ) -> Tuple[List[UsageEntry], Optional[List[Dict[str, Any]]]]:
        """Load usage entries from Claude Code data files.

        Args:
            data_path: Specific data path to use (auto-discovers if None).
            hours_back: Only load entries from the last N hours.
            include_raw: Whether to include raw data in the result.

        Returns:
            Tuple of (usage_entries, raw_data).
        """
        # Use provided path or discover one
        if data_path is None:
            discovered = self.discover_data_paths()
            if not discovered:
                logger.warning("No Claude Code data directories found")
                return [], None
            data_path = str(discovered[0])

        # Use existing reader implementation
        entries, raw_data = _load_usage_entries(
            data_path=data_path,
            hours_back=hours_back,
            mode=CostMode.AUTO,
            include_raw=include_raw,
        )

        # Add tool_name to entries
        for entry in entries:
            entry.tool_name = "claude-code"

        return entries, raw_data

    def calculate_cost(self, entry: UsageEntry) -> float:
        """Calculate cost for a Claude Code usage entry.

        Args:
            entry: The usage entry to calculate cost for.

        Returns:
            Cost in USD.
        """
        return self._pricing_calculator.calculate_cost(
            model=entry.model,
            input_tokens=entry.input_tokens,
            output_tokens=entry.output_tokens,
            cache_creation_tokens=entry.cache_creation_tokens,
            cache_read_tokens=entry.cache_read_tokens,
        )
