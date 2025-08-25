"""Advanced tests for BrowserScraper features."""

from unittest.mock import AsyncMock, patch

import pytest

from scrap_e.core.models import ScraperMetadata, ScraperResult, ScraperType
from scrap_e.scrapers.web.browser_scraper import BrowserPageData, BrowserScraper


@pytest.fixture
async def browser_scraper():
    """Create a browser scraper instance."""
    scraper = BrowserScraper()
    yield scraper
    if scraper._playwright:
        await scraper._cleanup()


@pytest.fixture
def mock_playwright_spa():
    """Create a mock playwright setup for SPA testing."""
    mock_page = AsyncMock()
    mock_page.url = "https://example.com"
    mock_page.title = AsyncMock(return_value="SPA Test")
    mock_page.content = AsyncMock(return_value="<html><body>SPA Content</body></html>")
    mock_page.goto = AsyncMock()
    mock_page.close = AsyncMock()
    mock_page.evaluate = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=b"screenshot_data")

    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()

    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    mock_browser_type = AsyncMock()
    mock_browser_type.launch = AsyncMock(return_value=mock_browser)

    mock_playwright = AsyncMock()
    mock_playwright.chromium = mock_browser_type
    mock_playwright.stop = AsyncMock()

    return {
        "playwright": mock_playwright,
        "browser": mock_browser,
        "context": mock_context,
        "page": mock_page,
    }


class TestBrowserScraperAdvanced:
    """Advanced tests for BrowserScraper features."""

    @pytest.mark.asyncio
    async def test_capture_screenshot(self, browser_scraper):
        """Test screenshot capture."""
        mock_page = AsyncMock()
        mock_page.screenshot = AsyncMock(return_value=b"screenshot_data")

        screenshot = await browser_scraper._capture_screenshot(mock_page, full_page=False)

        assert screenshot == b"screenshot_data"
        mock_page.screenshot.assert_called_once_with(full_page=False, type="png")

    @pytest.mark.asyncio
    async def test_capture_screenshot_jpeg(self, browser_scraper):
        """Test JPEG screenshot capture with quality."""
        mock_page = AsyncMock()
        mock_page.screenshot = AsyncMock(return_value=b"jpeg_data")

        browser_scraper.config.screenshot_format = "jpeg"
        browser_scraper.config.screenshot_quality = 80

        await browser_scraper._capture_screenshot(mock_page)

        mock_page.screenshot.assert_called_once_with(full_page=True, type="jpeg", quality=80)

    @pytest.mark.asyncio
    async def test_scrape_with_screenshot(self, browser_scraper, mock_playwright_spa):
        """Test scraping with screenshot capture."""
        browser_scraper.config.capture_screenshots = True

        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_spa["playwright"]
            )

            result = await browser_scraper._scrape("https://example.com")

            assert result.screenshot == b"screenshot_data"
            mock_playwright_spa["page"].screenshot.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_next_page(self, browser_scraper):
        """Test getting next page URL."""
        # Test with extracted data containing the next page URL
        result = ScraperResult(
            success=True,
            data=BrowserPageData(
                url="https://example.com/page1",
                extracted_data={"next_page_url": "https://example.com/page2"},
            ),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_BROWSER, source="https://example.com/page1"
            ),
        )

        next_url = await browser_scraper._get_next_page("https://example.com/page1", result, 1)
        assert next_url == "https://example.com/page2"

        # Test with no next page
        result.data.extracted_data = {}
        next_url = await browser_scraper._get_next_page("https://example.com/page1", result, 1)
        assert next_url is None

    @pytest.mark.asyncio
    async def test_scrape_spa(self, browser_scraper, mock_playwright_spa):
        """Test scraping Single Page Application."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_spa["playwright"]
            )

            routes = ["#/about", "#/contact", "#/products"]
            results = await browser_scraper.scrape_spa("https://example.com", routes)

            assert len(results) == 4  # Initial page + 3 routes
            assert all(isinstance(r, BrowserPageData) for r in results)
            # Verify navigation to routes
            assert mock_playwright_spa["page"].evaluate.call_count >= len(routes)

    @pytest.mark.asyncio
    async def test_scrape_spa_with_wait_time(self, browser_scraper, mock_playwright_spa):
        """Test SPA scraping with custom wait time."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_spa["playwright"]
            )

            routes = ["#/page1"]
            results = await browser_scraper.scrape_spa(
                "https://example.com", routes, wait_after_navigation=3
            )

            assert len(results) == 2
            # Verify wait was called after navigation
            assert mock_playwright_spa["page"].wait_for_timeout.called

    @pytest.mark.asyncio
    async def test_scrape_infinite_scroll(self, browser_scraper, mock_playwright_spa):
        """Test scraping infinite scroll page."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_spa["playwright"]
            )

            # Simulate scroll height changes
            scroll_heights = [1000, 2000, 3000, 3000]  # The last scroll shows no new content
            mock_playwright_spa["page"].evaluate = AsyncMock(
                side_effect=scroll_heights + [None] * 10
            )

            result = await browser_scraper.scrape_infinite_scroll(
                "https://example.com", max_scrolls=5
            )

            assert isinstance(result, BrowserPageData)
            # Verify scrolling occurred
            assert mock_playwright_spa["page"].evaluate.call_count >= 4

    @pytest.mark.asyncio
    async def test_scrape_infinite_scroll_with_wait(self, browser_scraper, mock_playwright_spa):
        """Test infinite scroll with wait between scrolls."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_spa["playwright"]
            )

            # Simulate the immediate end (no new content)
            # Need values for: scrollHeight, scrollTo, scrollHeight again
            mock_playwright_spa["page"].evaluate = AsyncMock(side_effect=[1000, None, 1000])

            with patch("asyncio.sleep") as mock_sleep:
                result = await browser_scraper.scrape_infinite_scroll(
                    "https://example.com", max_scrolls=3, wait_between_scrolls=2
                )

                assert isinstance(result, BrowserPageData)
                # Should have waited between scrolls
                assert mock_sleep.called

    @pytest.mark.asyncio
    async def test_scrape_paginated(self, browser_scraper, mock_playwright_spa):
        """Test paginated scraping."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_spa["playwright"]
            )

            # Mock different page contents
            page_contents = [
                "<html><body>Page 1<a href='/page2'>Next</a></body></html>",
                "<html><body>Page 2<a href='/page3'>Next</a></body></html>",
                "<html><body>Page 3</body></html>",  # No next link
            ]
            mock_playwright_spa["page"].content = AsyncMock(side_effect=page_contents)

            # Mock _get_next_page to return appropriate URLs
            with patch.object(browser_scraper, "_get_next_page") as mock_get_next:
                mock_get_next.side_effect = [
                    "https://example.com/page2",
                    "https://example.com/page3",
                    None,
                ]

                results = await browser_scraper.scrape_paginated(
                    "https://example.com/page1", max_pages=3
                )

                assert len(results) == 3
                assert all(isinstance(r.data, BrowserPageData) for r in results)

    @pytest.mark.asyncio
    async def test_scrape_with_cookies(self, browser_scraper, mock_playwright_spa):
        """Test scraping with initial cookies."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_spa["playwright"]
            )

            cookies = [
                {"name": "session", "value": "abc123", "domain": ".example.com", "path": "/"},
                {"name": "user_id", "value": "42", "domain": ".example.com", "path": "/"},
            ]

            mock_playwright_spa["context"].add_cookies = AsyncMock()

            await browser_scraper._scrape("https://example.com", cookies=cookies)

            mock_playwright_spa["context"].add_cookies.assert_called_once_with(cookies)

    @pytest.mark.asyncio
    async def test_scrape_with_proxy(self, browser_scraper):
        """Test scraping with proxy configuration."""
        browser_scraper.config.proxy = {
            "server": "https://proxy.example.com:8080",
            "username": "user",
            "password": "pass",
        }

        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_browser_type = AsyncMock()
        mock_browser_type.launch = AsyncMock(return_value=mock_browser)

        mock_playwright = AsyncMock()
        mock_playwright.chromium = mock_browser_type
        mock_playwright.stop = AsyncMock()

        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)

            await browser_scraper._initialize()

            # Verify proxy was passed to context creation
            context_call = mock_browser.new_context.call_args
            assert "proxy" in context_call[1]
            assert context_call[1]["proxy"]["server"] == "https://proxy.example.com:8080"

    @pytest.mark.asyncio
    async def test_scrape_with_user_agent(self, browser_scraper):
        """Test scraping with a custom user agent."""
        browser_scraper.config.user_agent = "CustomBot/1.0"

        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_browser_type = AsyncMock()
        mock_browser_type.launch = AsyncMock(return_value=mock_browser)

        mock_playwright = AsyncMock()
        mock_playwright.chromium = mock_browser_type
        mock_playwright.stop = AsyncMock()

        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)

            await browser_scraper._initialize()

            # Verify the user agent was passed to context creation
            context_call = mock_browser.new_context.call_args
            assert context_call[1]["user_agent"] == "CustomBot/1.0"

    @pytest.mark.asyncio
    async def test_scrape_with_viewport(self, browser_scraper):
        """Test scraping with a custom viewport size."""
        browser_scraper.config.viewport_width = 1920
        browser_scraper.config.viewport_height = 1080

        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_browser_type = AsyncMock()
        mock_browser_type.launch = AsyncMock(return_value=mock_browser)

        mock_playwright = AsyncMock()
        mock_playwright.chromium = mock_browser_type
        mock_playwright.stop = AsyncMock()

        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)

            await browser_scraper._initialize()

            # Verify the viewport was set
            context_call = mock_browser.new_context.call_args
            assert context_call[1]["viewport"]["width"] == 1920
            assert context_call[1]["viewport"]["height"] == 1080

    @pytest.mark.asyncio
    async def test_scrape_with_geolocation(self, browser_scraper):
        """Test scraping with geolocation settings."""
        browser_scraper.config.geolocation = {"latitude": 40.7128, "longitude": -74.0060}
        browser_scraper.config.permissions = ["geolocation"]

        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_browser_type = AsyncMock()
        mock_browser_type.launch = AsyncMock(return_value=mock_browser)

        mock_playwright = AsyncMock()
        mock_playwright.chromium = mock_browser_type
        mock_playwright.stop = AsyncMock()

        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)

            await browser_scraper._initialize()

            # Verify geolocation was set
            context_call = mock_browser.new_context.call_args
            assert "geolocation" in context_call[1]
            assert context_call[1]["geolocation"]["latitude"] == 40.7128
            assert "permissions" in context_call[1]
            assert "geolocation" in context_call[1]["permissions"]

    @pytest.mark.asyncio
    async def test_scrape_with_offline_mode(self, browser_scraper):
        """Test scraping in offline mode."""
        browser_scraper.config.offline = True

        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_browser_type = AsyncMock()
        mock_browser_type.launch = AsyncMock(return_value=mock_browser)

        mock_playwright = AsyncMock()
        mock_playwright.chromium = mock_browser_type
        mock_playwright.stop = AsyncMock()

        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)

            await browser_scraper._initialize()

            # Verify offline mode was set
            context_call = mock_browser.new_context.call_args
            assert context_call[1]["offline"] is True

    @pytest.mark.asyncio
    async def test_scrape_multiple_concurrent(self, browser_scraper, mock_playwright_spa):
        """Test concurrent scraping of multiple URLs."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_spa["playwright"]
            )

            urls = [
                "https://example.com/page1",
                "https://example.com/page2",
                "https://example.com/page3",
            ]

            results = await browser_scraper.scrape_multiple(urls, max_concurrent=2)

            assert len(results) == 3
            assert all(r.success for r in results)
            assert all(isinstance(r.data, BrowserPageData) for r in results)
