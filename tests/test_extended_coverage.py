"""Extended tests to improve coverage."""

import pytest
from pydantic import BaseModel

from scrap_e.core.config import ScraperConfig, WebScraperConfig
from scrap_e.core.models import (
    ExtractionRule,
    ScraperMetadata,
    ScraperResult,
    ScraperStats,
    ScraperType,
)
from scrap_e.scrapers.web.http_scraper import HttpScraper
from scrap_e.scrapers.web.parser import HtmlParser


class DataModelForTesting(BaseModel):
    """Test data model."""

    content: str
    value: int = 0


@pytest.mark.asyncio
class TestBasicCoverage:
    """Basic tests to improve coverage."""

    async def test_base_scraper_stats(self):
        """Test scraper stats methods."""
        scraper = HttpScraper()

        # Get initial stats
        stats = scraper.get_stats()
        assert isinstance(stats, ScraperStats)
        assert stats.total_requests == 0

        # Modify stats
        scraper.stats.total_requests = 5
        scraper.stats.total_duration = 10.0

        # Get stats with average calculation
        stats = scraper.get_stats()
        assert stats.average_response_time == 2.0

        # Reset stats
        scraper.reset_stats()
        assert scraper.stats.total_requests == 0

    async def test_base_scraper_count_records(self):
        """Test counting records."""
        scraper = HttpScraper()

        # Test various data types
        assert scraper._count_records(None) == 0
        assert scraper._count_records([1, 2, 3]) == 3
        assert scraper._count_records({"key": "value"}) == 1
        assert scraper._count_records("test") == 4
        assert scraper._count_records(42) == 1

    async def test_scraper_context_manager(self):
        """Test scraper as context manager."""
        scraper = HttpScraper()

        async with scraper as s:
            assert s._client is not None

        # Client should be closed
        assert scraper._client is None

    async def test_http_scraper_cleanup(self):
        """Test HTTP scraper cleanup."""
        scraper = HttpScraper()
        await scraper._initialize()
        assert scraper._client is not None

        await scraper._cleanup()
        assert scraper._client is None

    async def test_parser_initialization(self):
        """Test parser initialization."""
        html = "<html><body><h1>Test</h1></body></html>"
        parser = HtmlParser(html)
        assert parser.soup is not None

    async def test_parser_extract_metadata(self):
        """Test metadata extraction."""
        html = """
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
        </head>
        <body></body>
        </html>
        """
        parser = HtmlParser(html)
        metadata = parser.extract_metadata()

        assert metadata["title"] == "Test Page"
        assert metadata["description"] == "Test description"

    async def test_parser_extract_links(self):
        """Test link extraction."""
        html = """
        <html>
        <body>
            <a href="http://example.com">Example</a>
            <a href="/internal">Internal</a>
        </body>
        </html>
        """
        parser = HtmlParser(html)
        links = parser.extract_links()

        assert len(links) == 2
        assert any(link["url"] == "http://example.com" for link in links)

    async def test_parser_extract_images(self):
        """Test image extraction."""
        html = """
        <html>
        <body>
            <img src="/image.jpg" alt="Test">
        </body>
        </html>
        """
        parser = HtmlParser(html)
        images = parser.extract_images()

        assert len(images) == 1
        assert images[0]["src"] == "/image.jpg"

    async def test_parser_extract_tables(self):
        """Test table extraction."""
        html = """
        <table>
            <tr><th>Name</th><th>Value</th></tr>
            <tr><td>Test</td><td>123</td></tr>
        </table>
        """
        parser = HtmlParser(html)
        tables = parser.extract_tables()

        assert len(tables) == 1
        assert len(tables[0]) >= 1

    async def test_parser_extract_data(self):
        """Test data extraction from parser."""
        html = """
        <html>
        <body>
            <h1>Test Title</h1>
            <div class="content">Test content</div>
        </body>
        </html>
        """
        parser = HtmlParser(html)

        # Test that parser has soup attribute
        assert parser.soup is not None
        assert "Test Title" in str(parser.soup)

    async def test_parser_extract_structured_data(self):
        """Test structured data extraction."""
        html = """
        <script type="application/ld+json">
        {"@type": "Article", "name": "Test"}
        </script>
        """
        parser = HtmlParser(html)
        data = parser.extract_structured_data()

        # Data should be extracted
        assert data is not None
        assert isinstance(data, dict)

    async def test_config_defaults(self):
        """Test config default values."""
        config = ScraperConfig()
        assert config.name == "universal-scraper"
        assert config.debug is False
        assert config.max_workers == 10

    async def test_web_config_defaults(self):
        """Test web config defaults."""
        config = WebScraperConfig()
        assert config.extract_metadata is True
        assert config.extract_links is True

    async def test_extraction_rule(self):
        """Test extraction rule creation."""
        rule = ExtractionRule(name="test", selector="h1", required=False)
        assert rule.name == "test"
        assert rule.selector == "h1"

    async def test_scraper_metadata(self):
        """Test scraper metadata."""
        metadata = ScraperMetadata(
            scraper_type=ScraperType.WEB_HTTP,
            source="http://test.com",
            records_scraped=10,
        )
        assert metadata.scraper_type == ScraperType.WEB_HTTP
        assert metadata.records_scraped == 10

    async def test_scraper_result(self):
        """Test scraper result."""
        metadata = ScraperMetadata(
            scraper_type=ScraperType.WEB_HTTP, source="http://test.com"
        )
        result = ScraperResult(success=True, data={"test": "data"}, metadata=metadata)
        assert result.success is True
        assert result.data == {"test": "data"}

    async def test_http_scraper_properties(self):
        """Test HTTP scraper properties."""
        scraper = HttpScraper()
        assert scraper.scraper_type == ScraperType.WEB_HTTP

        config = scraper._get_default_config()
        assert isinstance(config, WebScraperConfig)

    async def test_http_scraper_add_extraction_rule(self):
        """Test adding extraction rules."""
        scraper = HttpScraper()
        rule = ExtractionRule(name="test", selector="h1")

        scraper.add_extraction_rule(rule)
        assert len(scraper.extraction_rules) == 1

    async def test_parser_basic_functionality(self):
        """Test basic parser functionality."""
        html = "<h1>Title</h1><p>Paragraph</p>"
        parser = HtmlParser(html)

        # Parser should have soup
        assert parser.soup is not None

        # Should be able to find elements
        h1 = parser.soup.find("h1")
        assert h1 is not None
        assert h1.text == "Title"

    async def test_parser_transforms(self):
        """Test parser transformations."""
        parser = HtmlParser("")

        # Test various transforms
        assert parser._apply_transform("  test  ", "strip") == "test"
        assert parser._apply_transform("TEST", "lower") == "test"
        assert parser._apply_transform("test", "upper") == "TEST"
        assert parser._apply_transform("42", "int") == 42
        assert parser._apply_transform("42.5", "float") == 42.5
        assert parser._apply_transform("unknown", "unknown") == "unknown"
