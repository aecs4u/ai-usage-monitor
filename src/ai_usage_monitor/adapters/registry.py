"""Central registry for tool adapters.

This module provides the AdapterRegistry class which manages all registered
tool adapters and provides methods for discovering and accessing them.
"""

import logging
from typing import Dict, List, Optional, Type

from ai_usage_monitor.adapters.base import ToolAdapter, ToolMetadata

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """Central registry for tool adapters.

    This class manages the registration and retrieval of tool adapters.
    Adapters can be registered using the @AdapterRegistry.register decorator.

    Example:
        >>> @AdapterRegistry.register
        ... class MyToolAdapter(ToolAdapter):
        ...     @property
        ...     def metadata(self):
        ...         return ToolMetadata(name="my-tool", ...)
        ...     # ... implement other methods

        >>> adapter = AdapterRegistry.get_adapter("my-tool")
        >>> if adapter and adapter.is_available():
        ...     entries, _ = adapter.load_usage_entries()
    """

    _adapters: Dict[str, Type[ToolAdapter]] = {}
    _instances: Dict[str, ToolAdapter] = {}

    @classmethod
    def register(cls, adapter_class: Type[ToolAdapter]) -> Type[ToolAdapter]:
        """Register an adapter class (decorator).

        Args:
            adapter_class: The adapter class to register.

        Returns:
            The same adapter class (for decorator chaining).

        Example:
            >>> @AdapterRegistry.register
            ... class ClaudeCodeAdapter(ToolAdapter):
            ...     pass
        """
        # Create a temporary instance to get the metadata
        try:
            instance = adapter_class()
            name = instance.metadata.name
            cls._adapters[name] = adapter_class
            logger.debug(f"Registered adapter: {name}")
        except Exception as e:
            logger.warning(f"Failed to register adapter {adapter_class.__name__}: {e}")
        return adapter_class

    @classmethod
    def get_adapter(cls, tool_name: str) -> Optional[ToolAdapter]:
        """Get an adapter instance by tool name.

        Args:
            tool_name: The tool identifier (e.g., 'claude-code').

        Returns:
            The adapter instance, or None if not found.
        """
        if tool_name not in cls._instances:
            if tool_name in cls._adapters:
                try:
                    cls._instances[tool_name] = cls._adapters[tool_name]()
                except Exception as e:
                    logger.error(f"Failed to instantiate adapter {tool_name}: {e}")
                    return None
        return cls._instances.get(tool_name)

    @classmethod
    def get_available_tools(cls) -> List[ToolMetadata]:
        """Get list of tools with data available on this system.

        Returns:
            List of ToolMetadata for tools that have data available.
        """
        available = []
        for name in cls._adapters:
            adapter = cls.get_adapter(name)
            if adapter and adapter.is_available():
                available.append(adapter.metadata)
        return available

    @classmethod
    def get_all_tools(cls) -> List[ToolMetadata]:
        """Get list of all registered tools (whether available or not).

        Returns:
            List of ToolMetadata for all registered tools.
        """
        tools = []
        for name in cls._adapters:
            adapter = cls.get_adapter(name)
            if adapter:
                tools.append(adapter.metadata)
        return tools

    @classmethod
    def get_tool_names(cls) -> List[str]:
        """Get list of all registered tool names.

        Returns:
            List of tool identifiers.
        """
        return list(cls._adapters.keys())

    @classmethod
    def is_registered(cls, tool_name: str) -> bool:
        """Check if a tool is registered.

        Args:
            tool_name: The tool identifier to check.

        Returns:
            True if the tool is registered.
        """
        return tool_name in cls._adapters

    @classmethod
    def clear(cls) -> None:
        """Clear all registered adapters (mainly for testing)."""
        cls._adapters.clear()
        cls._instances.clear()

    @classmethod
    def _load_builtin_adapters(cls) -> None:
        """Load all built-in adapters.

        This method imports all adapter implementations to trigger registration.
        """
        try:
            # Import all implementations to trigger @register decorators
            from ai_usage_monitor.adapters import implementations  # noqa: F401
        except ImportError as e:
            logger.warning(f"Failed to load built-in adapters: {e}")


# Auto-load built-in adapters when the module is imported
AdapterRegistry._load_builtin_adapters()
