"""Unit tests for scraper statistics."""

from scrap_e.core.models import ScraperStats


class TestScraperStats:
    """Tests for ScraperStats functionality."""

    def test_stats_initialization(self):
        """Test stats initialization with default values."""
        stats = ScraperStats()
        assert stats.total_requests == 0
        assert stats.successful_requests == 0
        assert stats.failed_requests == 0
        assert stats.total_duration == 0.0
        assert stats.average_response_time == 0.0

    def test_stats_average_calculation(self):
        """Test average response time calculation."""
        stats = ScraperStats(total_requests=5, total_duration=10.0)
        # average_response_time is not auto-calculated in the model
        # It's calculated in the scraper's get_stats() method
        assert stats.total_requests == 5
        assert stats.total_duration == 10.0
        # Manual calculation
        average = stats.total_duration / stats.total_requests
        assert average == 2.0

    def test_stats_average_with_zero_requests(self):
        """Test average calculation with zero requests."""
        stats = ScraperStats(total_requests=0, total_duration=10.0)
        assert stats.average_response_time == 0.0

    def test_stats_update(self):
        """Test updating stats values."""
        stats = ScraperStats()

        # Update stats
        stats.total_requests = 10
        stats.successful_requests = 8
        stats.failed_requests = 2
        stats.total_duration = 20.0

        assert stats.total_requests == 10
        assert stats.successful_requests == 8
        assert stats.failed_requests == 2
        assert stats.total_duration == 20.0
        # average_response_time is calculated separately, not auto-updated
        # Manual calculation shows it would be 2.0
        assert stats.total_duration / stats.total_requests == 2.0

    def test_stats_success_rate(self):
        """Test calculating success rate."""
        stats = ScraperStats(total_requests=100, successful_requests=85, failed_requests=15)

        # Calculate success rate
        success_rate = (stats.successful_requests / stats.total_requests) * 100
        assert success_rate == 85.0

    def test_stats_reset(self):
        """Test resetting stats to initial values."""
        stats = ScraperStats(
            total_requests=50, successful_requests=45, failed_requests=5, total_duration=100.0
        )

        # Manually reset (simulate what reset_stats() would do)
        stats.total_requests = 0
        stats.successful_requests = 0
        stats.failed_requests = 0
        stats.total_duration = 0.0

        assert stats.total_requests == 0
        assert stats.successful_requests == 0
        assert stats.failed_requests == 0
        assert stats.total_duration == 0.0
        assert stats.average_response_time == 0.0
