"""Core tests for BrowserScraper functionality."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from playwright.async_api import Browser, BrowserContext, Page

from scrap_e.core.config import WebScraperConfig
from scrap_e.core.exceptions import ConnectionError, ScraperError
from scrap_e.scrapers.web.browser_scraper import BrowserPageData, BrowserScraper


@pytest.fixture
async def browser_scraper():
    """Create a browser scraper instance."""
    scraper = BrowserScraper()
    yield scraper
    # Cleanup - accessing protected members intentionally for testing
    if scraper._playwright:
        await scraper._cleanup()


@pytest.fixture
def mock_playwright():
    """Create mock playwright objects."""
    mock_page = AsyncMock(spec=Page)
    mock_page.url = "https://example.com"
    mock_page.title = AsyncMock(return_value="Test Page")
    mock_page.content = AsyncMock(return_value="<html><body>Test Content</body></html>")
    mock_page.goto = AsyncMock()
    mock_page.close = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=b"screenshot_data")
    mock_page.query_selector_all = AsyncMock(return_value=[])
    mock_page.evaluate = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()

    mock_context = AsyncMock(spec=BrowserContext)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()
    mock_context.cookies = AsyncMock(return_value=[{"name": "test", "value": "cookie"}])

    mock_browser = AsyncMock(spec=Browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    mock_browser_type = AsyncMock()
    mock_browser_type.launch = AsyncMock(return_value=mock_browser)

    mock_playwright_instance = AsyncMock()
    mock_playwright_instance.chromium = mock_browser_type
    mock_playwright_instance.firefox = mock_browser_type
    mock_playwright_instance.webkit = mock_browser_type
    mock_playwright_instance.stop = AsyncMock()

    return {
        "playwright": mock_playwright_instance,
        "browser": mock_browser,
        "context": mock_context,
        "page": mock_page,
    }


class TestBrowserScraperCore:
    """Core tests for BrowserScraper class."""

    def test_init(self):
        """Test BrowserScraper initialization."""
        config = WebScraperConfig(enable_javascript=True)
        scraper = BrowserScraper(config)
        assert scraper.config.enable_javascript is True
        assert scraper._playwright is None
        assert scraper._browser is None
        assert scraper._context is None

    def test_init_with_browser_type(self):
        """Test initialization with different browser types."""
        config = WebScraperConfig(browser_type="firefox")
        scraper = BrowserScraper(config)
        assert scraper.config.browser_type == "firefox"

    def test_default_config(self):
        """Test default configuration."""
        scraper = BrowserScraper()
        config = scraper._get_default_config()
        assert config.enable_javascript is True

    def test_scraper_type(self):
        """Test scraper type property."""
        scraper = BrowserScraper()
        assert scraper.scraper_type.value == "web_browser"

    @pytest.mark.asyncio
    async def test_initialize(self, mock_playwright):
        """Test browser initialization."""
        scraper = BrowserScraper()

        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            await scraper._initialize()

            assert scraper._playwright is not None
            assert scraper._browser is not None
            assert scraper._context is not None
            mock_playwright["playwright"].chromium.launch.assert_called_once()
            mock_playwright["browser"].new_context.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_firefox(self, mock_playwright):
        """Test initialization with the Firefox browser."""
        scraper = BrowserScraper(WebScraperConfig(browser_type="firefox"))

        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            await scraper._initialize()

            mock_playwright["playwright"].firefox.launch.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_webkit(self, mock_playwright):
        """Test initialization with the WebKit browser."""
        scraper = BrowserScraper(WebScraperConfig(browser_type="webkit"))

        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            await scraper._initialize()

            mock_playwright["playwright"].webkit.launch.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_with_options(self, mock_playwright):
        """Test initialization with browser options."""
        config = WebScraperConfig(
            headless=False,
            browser_args=["--disable-gpu"],
            viewport_width=1920,
            viewport_height=1080,
        )
        scraper = BrowserScraper(config)

        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            await scraper._initialize()

            # Check launch was called with headless=False and args
            launch_call = mock_playwright["playwright"].chromium.launch.call_args
            assert launch_call[1]["headless"] is False
            assert "--disable-gpu" in launch_call[1]["args"]

            # Check context was created with viewport
            context_call = mock_playwright["browser"].new_context.call_args
            assert context_call[1]["viewport"]["width"] == 1920
            assert context_call[1]["viewport"]["height"] == 1080

    @pytest.mark.asyncio
    async def test_cleanup(self, mock_playwright):
        """Test cleanup of browser resources."""
        scraper = BrowserScraper()

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]

        await scraper._cleanup()

        mock_playwright["context"].close.assert_called_once()
        mock_playwright["browser"].close.assert_called_once()
        mock_playwright["playwright"].stop.assert_called_once()
        assert scraper._context is None
        assert scraper._browser is None
        assert scraper._playwright is None

    @pytest.mark.asyncio
    async def test_cleanup_no_resources(self):
        """Test cleanup when no resources are initialized."""
        scraper = BrowserScraper()
        await scraper._cleanup()  # Should not raise

    @pytest.mark.asyncio
    async def test_scrape_basic(self, browser_scraper, mock_playwright):
        """Test basic scraping functionality."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            result = await browser_scraper._scrape("https://example.com")

            assert isinstance(result, BrowserPageData)
            assert result.url == "https://example.com"
            assert result.title == "Test Page"
            assert result.content == "<html><body>Test Content</body></html>"
            mock_playwright["page"].goto.assert_called_once()
            mock_playwright["page"].close.assert_called_once()

    @pytest.mark.asyncio
    async def test_scrape_with_timeout(self, browser_scraper, mock_playwright):
        """Test scraping with custom timeout."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            await browser_scraper._scrape("https://example.com", timeout=60000)

            goto_call = mock_playwright["page"].goto.call_args
            assert goto_call[1]["timeout"] == 60000

    @pytest.mark.asyncio
    async def test_scrape_error_handling(self, browser_scraper, mock_playwright):
        """Test error handling during scraping."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )
            mock_playwright["page"].goto.side_effect = Exception("Navigation failed")

            with pytest.raises(ScraperError) as exc_info:
                await browser_scraper._scrape("https://example.com")

            assert "Browser scraping failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_navigate_to_page(self, browser_scraper, mock_playwright):
        """Test page navigation."""
        browser_scraper._context = mock_playwright["context"]
        page = mock_playwright["page"]

        await browser_scraper._navigate_to_page(page, "https://example.com")

        page.goto.assert_called_once_with(
            "https://example.com", wait_until="networkidle", timeout=30000
        )

    @pytest.mark.asyncio
    async def test_navigate_to_page_with_wait_until(self, browser_scraper, mock_playwright):
        """Test navigation with different wait_until options."""
        browser_scraper._context = mock_playwright["context"]
        page = mock_playwright["page"]

        await browser_scraper._navigate_to_page(
            page, "https://example.com", wait_until="domcontentloaded"
        )

        page.goto.assert_called_once_with(
            "https://example.com", wait_until="domcontentloaded", timeout=30000
        )

    @pytest.mark.asyncio
    async def test_navigate_to_page_error(self, browser_scraper, mock_playwright):
        """Test navigation error handling."""
        browser_scraper._context = mock_playwright["context"]
        page = mock_playwright["page"]
        page.goto.side_effect = Exception("Network error")

        with pytest.raises(ConnectionError) as exc_info:
            await browser_scraper._navigate_to_page(page, "https://example.com")

        assert "Failed to navigate" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_extract_page_data(self, browser_scraper, mock_playwright):
        """Test extracting page data."""
        page = mock_playwright["page"]
        browser_scraper.config.extract_metadata = True
        browser_scraper.config.extract_links = True
        browser_scraper.config.extract_images = True

        result = await browser_scraper._extract_page_data(page, "https://example.com")

        assert isinstance(result, BrowserPageData)
        assert result.url == "https://example.com"
        assert result.title == "Test Page"
        assert result.content == "<html><body>Test Content</body></html>"
        assert result.metadata is not None
        assert result.links is not None
        assert result.images is not None

    @pytest.mark.asyncio
    async def test_validate_source(self, browser_scraper, mock_playwright):
        """Test source URL validation."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            mock_response = Mock()
            mock_response.status = 200
            mock_playwright["page"].goto = AsyncMock(return_value=mock_response)

            await browser_scraper._validate_source("https://example.com")

            mock_playwright["context"].new_page.assert_called_once()
            mock_playwright["page"].close.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_source_error(self, browser_scraper, mock_playwright):
        """Test source validation with error status."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            mock_response = Mock()
            mock_response.status = 404
            mock_playwright["page"].goto = AsyncMock(return_value=mock_response)

            with pytest.raises(ConnectionError) as exc_info:
                await browser_scraper._validate_source("https://example.com")

            assert "URL returned status 404" in str(exc_info.value)

    def test_apply_transform(self, browser_scraper):
        """Test value transformations."""
        assert browser_scraper._apply_transform("  test  ", "strip") == "test"
        assert browser_scraper._apply_transform("Test", "lower") == "test"
        assert browser_scraper._apply_transform("test", "upper") == "TEST"
        assert browser_scraper._apply_transform("123", "int") == 123
        assert browser_scraper._apply_transform("12.34", "float") == 12.34
        assert browser_scraper._apply_transform("true", "bool") is True
        assert (
            browser_scraper._apply_transform("false", "bool") is True
        )  # Non-empty string is truthy
        assert browser_scraper._apply_transform("", "bool") is False
        assert browser_scraper._apply_transform("test", "unknown") == "test"
        assert browser_scraper._apply_transform(None, "strip") is None
