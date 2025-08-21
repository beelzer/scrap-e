"""Comprehensive tests for BrowserScraper."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from playwright.async_api import Browser, BrowserContext, Page

from scrap_e.core.config import WebScraperConfig
from scrap_e.core.exceptions import ConnectionError, ScraperError
from scrap_e.core.models import ExtractionRule, ScraperMetadata, ScraperResult, ScraperType
from scrap_e.scrapers.web.browser_scraper import BrowserPageData, BrowserScraper


@pytest.fixture
async def browser_scraper():
    """Create a browser scraper instance."""
    scraper = BrowserScraper()
    yield scraper
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


class TestBrowserScraper:
    """Test BrowserScraper class."""

    def test_init(self):
        """Test BrowserScraper initialization."""
        config = WebScraperConfig(enable_javascript=True)
        scraper = BrowserScraper(config)
        assert scraper.config.enable_javascript is True
        assert scraper._playwright is None
        assert scraper._browser is None
        assert scraper._context is None

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
    async def test_scrape_with_screenshot(self, browser_scraper, mock_playwright):
        """Test scraping with screenshot capture."""
        browser_scraper.config.capture_screenshots = True

        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            result = await browser_scraper._scrape("https://example.com")

            assert result.screenshot == b"screenshot_data"
            mock_playwright["page"].screenshot.assert_called_once()

    @pytest.mark.asyncio
    async def test_scrape_with_console_logs(self, browser_scraper, mock_playwright):
        """Test scraping with console log capture."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            # Mock the on method to simulate console messages
            console_logs = []

            def mock_on(event, callback):
                if event == "console":
                    msg = Mock()
                    msg.text = "Console log message"
                    console_logs.append(msg.text)

            mock_playwright["page"].on = Mock(side_effect=mock_on)

            result = await browser_scraper._scrape(
                "https://example.com", capture_console=True
            )

            # The test passes if no error is raised
            assert isinstance(result, BrowserPageData)

    @pytest.mark.asyncio
    async def test_scrape_with_network_capture(self, browser_scraper, mock_playwright):
        """Test scraping with network request capture."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            # Simulate network requests

            def on_request(event, callback):
                if event == "request":
                    req = Mock()
                    req.url = "https://api.example.com/data"
                    req.method = "GET"
                    req.resource_type = "xhr"
                    callback(req)

            mock_playwright["page"].on = on_request

            result = await browser_scraper._scrape(
                "https://example.com", capture_network=True
            )

            assert len(result.network_requests) == 1
            assert result.network_requests[0]["url"] == "https://api.example.com/data"

    @pytest.mark.asyncio
    async def test_scrape_with_custom_js(self, browser_scraper, mock_playwright):
        """Test scraping with custom JavaScript execution."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            custom_js = "document.body.style.background = 'red';"
            await browser_scraper._scrape("https://example.com", execute_js=custom_js)

            mock_playwright["page"].evaluate.assert_called_with(custom_js)

    @pytest.mark.asyncio
    async def test_scrape_with_scroll(self, browser_scraper, mock_playwright):
        """Test scraping with scroll to bottom."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            await browser_scraper._scrape("https://example.com", scroll_to_bottom=True)

            # Check that evaluate was called for scrolling
            assert mock_playwright["page"].evaluate.call_count >= 1

    @pytest.mark.asyncio
    async def test_scrape_with_extraction_rules(self, browser_scraper, mock_playwright):
        """Test scraping with extraction rules."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            # Mock element for extraction
            mock_element = AsyncMock()
            mock_element.text_content = AsyncMock(return_value="Extracted Text")
            mock_element.get_attribute = AsyncMock(return_value="attribute_value")
            mock_playwright["page"].query_selector_all = AsyncMock(
                return_value=[mock_element]
            )

            rule = ExtractionRule(
                name="test_field", selector=".test-class", required=False
            )
            browser_scraper.extraction_rules = [rule]

            result = await browser_scraper._scrape("https://example.com")

            assert result.extracted_data is not None
            assert "test_field" in result.extracted_data

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

        page.goto.assert_called_once()

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
    async def test_wait_for_content(self, browser_scraper, mock_playwright):
        """Test waiting for content to load."""
        browser_scraper._context = mock_playwright["context"]
        browser_scraper.config.wait_for_selector = ".content"
        browser_scraper.config.wait_for_timeout = 5
        page = mock_playwright["page"]

        await browser_scraper._wait_for_content(page)

        page.wait_for_selector.assert_called_once()

    @pytest.mark.asyncio
    async def test_wait_for_content_with_wait_time(
        self, browser_scraper, mock_playwright
    ):
        """Test waiting with additional wait time."""
        browser_scraper._context = mock_playwright["context"]
        page = mock_playwright["page"]

        with patch("asyncio.sleep") as mock_sleep:
            await browser_scraper._wait_for_content(page, wait_time=2)
            mock_sleep.assert_called_once_with(2)

    @pytest.mark.asyncio
    async def test_scroll_to_bottom(self, browser_scraper, mock_playwright):
        """Test scrolling to bottom of page."""
        page = mock_playwright["page"]

        await browser_scraper._scroll_to_bottom(page)

        # Verify evaluate was called with scroll script
        page.evaluate.assert_called_once()
        call_args = page.evaluate.call_args[0][0]
        assert "scrollingElement" in call_args
        assert "scrollBy" in call_args

    @pytest.mark.asyncio
    async def test_extract_page_data(self, browser_scraper, mock_playwright):
        """Test extracting page data."""
        page = mock_playwright["page"]
        browser_scraper.config.extract_metadata = True

        result = await browser_scraper._extract_page_data(page, "https://example.com")

        assert isinstance(result, BrowserPageData)
        assert result.url == "https://example.com"
        assert result.title == "Test Page"
        assert result.content == "<html><body>Test Content</body></html>"
        assert result.metadata is not None

    @pytest.mark.asyncio
    async def test_capture_screenshot(self, browser_scraper, mock_playwright):
        """Test screenshot capture."""
        page = mock_playwright["page"]

        screenshot = await browser_scraper._capture_screenshot(page, full_page=False)

        assert screenshot == b"screenshot_data"
        page.screenshot.assert_called_once_with(full_page=False, type="png")

    @pytest.mark.asyncio
    async def test_capture_screenshot_jpeg(self, browser_scraper, mock_playwright):
        """Test JPEG screenshot capture with quality."""
        page = mock_playwright["page"]
        browser_scraper.config.screenshot_format = "jpeg"
        browser_scraper.config.screenshot_quality = 80

        await browser_scraper._capture_screenshot(page)

        page.screenshot.assert_called_once_with(full_page=True, type="jpeg", quality=80)

    def test_apply_transform(self, browser_scraper):
        """Test value transformations."""
        assert browser_scraper._apply_transform("  test  ", "strip") == "test"
        assert browser_scraper._apply_transform("Test", "lower") == "test"
        assert browser_scraper._apply_transform("test", "upper") == "TEST"
        assert browser_scraper._apply_transform("123", "int") == 123
        assert browser_scraper._apply_transform("12.34", "float") == 12.34
        assert browser_scraper._apply_transform("true", "bool") is True
        assert browser_scraper._apply_transform("", "bool") is False
        assert browser_scraper._apply_transform("test", "unknown") == "test"

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

    @pytest.mark.asyncio
    async def test_get_next_page(self, browser_scraper):
        """Test getting next page URL."""
        # Test with extracted data
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

        next_url = await browser_scraper._get_next_page(
            "https://example.com/page1", result, 1
        )
        assert next_url == "https://example.com/page2"

        # Test with no next page
        result.data.extracted_data = {}
        next_url = await browser_scraper._get_next_page(
            "https://example.com/page1", result, 1
        )
        assert next_url is None

    @pytest.mark.asyncio
    async def test_scrape_spa(self, browser_scraper, mock_playwright):
        """Test scraping Single Page Application."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            routes = ["#/about", "#/contact"]
            results = await browser_scraper.scrape_spa("https://example.com", routes)

            assert len(results) == 3  # Initial page + 2 routes
            assert all(isinstance(r, BrowserPageData) for r in results)
            # Verify navigation to routes
            assert mock_playwright["page"].evaluate.call_count >= len(routes)

    @pytest.mark.asyncio
    async def test_scrape_infinite_scroll(self, browser_scraper, mock_playwright):
        """Test scraping infinite scroll page."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            # Simulate scroll height changes
            scroll_heights = [1000, 2000, 2000]  # Third scroll shows no new content
            mock_playwright["page"].evaluate = AsyncMock(
                side_effect=scroll_heights + [None] * 10
            )

            result = await browser_scraper.scrape_infinite_scroll(
                "https://example.com", max_scrolls=5
            )

            assert isinstance(result, BrowserPageData)
            # Verify scrolling occurred
            assert mock_playwright["page"].evaluate.call_count >= 3

    @pytest.mark.asyncio
    async def test_interact_and_scrape(self, browser_scraper, mock_playwright):
        """Test scraping with page interactions."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            mock_playwright["page"].click = AsyncMock()
            mock_playwright["page"].fill = AsyncMock()
            mock_playwright["page"].select_option = AsyncMock()
            mock_playwright["page"].hover = AsyncMock()

            interactions = [
                {"action": "click", "selector": "#button"},
                {"action": "fill", "selector": "#input", "value": "test"},
                {"action": "select", "selector": "#dropdown", "value": "option1"},
                {"action": "hover", "selector": "#menu"},
                {"action": "wait", "time": 1},
            ]

            with patch("asyncio.sleep") as mock_sleep:
                result = await browser_scraper.interact_and_scrape(
                    "https://example.com", interactions
                )

            assert isinstance(result, BrowserPageData)
            mock_playwright["page"].click.assert_called_once_with("#button")
            mock_playwright["page"].fill.assert_called_once_with("#input", "test")
            mock_playwright["page"].select_option.assert_called_once_with(
                "#dropdown", "option1"
            )
            mock_playwright["page"].hover.assert_called_once_with("#menu")
            # Check sleep was called for wait and after each interaction
            assert mock_sleep.call_count >= len(interactions)

    @pytest.mark.asyncio
    async def test_stream_scrape(self, browser_scraper, mock_playwright):
        """Test stream scraping (yields single result for browser)."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )

            results = []
            async for data in browser_scraper._stream_scrape(
                "https://example.com", chunk_size=1024
            ):
                results.append(data)

            assert len(results) == 1
            assert isinstance(results[0], BrowserPageData)

    @pytest.mark.asyncio
    async def test_extract_data_from_page_with_multiple(
        self, browser_scraper, mock_playwright
    ):
        """Test extracting multiple values from page."""
        page = mock_playwright["page"]

        # Mock multiple elements
        mock_elements = []
        for i in range(3):
            elem = AsyncMock()
            elem.text_content = AsyncMock(return_value=f"Text {i}")
            elem.get_attribute = AsyncMock(return_value=f"attr_{i}")
            mock_elements.append(elem)

        page.query_selector_all = AsyncMock(return_value=mock_elements)

        rule = ExtractionRule(name="items", selector=".item", multiple=True)

        result = await browser_scraper._extract_data_from_page(page, [rule])

        assert "items" in result
        assert len(result["items"]) == 3
        assert result["items"][0] == "Text 0"

    @pytest.mark.asyncio
    async def test_extract_data_from_page_with_attribute(
        self, browser_scraper, mock_playwright
    ):
        """Test extracting attribute values from page."""
        page = mock_playwright["page"]

        mock_element = AsyncMock()
        mock_element.get_attribute = AsyncMock(
            return_value="https://example.com/image.jpg"
        )
        page.query_selector_all = AsyncMock(return_value=[mock_element])

        rule = ExtractionRule(name="image_url", selector="img", attribute="src")

        result = await browser_scraper._extract_data_from_page(page, [rule])

        assert result["image_url"] == "https://example.com/image.jpg"
        mock_element.get_attribute.assert_called_once_with("src")

    @pytest.mark.asyncio
    async def test_extract_data_from_page_with_transform(
        self, browser_scraper, mock_playwright
    ):
        """Test extracting with transformation."""
        page = mock_playwright["page"]

        mock_element = AsyncMock()
        mock_element.text_content = AsyncMock(return_value="  UPPERCASE  ")
        page.query_selector_all = AsyncMock(return_value=[mock_element])

        rule = ExtractionRule(name="cleaned_text", selector=".text", transform="strip")

        result = await browser_scraper._extract_data_from_page(page, [rule])

        assert result["cleaned_text"] == "UPPERCASE"

    @pytest.mark.asyncio
    async def test_extract_data_from_page_fallback_to_parser(
        self, browser_scraper, mock_playwright
    ):
        """Test extraction falling back to HTML parser."""
        page = mock_playwright["page"]
        page.content = AsyncMock(return_value="<div>Regex content: 12345</div>")

        rule = ExtractionRule(name="number", regex=r"content: (\d+)")

        result = await browser_scraper._extract_data_from_page(page, [rule])

        assert result["number"] == "12345"

    @pytest.mark.asyncio
    async def test_error_screenshot_on_failure(self, browser_scraper, mock_playwright):
        """Test error screenshot capture on failure."""
        browser_scraper.config.browser_screenshot_on_error = True
        browser_scraper.config.temp_dir = "/tmp"

        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright["playwright"]
            )
            mock_playwright["page"].goto.side_effect = Exception("Navigation failed")

            with patch("pathlib.Path.write_bytes"):
                with pytest.raises(ScraperError):
                    await browser_scraper._scrape("https://example.com")

                mock_playwright["page"].screenshot.assert_called_once_with(
                    full_page=True
                )
