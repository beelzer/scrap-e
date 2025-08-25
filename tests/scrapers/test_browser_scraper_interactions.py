"""Tests for BrowserScraper page interaction features."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from playwright.async_api import Page

from scrap_e.core.models import ExtractionRule
from scrap_e.scrapers.web.browser_scraper import BrowserPageData, BrowserScraper


@pytest.fixture
async def browser_scraper():
    """Create a browser scraper instance."""
    scraper = BrowserScraper()
    yield scraper
    if scraper._playwright:
        await scraper._cleanup()


@pytest.fixture
def mock_page():
    """Create a mock page object."""
    page = AsyncMock(spec=Page)
    page.url = "https://example.com"
    page.title = AsyncMock(return_value="Test Page")
    page.content = AsyncMock(return_value="<html><body>Test Content</body></html>")
    page.goto = AsyncMock()
    page.close = AsyncMock()
    page.screenshot = AsyncMock(return_value=b"screenshot_data")
    page.query_selector_all = AsyncMock(return_value=[])
    page.evaluate = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.click = AsyncMock()
    page.fill = AsyncMock()
    page.select_option = AsyncMock()
    page.check = AsyncMock()
    page.uncheck = AsyncMock()
    page.hover = AsyncMock()
    page.keyboard = Mock()
    page.keyboard.press = AsyncMock()
    page.on = Mock()
    return page


@pytest.fixture
def mock_playwright_full(mock_page):
    """Create a full mock playwright setup."""
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


class TestBrowserScraperInteractions:
    """Tests for browser page interaction features."""

    @pytest.mark.asyncio
    async def test_wait_for_content(self, browser_scraper, mock_page):
        """Test waiting for content to load."""
        browser_scraper.config.wait_for_selector = ".content"
        browser_scraper.config.wait_for_timeout = 5

        await browser_scraper._wait_for_content(mock_page)

        mock_page.wait_for_selector.assert_called_once_with(".content", timeout=5000)

    @pytest.mark.asyncio
    async def test_wait_for_content_with_wait_time(self, browser_scraper, mock_page):
        """Test waiting with additional wait time."""
        with patch("asyncio.sleep") as mock_sleep:
            await browser_scraper._wait_for_content(mock_page, wait_time=2)
            mock_sleep.assert_called_once_with(2)

    @pytest.mark.asyncio
    async def test_wait_for_content_no_selector(self, browser_scraper, mock_page):
        """Test waiting without a selector."""
        browser_scraper.config.wait_for_selector = None

        with patch("asyncio.sleep") as mock_sleep:
            await browser_scraper._wait_for_content(mock_page, wait_time=1)
            mock_sleep.assert_called_once_with(1)
            mock_page.wait_for_selector.assert_not_called()

    @pytest.mark.asyncio
    async def test_scroll_to_bottom(self, browser_scraper, mock_page):
        """Test scrolling to bottom of page."""
        await browser_scraper._scroll_to_bottom(mock_page)

        # Verify evaluate was called with a scroll script
        mock_page.evaluate.assert_called_once()
        call_args = mock_page.evaluate.call_args[0][0]
        assert "scrollingElement" in call_args
        assert "scrollBy" in call_args

    @pytest.mark.asyncio
    async def test_scrape_with_scroll(self, browser_scraper, mock_playwright_full):
        """Test scraping with scroll to bottom."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_full["playwright"]
            )

            await browser_scraper._scrape("https://example.com", scroll_to_bottom=True)

            # Check that evaluate was called for scrolling
            assert mock_playwright_full["page"].evaluate.call_count >= 1

    @pytest.mark.asyncio
    async def test_scrape_with_custom_js(self, browser_scraper, mock_playwright_full):
        """Test scraping with custom JavaScript execution."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_full["playwright"]
            )

            custom_js = "document.body.style.background = 'red';"
            await browser_scraper._scrape("https://example.com", execute_js=custom_js)

            mock_playwright_full["page"].evaluate.assert_called_with(custom_js)

    @pytest.mark.asyncio
    async def test_scrape_with_console_logs(self, browser_scraper, mock_playwright_full):
        """Test scraping with console log capture."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_full["playwright"]
            )

            # Mock the on method to simulate console messages
            console_logs = []

            def mock_on(event, callback):
                if event == "console":
                    msg = Mock()
                    msg.text = "Console log message"
                    console_logs.append(msg.text)

            mock_playwright_full["page"].on = Mock(side_effect=mock_on)

            result = await browser_scraper._scrape("https://example.com", capture_console=True)

            # The test passes if no error is raised
            assert isinstance(result, BrowserPageData)

    @pytest.mark.asyncio
    async def test_scrape_with_network_capture(self, browser_scraper, mock_playwright_full):
        """Test scraping with network request capture."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_full["playwright"]
            )

            # Simulate network requests
            def on_request(event, callback):
                if event == "request":
                    req = Mock()
                    req.url = "https://api.example.com/data"
                    req.method = "GET"
                    req.resource_type = "xhr"
                    callback(req)

            mock_playwright_full["page"].on = on_request

            result = await browser_scraper._scrape("https://example.com", capture_network=True)

            assert len(result.network_requests) == 1
            assert result.network_requests[0]["url"] == "https://api.example.com/data"

    @pytest.mark.asyncio
    async def test_interact_and_scrape(self, browser_scraper, mock_playwright_full):
        """Test scraping with page interactions."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_full["playwright"]
            )

            interactions = [
                {"action": "click", "selector": "#submit-button"},
                {"action": "fill", "selector": "#search-input", "value": "test search"},
                {"action": "wait", "time": 1},
            ]

            result = await browser_scraper.interact_and_scrape("https://example.com", interactions)

            assert isinstance(result, BrowserPageData)
            mock_playwright_full["page"].click.assert_called_once_with("#submit-button")
            mock_playwright_full["page"].fill.assert_called_once_with(
                "#search-input", "test search"
            )

    @pytest.mark.asyncio
    async def test_interact_with_select(self, browser_scraper, mock_playwright_full):
        """Test interaction with select elements."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_full["playwright"]
            )

            interactions = [
                {"action": "select", "selector": "#dropdown", "value": "option2"},
            ]

            await browser_scraper.interact_and_scrape("https://example.com", interactions)

            mock_playwright_full["page"].select_option.assert_called_once_with(
                "#dropdown", "option2"
            )

    @pytest.mark.asyncio
    async def test_interact_with_checkbox(self, browser_scraper, mock_playwright_full):
        """Test interaction with checkboxes."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_full["playwright"]
            )

            interactions = [
                {"action": "check", "selector": "#checkbox1"},
                {"action": "uncheck", "selector": "#checkbox2"},
            ]

            await browser_scraper.interact_and_scrape("https://example.com", interactions)

            mock_playwright_full["page"].check.assert_called_once_with("#checkbox1")
            mock_playwright_full["page"].uncheck.assert_called_once_with("#checkbox2")

    @pytest.mark.asyncio
    async def test_interact_with_hover(self, browser_scraper, mock_playwright_full):
        """Test hover interaction."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_full["playwright"]
            )

            interactions = [
                {"action": "hover", "selector": "#menu-item"},
            ]

            await browser_scraper.interact_and_scrape("https://example.com", interactions)

            mock_playwright_full["page"].hover.assert_called_once_with("#menu-item")

    @pytest.mark.asyncio
    async def test_interact_with_keyboard(self, browser_scraper, mock_playwright_full):
        """Test keyboard interactions."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_full["playwright"]
            )

            interactions = [
                {"action": "press", "key": "Enter"},
                {"action": "press", "key": "Escape"},
            ]

            await browser_scraper.interact_and_scrape("https://example.com", interactions)

            assert mock_playwright_full["page"].keyboard.press.call_count == 2
            mock_playwright_full["page"].keyboard.press.assert_any_call("Enter")
            mock_playwright_full["page"].keyboard.press.assert_any_call("Escape")

    @pytest.mark.asyncio
    async def test_scrape_with_extraction_rules(self, browser_scraper, mock_playwright_full):
        """Test scraping with extraction rules."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_full["playwright"]
            )

            # Mock element for extraction
            mock_element = AsyncMock()
            mock_element.text_content = AsyncMock(return_value="Extracted Text")
            mock_element.get_attribute = AsyncMock(return_value="attribute_value")
            mock_playwright_full["page"].query_selector_all = AsyncMock(return_value=[mock_element])

            rule = ExtractionRule(name="test_field", selector=".test-class", required=False)
            browser_scraper.extraction_rules = [rule]

            result = await browser_scraper._scrape("https://example.com")

            assert result.extracted_data is not None
            assert "test_field" in result.extracted_data

    @pytest.mark.asyncio
    async def test_scrape_with_multiple_extraction_rules(
        self, browser_scraper, mock_playwright_full
    ):
        """Test scraping with multiple extraction rules."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_full["playwright"]
            )

            # Mock elements for different selectors
            mock_title = AsyncMock()
            mock_title.text_content = AsyncMock(return_value="Page Title")

            mock_price = AsyncMock()
            mock_price.text_content = AsyncMock(return_value="$99.99")

            mock_description = AsyncMock()
            mock_description.text_content = AsyncMock(return_value="Product description")

            def mock_query_selector_all(selector):
                if selector == "h1":
                    return [mock_title]
                if selector == ".price":
                    return [mock_price]
                if selector == ".description":
                    return [mock_description]
                return []

            mock_playwright_full["page"].query_selector_all = AsyncMock(
                side_effect=mock_query_selector_all
            )

            rules = [
                ExtractionRule(name="title", selector="h1"),
                ExtractionRule(name="price", selector=".price"),
                ExtractionRule(name="description", selector=".description"),
            ]
            browser_scraper.extraction_rules = rules

            result = await browser_scraper._scrape("https://example.com")

            assert result.extracted_data is not None
            assert result.extracted_data["title"] == "Page Title"
            assert result.extracted_data["price"] == "$99.99"
            assert result.extracted_data["description"] == "Product description"

    @pytest.mark.asyncio
    async def test_scrape_form_submission(self, browser_scraper, mock_playwright_full):
        """Test form submission workflow."""
        with patch(
            "scrap_e.scrapers.web.browser_scraper.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright_full["playwright"]
            )

            interactions = [
                {"action": "fill", "selector": "#username", "value": "testuser"},
                {"action": "fill", "selector": "#password", "value": "testpass"},
                {"action": "click", "selector": "#submit"},
                {"action": "wait", "time": 2},
            ]

            await browser_scraper.interact_and_scrape("https://example.com/login", interactions)

            # Verify form-filling sequence
            assert mock_playwright_full["page"].fill.call_count == 2
            mock_playwright_full["page"].fill.assert_any_call("#username", "testuser")
            mock_playwright_full["page"].fill.assert_any_call("#password", "testpass")
            mock_playwright_full["page"].click.assert_called_once_with("#submit")
