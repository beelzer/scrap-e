"""Integration tests for scraper and parser components."""

from unittest.mock import patch

import pytest

from scrap_e.core.models import ExtractionRule
from scrap_e.scrapers.web.http_scraper import HttpScraper
from tests.fixtures import COMPLEX_HTML, TABLE_HTML, create_mock_response


class TestHttpScraperParserIntegration:
    """Test integration between HTTP scraper and HTML parser."""

    @pytest.mark.asyncio
    async def test_scrape_and_extract_data(self):
        """Test scraping and extracting data in one flow."""
        scraper = HttpScraper()

        # Add extraction rules
        rules = [
            ExtractionRule(name="title", selector="h1#main-title"),
            ExtractionRule(name="description", selector="p.description"),
            ExtractionRule(name="items", selector=".items span", multiple=True),
            ExtractionRule(name="author", selector=".author"),
        ]

        for rule in rules:
            scraper.add_extraction_rule(rule)

        # Mock the HTTP response
        mock_response = create_mock_response(content=COMPLEX_HTML)

        with patch.object(scraper, "_make_request", return_value=mock_response):
            result = await scraper.scrape("https://example.com")

        assert result.success is True
        assert result.data.extracted_data is not None
        assert result.data.extracted_data["title"] == "Complex Test Page"
        assert "complex test page" in result.data.extracted_data["description"].lower()
        assert len(result.data.extracted_data["items"]) == 3
        assert result.data.extracted_data["author"] == "John Doe"

    @pytest.mark.asyncio
    async def test_scrape_with_metadata_and_links(self):
        """Test scraping with metadata and link extraction."""
        scraper = HttpScraper()
        scraper.config.extract_metadata = True
        scraper.config.extract_links = True

        mock_response = create_mock_response(content=COMPLEX_HTML)

        with patch.object(scraper, "_make_request", return_value=mock_response):
            result = await scraper.scrape("https://example.com")

        assert result.success is True
        assert result.data.metadata is not None
        assert result.data.metadata["title"] == "Complex Test Page"
        assert result.data.links is not None
        assert len(result.data.links) > 0
        assert any("/about" in link["url"] for link in result.data.links)

    @pytest.mark.asyncio
    async def test_scrape_table_extraction(self):
        """Test scraping and extracting table data."""
        scraper = HttpScraper()
        scraper.config.extract_tables = True

        mock_response = create_mock_response(content=TABLE_HTML)

        with patch.object(scraper, "_make_request", return_value=mock_response):
            result = await scraper.scrape("https://example.com")

        assert result.success is True
        assert result.data.tables is not None
        assert len(result.data.tables) == 1

        table = result.data.tables[0]
        assert len(table) >= 3  # Headers and at least 2 data rows

    @pytest.mark.asyncio
    async def test_scrape_with_transforms(self):
        """Test scraping with data transformations."""
        scraper = HttpScraper()

        html = """
        <html>
            <body>
                <span class="price">  $99.99  </span>
                <span class="quantity">42</span>
                <span class="name">  PRODUCT NAME  </span>
            </body>
        </html>
        """

        rules = [
            ExtractionRule(name="price", selector=".price", transform="strip"),
            ExtractionRule(name="quantity", selector=".quantity", transform="int"),
            ExtractionRule(name="name", selector=".name", transform="lower"),
        ]

        for rule in rules:
            scraper.add_extraction_rule(rule)

        mock_response = create_mock_response(content=html)

        with patch.object(scraper, "_make_request", return_value=mock_response):
            result = await scraper.scrape("https://example.com")

        assert result.success is True
        assert result.data.extracted_data["price"] == "$99.99"
        assert result.data.extracted_data["quantity"] == 42
        assert "product name" in result.data.extracted_data["name"].lower()

    @pytest.mark.asyncio
    async def test_scrape_multiple_with_extraction(self):
        """Test scraping multiple URLs with extraction rules."""
        scraper = HttpScraper()

        rule = ExtractionRule(name="title", selector="h1")
        scraper.add_extraction_rule(rule)

        urls = [
            "https://example1.com",
            "https://example2.com",
            "https://example3.com",
        ]

        mock_response = create_mock_response(content=COMPLEX_HTML)

        with patch.object(scraper, "_make_request", return_value=mock_response):
            results = await scraper.scrape_multiple(urls)

        assert len(results) == 3
        for result in results:
            assert result.success is True
            assert result.data.extracted_data is not None
            assert "title" in result.data.extracted_data


class TestParserScraperEdgeCases:
    """Test edge cases in scraper-parser integration."""

    @pytest.mark.asyncio
    async def test_scrape_empty_html(self):
        """Test scraping empty HTML content."""
        scraper = HttpScraper()
        scraper.add_extraction_rule(ExtractionRule(name="title", selector="h1", default="No Title"))

        mock_response = create_mock_response(content="")

        with patch.object(scraper, "_make_request", return_value=mock_response):
            result = await scraper.scrape("https://example.com")

        assert result.success is True
        assert result.data.extracted_data["title"] == "No Title"

    @pytest.mark.asyncio
    async def test_scrape_malformed_html(self):
        """Test scraping malformed HTML."""
        scraper = HttpScraper()

        malformed = "<h1>Title<p>Paragraph</h1></p>"
        mock_response = create_mock_response(content=malformed)

        with patch.object(scraper, "_make_request", return_value=mock_response):
            result = await scraper.scrape("https://example.com")

        assert result.success is True
        assert result.data is not None

    @pytest.mark.asyncio
    async def test_scrape_non_html_content(self):
        """Test scraping non-HTML content."""
        scraper = HttpScraper()

        json_content = '{"key": "value"}'
        mock_response = create_mock_response(
            content=json_content, headers={"content-type": "application/json"}
        )

        with patch.object(scraper, "_make_request", return_value=mock_response):
            result = await scraper.scrape("https://api.example.com")

        assert result.success is True
        assert result.data is not None
        assert json_content in result.data.content


class TestComplexExtractionScenarios:
    """Test complex extraction scenarios."""

    @pytest.mark.asyncio
    async def test_nested_extraction_rules(self):
        """Test extraction with nested selectors."""
        scraper = HttpScraper()

        html = """
        <div class="product">
            <div class="details">
                <h2>Product Name</h2>
                <div class="pricing">
                    <span class="price">$99.99</span>
                    <span class="discount">20% off</span>
                </div>
            </div>
        </div>
        """

        rules = [
            ExtractionRule(name="name", selector=".product .details h2"),
            ExtractionRule(name="price", selector=".product .pricing .price"),
            ExtractionRule(name="discount", selector=".product .pricing .discount"),
        ]

        for rule in rules:
            scraper.add_extraction_rule(rule)

        mock_response = create_mock_response(content=html)

        with patch.object(scraper, "_make_request", return_value=mock_response):
            result = await scraper.scrape("https://example.com")

        assert result.data.extracted_data["name"] == "Product Name"
        assert result.data.extracted_data["price"] == "$99.99"
        assert result.data.extracted_data["discount"] == "20% off"

    @pytest.mark.asyncio
    async def test_mixed_extraction_methods(self):
        """Test mixing CSS, XPath, and regex extraction."""
        scraper = HttpScraper()

        html = """
        <html>
            <body>
                <h1>Page Title</h1>
                <div id="content">
                    <p>Price: $49.99</p>
                    <p>Email: contact@example.com</p>
                </div>
            </body>
        </html>
        """

        rules = [
            ExtractionRule(name="title", selector="h1"),  # CSS
            ExtractionRule(name="content_text", xpath="//div[@id='content']/p[1]"),  # XPath
            ExtractionRule(name="price", regex=r"\$(\d+\.\d+)"),  # Regex
            ExtractionRule(name="email", regex=r"[\w\.-]+@[\w\.-]+"),  # Regex
        ]

        for rule in rules:
            scraper.add_extraction_rule(rule)

        mock_response = create_mock_response(content=html)

        with patch.object(scraper, "_make_request", return_value=mock_response):
            result = await scraper.scrape("https://example.com")

        assert result.data.extracted_data["title"] == "Page Title"
        assert "Price" in str(result.data.extracted_data["content_text"])
        assert result.data.extracted_data["price"] == "49.99"
        assert result.data.extracted_data["email"] == "contact@example.com"
