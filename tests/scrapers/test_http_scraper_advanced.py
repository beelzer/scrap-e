"""Advanced tests for HttpScraper to improve coverage."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from scrap_e.core.config import PaginationConfig
from scrap_e.core.exceptions import ConnectionError, ScraperError
from scrap_e.core.models import (
    ExtractionRule,
    HttpRequest,
    ScraperMetadata,
    ScraperResult,
    ScraperType,
)
from scrap_e.scrapers.web.http_scraper import HttpScraper, WebPageData


@pytest.fixture
async def http_scraper():
    """Create an HTTP scraper instance."""
    scraper = HttpScraper()
    yield scraper
    if scraper._client and hasattr(scraper._client, "aclose"):
        await scraper._cleanup()


@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""
    response = Mock(spec=httpx.Response)
    response.status_code = 200
    response.text = "<html><body><h1>Test Page</h1></body></html>"
    response.content = response.text.encode()
    response.headers = {"content-type": "text/html"}
    response.url = "https://example.com"
    response.raise_for_status = Mock()
    return response


class TestHttpScraperAdvanced:
    """Advanced tests for HttpScraper."""

    @pytest.mark.asyncio
    async def test_scrape_with_extraction_rules(self, http_scraper, mock_response):
        """Test scraping with extraction rules."""
        mock_response.text = """
        <html>
            <body>
                <h1>Product Title</h1>
                <span class="price">$99.99</span>
                <div class="description">Great product</div>
            </body>
        </html>
        """

        rules = [
            ExtractionRule(name="title", selector="h1"),
            ExtractionRule(name="price", selector=".price", transform="strip"),
            ExtractionRule(name="description", selector=".description"),
        ]

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)

            result = await http_scraper._scrape("https://example.com", extraction_rules=rules)

            assert result.extracted_data is not None
            assert result.extracted_data["title"] == "Product Title"
            assert result.extracted_data["price"] == "$99.99"
            assert result.extracted_data["description"] == "Great product"

    @pytest.mark.asyncio
    async def test_scrape_with_stored_extraction_rules(self, http_scraper, mock_response):
        """Test scraping with stored extraction rules."""
        mock_response.text = "<html><body><h1>Title</h1></body></html>"

        rule = ExtractionRule(name="title", selector="h1")
        http_scraper.add_extraction_rule(rule)

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)

            result = await http_scraper._scrape("https://example.com")

            assert result.extracted_data is not None
            assert result.extracted_data["title"] == "Title"

        # Test clearing rules
        http_scraper.clear_extraction_rules()
        assert len(http_scraper.extraction_rules) == 0

    @pytest.mark.asyncio
    async def test_scrape_with_metadata_extraction(self, http_scraper, mock_response):
        """Test metadata extraction."""
        mock_response.text = """
        <html>
            <head>
                <title>Page Title</title>
                <meta name="description" content="Page description">
            </head>
            <body>Content</body>
        </html>
        """

        http_scraper.config.extract_metadata = True

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)

            result = await http_scraper._scrape("https://example.com")

            assert result.metadata is not None
            assert result.metadata["title"] == "Page Title"
            assert result.metadata["description"] == "Page description"

    @pytest.mark.asyncio
    async def test_scrape_with_link_extraction(self, http_scraper, mock_response):
        """Test link extraction."""
        mock_response.text = """
        <html>
            <body>
                <a href="/page1">Link 1</a>
                <a href="https://external.com">External</a>
            </body>
        </html>
        """

        http_scraper.config.extract_links = True

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)

            result = await http_scraper._scrape("https://example.com")

            assert result.links is not None
            assert len(result.links) >= 2

    @pytest.mark.asyncio
    async def test_scrape_with_image_extraction(self, http_scraper, mock_response):
        """Test image extraction."""
        mock_response.text = """
        <html>
            <body>
                <img src="/image1.jpg" alt="Image 1">
                <img src="https://cdn.example.com/image2.png">
            </body>
        </html>
        """

        http_scraper.config.extract_images = True

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)

            result = await http_scraper._scrape("https://example.com")

            assert result.images is not None
            assert len(result.images) >= 2

    @pytest.mark.asyncio
    async def test_build_request_with_all_params(self, http_scraper):
        """Test building request with all parameters."""
        request = http_scraper._build_request(
            "https://example.com",
            method="POST",
            headers={"X-Custom": "value"},
            params={"q": "search"},
            data="form_data",
            json={"key": "value"},
            timeout=60,
            follow_redirects=False,
            verify_ssl=False,
            cookies={"session": "abc123"},
        )

        assert request.method.value == "POST"
        assert request.headers["X-Custom"] == "value"
        assert request.headers["User-Agent"] == http_scraper.config.user_agent
        assert request.params == {"q": "search"}
        assert request.data == "form_data"
        assert request.json_data == {"key": "value"}
        assert request.timeout == 60
        assert request.follow_redirects is False
        assert request.verify_ssl is False
        assert request.cookies == {"session": "abc123"}

    @pytest.mark.asyncio
    async def test_make_request_with_cookies(self, mock_response):
        """Test making request with cookies."""
        http_scraper = HttpScraper()
        http_scraper._client = Mock()
        http_scraper._client.request = AsyncMock(return_value=mock_response)

        request = HttpRequest(url="https://example.com", cookies={"session": "abc123"})

        await http_scraper._make_request(request)

        http_scraper._client.request.assert_called_once()
        call_kwargs = http_scraper._client.request.call_args[1]
        assert "cookies" in call_kwargs
        assert call_kwargs["cookies"] == {"session": "abc123"}

    @pytest.mark.asyncio
    async def test_make_request_with_json_data(self, mock_response):
        """Test making request with JSON data."""
        http_scraper = HttpScraper()
        http_scraper._client = Mock()
        http_scraper._client.request = AsyncMock(return_value=mock_response)

        request = HttpRequest(url="https://example.com", method="POST", json_data={"key": "value"})

        await http_scraper._make_request(request)

        http_scraper._client.request.assert_called_once()
        call_kwargs = http_scraper._client.request.call_args[1]
        assert "json" in call_kwargs
        assert call_kwargs["json"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_extract_data_with_parsing_error(self, http_scraper):
        """Test extraction with parsing error handling."""
        content = "<html><body>Content</body></html>"

        # Rule that will fail - use a truly invalid selector
        rule_required = ExtractionRule(
            name="required_field", selector=".nonexistent", required=True, default=None
        )

        # This should not raise an error, but return None/default
        result = await http_scraper._extract_data(content, [rule_required])
        assert result["required_field"] is None

        # Rule with default value
        rule_optional = ExtractionRule(
            name="optional_field",
            selector=".nonexistent",
            required=False,
            default="default_value",
        )

        result = await http_scraper._extract_data(content, [rule_optional])
        assert result["optional_field"] == "default_value"

    @pytest.mark.asyncio
    async def test_extract_data_empty_content(self, http_scraper):
        """Test extraction with empty content."""
        result = await http_scraper._extract_data("", [])
        assert result == {}

        result = await http_scraper._extract_data(None, [])
        assert result == {}

    @pytest.mark.asyncio
    async def test_stream_scrape(self):
        """Test stream scraping for large responses."""
        # Create mock streaming response
        http_scraper = HttpScraper()
        mock_client = Mock()
        http_scraper._client = mock_client

        chunks = ["chunk1", "chunk2", "chunk3"] * 5  # 15 chunks total

        async def mock_aiter_text(chunk_size):
            for chunk in chunks:
                yield chunk

        mock_stream = AsyncMock()
        mock_stream.aiter_text = mock_aiter_text
        mock_stream.url = "https://example.com"
        mock_stream.status_code = 200
        mock_stream.headers = {}
        mock_stream.raise_for_status = Mock()
        mock_stream.__aenter__ = AsyncMock(return_value=mock_stream)
        mock_stream.__aexit__ = AsyncMock()

        mock_client.stream = Mock(return_value=mock_stream)

        results = []
        async for data in http_scraper._stream_scrape("https://example.com", chunk_size=1024):
            results.append(data)

        # Should yield partial results every 10 chunks + final chunk
        assert len(results) == 2  # One partial (10 chunks) + final (5 chunks)
        assert all(isinstance(r, WebPageData) for r in results)

    @pytest.mark.asyncio
    async def test_validate_source_success(self):
        """Test successful source validation."""
        http_scraper = HttpScraper()
        mock_client = Mock()
        http_scraper._client = mock_client

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_client.head = AsyncMock(return_value=mock_response)

        await http_scraper._validate_source("https://example.com")

        mock_client.head.assert_called_once_with("https://example.com", follow_redirects=True)

    @pytest.mark.asyncio
    async def test_validate_source_failure(self):
        """Test source validation failure."""
        http_scraper = HttpScraper()
        mock_client = Mock()
        http_scraper._client = mock_client

        mock_client.head = AsyncMock(side_effect=httpx.HTTPError("404 Not Found"))

        with pytest.raises(ConnectionError) as exc_info:
            await http_scraper._validate_source("https://example.com")

        assert "URL validation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_next_page_from_extracted_data(self, http_scraper):
        """Test getting next page from extracted data."""
        result = ScraperResult(
            success=True,
            data=WebPageData(
                url="https://example.com/page1",
                status_code=200,
                headers={},
                extracted_data={"next_page_url": "https://example.com/page2"},
            ),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP, source="https://example.com/page1"
            ),
        )

        next_url = await http_scraper._get_next_page("https://example.com/page1", result, 1)
        assert next_url == "https://example.com/page2"

    @pytest.mark.asyncio
    async def test_get_next_page_from_selector(self, http_scraper):
        """Test getting next page from CSS selector."""
        http_scraper.config.pagination = PaginationConfig(enabled=True, next_page_selector="a.next")

        result = ScraperResult(
            success=True,
            data=WebPageData(
                url="https://example.com/page1",
                status_code=200,
                headers={},
                content='<html><body><a class="next" href="/page2">Next</a></body></html>',
            ),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP, source="https://example.com/page1"
            ),
        )

        next_url = await http_scraper._get_next_page("https://example.com/page1", result, 1)
        assert next_url == "https://example.com/page2"

    @pytest.mark.asyncio
    async def test_get_next_page_from_url_pattern(self, http_scraper):
        """Test getting next page from URL pattern."""
        http_scraper.config.pagination = PaginationConfig(
            enabled=True, next_page_url_pattern="https://example.com/page/{page}"
        )

        result = ScraperResult(
            success=True,
            data=WebPageData(url="https://example.com/page/1", status_code=200, headers={}),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP, source="https://example.com/page/1"
            ),
        )

        next_url = await http_scraper._get_next_page("https://example.com/page/1", result, 1)
        assert next_url == "https://example.com/page/2"

    @pytest.mark.asyncio
    async def test_get_next_page_no_pagination(self, http_scraper):
        """Test getting next page with no pagination."""
        result = ScraperResult(
            success=True,
            data=WebPageData(url="https://example.com", status_code=200, headers={}),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP, source="https://example.com"
            ),
        )

        next_url = await http_scraper._get_next_page("https://example.com", result, 1)
        assert next_url is None

    @pytest.mark.asyncio
    async def test_scrape_sitemap(self):
        """Test sitemap scraping."""
        http_scraper = HttpScraper()
        mock_client = Mock()
        http_scraper._client = mock_client

        # Simple sitemap
        sitemap_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/page1</loc></url>
            <url><loc>https://example.com/page2</loc></url>
        </urlset>"""

        mock_response = Mock()
        mock_response.content = sitemap_xml
        mock_response.raise_for_status = Mock()
        mock_client.get = AsyncMock(return_value=mock_response)

        urls = await http_scraper.scrape_sitemap("https://example.com/sitemap.xml")

        assert len(urls) == 2
        assert "https://example.com/page1" in urls
        assert "https://example.com/page2" in urls

    @pytest.mark.asyncio
    async def test_scrape_sitemap_index(self):
        """Test sitemap index scraping."""
        http_scraper = HttpScraper()
        mock_client = Mock()
        http_scraper._client = mock_client

        # Sitemap index
        sitemap_index = b"""<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap><loc>https://example.com/sitemap1.xml</loc></sitemap>
        </sitemapindex>"""

        # Child sitemap
        sitemap1 = b"""<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/page1</loc></url>
        </urlset>"""

        responses = [Mock(content=sitemap_index), Mock(content=sitemap1)]
        for r in responses:
            r.raise_for_status = Mock()

        mock_client.get = AsyncMock(side_effect=responses)

        urls = await http_scraper.scrape_sitemap("https://example.com/sitemap_index.xml")

        assert len(urls) == 1
        assert "https://example.com/page1" in urls

    @pytest.mark.asyncio
    async def test_scrape_with_session(self, http_scraper):
        """Test scraping multiple URLs with session cookies."""
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.text = "Page 1"
        mock_response1.headers = {"set-cookie": "session=abc123; path=/"}
        mock_response1.url = "https://example.com/page1"
        mock_response1.raise_for_status = Mock()

        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.text = "Page 2"
        mock_response2.headers = {"set-cookie": "user=john; path=/"}
        mock_response2.url = "https://example.com/page2"
        mock_response2.raise_for_status = Mock()

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(side_effect=[mock_response1, mock_response2])

            urls = ["https://example.com/page1", "https://example.com/page2"]
            results = await http_scraper.scrape_with_session(urls, {"initial": "cookie"})

            assert len(results) == 2
            assert all(r.success for r in results)

            # Check that cookies were passed to second request
            second_call_kwargs = mock_client.request.call_args_list[1][1]
            assert "cookies" in second_call_kwargs

    @pytest.mark.asyncio
    async def test_scrape_with_session_cookie_parsing(self, http_scraper):
        """Test session cookie parsing from set-cookie headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Page"
        mock_response.headers = {"set-cookie": "key1=value1; path=/, key2=value2; secure"}
        mock_response.url = "https://example.com"
        mock_response.raise_for_status = Mock()

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)

            results = await http_scraper.scrape_with_session(["https://example.com"])

            assert len(results) == 1
            assert results[0].success

    @pytest.mark.asyncio
    async def test_scrape_error_handling(self, http_scraper):
        """Test error handling during scraping."""
        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(side_effect=httpx.HTTPError("Connection failed"))

            with pytest.raises(ConnectionError) as exc_info:
                await http_scraper._scrape("https://example.com")

            assert "HTTP error occurred" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_scrape_generic_exception(self, http_scraper):
        """Test handling of generic exceptions during scraping."""
        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(side_effect=Exception("Unknown error"))

            with pytest.raises(ScraperError) as exc_info:
                await http_scraper._scrape("https://example.com")

            assert "Failed to scrape" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self, http_scraper):
        """Test that initialize doesn't create duplicate clients."""
        await http_scraper._initialize()
        first_client = http_scraper._client

        await http_scraper._initialize()
        second_client = http_scraper._client

        assert first_client is second_client

    @pytest.mark.asyncio
    async def test_cleanup_no_client(self, http_scraper):
        """Test cleanup when no client exists."""
        await http_scraper._cleanup()  # Should not raise

    @pytest.mark.asyncio
    async def test_parse_response_no_content(self, http_scraper):
        """Test parsing response with no content."""
        mock_response = Mock()
        mock_response.text = ""
        mock_response.url = "https://example.com"
        mock_response.status_code = 200
        mock_response.headers = {}

        result = await http_scraper._parse_response(mock_response, "https://example.com")

        assert result.content == ""
        assert result.metadata is None
        assert result.links is None
        assert result.images is None
