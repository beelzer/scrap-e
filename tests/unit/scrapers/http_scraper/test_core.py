"""Core HTTP scraper functionality tests."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from scrap_e.scrapers.web.http_scraper import HttpScraper, WebPageData
from tests.fixtures import BASIC_HTML, create_mock_response, mock_http_error


class TestHttpScraperInitialization:
    """Test HTTP scraper initialization and configuration."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test HTTP scraper initialization."""
        scraper = HttpScraper()
        assert scraper is not None
        assert scraper.scraper_type.value == "web_http"
        assert scraper._client is None  # Client not created until first use

    @pytest.mark.asyncio
    async def test_initialization_with_config(self):
        """Test HTTP scraper initialization with custom config."""
        from scrap_e.core.config import WebScraperConfig

        config = WebScraperConfig(
            timeout=60,
            headers={"User-Agent": "Test Bot"},
            follow_redirects=False,
        )
        scraper = HttpScraper(config=config)

        assert scraper.config.timeout == 60
        assert scraper.config.headers["User-Agent"] == "Test Bot"
        assert scraper.config.follow_redirects is False

    @pytest.mark.asyncio
    async def test_client_creation(self, http_scraper):
        """Test lazy client creation."""
        assert http_scraper._client is None

        # Client should be created on initialization
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            await http_scraper._initialize()
            assert http_scraper._client is not None
            assert http_scraper._client == mock_client

    @pytest.mark.asyncio
    async def test_cleanup(self, http_scraper):
        """Test scraper cleanup."""
        # Create a mock client
        mock_client = AsyncMock()
        http_scraper._client = mock_client

        await http_scraper._cleanup()

        mock_client.aclose.assert_called_once()
        assert http_scraper._client is None


class TestHttpScraperBasicOperations:
    """Test basic HTTP scraping operations."""

    @pytest.mark.asyncio
    async def test_scrape_success(self, http_scraper):
        """Test successful HTTP scraping."""
        mock_response = create_mock_response(
            status_code=200,
            content=BASIC_HTML,
            headers={"content-type": "text/html"},
        )

        with patch.object(http_scraper, "_make_request", return_value=mock_response):
            result = await http_scraper.scrape("https://example.com")

            assert result.success is True
            assert result.data is not None
            assert isinstance(result.data, WebPageData)
            assert result.data.status_code == 200
            assert "Test Page" in result.data.content

    @pytest.mark.asyncio
    async def test_scrape_error_handling(self, http_scraper):
        """Test error handling during scraping."""
        error = mock_http_error(status_code=404, message="Not Found")

        with patch.object(http_scraper, "_make_request", side_effect=error):
            result = await http_scraper.scrape("https://example.com")

            assert result.success is False
            assert result.error is not None
            assert "404" in result.error

    @pytest.mark.asyncio
    async def test_scrape_connection_error(self, http_scraper):
        """Test connection error handling."""
        with patch.object(
            http_scraper, "_make_request", side_effect=httpx.ConnectError("Connection failed")
        ):
            result = await http_scraper.scrape("https://example.com")

            assert result.success is False
            assert result.error is not None
            assert "Connection" in result.error

    @pytest.mark.asyncio
    async def test_scrape_timeout(self, http_scraper):
        """Test timeout handling."""
        with patch.object(
            http_scraper, "_make_request", side_effect=httpx.TimeoutException("Request timed out")
        ):
            result = await http_scraper.scrape("https://example.com")

            assert result.success is False
            assert result.error is not None

    @pytest.mark.asyncio
    async def test_scrape_multiple_urls(self, http_scraper):
        """Test scraping multiple URLs."""
        urls = [
            "https://example1.com",
            "https://example2.com",
            "https://example3.com",
        ]

        mock_response = create_mock_response(content=BASIC_HTML)

        with patch.object(http_scraper, "_make_request", return_value=mock_response):
            results = await http_scraper.scrape_multiple(urls)

            assert len(results) == 3
            for result in results:
                assert result.success is True
                assert result.data is not None


class TestHttpScraperRequestBuilding:
    """Test HTTP request building and configuration."""

    @pytest.mark.asyncio
    async def test_build_request_basic(self, http_scraper):
        """Test basic request building."""
        from scrap_e.core.models import HttpRequest

        request = HttpRequest(
            url="https://example.com",
            method="GET",
        )

        mock_response = create_mock_response(content="Response")

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)

            await http_scraper._make_request(request)

            mock_client.request.assert_called_once()
            call_args = mock_client.request.call_args
            assert call_args[1]["method"] == "GET"
            assert str(call_args[1]["url"]) in ["https://example.com", "https://example.com/"]

    @pytest.mark.asyncio
    async def test_build_request_with_headers(self, http_scraper):
        """Test request building with custom headers."""
        from scrap_e.core.models import HttpRequest

        request = HttpRequest(
            url="https://example.com",
            headers={"Authorization": "Bearer token"},
        )

        mock_response = create_mock_response()

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)

            await http_scraper._make_request(request)

            call_args = mock_client.request.call_args
            assert "Authorization" in call_args[1]["headers"]

    @pytest.mark.asyncio
    async def test_build_request_with_data(self, http_scraper):
        """Test request building with POST data."""
        from scrap_e.core.models import HttpRequest

        request = HttpRequest(
            url="https://example.com",
            method="POST",
            data={"key": "value"},
        )

        mock_response = create_mock_response()

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)

            await http_scraper._make_request(request)

            call_args = mock_client.request.call_args
            assert call_args[1]["method"] == "POST"
            assert "data" in call_args[1] or "json" in call_args[1]

    @pytest.mark.asyncio
    async def test_build_request_with_params(self, http_scraper):
        """Test request building with query parameters."""
        from scrap_e.core.models import HttpRequest

        request = HttpRequest(
            url="https://example.com",
            params={"q": "search", "page": "1"},
        )

        mock_response = create_mock_response()

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)

            await http_scraper._make_request(request)

            call_args = mock_client.request.call_args
            assert "params" in call_args[1]
            assert call_args[1]["params"]["q"] == "search"


class TestHttpScraperRetry:
    """Test retry functionality."""

    @pytest.mark.skip(reason="Retry functionality not yet implemented")
    @pytest.mark.asyncio
    async def test_retry_on_failure(self, http_scraper):
        """Test retry on request failure."""
        http_scraper.config.retry_count = 3

        # Fail twice, then succeed
        responses = [
            httpx.HTTPStatusError("Error", request=None, response=MagicMock(status_code=500)),
            httpx.HTTPStatusError("Error", request=None, response=MagicMock(status_code=500)),
            create_mock_response(content="Success"),
        ]

        with patch.object(http_scraper, "_make_request", side_effect=responses):
            result = await http_scraper.scrape("https://example.com")

            assert result.success is True
            assert result.data is not None

    @pytest.mark.skip(reason="Retry functionality not yet implemented")
    @pytest.mark.asyncio
    async def test_retry_exhaustion(self, http_scraper):
        """Test retry exhaustion."""
        http_scraper.config.retry_count = 2

        error = httpx.HTTPStatusError("Error", request=None, response=MagicMock(status_code=500))

        with patch.object(http_scraper, "_make_request", side_effect=error):
            result = await http_scraper.scrape("https://example.com")

            assert result.success is False
            assert result.error is not None

    @pytest.mark.skip(reason="Retry functionality not yet implemented")
    @pytest.mark.asyncio
    async def test_no_retry_on_client_error(self, http_scraper):
        """Test no retry on 4xx errors."""
        http_scraper.config.retry_count = 3

        error = mock_http_error(status_code=404)

        with patch.object(http_scraper, "_make_request", side_effect=error) as mock:
            result = await http_scraper.scrape("https://example.com")

            # Should only be called once (no retry for 404)
            assert mock.call_count == 1
            assert result.success is False
