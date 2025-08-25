"""Tests for HTTP scraper session management."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from scrap_e.core.models import HttpRequest
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
    response = Mock()
    response.status_code = 200
    response.text = "<html><body><h1>Test Page</h1></body></html>"
    response.content = response.text.encode()
    response.headers = {"content-type": "text/html"}
    response.url = "https://example.com"
    response.raise_for_status = Mock()
    return response


class TestHttpScraperSession:
    """Tests for HTTP scraper session management."""

    @pytest.mark.asyncio
    async def test_session_context_manager(self, http_scraper, mock_response):
        """Test HTTP scraper session context manager."""
        mock_response.text = "<html><body>Test</body></html>"

        async with http_scraper.session() as session:
            with patch.object(session, "_make_request", return_value=mock_response):
                result = await session.scrape("https://example.com")
                assert result.success is True
                assert isinstance(result.data, WebPageData)

    @pytest.mark.asyncio
    async def test_scrape_with_session_cookies(self, http_scraper):
        """Test scraping multiple URLs with session cookies."""
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.text = "Login Page"
        mock_response1.headers = {"set-cookie": "session=abc123; path=/; secure"}
        mock_response1.url = "https://example.com/login"
        mock_response1.raise_for_status = Mock()

        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.text = "Protected Page"
        mock_response2.headers = {"set-cookie": "user=john; path=/"}
        mock_response2.url = "https://example.com/protected"
        mock_response2.raise_for_status = Mock()

        mock_response3 = Mock()
        mock_response3.status_code = 200
        mock_response3.text = "Another Protected Page"
        mock_response3.headers = {}
        mock_response3.url = "https://example.com/another"
        mock_response3.raise_for_status = Mock()

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(
                side_effect=[mock_response1, mock_response2, mock_response3]
            )

            urls = [
                "https://example.com/login",
                "https://example.com/protected",
                "https://example.com/another",
            ]
            results = await http_scraper.scrape_with_session(
                urls, initial_cookies={"initial": "cookie"}
            )

            assert len(results) == 3
            assert all(r.success for r in results)
            assert results[0].data.content == "Login Page"
            assert results[1].data.content == "Protected Page"
            assert results[2].data.content == "Another Protected Page"

            # Verify cookies were passed along
            call_args_list = mock_client.request.call_args_list
            # First call should have initial cookies
            assert call_args_list[0][1]["cookies"] == {"initial": "cookie"}
            # Second call should have accumulated cookies
            assert "cookies" in call_args_list[1][1]
            # Third call should have all accumulated cookies
            assert "cookies" in call_args_list[2][1]

    @pytest.mark.asyncio
    async def test_session_cookie_parsing(self, http_scraper):
        """Test parsing of set-cookie headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Page"
        # Multiple set-cookie headers
        mock_response.headers = {"set-cookie": "key1=value1; path=/; secure, key2=value2; httponly"}
        mock_response.url = "https://example.com"
        mock_response.raise_for_status = Mock()

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)

            results = await http_scraper.scrape_with_session(["https://example.com"])

            assert len(results) == 1
            assert results[0].success

    @pytest.mark.asyncio
    async def test_session_cookie_persistence(self, http_scraper):
        """Test that cookies persist across multiple requests in a session."""
        responses = []
        for i in range(5):
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.text = f"Page {i}"
            mock_resp.headers = {"set-cookie": f"cookie{i}=value{i}; path=/"}
            mock_resp.url = f"https://example.com/page{i}"
            mock_resp.raise_for_status = Mock()
            responses.append(mock_resp)

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(side_effect=responses)

            urls = [f"https://example.com/page{i}" for i in range(5)]
            results = await http_scraper.scrape_with_session(urls)

            assert len(results) == 5
            assert all(r.success for r in results)

            # Verify cookies accumulate
            call_args_list = mock_client.request.call_args_list
            for i in range(1, 5):
                # Each subsequent call should have cookies from previous responses
                assert "cookies" in call_args_list[i][1]

    @pytest.mark.asyncio
    async def test_session_with_authentication(self, http_scraper):
        """Test session-based authentication flow."""
        # Login response with auth token
        login_response = Mock()
        login_response.status_code = 200
        login_response.text = '{"token": "auth_token_123"}'
        login_response.headers = {"set-cookie": "auth_token=auth_token_123; path=/; httponly"}
        login_response.url = "https://api.example.com/login"
        login_response.raise_for_status = Mock()

        # Protected endpoint response
        protected_response = Mock()
        protected_response.status_code = 200
        protected_response.text = '{"data": "protected data"}'
        protected_response.headers = {}
        protected_response.url = "https://api.example.com/protected"
        protected_response.raise_for_status = Mock()

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(side_effect=[login_response, protected_response])

            # First login, then access protected resource
            urls = ["https://api.example.com/login", "https://api.example.com/protected"]
            results = await http_scraper.scrape_with_session(urls)

            assert len(results) == 2
            assert all(r.success for r in results)

            # Verify auth token was passed to protected endpoint
            protected_call = mock_client.request.call_args_list[1]
            assert "cookies" in protected_call[1]

    @pytest.mark.asyncio
    async def test_session_with_custom_headers(self, http_scraper, mock_response):
        """Test maintaining custom headers across session requests."""
        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(return_value=mock_response)

            # Set custom headers for the session
            http_scraper.config.headers = {
                "X-Custom-Header": "custom_value",
                "Authorization": "Bearer token",
            }

            urls = ["https://example.com/page1", "https://example.com/page2"]
            results = await http_scraper.scrape_with_session(urls)

            assert len(results) == 2

            # Verify custom headers were included in all requests
            for call in mock_client.request.call_args_list:
                headers = call[1]["headers"]
                assert "X-Custom-Header" in headers
                assert headers["X-Custom-Header"] == "custom_value"
                assert "Authorization" in headers

    @pytest.mark.asyncio
    async def test_session_error_handling(self, http_scraper):
        """Test error handling in session scraping."""
        success_response = Mock()
        success_response.status_code = 200
        success_response.text = "Success"
        success_response.headers = {}
        success_response.url = "https://example.com/success"
        success_response.raise_for_status = Mock()

        with patch.object(http_scraper, "_client") as mock_client:
            # Mix of successful and failed requests
            mock_client.request = AsyncMock(
                side_effect=[
                    success_response,
                    httpx.HTTPError("Connection failed"),
                    success_response,
                ]
            )

            urls = [
                "https://example.com/page1",
                "https://example.com/error",
                "https://example.com/page3",
            ]

            # Session should continue despite individual failures
            results = await http_scraper.scrape_with_session(urls)

            assert len(results) == 3
            assert results[0].success is True
            assert results[1].success is False
            assert results[1].error is not None
            assert results[2].success is True

    @pytest.mark.asyncio
    async def test_client_initialization(self, http_scraper):
        """Test HTTP client initialization."""
        await http_scraper._initialize()
        assert http_scraper._client is not None

        # Test that re-initialization doesn't create duplicate clients
        first_client = http_scraper._client
        await http_scraper._initialize()
        assert http_scraper._client is first_client

    @pytest.mark.asyncio
    async def test_client_cleanup(self, http_scraper):
        """Test HTTP client cleanup."""
        await http_scraper._initialize()
        assert http_scraper._client is not None

        await http_scraper._cleanup()
        assert http_scraper._client is None

        # Test cleanup when no client exists
        await http_scraper._cleanup()  # Should not raise

    @pytest.mark.asyncio
    async def test_make_request_with_cookies(self, http_scraper, mock_response):
        """Test making requests with cookies."""
        mock_client = Mock()
        mock_client.aclose = AsyncMock()  # Add async aclose method for cleanup
        mock_client.request = AsyncMock(return_value=mock_response)
        http_scraper._client = mock_client

        request = HttpRequest(
            url="https://example.com", cookies={"session": "abc123", "user_id": "42"}
        )

        await http_scraper._make_request(request)

        http_scraper._client.request.assert_called_once()
        call_kwargs = http_scraper._client.request.call_args[1]
        assert "cookies" in call_kwargs
        assert call_kwargs["cookies"] == {"session": "abc123", "user_id": "42"}

    @pytest.mark.asyncio
    async def test_concurrent_session_requests(self, http_scraper):
        """Test concurrent requests within a session."""
        # Create multiple mock responses
        responses = []
        for i in range(10):
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.text = f"Page {i}"
            mock_resp.headers = {}
            mock_resp.url = f"https://example.com/page{i}"
            mock_resp.raise_for_status = Mock()
            responses.append(mock_resp)

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(side_effect=responses)

            urls = [f"https://example.com/page{i}" for i in range(10)]

            # Use scrape_multiple which handles concurrency
            results = await http_scraper.scrape_multiple(urls, max_concurrent=5)

            assert len(results) == 10
            assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_session_with_redirects(self, http_scraper):
        """Test session handling with redirects."""
        # Initial response with redirect
        redirect_response = Mock()
        redirect_response.status_code = 302
        redirect_response.headers = {
            "location": "https://example.com/redirected",
            "set-cookie": "redirect_cookie=value; path=/",
        }
        redirect_response.url = "https://example.com/original"
        redirect_response.raise_for_status = Mock()

        # Final response after redirect
        final_response = Mock()
        final_response.status_code = 200
        final_response.text = "Final Page"
        final_response.headers = {}
        final_response.url = "https://example.com/redirected"
        final_response.raise_for_status = Mock()

        mock_client = Mock()
        mock_client.aclose = AsyncMock()  # Add async aclose method for cleanup
        mock_client.request = AsyncMock(return_value=final_response)
        http_scraper._client = mock_client

        request = HttpRequest(url="https://example.com/original", follow_redirects=True)

        result = await http_scraper._make_request(request)

        assert result.status_code == 200
        assert result.text == "Final Page"
