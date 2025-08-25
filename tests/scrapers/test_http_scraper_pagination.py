"""Tests for HTTP scraper pagination functionality."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from scrap_e.core.config import PaginationConfig
from scrap_e.core.models import ScraperMetadata, ScraperResult, ScraperType
from scrap_e.scrapers.web.http_scraper import HttpScraper, WebPageData


@pytest.fixture
async def http_scraper():
    """Create an HTTP scraper instance."""
    scraper = HttpScraper()
    yield scraper
    if scraper._client and hasattr(scraper._client, "aclose"):
        await scraper._cleanup()


class TestHttpScraperPagination:
    """Tests for HTTP scraper pagination features."""

    @pytest.mark.asyncio
    async def test_get_next_page_from_extracted_data(self, http_scraper):
        """Test getting next page URL from extracted data."""
        result = ScraperResult(
            success=True,
            data=WebPageData(
                url="https://example.com/page1",
                status_code=200,
                headers={},
                extracted_data={
                    "next_page_url": "https://example.com/page2",
                    "products": ["Product 1", "Product 2"],
                },
            ),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP, source="https://example.com/page1"
            ),
        )

        next_url = await http_scraper._get_next_page("https://example.com/page1", result, 1)
        assert next_url == "https://example.com/page2"

    @pytest.mark.asyncio
    async def test_get_next_page_from_css_selector(self, http_scraper):
        """Test getting next page URL from CSS selector."""
        http_scraper.config.pagination = PaginationConfig(
            enabled=True, next_page_selector="a.next-page"
        )

        result = ScraperResult(
            success=True,
            data=WebPageData(
                url="https://example.com/page1",
                status_code=200,
                headers={},
                content="""
                <html>
                    <body>
                        <div class="pagination">
                            <a class="prev-page" href="/page0">Previous</a>
                            <a class="current">1</a>
                            <a class="next-page" href="/page2">Next</a>
                        </div>
                    </body>
                </html>
                """,
            ),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP, source="https://example.com/page1"
            ),
        )

        next_url = await http_scraper._get_next_page("https://example.com/page1", result, 1)
        assert next_url == "https://example.com/page2"

    @pytest.mark.asyncio
    async def test_get_next_page_from_multiple_selectors(self, http_scraper):
        """Test getting next page with multiple possible selectors."""
        http_scraper.config.pagination = PaginationConfig(
            enabled=True, next_page_selector=".pagination .next, a[rel='next'], .next-button"
        )

        result = ScraperResult(
            success=True,
            data=WebPageData(
                url="https://example.com/page1",
                status_code=200,
                headers={},
                content="""
                <html>
                    <body>
                        <a rel="next" href="/page2">Next Page</a>
                    </body>
                </html>
                """,
            ),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP, source="https://example.com/page1"
            ),
        )

        next_url = await http_scraper._get_next_page("https://example.com/page1", result, 1)
        assert next_url == "https://example.com/page2"

    @pytest.mark.asyncio
    async def test_get_next_page_from_url_pattern(self, http_scraper):
        """Test getting next page URL from URL pattern."""
        http_scraper.config.pagination = PaginationConfig(
            enabled=True, next_page_url_pattern="https://example.com/products?page={page}"
        )

        result = ScraperResult(
            success=True,
            data=WebPageData(
                url="https://example.com/products?page=1", status_code=200, headers={}
            ),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP, source="https://example.com/products?page=1"
            ),
        )

        # Test incrementing page number
        next_url = await http_scraper._get_next_page(
            "https://example.com/products?page=1", result, 1
        )
        assert next_url == "https://example.com/products?page=2"

        # Test with higher page number
        next_url = await http_scraper._get_next_page(
            "https://example.com/products?page=10", result, 10
        )
        assert next_url == "https://example.com/products?page=11"

    @pytest.mark.asyncio
    async def test_get_next_page_with_offset_pattern(self, http_scraper):
        """Test pagination with offset-based URL pattern."""
        http_scraper.config.pagination = PaginationConfig(
            enabled=True,
            next_page_url_pattern="https://api.example.com/items?offset={offset}&limit=20",
        )

        result = ScraperResult(
            success=True,
            data=WebPageData(
                url="https://api.example.com/items?offset=0&limit=20", status_code=200, headers={}
            ),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP,
                source="https://api.example.com/items?offset=0&limit=20",
            ),
        )

        # Offset should be calculated based on page number
        next_url = await http_scraper._get_next_page(
            "https://api.example.com/items?offset=0&limit=20", result, 1
        )
        # Page 2 would be offset=20 (page 1 * 20 items per page)
        assert "offset=" in next_url

    @pytest.mark.asyncio
    async def test_get_next_page_max_pages_limit(self, http_scraper):
        """Test pagination respects max_pages limit."""
        http_scraper.config.pagination = PaginationConfig(
            enabled=True, max_pages=5, next_page_url_pattern="https://example.com/page/{page}"
        )

        result = ScraperResult(
            success=True,
            data=WebPageData(url="https://example.com/page/5", status_code=200, headers={}),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP, source="https://example.com/page/5"
            ),
        )

        # Should return None when max_pages is reached
        next_url = await http_scraper._get_next_page("https://example.com/page/5", result, 5)
        assert next_url is None

    @pytest.mark.asyncio
    async def test_get_next_page_no_pagination_config(self, http_scraper):
        """Test getting next page with no pagination configuration."""
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
    async def test_get_next_page_pagination_disabled(self, http_scraper):
        """Test getting next page with pagination disabled."""
        http_scraper.config.pagination = PaginationConfig(
            enabled=False, next_page_selector="a.next"
        )

        result = ScraperResult(
            success=True,
            data=WebPageData(
                url="https://example.com/page1",
                status_code=200,
                headers={},
                content='<a class="next" href="/page2">Next</a>',
            ),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP, source="https://example.com/page1"
            ),
        )

        next_url = await http_scraper._get_next_page("https://example.com/page1", result, 1)
        assert next_url is None

    @pytest.mark.asyncio
    async def test_scrape_with_pagination_integration(self, http_scraper):
        """Test full pagination flow with multiple pages."""
        http_scraper.config.pagination = PaginationConfig(
            enabled=True, max_pages=3, next_page_selector="a.next"
        )

        # Mock responses for 3 pages
        page1_response = Mock()
        page1_response.status_code = 200
        page1_response.text = """
            <html><body>
                <div>Page 1 Content</div>
                <a class="next" href="/page2">Next</a>
            </body></html>
        """
        page1_response.headers = {}
        page1_response.url = "https://example.com/page1"
        page1_response.raise_for_status = Mock()

        page2_response = Mock()
        page2_response.status_code = 200
        page2_response.text = """
            <html><body>
                <div>Page 2 Content</div>
                <a class="next" href="/page3">Next</a>
            </body></html>
        """
        page2_response.headers = {}
        page2_response.url = "https://example.com/page2"
        page2_response.raise_for_status = Mock()

        page3_response = Mock()
        page3_response.status_code = 200
        page3_response.text = """
            <html><body>
                <div>Page 3 Content</div>
                <!-- No next link, end of pagination -->
            </body></html>
        """
        page3_response.headers = {}
        page3_response.url = "https://example.com/page3"
        page3_response.raise_for_status = Mock()

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(
                side_effect=[page1_response, page2_response, page3_response]
            )

            results = await http_scraper.scrape_paginated("https://example.com/page1")

            assert len(results) == 3
            assert all(r.success for r in results)
            assert "Page 1 Content" in results[0].data.content
            assert "Page 2 Content" in results[1].data.content
            assert "Page 3 Content" in results[2].data.content

    @pytest.mark.asyncio
    async def test_scrape_paginated_with_stop_condition(self, http_scraper):
        """Test pagination with stop condition."""
        http_scraper.config.pagination = PaginationConfig(
            enabled=True, next_page_selector="a.next", stop_condition="No more results"
        )

        # Page with stop condition text
        response_with_stop = Mock()
        response_with_stop.status_code = 200
        response_with_stop.text = """
            <html><body>
                <div>No more results</div>
                <a class="next" href="/page2">Next</a>
            </body></html>
        """
        response_with_stop.headers = {}
        response_with_stop.url = "https://example.com/page1"
        response_with_stop.raise_for_status = Mock()

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(return_value=response_with_stop)

            results = await http_scraper.scrape_paginated("https://example.com/page1")

            # Should stop after first page due to stop condition
            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_pagination_with_relative_urls(self, http_scraper):
        """Test pagination with relative URLs."""
        http_scraper.config.pagination = PaginationConfig(enabled=True, next_page_selector="a.next")

        result = ScraperResult(
            success=True,
            data=WebPageData(
                url="https://example.com/products/page1",
                status_code=200,
                headers={},
                content="""
                <html>
                    <body>
                        <a class="next" href="../page2">Next</a>
                    </body>
                </html>
                """,
            ),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP, source="https://example.com/products/page1"
            ),
        )

        next_url = await http_scraper._get_next_page(
            "https://example.com/products/page1", result, 1
        )
        # Should resolve relative URL correctly
        assert next_url == "https://example.com/page2"

    @pytest.mark.asyncio
    async def test_pagination_with_query_parameters(self, http_scraper):
        """Test pagination with query parameters in URL."""
        http_scraper.config.pagination = PaginationConfig(enabled=True, next_page_selector="a.next")

        result = ScraperResult(
            success=True,
            data=WebPageData(
                url="https://example.com/search?q=test&page=1",
                status_code=200,
                headers={},
                content="""
                <html>
                    <body>
                        <a class="next" href="?q=test&page=2">Next</a>
                    </body>
                </html>
                """,
            ),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP, source="https://example.com/search?q=test&page=1"
            ),
        )

        next_url = await http_scraper._get_next_page(
            "https://example.com/search?q=test&page=1", result, 1
        )
        assert next_url == "https://example.com/search?q=test&page=2"

    @pytest.mark.asyncio
    async def test_pagination_with_ajax_endpoints(self, http_scraper):
        """Test pagination with AJAX/API endpoints."""
        http_scraper.config.pagination = PaginationConfig(
            enabled=True,
            next_page_url_pattern="https://api.example.com/data?page={page}&format=json",
        )

        # Simulate JSON response
        json_response = Mock()
        json_response.status_code = 200
        json_response.text = '{"items": [], "hasNext": true}'
        json_response.headers = {"content-type": "application/json"}
        json_response.url = "https://api.example.com/data?page=1&format=json"
        json_response.raise_for_status = Mock()

        result = ScraperResult(
            success=True,
            data=WebPageData(
                url="https://api.example.com/data?page=1&format=json",
                status_code=200,
                headers={"content-type": "application/json"},
                content=json_response.text,
            ),
            metadata=ScraperMetadata(
                scraper_type=ScraperType.WEB_HTTP,
                source="https://api.example.com/data?page=1&format=json",
            ),
        )

        next_url = await http_scraper._get_next_page(
            "https://api.example.com/data?page=1&format=json", result, 1
        )
        assert next_url == "https://api.example.com/data?page=2&format=json"

    @pytest.mark.asyncio
    async def test_pagination_error_handling(self, http_scraper):
        """Test error handling during pagination."""
        http_scraper.config.pagination = PaginationConfig(
            enabled=True, max_pages=5, next_page_selector="a.next"
        )

        # First page succeeds
        page1_response = Mock()
        page1_response.status_code = 200
        page1_response.text = (
            '<html><body>Page 1<a class="next" href="/page2">Next</a></body></html>'
        )
        page1_response.headers = {}
        page1_response.url = "https://example.com/page1"
        page1_response.raise_for_status = Mock()

        # Second page fails
        from httpx import HTTPError

        with patch.object(http_scraper, "_client") as mock_client:
            mock_client.request = AsyncMock(
                side_effect=[page1_response, HTTPError("Connection failed")]
            )

            results = await http_scraper.scrape_paginated("https://example.com/page1")

            # Should have results from first page and error from second
            assert len(results) == 2
            assert results[0].success is True
            assert results[1].success is False
            assert results[1].error is not None
