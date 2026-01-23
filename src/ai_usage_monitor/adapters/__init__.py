"""Tool adapters for AI Usage Monitor.

This module provides the adapter pattern for supporting multiple AI coding tools.
Each tool has its own adapter that knows how to read and parse usage data.
"""

from ai_usage_monitor.adapters.base import ToolAdapter, ToolMetadata
from ai_usage_monitor.adapters.registry import AdapterRegistry

__all__ = [
    "ToolAdapter",
    "ToolMetadata",
    "AdapterRegistry",
]
