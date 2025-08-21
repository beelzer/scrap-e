"""Browser-based web scraper using Playwright for JavaScript-heavy sites."""

import asyncio
import re
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from pydantic import BaseModel

from scrap_e.core.base_scraper import PaginatedScraper
from scrap_e.core.config import WebScraperConfig
from scrap_e.core.exceptions import ConnectionError, ScraperError
from scrap_e.core.models import ExtractionRule, ScraperResult, ScraperType
from scrap_e.scrapers.web.parser import HtmlParser


class BrowserPageData(BaseModel):
    """Model for scraped browser page data."""

    url: str
    title: str | None = None
    content: str | None = None
    screenshot: bytes | None = None
    extracted_data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    cookies: list[dict[str, Any]] | None = None
    console_logs: list[str] | None = None
    network_requests: list[dict[str, Any]] | None = None


class BrowserScraper(PaginatedScraper[BrowserPageData, WebScraperConfig]):
    """Browser-based scraper for JavaScript-heavy websites."""

    def __init__(self, config: WebScraperConfig | None = None) -> None:
        super().__init__(config)
        self._playwright: Any | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self.extraction_rules: list[ExtractionRule] = []

    def _get_default_config(self) -> WebScraperConfig:
        """Get default configuration for browser scraper."""
        return WebScraperConfig(enable_javascript=True)

    @property
    def scraper_type(self) -> ScraperType:
        """Return the type of this scraper."""
        return ScraperType.WEB_BROWSER

    async def _initialize(self) -> None:
        """Initialize Playwright browser."""
        if self._playwright is None:
            self._playwright = await async_playwright().start()

            # Launch browser based on config
            browser_type = getattr(self._playwright, self.config.browser_type)
            self._browser = await browser_type.launch(
                headless=self.config.browser_headless,
                args=(
                    ["--no-sandbox", "--disable-setuid-sandbox"]
                    if self.config.browser_headless
                    else []
                ),
            )

            # Create browser context with viewport
            if self._browser is None:
                raise ScraperError("Browser not initialized")
            self._context = await self._browser.new_context(
                viewport={
                    "width": self.config.browser_viewport_width,
                    "height": self.config.browser_viewport_height,
                },
                user_agent=self.config.user_agent,
                ignore_https_errors=not self.config.verify_ssl,
            )

            self.logger.info(
                "Browser initialized",
                browser_type=self.config.browser_type,
                headless=self.config.browser_headless,
            )

    async def _cleanup(self) -> None:
        """Clean up browser resources."""
        if self._context:
            await self._context.close()
            self._context = None

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

        self.logger.info("Browser resources cleaned up")

    async def _scrape(self, source: str, **kwargs: Any) -> BrowserPageData:
        """Scrape a web page using browser."""
        if not self._context:
            await self._initialize()

        if self._context is None:
            raise ScraperError("Browser context not initialized")

        page: Page | None = None
        try:
            page = await self._context.new_page()

            # Set up monitoring
            console_logs, network_requests = await self._setup_page_monitoring(page, **kwargs)

            # Load and prepare page
            await self._load_page(page, source, **kwargs)

            # Extract data
            page_data = await self._extract_page_data(page, source)

            # Enhance page data with additional info
            await self._enhance_page_data(page_data, page, console_logs, network_requests, **kwargs)

            return page_data

        except Exception as e:
            await self._handle_scrape_error(e, page, source)
            raise

        finally:
            if page:
                await page.close()

    async def _setup_page_monitoring(self, page: Page, **kwargs: Any) -> tuple[list, list]:
        """Set up console and network monitoring."""
        console_logs = []
        network_requests = []

        if kwargs.get("capture_console", False):
            page.on("console", lambda msg: console_logs.append(msg.text))

        if kwargs.get("capture_network", False):
            page.on(
                "request",
                lambda req: network_requests.append(
                    {
                        "url": req.url,
                        "method": req.method,
                        "type": req.resource_type,
                    }
                ),
            )

        return console_logs, network_requests

    async def _load_page(self, page: Page, source: str, **kwargs: Any) -> None:
        """Load page with navigation and interactions."""
        await self._navigate_to_page(page, source, **kwargs)
        await self._wait_for_content(page, **kwargs)

        # Execute custom JavaScript if provided
        if custom_js := kwargs.get("execute_js"):
            await page.evaluate(custom_js)

        # Scroll to load lazy content if requested
        if kwargs.get("scroll_to_bottom", False):
            await self._scroll_to_bottom(page)

    async def _enhance_page_data(
        self,
        page_data: BrowserPageData,
        page: Page,
        console_logs: list,
        network_requests: list,
        **kwargs: Any,
    ) -> None:
        """Add additional data to page_data."""
        # Capture screenshot if configured
        if self.config.capture_screenshots or kwargs.get("screenshot", False):
            page_data.screenshot = await self._capture_screenshot(page, **kwargs)

        # Add monitoring data
        if console_logs:
            page_data.console_logs = console_logs
        if network_requests:
            page_data.network_requests = network_requests

        # Get cookies
        page_data.cookies = await self._context.cookies()

        # Apply extraction rules
        if self.extraction_rules or kwargs.get("extraction_rules"):
            rules = kwargs.get("extraction_rules", self.extraction_rules)
            page_data.extracted_data = await self._extract_data_from_page(page, rules)

    async def _handle_scrape_error(self, error: Exception, page: Page | None, source: str) -> None:
        """Handle scraping errors."""
        if self.config.browser_screenshot_on_error and page:
            try:
                screenshot = await page.screenshot(full_page=True)
                error_path = Path(self.config.temp_dir) / f"error_{source.replace('/', '_')}.png"
                error_path.write_bytes(screenshot)
                self.logger.error(f"Error screenshot saved to {error_path}")
            except Exception as screenshot_error:
                self.logger.debug(f"Failed to capture error screenshot: {screenshot_error!s}")

        raise ScraperError(f"Browser scraping failed: {error!s}", {"url": source}) from error

    async def _navigate_to_page(self, page: Page, url: str, **kwargs: Any) -> None:
        """Navigate to a URL with proper wait conditions."""
        wait_until = kwargs.get("wait_until", self.config.browser_wait_until)
        timeout = kwargs.get("timeout", self.config.browser_timeout) * 1000

        try:
            await page.goto(url, wait_until=wait_until, timeout=timeout)
        except Exception as e:
            raise ConnectionError(f"Failed to navigate to {url}: {e!s}", {"url": url}) from e

    async def _wait_for_content(self, page: Page, **kwargs: Any) -> None:
        """Wait for content to load based on configuration."""
        # Wait for specific selector if provided
        if wait_selector := (kwargs.get("wait_for_selector") or self.config.wait_for_selector):
            timeout = kwargs.get("wait_for_timeout", self.config.wait_for_timeout) * 1000
            try:
                await page.wait_for_selector(wait_selector, timeout=timeout)
            except Exception:
                self.logger.warning(f"Timeout waiting for selector: {wait_selector}")

        # Additional wait time if specified
        if wait_time := kwargs.get("wait_time"):
            await asyncio.sleep(wait_time)

    async def _scroll_to_bottom(self, page: Page) -> None:
        """Scroll to the bottom of the page to trigger lazy loading."""
        await page.evaluate(
            """
            async () => {
                const distance = 100;
                const delay = 100;
                while (document.scrollingElement.scrollTop + window.innerHeight < document.scrollingElement.scrollHeight) {
                    document.scrollingElement.scrollBy(0, distance);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        """
        )

    async def _extract_page_data(self, page: Page, _url: str) -> BrowserPageData:
        """Extract data from the browser page."""
        # Get page content
        content = await page.content()

        # Get page title
        title = await page.title()

        page_data = BrowserPageData(
            url=page.url,
            title=title,
            content=content,
        )

        # Extract metadata if configured
        if self.config.extract_metadata and content:
            parser = HtmlParser(content)
            page_data.metadata = parser.extract_metadata()

        return page_data

    async def _capture_screenshot(self, page: Page, **kwargs: Any) -> bytes:
        """Capture a screenshot of the page."""
        screenshot_options = {
            "full_page": kwargs.get("full_page", True),
            "type": kwargs.get("screenshot_format", self.config.screenshot_format),
        }

        if screenshot_options["type"] == "jpeg":
            screenshot_options["quality"] = kwargs.get(
                "screenshot_quality", self.config.screenshot_quality
            )

        return await page.screenshot(**screenshot_options)

    async def _extract_data_from_page(
        self, page: Page, rules: list[ExtractionRule]
    ) -> dict[str, Any]:
        """Extract data from page using extraction rules."""
        extracted = {}

        for rule in rules:
            try:
                if rule.selector:
                    extracted[rule.name] = await self._extract_with_selector(page, rule)
                else:
                    # Fall back to HTML parser for other extraction methods
                    content = await page.content()
                    parser = HtmlParser(content)
                    extracted[rule.name] = parser.extract_with_rule(rule)

            except Exception as e:
                if rule.required:
                    raise
                self.logger.warning(f"Failed to extract {rule.name}: {e!s}")
                extracted[rule.name] = rule.default

        return extracted

    async def _extract_with_selector(self, page: Page, rule: ExtractionRule) -> Any:
        """Extract data using CSS selector."""
        elements = await page.query_selector_all(rule.selector)

        if not elements:
            return rule.default

        if rule.multiple:
            values = []
            for element in elements:
                value = await self._get_element_value(element, rule)
                values.append(value)
            return values
        return await self._get_element_value(elements[0], rule)

    async def _get_element_value(self, element: Any, rule: ExtractionRule) -> Any:
        """Get value from a page element."""
        if rule.attribute:
            value = await element.get_attribute(rule.attribute)
        else:
            value = await element.text_content()

        if rule.transform:
            value = self._apply_transform(value, rule.transform)

        return value

    def _apply_transform(self, value: Any, transform: str) -> Any:
        """Apply transformation to extracted value."""
        # String transformations
        if transform in {"strip", "lower", "upper"} and isinstance(value, str):
            return getattr(value, transform)()

        # Type conversions
        if transform == "int":
            try:
                return int(re.sub(r"[^\d-]", "", str(value)))
            except ValueError:
                return 0
        if transform == "float":
            try:
                return float(re.sub(r"[^\d.-]", "", str(value)))
            except ValueError:
                return 0.0
        if transform == "bool":
            return bool(value)

        return value

    async def _stream_scrape(
        self,
        source: str,
        chunk_size: int,  # noqa: ARG002
        **kwargs: Any,
    ) -> AsyncIterator[BrowserPageData]:
        """Stream scraping not directly applicable to browser scraping."""
        # For browser scraping, we'll yield page data as we navigate through pages
        yield await self._scrape(source, **kwargs)

    async def _validate_source(self, source: str, **_kwargs: Any) -> None:
        """Validate that a URL is accessible via browser."""
        if not self._context:
            await self._initialize()

        page = await self._context.new_page()
        try:
            response = await page.goto(source, wait_until="domcontentloaded")
            if response and response.status >= 400:
                raise ConnectionError(f"URL returned status {response.status}", {"url": source})
        finally:
            await page.close()

    async def _get_next_page(
        self,
        current_source: str,
        result: ScraperResult[BrowserPageData],
        page_number: int,  # noqa: ARG002
    ) -> str | None:
        """Get the URL for the next page."""
        if not result.success or not result.data:
            return None

        # Check for next page in extracted data
        if result.data.extracted_data and "next_page_url" in result.data.extracted_data:
            return result.data.extracted_data["next_page_url"]

        # Check pagination config
        if (
            self.config.pagination.enabled
            and self.config.pagination.next_page_selector
            and result.data.content
        ):
            parser = HtmlParser(result.data.content)
            next_link = parser.soup.select_one(self.config.pagination.next_page_selector)
            if next_link and next_link.get("href"):
                return urljoin(current_source, next_link["href"])

        return None

    async def scrape_spa(
        self, url: str, routes: list[str] | None = None, **kwargs: Any
    ) -> list[BrowserPageData]:
        """Scrape a Single Page Application by navigating through routes."""
        if not self._context:
            await self._initialize()

        results = []
        page = await self._context.new_page()

        try:
            # Initial navigation
            await self._navigate_to_page(page, url, **kwargs)
            await self._wait_for_content(page, **kwargs)

            # Scrape initial page
            initial_data = await self._extract_page_data(page, url)
            results.append(initial_data)

            # Navigate through routes if provided
            if routes:
                for route in routes:
                    # Navigate to route (client-side)
                    await page.evaluate(f"window.location.hash = '{route}'")
                    await asyncio.sleep(1)  # Wait for route change

                    # Extract data from route
                    route_data = await self._extract_page_data(page, f"{url}#{route}")
                    results.append(route_data)

        finally:
            await page.close()

        return results

    async def scrape_infinite_scroll(
        self, url: str, max_scrolls: int = 10, **kwargs: Any
    ) -> BrowserPageData:
        """Scrape a page with infinite scroll."""
        if not self._context:
            await self._initialize()

        page = await self._context.new_page()

        try:
            await self._navigate_to_page(page, url, **kwargs)
            await self._wait_for_content(page, **kwargs)

            # Scroll and collect content
            for i in range(max_scrolls):
                prev_height = await page.evaluate("document.body.scrollHeight")

                # Scroll to bottom
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                # Wait for new content to load
                await asyncio.sleep(2)

                new_height = await page.evaluate("document.body.scrollHeight")

                # Check if we've reached the end
                if new_height == prev_height:
                    self.logger.info(f"Reached end of infinite scroll after {i + 1} scrolls")
                    break

            # Extract final page data
            return await self._extract_page_data(page, url)

        finally:
            await page.close()

    async def interact_and_scrape(
        self, url: str, interactions: list[dict[str, Any]], **kwargs: Any
    ) -> BrowserPageData:
        """
        Scrape after performing interactions on the page.

        Args:
            url: The URL to scrape
            interactions: List of interactions to perform
                Example: [
                    {"action": "click", "selector": "#button"},
                    {"action": "fill", "selector": "#input", "value": "text"},
                    {"action": "select", "selector": "#dropdown", "value": "option"},
                ]
        """
        if not self._context:
            await self._initialize()

        page = await self._context.new_page()

        try:
            await self._navigate_to_page(page, url, **kwargs)
            await self._wait_for_content(page, **kwargs)

            # Perform interactions
            for interaction in interactions:
                action = interaction.get("action")
                selector = interaction.get("selector")

                if action == "click":
                    await page.click(selector)
                elif action == "fill":
                    value = interaction.get("value", "")
                    await page.fill(selector, value)
                elif action == "select":
                    value = interaction.get("value", "")
                    await page.select_option(selector, value)
                elif action == "hover":
                    await page.hover(selector)
                elif action == "wait":
                    wait_time = interaction.get("time", 1)
                    await asyncio.sleep(wait_time)

                # Wait after each interaction
                await asyncio.sleep(0.5)

            # Extract page data after interactions
            return await self._extract_page_data(page, url)

        finally:
            await page.close()
