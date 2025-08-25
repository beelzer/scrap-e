"""Unit tests for configuration classes."""

from scrap_e.core.config import ScraperConfig, WebScraperConfig


class TestScraperConfig:
    """Tests for base ScraperConfig."""

    def test_config_defaults(self):
        """Test config default values."""
        config = ScraperConfig()
        assert config.name == "universal-scraper"
        assert config.debug is False
        assert config.max_workers == 10

    def test_config_custom_values(self):
        """Test config with custom values."""
        config = ScraperConfig(name="custom-scraper", debug=True, max_workers=5)
        assert config.name == "custom-scraper"
        assert config.debug is True
        assert config.max_workers == 5


class TestWebScraperConfig:
    """Tests for WebScraperConfig."""

    def test_web_config_defaults(self):
        """Test web config default values."""
        config = WebScraperConfig()
        # Basic scraper config fields
        assert config.name == "universal-scraper"
        assert config.debug is False
        assert config.max_workers == 10

    def test_web_config_custom_values(self):
        """Test web config with custom values."""
        config = WebScraperConfig(
            extract_metadata=False,
            extract_links=False,
            extract_images=False,
            extract_tables=False,
            follow_redirects=False,
            user_agent="CustomBot/1.0",
        )
        assert config.extract_metadata is False
        assert config.extract_links is False
        assert config.extract_images is False
        assert config.extract_tables is False
        assert config.follow_redirects is False
        assert config.user_agent == "CustomBot/1.0"

    def test_web_config_inheritance(self):
        """Test that WebScraperConfig inherits from ScraperConfig."""
        config = WebScraperConfig(name="web-scraper", debug=True, extract_metadata=False)
        # Check inherited fields
        assert config.name == "web-scraper"
        assert config.debug is True
        # Check web-specific fields
        assert config.extract_metadata is False
        assert config.extract_links is True  # Default
