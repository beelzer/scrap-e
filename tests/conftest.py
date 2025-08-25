"""Pytest configuration and shared fixtures."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scrap_e.core.config import ScraperConfig, WebScraperConfig  # noqa: E402
from scrap_e.scrapers.web.http_scraper import HttpScraper  # noqa: E402
from scrap_e.scrapers.web.parser import HtmlParser  # noqa: E402
from tests.fixtures import BASIC_HTML, create_mock_response  # noqa: E402


@pytest.fixture
def basic_html():
    """Provide basic HTML for testing."""
    return BASIC_HTML


@pytest.fixture
def html_parser():
    """Create an HTML parser with basic HTML."""
    return HtmlParser(BASIC_HTML)


@pytest.fixture
def scraper_config():
    """Provide default scraper configuration."""
    return ScraperConfig()


@pytest.fixture
def web_scraper_config():
    """Provide default web scraper configuration."""
    return WebScraperConfig()


@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""
    return create_mock_response(
        status_code=200,
        content=BASIC_HTML,
        headers={"content-type": "text/html"},
    )


@pytest_asyncio.fixture
async def http_scraper():
    """Create an HTTP scraper instance."""
    scraper = HttpScraper()
    yield scraper
    # Cleanup if needed
    if hasattr(scraper, "_client") and scraper._client:
        await scraper._client.aclose()


@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient."""
    with patch("httpx.AsyncClient") as mock:
        client = MagicMock(spec=AsyncClient)
        mock.return_value.__aenter__.return_value = client
        mock.return_value.__aexit__.return_value = None
        yield client


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Performance testing fixtures
@pytest.fixture
def benchmark_html():
    """Generate large HTML for performance testing."""
    items = "\n".join([f'<div class="item-{i}">Content {i}</div>' for i in range(1000)])
    return f"""
    <html>
        <body>
            <div class="container">
                {items}
            </div>
        </body>
    </html>
    """


@pytest.fixture
def mock_browser_page():
    """Mock Playwright page object."""
    page = MagicMock()
    page.goto = MagicMock(return_value=asyncio.coroutine(lambda: None)())
    page.content = MagicMock(return_value=asyncio.coroutine(lambda: BASIC_HTML)())
    page.evaluate = MagicMock(return_value=asyncio.coroutine(lambda: {})())
    page.screenshot = MagicMock(return_value=asyncio.coroutine(lambda: b"fake_image")())
    return page


# Markers for test organization
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "network: mark test as requiring network access")


# Test data fixtures
@pytest.fixture
def sample_extraction_rules():
    """Provide sample extraction rules."""
    from scrap_e.core.models import ExtractionRule

    return [
        ExtractionRule(name="title", selector="h1"),
        ExtractionRule(name="description", selector=".description"),
        ExtractionRule(name="items", selector=".items span", multiple=True),
    ]


@pytest.fixture
def sample_urls():
    """Provide sample URLs for testing."""
    return [
        "https://example.com",
        "https://example.com/page1",
        "https://example.com/page2",
    ]


# Async test utilities
@pytest.fixture
def async_mock():
    """Create an async mock function."""

    def _async_mock(return_value=None):
        async def mock_func(*args, **kwargs):
            return return_value

        return MagicMock(side_effect=mock_func)

    return _async_mock
