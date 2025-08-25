"""Integration tests for HTTP scraper with parser."""

import pytest

from scrap_e.core.models import ExtractionRule, ScraperType
from scrap_e.scrapers.web.http_scraper import HttpScraper
from scrap_e.scrapers.web.parser import HtmlParser


@pytest.mark.asyncio
class TestHttpScraperIntegration:
    """Integration tests for HTTP scraper functionality."""

    async def test_scraper_properties(self):
        """Test HTTP scraper properties and configuration."""
        scraper = HttpScraper()

        # Test scraper type
        assert scraper.scraper_type == ScraperType.WEB_HTTP

        # Test default config
        config = scraper._get_default_config()
        assert config is not None
        assert config.extract_metadata is True
        assert config.extract_links is True

    async def test_add_extraction_rules(self):
        """Test adding and managing extraction rules."""
        scraper = HttpScraper()

        # Initially no rules
        assert len(scraper.extraction_rules) == 0

        # Add single rule
        rule1 = ExtractionRule(name="title", selector="h1")
        scraper.add_extraction_rule(rule1)
        assert len(scraper.extraction_rules) == 1

        # Add multiple rules
        rule2 = ExtractionRule(name="content", selector=".content", multiple=True)
        rule3 = ExtractionRule(name="author", selector=".author", required=False)

        scraper.add_extraction_rule(rule2)
        scraper.add_extraction_rule(rule3)

        assert len(scraper.extraction_rules) == 3
        assert scraper.extraction_rules[0].name == "title"
        assert scraper.extraction_rules[1].multiple is True
        assert scraper.extraction_rules[2].required is False

    async def test_scraper_with_parser_integration(self):
        """Test scraper working with parser for data extraction."""

        # Sample HTML that might be returned
        html = """
        <html>
        <head>
            <title>Integration Test</title>
            <meta name="description" content="Testing integration">
        </head>
        <body>
            <h1>Main Title</h1>
            <div class="content">
                <p>Paragraph 1</p>
                <p>Paragraph 2</p>
            </div>
            <a href="/link1">Link 1</a>
            <a href="/link2">Link 2</a>
        </body>
        </html>
        """

        # Parse HTML
        parser = HtmlParser(html)

        # Extract metadata
        metadata = parser.extract_metadata()
        assert metadata["title"] == "Integration Test"
        assert metadata["description"] == "Testing integration"

        # Extract links
        links = parser.extract_links()
        assert len(links) == 2
        assert any(link["url"] == "/link1" for link in links)

        # Test with extraction rules
        title_text = parser.soup.select_one("h1").text
        assert title_text == "Main Title"

        paragraphs = parser.soup.select(".content p")
        assert len(paragraphs) == 2

    async def test_scraper_session_management(self):
        """Test HTTP scraper session lifecycle."""
        scraper = HttpScraper()

        # Test initialization
        await scraper._initialize()
        assert scraper._client is not None

        # Test reinitialization
        await scraper._initialize()
        client2 = scraper._client
        assert client2 is not None

        # Test cleanup
        await scraper._cleanup()
        assert scraper._client is None

    async def test_extraction_rules_with_transforms(self):
        """Test extraction rules with transformation functions."""
        html = """
        <div class="price">  $42.99  </div>
        <div class="quantity">  10  </div>
        <div class="name">  Product Name  </div>
        """

        parser = HtmlParser(html)

        # Test price extraction with strip transform
        price_elem = parser.soup.select_one(".price")
        price = parser._apply_transform(price_elem.text, "strip")
        assert price == "$42.99"

        # Test quantity extraction with int transform
        qty_elem = parser.soup.select_one(".quantity")
        qty = parser._apply_transform(qty_elem.text.strip(), "int")
        assert qty == 10

        # Test name extraction with title transform
        name_elem = parser.soup.select_one(".name")
        name = parser._apply_transform(name_elem.text.strip(), "title")
        assert name == "Product Name"
