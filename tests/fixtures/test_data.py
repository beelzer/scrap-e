"""Common test data for scrap-e tests."""

from scrap_e.core.config import ScraperConfig, WebScraperConfig
from scrap_e.core.models import ExtractionRule

# Sample URLs for testing
SAMPLE_URLS = [
    "https://example.com",
    "https://example.com/page1",
    "https://example.com/page2",
    "https://test.example.com",
    "http://localhost:8000",
]

# Sample extraction rules
EXTRACTION_RULES = {
    "title": ExtractionRule(
        name="title",
        selector="h1",
        required=False,
    ),
    "description": ExtractionRule(
        name="description",
        selector=".description",
        required=False,
    ),
    "items": ExtractionRule(
        name="items",
        selector=".items span",
        multiple=True,
        required=False,
    ),
    "price": ExtractionRule(
        name="price",
        regex=r"\$(\d+\.\d{2})",
        required=False,
    ),
    "email": ExtractionRule(
        name="email",
        regex=r"[\w\.-]+@[\w\.-]+\.\w+",
        required=False,
    ),
    "meta_description": ExtractionRule(
        name="meta_description",
        selector="meta[name='description']",
        attribute="content",
        required=False,
    ),
    "links": ExtractionRule(
        name="links",
        selector="a",
        attribute="href",
        multiple=True,
        required=False,
    ),
    "xpath_title": ExtractionRule(
        name="title",
        xpath="//h1/text()",
        required=False,
    ),
    "xpath_items": ExtractionRule(
        name="items",
        xpath="//div[@class='items']//span",
        multiple=True,
        required=False,
    ),
    "transformed": ExtractionRule(
        name="transformed",
        selector=".stats span",
        transform="lambda x: x.replace(',', '')",
        required=False,
    ),
}

# Sample configurations
SAMPLE_CONFIGS = {
    "default": ScraperConfig(),
    "custom": ScraperConfig(
        max_workers=10,
        timeout=60,
        retry_count=5,
        delay=2.0,
    ),
    "web_default": WebScraperConfig(),
    "web_custom": WebScraperConfig(
        max_workers=5,
        timeout=30,
        retry_count=2,
        delay=1.0,
        headers={"User-Agent": "Test Bot"},
        follow_redirects=False,
        verify_ssl=False,
    ),
}

# Sample metadata
SAMPLE_METADATA = {
    "basic": {
        "title": "Test Page",
        "description": "A test page",
        "keywords": ["test", "sample"],
    },
    "full": {
        "title": "Complex Page",
        "description": "A complex test page with metadata",
        "keywords": ["test", "complex", "metadata"],
        "author": "Test Author",
        "published_date": "2024-01-01",
        "modified_date": "2024-01-15",
        "language": "en",
        "canonical_url": "https://example.com/page",
        "og_data": {
            "title": "OG Title",
            "description": "OG Description",
            "image": "https://example.com/image.jpg",
        },
        "twitter_data": {
            "card": "summary",
            "title": "Twitter Title",
            "description": "Twitter Description",
        },
        "json_ld": {
            "@type": "Article",
            "headline": "Test Article",
            "author": "Test Author",
        },
    },
}

# Performance test data
PERFORMANCE_TEST_SIZES = {
    "small": 10,
    "medium": 100,
    "large": 1000,
    "xlarge": 10000,
}

# Test timeouts and delays
TEST_TIMEOUTS = {
    "fast": 0.1,
    "normal": 1.0,
    "slow": 5.0,
}

# Browser test data
BROWSER_TEST_CONFIG = {
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "Mozilla/5.0 (Test Browser)",
    "timeout": 30000,
    "wait_until": "networkidle",
}

# API test endpoints
API_ENDPOINTS = {
    "json": "https://jsonplaceholder.typicode.com/posts",
    "xml": "https://httpbin.org/xml",
    "html": "https://httpbin.org/html",
    "status": "https://httpbin.org/status",
}
