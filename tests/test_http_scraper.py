"""Tests for HTTP scraper."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from scrap_e.core.models import ExtractionRule
from scrap_e.scrapers.web.http_scraper import HttpScraper, WebPageData


@pytest.mark.asyncio
async def test_http_scraper_initialization():
    """Test HTTP scraper initialization."""
    scraper = HttpScraper()
    assert scraper is not None
    assert scraper.scraper_type.value == "web_http"


@pytest.mark.asyncio
async def test_http_scraper_scrape_success():
    """Test successful HTTP scraping."""
    scraper = HttpScraper()

    # Mock HTTP response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body><h1>Test Page</h1></body></html>"
    mock_response.headers = {"content-type": "text/html"}
    mock_response.url = "https://example.com"
    mock_response.raise_for_status = MagicMock()

    with patch.object(scraper, "_make_request", return_value=mock_response):
        result = await scraper.scrape("https://example.com")

        assert result.success is True
        assert result.data is not None
        assert isinstance(result.data, WebPageData)
        assert result.data.status_code == 200
        assert "<h1>Test Page</h1>" in result.data.content


@pytest.mark.asyncio
async def test_http_scraper_with_extraction_rules():
    """Test HTTP scraping with extraction rules."""
    scraper = HttpScraper()

    # Add extraction rule
    rule = ExtractionRule(name="title", selector="h1", required=False)
    scraper.add_extraction_rule(rule)

    # Mock HTTP response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body><h1>Test Title</h1></body></html>"
    mock_response.headers = {"content-type": "text/html"}
    mock_response.url = "https://example.com"
    mock_response.raise_for_status = MagicMock()

    with patch.object(scraper, "_make_request", return_value=mock_response):
        result = await scraper.scrape("https://example.com")

        assert result.success is True
        assert result.data.extracted_data is not None
        assert result.data.extracted_data["title"] == "Test Title"


@pytest.mark.asyncio
async def test_http_scraper_error_handling():
    """Test HTTP scraper error handling."""
    scraper = HttpScraper()

    with patch.object(
        scraper, "_make_request", side_effect=httpx.HTTPError("Connection failed")
    ):
        result = await scraper.scrape("https://example.com")

        assert result.success is False
        assert result.error is not None
        assert "HTTP error occurred" in result.error


@pytest.mark.asyncio
async def test_http_scraper_multiple_urls():
    """Test scraping multiple URLs."""
    scraper = HttpScraper()

    urls = ["https://example1.com", "https://example2.com", "https://example3.com"]

    # Mock responses
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Test</body></html>"
    mock_response.headers = {}
    mock_response.url = "https://example.com"
    mock_response.raise_for_status = MagicMock()

    with patch.object(scraper, "_make_request", return_value=mock_response):
        results = await scraper.scrape_multiple(urls, max_concurrent=2)

        assert len(results) == 3
        assert all(r.success for r in results)


@pytest.mark.asyncio
async def test_http_scraper_metadata_extraction():
    """Test metadata extraction from HTML."""
    scraper = HttpScraper()
    scraper.config.extract_metadata = True

    html_content = """
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="Test description">
        <meta name="keywords" content="test, scraper">
        <meta property="og:title" content="OG Title">
    </head>
    <body><h1>Content</h1></body>
    </html>
    """

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = html_content
    mock_response.headers = {}
    mock_response.url = "https://example.com"
    mock_response.raise_for_status = MagicMock()

    with patch.object(scraper, "_make_request", return_value=mock_response):
        result = await scraper.scrape("https://example.com")

        assert result.success is True
        assert result.data.metadata is not None
        assert result.data.metadata["title"] == "Test Page"
        assert result.data.metadata["description"] == "Test description"
        assert result.data.metadata["keywords"] == "test, scraper"


@pytest.mark.asyncio
async def test_http_scraper_session_context():
    """Test HTTP scraper session context manager."""
    scraper = HttpScraper()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Test</body></html>"
    mock_response.headers = {}
    mock_response.url = "https://example.com"
    mock_response.raise_for_status = MagicMock()

    async with scraper.session() as s:
        with patch.object(s, "_make_request", return_value=mock_response):
            result = await s.scrape("https://example.com")
            assert result.success is True
