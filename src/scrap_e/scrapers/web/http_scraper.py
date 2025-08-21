"""HTTP-based web scraper using httpx."""

from collections.abc import AsyncIterator
from typing import Any
from urllib.parse import urljoin

import httpx
from lxml import etree
from pydantic import BaseModel, HttpUrl

from scrap_e.core.base_scraper import PaginatedScraper
from scrap_e.core.config import WebScraperConfig
from scrap_e.core.exceptions import ConnectionError, ParsingError, ScraperError
from scrap_e.core.models import ExtractionRule, HttpRequest, ScraperResult, ScraperType
from scrap_e.scrapers.web.parser import HtmlParser


class WebPageData(BaseModel):
    """Model for scraped web page data."""

    url: str
    status_code: int
    headers: dict[str, str]
    content: str | None = None
    extracted_data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    links: list[dict[str, str]] | None = None
    images: list[dict[str, str]] | None = None


class HttpScraper(PaginatedScraper[WebPageData, WebScraperConfig]):
    """HTTP scraper for web pages."""

    def __init__(self, config: WebScraperConfig | None = None) -> None:
        super().__init__(config)
        self._client: httpx.AsyncClient | None = None
        self.extraction_rules: list[ExtractionRule] = []

    def _get_default_config(self) -> WebScraperConfig:
        """Get default configuration for web scraper."""
        return WebScraperConfig()

    @property
    def scraper_type(self) -> ScraperType:
        """Return the type of this scraper."""
        return ScraperType.WEB_HTTP

    async def _initialize(self) -> None:
        """Initialize HTTP client."""
        if self._client is None:
            headers = {
                "User-Agent": self.config.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

            timeout = httpx.Timeout(
                connect=10.0,
                read=self.config.default_timeout,
                write=10.0,
                pool=5.0,
            )

            limits = httpx.Limits(
                max_keepalive_connections=5,
                max_connections=self.config.concurrent_requests,
                keepalive_expiry=30.0,
            )

            self._client = httpx.AsyncClient(
                headers=headers,
                timeout=timeout,
                limits=limits,
                follow_redirects=self.config.follow_redirects,
                max_redirects=self.config.max_redirects,
                verify=self.config.verify_ssl,
                http2=False,  # Disable HTTP/2 for compatibility
            )

            self.logger.info("HTTP client initialized")

    async def _cleanup(self) -> None:
        """Clean up HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            self.logger.info("HTTP client closed")

    async def _scrape(self, source: str, **kwargs: Any) -> WebPageData:
        """Scrape a web page."""
        if not self._client:
            await self._initialize()

        try:
            # Build request from source and kwargs
            request = self._build_request(source, **kwargs)

            # Make HTTP request
            response = await self._make_request(request)

            # Parse response
            page_data = await self._parse_response(response, source)

            # Apply extraction rules if provided
            if self.extraction_rules or kwargs.get("extraction_rules"):
                rules = kwargs.get("extraction_rules", self.extraction_rules)
                if page_data.content is not None:
                    page_data.extracted_data = await self._extract_data(page_data.content, rules)

            return page_data

        except httpx.HTTPError as e:
            raise ConnectionError(f"HTTP error occurred: {e!s}", {"url": source}) from e
        except Exception as e:
            raise ScraperError(f"Failed to scrape {source}: {e!s}", {"url": source}) from e

    def _build_request(self, url: str, **kwargs: Any) -> HttpRequest:
        """Build HTTP request from URL and kwargs."""
        request = HttpRequest(
            url=HttpUrl(url),
            method=kwargs.get("method", "GET"),
            headers=kwargs.get("headers", {}),
            params=kwargs.get("params", {}),
            data=kwargs.get("data"),
            json_data=kwargs.get("json"),
            timeout=kwargs.get("timeout", self.config.default_timeout),
            follow_redirects=kwargs.get("follow_redirects", self.config.follow_redirects),
            verify_ssl=kwargs.get("verify_ssl", self.config.verify_ssl),
            cookies=kwargs.get("cookies"),
        )

        # Add default headers
        if "User-Agent" not in request.headers:
            request.headers["User-Agent"] = self.config.user_agent

        return request

    async def _make_request(self, request: HttpRequest) -> httpx.Response:
        """Make HTTP request."""
        kwargs = {
            "headers": request.headers,
            "params": request.params,
            "timeout": request.timeout,
            "follow_redirects": request.follow_redirects,
        }

        if request.cookies:
            kwargs["cookies"] = request.cookies

        if request.data:
            kwargs["data"] = request.data
        elif request.json_data:
            kwargs["json"] = request.json_data

        if self._client is None:
            raise ScraperError("HTTP client not initialized")
        response = await self._client.request(
            method=request.method.value,
            url=str(request.url),
            **kwargs,  # type: ignore[arg-type]
        )

        response.raise_for_status()
        return response

    async def _parse_response(self, response: httpx.Response, _url: str) -> WebPageData:
        """Parse HTTP response into WebPageData."""
        content = response.text

        page_data = WebPageData(
            url=str(response.url),
            status_code=response.status_code,
            headers=dict(response.headers),
            content=content,
        )

        # Extract metadata if configured
        if self.config.extract_metadata and content:
            parser = HtmlParser(content)
            page_data.metadata = parser.extract_metadata()

        # Extract links if configured
        if self.config.extract_links and content:
            parser = HtmlParser(content)
            page_data.links = parser.extract_links(str(response.url))

        # Extract images if configured
        if self.config.extract_images and content:
            parser = HtmlParser(content)
            page_data.images = parser.extract_images(str(response.url))

        return page_data

    async def _extract_data(self, content: str, rules: list[ExtractionRule]) -> dict[str, Any]:
        """Extract data using extraction rules."""
        if not content:
            return {}

        parser = HtmlParser(content, self.config.parser)
        extracted = {}

        for rule in rules:
            try:
                value = parser.extract_with_rule(rule)
                extracted[rule.name] = value
            except ParsingError as e:
                if rule.required:
                    raise
                self.logger.warning(f"Failed to extract {rule.name}: {e!s}")
                extracted[rule.name] = rule.default

        return extracted

    async def _stream_scrape(
        self, source: str, chunk_size: int, **kwargs: Any
    ) -> AsyncIterator[WebPageData]:
        """Stream scraping for large responses."""
        if not self._client:
            await self._initialize()

        request = self._build_request(source, **kwargs)

        if self._client is None:
            raise ScraperError("HTTP client not initialized")
        async with self._client.stream(
            method=request.method.value,
            url=str(request.url),
            headers=request.headers,
            params=request.params,
        ) as response:
            response.raise_for_status()

            content_chunks = []
            async for chunk in response.aiter_text(chunk_size):
                content_chunks.append(chunk)

                # Yield partial data periodically
                if len(content_chunks) >= 10:
                    partial_content = "".join(content_chunks)
                    yield WebPageData(
                        url=str(response.url),
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        content=partial_content,
                    )
                    content_chunks = []

            # Yield final chunk
            if content_chunks:
                final_content = "".join(content_chunks)
                yield WebPageData(
                    url=str(response.url),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    content=final_content,
                )

    async def _validate_source(self, source: str, **_kwargs: Any) -> None:
        """Validate that a URL is accessible."""
        if not self._client:
            await self._initialize()

        try:
            if self._client is None:
                raise ScraperError("HTTP client not initialized")
            response = await self._client.head(source, follow_redirects=True)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise ConnectionError(f"URL validation failed: {e!s}", {"url": source}) from e

    async def _get_next_page(
        self,
        current_source: str,
        result: ScraperResult[WebPageData],
        page_number: int,
    ) -> str | None:
        """Get the URL for the next page."""
        if not result.success or not result.data:
            return None

        # Check for next page link in extracted data
        if result.data.extracted_data and "next_page_url" in result.data.extracted_data:
            next_url = result.data.extracted_data["next_page_url"]
            return next_url if isinstance(next_url, str) else None

        # Check for next page in pagination config
        if self.config.pagination.enabled:
            if self.config.pagination.next_page_selector and result.data.content:
                parser = HtmlParser(result.data.content)
                next_link = parser.soup.select_one(self.config.pagination.next_page_selector)
                if next_link and next_link.get("href"):
                    href = next_link.get("href")
                    if isinstance(href, str):
                        return urljoin(current_source, href)
                    return None

            # URL pattern-based pagination
            if self.config.pagination.next_page_url_pattern:
                return self.config.pagination.next_page_url_pattern.format(page=page_number + 1)

        return None

    def add_extraction_rule(self, rule: ExtractionRule) -> None:
        """Add an extraction rule."""
        self.extraction_rules.append(rule)

    def clear_extraction_rules(self) -> None:
        """Clear all extraction rules."""
        self.extraction_rules = []

    async def scrape_sitemap(self, sitemap_url: str) -> list[str]:
        """Scrape URLs from a sitemap."""
        if not self._client:
            await self._initialize()

        if self._client is None:
            raise ScraperError("HTTP client not initialized")
        response = await self._client.get(sitemap_url)
        response.raise_for_status()

        root = etree.fromstring(response.content)

        # Handle sitemap index
        if root.tag.endswith("sitemapindex"):
            sitemap_urls = []
            sitemap_locs = root.xpath("//ns:sitemap/ns:loc", namespaces={"ns": root.nsmap[None]})
            if isinstance(sitemap_locs, list):
                for sitemap in sitemap_locs:
                    if isinstance(sitemap, etree._Element) and sitemap.text:
                        sitemap_urls.extend(await self.scrape_sitemap(sitemap.text))
            return sitemap_urls

        # Handle URL set
        url_locs = root.xpath("//ns:url/ns:loc", namespaces={"ns": root.nsmap[None]})
        urls = []
        if isinstance(url_locs, list):
            for url in url_locs:
                if isinstance(url, etree._Element) and url.text:
                    urls.append(url.text)
        return urls

    async def scrape_with_session(
        self, urls: list[str], session_cookies: dict[str, str] | None = None
    ) -> list[ScraperResult[WebPageData]]:
        """Scrape multiple URLs while maintaining session."""
        results = []

        # Store cookies across requests
        cookies = session_cookies or {}

        for url in urls:
            result = await self.scrape(url, cookies=cookies)

            # Update cookies from response
            if result.success and result.data:
                response_cookies = {}
                for cookie_header in result.data.headers.get("set-cookie", "").split(","):
                    if "=" in cookie_header:
                        key, value = cookie_header.split("=", 1)
                        response_cookies[key.strip()] = value.split(";")[0].strip()
                cookies.update(response_cookies)

            results.append(result)

        return results
