"""Tool adapter implementations.

This module contains all built-in tool adapters. Importing this module
will register all adapters with the AdapterRegistry.
"""

# Import all adapters to trigger registration
from ai_usage_monitor.adapters.implementations.claude_code import ClaudeCodeAdapter
from ai_usage_monitor.adapters.implementations.cline import ClineAdapter
from ai_usage_monitor.adapters.implementations.codex_cli import CodexCLIAdapter
from ai_usage_monitor.adapters.implementations.gemini_cli import GeminiCLIAdapter
from ai_usage_monitor.adapters.implementations.github_copilot import GitHubCopilotAdapter
from ai_usage_monitor.adapters.implementations.kilo_code import KiloCodeAdapter
from ai_usage_monitor.adapters.implementations.opencode import OpenCodeAdapter
from ai_usage_monitor.adapters.implementations.pi_agent import PiAgentAdapter
from ai_usage_monitor.adapters.implementations.roo_code import RooCodeAdapter

__all__ = [
    "ClaudeCodeAdapter",
    "ClineAdapter",
    "CodexCLIAdapter",
    "GeminiCLIAdapter",
    "GitHubCopilotAdapter",
    "KiloCodeAdapter",
    "OpenCodeAdapter",
    "PiAgentAdapter",
    "RooCodeAdapter",
]
