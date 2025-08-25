"""Unit tests for base scraper functionality."""

import pytest

from scrap_e.core.models import ScraperStats
from scrap_e.scrapers.web.http_scraper import HttpScraper


class TestBaseScraperStats:
    """Tests for base scraper statistics management."""

    @pytest.mark.asyncio
    async def test_scraper_stats_initialization(self):
        """Test scraper stats initialization."""
        scraper = HttpScraper()

        stats = scraper.get_stats()
        assert isinstance(stats, ScraperStats)
        assert stats.total_requests == 0
        assert stats.successful_requests == 0
        assert stats.failed_requests == 0

    @pytest.mark.asyncio
    async def test_scraper_stats_update(self):
        """Test updating scraper stats."""
        scraper = HttpScraper()

        # Modify stats
        scraper.stats.total_requests = 5
        scraper.stats.successful_requests = 4
        scraper.stats.failed_requests = 1
        scraper.stats.total_duration = 10.0

        # Get updated stats
        stats = scraper.get_stats()
        assert stats.total_requests == 5
        assert stats.successful_requests == 4
        assert stats.failed_requests == 1
        assert stats.average_response_time == 2.0

    @pytest.mark.asyncio
    async def test_scraper_stats_reset(self):
        """Test resetting scraper stats."""
        scraper = HttpScraper()

        # Set some stats
        scraper.stats.total_requests = 10
        scraper.stats.successful_requests = 8
        scraper.stats.failed_requests = 2
        scraper.stats.total_duration = 20.0

        # Reset stats
        scraper.reset_stats()

        # Verify reset
        assert scraper.stats.total_requests == 0
        assert scraper.stats.successful_requests == 0
        assert scraper.stats.failed_requests == 0
        assert scraper.stats.total_duration == 0.0


class TestBaseScraperUtilities:
    """Tests for base scraper utility methods."""

    @pytest.mark.asyncio
    async def test_count_records_none(self):
        """Test counting records with None value."""
        scraper = HttpScraper()
        assert scraper._count_records(None) == 0

    @pytest.mark.asyncio
    async def test_count_records_list(self):
        """Test counting records with list."""
        scraper = HttpScraper()
        assert scraper._count_records([1, 2, 3]) == 3
        assert scraper._count_records([]) == 0

    @pytest.mark.asyncio
    async def test_count_records_dict(self):
        """Test counting records with dictionary."""
        scraper = HttpScraper()
        assert scraper._count_records({"key": "value"}) == 1
        assert scraper._count_records({}) == 1  # Empty dict counts as 1

    @pytest.mark.asyncio
    async def test_count_records_string(self):
        """Test counting records with string."""
        scraper = HttpScraper()
        assert scraper._count_records("test") == 4  # String length
        assert scraper._count_records("") == 0

    @pytest.mark.asyncio
    async def test_count_records_numeric(self):
        """Test counting records with numeric values."""
        scraper = HttpScraper()
        assert scraper._count_records(42) == 1
        assert scraper._count_records(3.14) == 1
        assert scraper._count_records(0) == 1

    @pytest.mark.asyncio
    async def test_count_records_nested(self):
        """Test counting records with nested structures."""
        scraper = HttpScraper()

        # Nested list
        nested_list = [[1, 2], [3, 4], [5]]
        assert scraper._count_records(nested_list) == 3

        # List of dicts
        list_of_dicts = [{"a": 1}, {"b": 2}, {"c": 3}]
        assert scraper._count_records(list_of_dicts) == 3


class TestBaseScraperLifecycle:
    """Tests for scraper lifecycle management."""

    @pytest.mark.asyncio
    async def test_scraper_context_manager(self):
        """Test scraper as async context manager."""
        scraper = HttpScraper()

        async with scraper as s:
            assert s._client is not None
            assert s is scraper

        # Client should be closed after context
        assert scraper._client is None

    @pytest.mark.asyncio
    async def test_scraper_initialization(self):
        """Test manual scraper initialization."""
        scraper = HttpScraper()
        assert scraper._client is None

        await scraper._initialize()
        assert scraper._client is not None

        await scraper._cleanup()
        assert scraper._client is None

    @pytest.mark.asyncio
    async def test_scraper_cleanup(self):
        """Test scraper cleanup."""
        scraper = HttpScraper()

        # Initialize first
        await scraper._initialize()
        assert scraper._client is not None

        # Cleanup
        await scraper._cleanup()
        assert scraper._client is None

        # Cleanup again should not raise error
        await scraper._cleanup()
        assert scraper._client is None

    @pytest.mark.asyncio
    async def test_scraper_multiple_initialization(self):
        """Test multiple initialization calls."""
        scraper = HttpScraper()

        # First initialization
        await scraper._initialize()
        client1 = scraper._client
        assert client1 is not None

        # Second initialization should create new client
        await scraper._initialize()
        client2 = scraper._client
        assert client2 is not None

        # Cleanup
        await scraper._cleanup()
