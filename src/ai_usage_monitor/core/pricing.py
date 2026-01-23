"""Pricing calculations for Claude models.

This module provides the PricingCalculator class for calculating costs
based on token usage and model pricing. It supports all Claude model types
(Opus, Sonnet, Haiku) and provides both simple and detailed cost calculations
with caching.
"""

from typing import Any, Dict, Optional

from ai_usage_monitor.core.models import CostMode, TokenCounts, normalize_model_name


class PricingCalculator:
    """Calculates costs based on model pricing with caching support.

    This class provides methods for calculating costs for individual models/tokens
    as well as detailed cost breakdowns for collections of usage entries.
    It supports custom pricing configurations and caches calculations for performance.

    Features:
    - Configurable pricing (from config or custom)
    - Fallback hardcoded pricing for robustness
    - Caching for performance
    - Support for all token types including cache
    - Backward compatible with both APIs
    """

    # Pricing per million tokens (MTok) - Updated January 2026
    # Source: https://claude.com/pricing
    FALLBACK_PRICING: Dict[str, Dict[str, float]] = {
        # Claude 4.5 family (latest)
        "opus-4.5": {
            "input": 5.0,
            "output": 25.0,
            "cache_creation": 6.25,
            "cache_read": 0.50,
        },
        "sonnet-4.5": {
            "input": 3.0,  # ≤200K tokens pricing (standard)
            "output": 15.0,
            "cache_creation": 3.75,
            "cache_read": 0.30,
        },
        "haiku-4.5": {
            "input": 1.0,
            "output": 5.0,
            "cache_creation": 1.25,
            "cache_read": 0.10,
        },
        # Claude 4.1 family
        "opus-4.1": {
            "input": 15.0,
            "output": 75.0,
            "cache_creation": 18.75,
            "cache_read": 1.5,
        },
        # Claude 4 family
        "opus-4": {
            "input": 15.0,
            "output": 75.0,
            "cache_creation": 18.75,
            "cache_read": 1.5,
        },
        "sonnet-4": {
            "input": 3.0,
            "output": 15.0,
            "cache_creation": 3.75,
            "cache_read": 0.30,
        },
        # Claude 3.5 family
        "sonnet-3.5": {
            "input": 3.0,
            "output": 15.0,
            "cache_creation": 3.75,
            "cache_read": 0.30,
        },
        "haiku-3.5": {
            "input": 1.0,
            "output": 5.0,
            "cache_creation": 1.25,
            "cache_read": 0.10,
        },
        # Claude 3 family (legacy)
        "opus-3": {
            "input": 15.0,
            "output": 75.0,
            "cache_creation": 18.75,
            "cache_read": 1.5,
        },
        "sonnet-3": {
            "input": 3.0,
            "output": 15.0,
            "cache_creation": 3.75,
            "cache_read": 0.30,
        },
        "haiku-3": {
            "input": 0.25,
            "output": 1.25,
            "cache_creation": 0.30,
            "cache_read": 0.03,
        },
        # Backward compatibility aliases
        "opus": {
            "input": 5.0,  # Default to latest (4.5)
            "output": 25.0,
            "cache_creation": 6.25,
            "cache_read": 0.50,
        },
        "sonnet": {
            "input": 3.0,
            "output": 15.0,
            "cache_creation": 3.75,
            "cache_read": 0.30,
        },
        "haiku": {
            "input": 1.0,  # Default to latest (4.5)
            "output": 5.0,
            "cache_creation": 1.25,
            "cache_read": 0.10,
        },
        # OpenAI models - January 2026 pricing
        # Source: https://openai.com/api/pricing/
        "gpt-4o": {
            "input": 2.50,
            "output": 10.0,
            "cache_creation": 0.0,
            "cache_read": 1.25,  # Cached input tokens
        },
        "gpt-4o-mini": {
            "input": 0.15,
            "output": 0.60,
            "cache_creation": 0.0,
            "cache_read": 0.075,  # Cached input tokens
        },
        "gpt-4-turbo": {
            "input": 10.0,
            "output": 30.0,
            "cache_creation": 0.0,
            "cache_read": 5.0,
        },
        "gpt-4": {
            "input": 30.0,
            "output": 60.0,
            "cache_creation": 0.0,
            "cache_read": 15.0,
        },
        "gpt-3.5-turbo": {
            "input": 0.50,
            "output": 1.50,
            "cache_creation": 0.0,
            "cache_read": 0.25,
        },
        "o1": {
            "input": 15.0,
            "output": 60.0,
            "cache_creation": 0.0,
            "cache_read": 7.5,
        },
        "o1-mini": {
            "input": 3.0,
            "output": 12.0,
            "cache_creation": 0.0,
            "cache_read": 1.5,
        },
        "o3-mini": {
            "input": 1.10,
            "output": 4.40,
            "cache_creation": 0.0,
            "cache_read": 0.55,
        },
        # Generic OpenAI fallback (uses GPT-4o pricing)
        "openai": {
            "input": 2.50,
            "output": 10.0,
            "cache_creation": 0.0,
            "cache_read": 1.25,
        },
    }

    def __init__(
        self, custom_pricing: Optional[Dict[str, Dict[str, float]]] = None
    ) -> None:
        """Initialize with optional custom pricing.

        Args:
            custom_pricing: Optional custom pricing dictionary to override defaults.
                          Should follow same structure as MODEL_PRICING.
        """
        # Use fallback pricing if no custom pricing provided
        self.pricing: Dict[str, Dict[str, float]] = custom_pricing or {
            # Claude 4.5 models
            "claude-opus-4-5-20251101": self.FALLBACK_PRICING["opus-4.5"],
            "claude-sonnet-4-5-20251101": self.FALLBACK_PRICING["sonnet-4.5"],
            "claude-haiku-4-5-20251101": self.FALLBACK_PRICING["haiku-4.5"],
            # Claude 4.1 models
            "claude-opus-4-1-20250414": self.FALLBACK_PRICING["opus-4.1"],
            # Claude 4 models
            "claude-opus-4-20250514": self.FALLBACK_PRICING["opus-4"],
            "claude-sonnet-4-20250514": self.FALLBACK_PRICING["sonnet-4"],
            # Claude 3.5 models
            "claude-3-5-sonnet": self.FALLBACK_PRICING["sonnet-3.5"],
            "claude-3-5-haiku": self.FALLBACK_PRICING["haiku-3.5"],
            # Claude 3 models (legacy)
            "claude-3-opus": self.FALLBACK_PRICING["opus-3"],
            "claude-3-sonnet": self.FALLBACK_PRICING["sonnet-3"],
            "claude-3-haiku": self.FALLBACK_PRICING["haiku-3"],
            # OpenAI models
            "gpt-4o": self.FALLBACK_PRICING["gpt-4o"],
            "gpt-4o-2024-11-20": self.FALLBACK_PRICING["gpt-4o"],
            "gpt-4o-2024-08-06": self.FALLBACK_PRICING["gpt-4o"],
            "gpt-4o-2024-05-13": self.FALLBACK_PRICING["gpt-4o"],
            "gpt-4o-mini": self.FALLBACK_PRICING["gpt-4o-mini"],
            "gpt-4o-mini-2024-07-18": self.FALLBACK_PRICING["gpt-4o-mini"],
            "gpt-4-turbo": self.FALLBACK_PRICING["gpt-4-turbo"],
            "gpt-4-turbo-2024-04-09": self.FALLBACK_PRICING["gpt-4-turbo"],
            "gpt-4": self.FALLBACK_PRICING["gpt-4"],
            "gpt-4-0613": self.FALLBACK_PRICING["gpt-4"],
            "gpt-3.5-turbo": self.FALLBACK_PRICING["gpt-3.5-turbo"],
            "gpt-3.5-turbo-0125": self.FALLBACK_PRICING["gpt-3.5-turbo"],
            "o1": self.FALLBACK_PRICING["o1"],
            "o1-2024-12-17": self.FALLBACK_PRICING["o1"],
            "o1-preview": self.FALLBACK_PRICING["o1"],
            "o1-mini": self.FALLBACK_PRICING["o1-mini"],
            "o1-mini-2024-09-12": self.FALLBACK_PRICING["o1-mini"],
            "o3-mini": self.FALLBACK_PRICING["o3-mini"],
            "o3-mini-2025-01-31": self.FALLBACK_PRICING["o3-mini"],
            # Generic OpenAI fallback
            "openai": self.FALLBACK_PRICING["openai"],
        }
        self._cost_cache: Dict[str, float] = {}

    def calculate_cost(
        self,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cache_creation_tokens: int = 0,
        cache_read_tokens: int = 0,
        tokens: Optional[TokenCounts] = None,
        strict: bool = False,
    ) -> float:
        """Calculate cost with flexible API supporting both signatures.

        Args:
            model: Model name
            input_tokens: Number of input tokens (ignored if tokens provided)
            output_tokens: Number of output tokens (ignored if tokens provided)
            cache_creation_tokens: Number of cache creation tokens
            cache_read_tokens: Number of cache read tokens
            tokens: Optional TokenCounts object (takes precedence)

        Returns:
            Total cost in USD
        """
        # Handle synthetic model
        if model == "<synthetic>":
            return 0.0

        # Support TokenCounts object
        if tokens is not None:
            input_tokens = tokens.input_tokens
            output_tokens = tokens.output_tokens
            cache_creation_tokens = tokens.cache_creation_tokens
            cache_read_tokens = tokens.cache_read_tokens

        # Create cache key
        cache_key = (
            f"{model}:{input_tokens}:{output_tokens}:"
            f"{cache_creation_tokens}:{cache_read_tokens}"
        )

        # Check cache
        if cache_key in self._cost_cache:
            return self._cost_cache[cache_key]

        # Get pricing for model
        pricing = self._get_pricing_for_model(model, strict=strict)

        # Calculate costs (pricing is per million tokens)
        cost = (
            (input_tokens / 1_000_000) * pricing["input"]
            + (output_tokens / 1_000_000) * pricing["output"]
            + (cache_creation_tokens / 1_000_000)
            * pricing.get("cache_creation", pricing["input"] * 1.25)
            + (cache_read_tokens / 1_000_000)
            * pricing.get("cache_read", pricing["input"] * 0.1)
        )

        # Round to 6 decimal places
        cost = round(cost, 6)

        # Cache result
        self._cost_cache[cache_key] = cost
        return cost

    def _get_pricing_for_model(
        self, model: str, strict: bool = False
    ) -> Dict[str, float]:
        """Get pricing for a model with optional fallback logic.

        Args:
            model: Model name
            strict: If True, raise KeyError for unknown models

        Returns:
            Pricing dictionary with input/output/cache costs

        Raises:
            KeyError: If strict=True and model is unknown
        """
        # Try normalized model name first
        normalized = normalize_model_name(model)

        # Check configured pricing
        if normalized in self.pricing:
            pricing = self.pricing[normalized]
            # Ensure cache pricing exists
            if "cache_creation" not in pricing:
                pricing["cache_creation"] = pricing["input"] * 1.25
            if "cache_read" not in pricing:
                pricing["cache_read"] = pricing["input"] * 0.1
            return pricing

        # Check original model name
        if model in self.pricing:
            pricing = self.pricing[model]
            if "cache_creation" not in pricing:
                pricing["cache_creation"] = pricing["input"] * 1.25
            if "cache_read" not in pricing:
                pricing["cache_read"] = pricing["input"] * 0.1
            return pricing

        # If strict mode, raise KeyError for unknown models
        if strict:
            raise KeyError(f"Unknown model: {model}")

        # Fallback to hardcoded pricing based on model type and version
        model_lower = model.lower()

        # Determine version
        version = None
        if "4-5" in model_lower or "4.5" in model_lower:
            version = "4.5"
        elif "4-1" in model_lower or "4.1" in model_lower:
            version = "4.1"
        elif "4-" in model_lower or "-4" in model_lower:
            version = "4"
        elif "3-5" in model_lower or "3.5" in model_lower:
            version = "3.5"
        elif "3-" in model_lower or "-3" in model_lower:
            version = "3"

        # Determine model type and return appropriate pricing
        if "opus" in model_lower:
            if version == "4.5":
                return self.FALLBACK_PRICING["opus-4.5"]
            elif version == "4.1":
                return self.FALLBACK_PRICING["opus-4.1"]
            elif version == "4":
                return self.FALLBACK_PRICING["opus-4"]
            elif version == "3":
                return self.FALLBACK_PRICING["opus-3"]
            return self.FALLBACK_PRICING["opus"]  # Default to latest

        if "haiku" in model_lower:
            if version == "4.5":
                return self.FALLBACK_PRICING["haiku-4.5"]
            elif version == "3.5":
                return self.FALLBACK_PRICING["haiku-3.5"]
            elif version == "3":
                return self.FALLBACK_PRICING["haiku-3"]
            return self.FALLBACK_PRICING["haiku"]  # Default to latest

        # Default to Sonnet pricing
        if version == "4.5":
            return self.FALLBACK_PRICING["sonnet-4.5"]
        elif version == "4":
            return self.FALLBACK_PRICING["sonnet-4"]
        elif version == "3.5":
            return self.FALLBACK_PRICING["sonnet-3.5"]
        elif version == "3":
            return self.FALLBACK_PRICING["sonnet-3"]
        return self.FALLBACK_PRICING["sonnet"]  # Default to latest

    def calculate_cost_for_entry(
        self, entry_data: Dict[str, Any], mode: CostMode
    ) -> float:
        """Calculate cost for a single entry (backward compatibility).

        Args:
            entry_data: Entry data dictionary
            mode: Cost mode (for backward compatibility)

        Returns:
            Cost in USD
        """
        # If cost is present and mode is cached, use it
        if mode.value == "cached":
            cost_value = entry_data.get("costUSD") or entry_data.get("cost_usd")
            if cost_value is not None:
                return float(cost_value)

        # Otherwise calculate from tokens
        model = entry_data.get("model") or entry_data.get("Model")
        if not model:
            raise KeyError("Missing 'model' key in entry_data")

        # Extract token counts with different possible keys
        input_tokens = entry_data.get("inputTokens", 0) or entry_data.get(
            "input_tokens", 0
        )
        output_tokens = entry_data.get("outputTokens", 0) or entry_data.get(
            "output_tokens", 0
        )
        cache_creation = entry_data.get(
            "cacheCreationInputTokens", 0
        ) or entry_data.get("cache_creation_tokens", 0)
        cache_read = (
            entry_data.get("cacheReadInputTokens", 0)
            or entry_data.get("cache_read_input_tokens", 0)
            or entry_data.get("cache_read_tokens", 0)
        )

        return self.calculate_cost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_creation_tokens=cache_creation,
            cache_read_tokens=cache_read,
        )
