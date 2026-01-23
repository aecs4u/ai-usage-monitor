"""MCP (Model Context Protocol) server for AI Usage Monitor.

This module provides an MCP server that exposes usage monitoring
capabilities as tools that can be used by AI assistants.
"""

from ai_usage_monitor.mcp.server import main, serve

__all__ = ["main", "serve"]
