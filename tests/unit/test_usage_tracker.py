"""Tests for usage tracker."""

from src.promtior_assistant.infrastructure.persistence.usage_tracker import (
    UsageStats,
    UsageTracker,
)


class TestUsageStats:
    """Tests for UsageStats dataclass."""

    def test_default_values(self):
        """Test default values."""
        stats = UsageStats()
        assert stats.input_tokens == 0
        assert stats.output_tokens == 0
        assert stats.model == ""
        assert stats.cost == 0.0

    def test_calculate_cost_gpt4o_mini(self):
        """Test cost calculation for gpt-4o-mini."""
        stats = UsageStats(input_tokens=1000, output_tokens=500, model="gpt-4o-mini")
        cost = stats.calculate_cost()
        assert cost > 0

    def test_calculate_cost_gpt4o(self):
        """Test cost calculation for gpt-4o."""
        stats = UsageStats(input_tokens=1000, output_tokens=500, model="gpt-4o")
        cost = stats.calculate_cost()
        assert cost > 0

    def test_calculate_cost_gpt35_turbo(self):
        """Test cost calculation for gpt-3.5-turbo."""
        stats = UsageStats(input_tokens=1000, output_tokens=500, model="gpt-3.5-turbo")
        cost = stats.calculate_cost()
        assert cost > 0

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation for unknown model uses default rate."""
        stats = UsageStats(input_tokens=1000, output_tokens=500, model="unknown-model")
        cost = stats.calculate_cost()
        assert cost > 0


class TestUsageTracker:
    """Tests for UsageTracker class."""

    def test_log_stats(self, caplog):
        """Test logging usage statistics."""
        tracker = UsageTracker()
        stats = UsageStats(input_tokens=1000, output_tokens=500, model="gpt-4o-mini", cost=0.001)
        tracker.log(stats)
        assert len(tracker.stats) == 1

    def test_get_total_cost(self):
        """Test calculating total cost."""
        tracker = UsageTracker()
        tracker.log(
            UsageStats(input_tokens=1000, output_tokens=500, model="gpt-4o-mini", cost=0.001)
        )
        tracker.log(
            UsageStats(input_tokens=2000, output_tokens=1000, model="gpt-4o-mini", cost=0.002)
        )
        total = tracker.get_total_cost()
        assert total == 0.003

    def test_get_total_cost_empty(self):
        """Test total cost when no stats logged."""
        tracker = UsageTracker()
        total = tracker.get_total_cost()
        assert total == 0.0
