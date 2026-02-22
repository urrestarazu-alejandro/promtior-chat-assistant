"""Usage tracking for AI API calls."""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class UsageStats:
    """Track AI usage for cost management."""

    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    cost: float = 0.0

    def calculate_cost(self) -> float:
        """Calculate cost based on token usage.

        Returns:
            Cost in USD
        """
        rates = {
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        }
        rate = rates.get(self.model, {"input": 0.50, "output": 1.50})
        return (self.input_tokens * rate["input"] + self.output_tokens * rate["output"]) / 1_000_000


class UsageTracker:
    """Track and log AI API usage."""

    def __init__(self):
        self.stats: list[UsageStats] = []

    def log(self, stats: UsageStats):
        """Log usage statistics.

        Args:
            stats: Usage statistics to log
        """
        self.stats.append(stats)
        logger.info(
            f"AI Usage - Model: {stats.model}, "
            f"Input: {stats.input_tokens}, Output: {stats.output_tokens}, "
            f"Cost: ${stats.cost:.4f}"
        )

    def get_total_cost(self) -> float:
        """Get total cost across all tracked usage.

        Returns:
            Total cost in USD
        """
        return sum(s.cost for s in self.stats)


usage_tracker = UsageTracker()
