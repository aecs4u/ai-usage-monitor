"""Data models for AI Usage Monitor.
Core data structures for usage tracking, session management, and token calculations.
Supports multiple AI coding tools (Claude, Codex, Gemini, Cline, etc.).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class CostMode(Enum):
    """Cost calculation modes for token usage analysis."""

    AUTO = "auto"
    CACHED = "cached"
    CALCULATED = "calculate"


@dataclass
class UsageEntry:
    """Individual usage record from AI coding tools.

    This model is designed to work with multiple AI tools including
    Claude Code, Codex CLI, Gemini CLI, Cline, and others.
    """

    timestamp: datetime
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    cost_usd: float = 0.0
    model: str = ""
    message_id: str = ""
    request_id: str = ""
    # Multi-tool support fields
    tool_name: str = "claude-code"
    """Tool identifier (e.g., 'claude-code', 'codex-cli', 'gemini-cli')."""
    session_id: str = ""
    """Session identifier for grouping related entries."""
    # Cloud sync fields
    user_id: str = ""
    """Clerk user ID for cloud sync."""
    machine_id: str = ""
    """Machine identifier for cross-device tracking."""
    organization_id: str = ""
    """Clerk organization ID for team tracking."""
    # Additional metadata
    duration_seconds: float = 0.0
    """Duration of the request (for tools that track this)."""
    success: bool = True
    """Whether the request was successful."""
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional tool-specific metadata."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_creation_tokens": self.cache_creation_tokens,
            "cache_read_tokens": self.cache_read_tokens,
            "cost_usd": self.cost_usd,
            "model": self.model,
            "message_id": self.message_id,
            "request_id": self.request_id,
            "tool_name": self.tool_name,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "machine_id": self.machine_id,
            "organization_id": self.organization_id,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
            "metadata": self.metadata,
        }

    @property
    def total_tokens(self) -> int:
        """Get total tokens for this entry."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_tokens
            + self.cache_read_tokens
        )


@dataclass
class TokenCounts:
    """Token aggregation structure with computed totals."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Get total tokens across all types."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_tokens
            + self.cache_read_tokens
        )


@dataclass
class BurnRate:
    """Token consumption rate metrics."""

    tokens_per_minute: float
    cost_per_hour: float


@dataclass
class UsageProjection:
    """Usage projection calculations for active blocks."""

    projected_total_tokens: int
    projected_total_cost: float
    remaining_minutes: float


@dataclass
class SessionBlock:
    """Aggregated session block representing a 5-hour period."""

    id: str
    start_time: datetime
    end_time: datetime
    entries: List[UsageEntry] = field(default_factory=list)
    token_counts: TokenCounts = field(default_factory=TokenCounts)
    is_active: bool = False
    is_gap: bool = False
    burn_rate: Optional[BurnRate] = None
    actual_end_time: Optional[datetime] = None
    per_model_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    models: List[str] = field(default_factory=list)
    sent_messages_count: int = 0
    cost_usd: float = 0.0
    limit_messages: List[Dict[str, Any]] = field(default_factory=list)
    projection_data: Optional[Dict[str, Any]] = None
    burn_rate_snapshot: Optional[BurnRate] = None

    @property
    def total_tokens(self) -> int:
        """Get total tokens from token_counts."""
        return self.token_counts.total_tokens

    @property
    def total_cost(self) -> float:
        """Get total cost - alias for cost_usd."""
        return self.cost_usd

    @property
    def duration_minutes(self) -> float:
        """Get duration in minutes."""
        if self.actual_end_time:
            duration = (self.actual_end_time - self.start_time).total_seconds() / 60
        else:
            duration = (self.end_time - self.start_time).total_seconds() / 60
        return max(duration, 1.0)


def normalize_model_name(model: str) -> str:
    """Normalize model name for consistent usage across the application.

    Handles various model name formats and maps them to standard keys.
    Supports Claude 4.5, 4.1, 4, 3.5, and 3 model families.

    Args:
        model: Raw model name from usage data

    Returns:
        Normalized model key

    Examples:
        >>> normalize_model_name("claude-opus-4-5-20251101")
        'claude-opus-4-5-20251101'
        >>> normalize_model_name("claude-3-opus-20240229")
        'claude-3-opus'
        >>> normalize_model_name("Claude 3.5 Sonnet")
        'claude-3-5-sonnet'
    """
    if not model:
        return ""

    model_lower = model.lower()

    # Claude 4.5 models - return as-is (lowercased)
    if "4-5" in model_lower or "4.5" in model_lower:
        if "opus" in model_lower:
            return "claude-opus-4-5-20251101"
        if "sonnet" in model_lower:
            return "claude-sonnet-4-5-20251101"
        if "haiku" in model_lower:
            return "claude-haiku-4-5-20251101"
        return model_lower

    # Claude 4.1 models
    if "4-1" in model_lower or "4.1" in model_lower:
        if "opus" in model_lower:
            return "claude-opus-4-1-20250414"
        return model_lower

    # Claude 4 models (not 4.5 or 4.1)
    if (
        "claude-opus-4-" in model_lower
        or "claude-sonnet-4-" in model_lower
        or "claude-haiku-4-" in model_lower
        or "sonnet-4-" in model_lower
        or "opus-4-" in model_lower
        or "haiku-4-" in model_lower
    ):
        return model_lower

    # Claude 3.5 models
    if "3.5" in model_lower or "3-5" in model_lower:
        if "sonnet" in model_lower:
            return "claude-3-5-sonnet"
        if "haiku" in model_lower:
            return "claude-3-5-haiku"
        return model_lower

    # Claude 3 models (legacy)
    if "opus" in model_lower:
        return "claude-3-opus"
    if "sonnet" in model_lower:
        return "claude-3-sonnet"
    if "haiku" in model_lower:
        return "claude-3-haiku"

    return model
