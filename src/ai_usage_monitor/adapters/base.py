"""Abstract base class for tool-specific data adapters.

This module defines the interface that all tool adapters must implement.
Each adapter is responsible for:
- Discovering data directories for its tool
- Loading and parsing usage data
- Calculating costs (if pricing is available)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ai_usage_monitor.core.models import UsageEntry


@dataclass
class ToolMetadata:
    """Metadata about a supported AI coding tool."""

    name: str
    """Unique identifier for the tool (e.g., 'claude-code', 'codex-cli')."""

    display_name: str
    """Human-readable name for the tool (e.g., 'Claude Code', 'Codex CLI')."""

    data_format: str
    """Primary data format: 'jsonl', 'json', 'sqlite', 'txt'."""

    default_paths: List[str]
    """Default data directory paths to check (with ~ expansion)."""

    supported_features: List[str] = field(default_factory=list)
    """Features this tool supports: 'tokens', 'cost', 'sessions', 'models', 'cache'."""

    pricing_available: bool = False
    """Whether cost calculation is available for this tool."""

    version: str = "1.0.0"
    """Version of this adapter implementation."""

    description: str = ""
    """Brief description of the tool."""


class ToolAdapter(ABC):
    """Abstract base class for tool-specific data adapters.

    Each AI coding tool has its own adapter that implements this interface.
    Adapters are responsible for:
    - Discovering where the tool stores its data
    - Loading and parsing usage entries
    - Calculating costs (if pricing information is available)

    Example:
        >>> from ai_usage_monitor.adapters import AdapterRegistry
        >>> adapter = AdapterRegistry.get_adapter("claude-code")
        >>> if adapter.is_available():
        ...     entries, _ = adapter.load_usage_entries(hours_back=24)
        ...     print(f"Found {len(entries)} entries")
    """

    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """Return metadata about this tool adapter.

        Returns:
            ToolMetadata with name, paths, features, etc.
        """
        pass

    @abstractmethod
    def discover_data_paths(
        self, custom_paths: Optional[List[str]] = None
    ) -> List[Path]:
        """Discover data directories for this tool.

        Args:
            custom_paths: Optional custom paths to check instead of defaults.

        Returns:
            List of existing data directory paths.
        """
        pass

    @abstractmethod
    def load_usage_entries(
        self,
        data_path: Optional[str] = None,
        hours_back: Optional[int] = None,
        include_raw: bool = False,
    ) -> Tuple[List[UsageEntry], Optional[List[Dict[str, Any]]]]:
        """Load usage entries from this tool's data.

        Args:
            data_path: Specific data path to use (uses default if None).
            hours_back: Only load entries from the last N hours.
            include_raw: Whether to include raw data in the result.

        Returns:
            Tuple of (usage_entries, raw_data).
            raw_data is None if include_raw is False.
        """
        pass

    @abstractmethod
    def calculate_cost(self, entry: UsageEntry) -> float:
        """Calculate cost for a usage entry.

        Args:
            entry: The usage entry to calculate cost for.

        Returns:
            Cost in USD, or 0.0 if pricing is not available.
        """
        pass

    def is_available(self) -> bool:
        """Check if this tool's data is available on the system.

        Returns:
            True if at least one data directory exists.
        """
        return len(self.discover_data_paths()) > 0

    def get_supported_features(self) -> List[str]:
        """Get list of features this tool supports.

        Returns:
            List of feature names (e.g., ['tokens', 'cost', 'sessions']).
        """
        return self.metadata.supported_features

    def supports_feature(self, feature: str) -> bool:
        """Check if this tool supports a specific feature.

        Args:
            feature: Feature name to check.

        Returns:
            True if the feature is supported.
        """
        return feature in self.metadata.supported_features
