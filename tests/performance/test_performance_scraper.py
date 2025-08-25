"""Performance benchmark tests for scraper operations."""

import json
import re
from functools import lru_cache

import pytest

from scrap_e.scrapers.web.http_scraper import HttpScraper


@pytest.mark.performance
@pytest.mark.benchmark(group="scraper")
@pytest.mark.asyncio
async def test_http_scraper_initialization_performance(benchmark):
    """Benchmark HTTP scraper initialization."""

    def init_scraper():
        return HttpScraper()

    scraper = benchmark(init_scraper)
    assert scraper is not None


@pytest.mark.performance
@pytest.mark.benchmark(group="scraper")
@pytest.mark.asyncio
async def test_http_request_building_performance(benchmark):
    """Benchmark HTTP request building."""
    scraper = HttpScraper()

    def build_request():
        return scraper._build_request(
            "https://example.com/page",
            headers={"Custom-Header": "Value", "Authorization": "Bearer token"},
            params={"page": 1, "limit": 100, "sort": "desc", "filter": "active"},
            cookies={"session": "abc123", "user_id": "42", "preferences": "dark_mode"},
        )

    request = benchmark(build_request)
    assert str(request.url) == "https://example.com/page"


@pytest.mark.performance
@pytest.mark.benchmark(group="scraper")
def test_concurrent_scraping_setup(benchmark):
    """Benchmark setup for concurrent scraping operations."""
    urls = [f"https://example.com/page{i}" for i in range(100)]

    def setup_batch():
        scraper = HttpScraper()
        scraper.config.concurrent_requests = 10
        request_batch = []
        for url in urls:
            request_batch.append(
                {
                    "url": url,
                    "headers": {"User-Agent": scraper.config.user_agent},
                    "timeout": scraper.config.default_timeout,
                }
            )
        return request_batch

    batch = benchmark(setup_batch)
    assert len(batch) == 100


@pytest.mark.performance
@pytest.mark.benchmark(group="scraper")
def test_scraper_config_validation(benchmark):
    """Benchmark configuration validation and setup."""

    def validate_config():
        scraper = HttpScraper()
        # Simulate config updates that trigger validation
        scraper.config.default_timeout = 30
        scraper.config.max_retries = 3
        scraper.config.concurrent_requests = 10
        scraper.config.rate_limit = 1.0
        scraper.config.user_agent = "CustomBot/1.0"
        scraper.config.headers = {"Accept": "text/html", "Accept-Language": "en-US"}
        scraper.config.proxy = {"http": "http://proxy:8080"}
        scraper.config.verify_ssl = True
        scraper.config.follow_redirects = True
        scraper.config.max_redirects = 5
        return scraper.config

    config = benchmark(validate_config)
    assert config.default_timeout == 30


@pytest.mark.performance
@pytest.mark.benchmark(group="scraper")
def test_url_processing_performance(benchmark):
    """Benchmark URL processing and normalization."""
    base_url = "https://example.com"
    relative_urls = [
        "/page1",
        "../page2",
        "./page3",
        "page4",
        "//cdn.example.com/resource",
        "https://external.com/page",
        "#fragment",
        "?query=param",
        "mailto:test@example.com",
        "javascript:void(0)",
    ]

    def process_urls():
        from urllib.parse import urljoin, urlparse

        results = []
        for url in relative_urls * 10:  # Process 100 URLs
            parsed = urlparse(url)
            if parsed.scheme in ("", "http", "https"):
                normalized = urljoin(base_url, url)
                results.append(normalized)
        return results

    result = benchmark(process_urls)
    assert len(result) > 0


@pytest.mark.performance
@pytest.mark.benchmark(group="string")
def test_string_manipulation_performance(benchmark):
    """Benchmark string manipulation operations common in scraping."""
    text = "  This is a TEST string with    MIXED case and   extra  spaces.  " * 100

    def clean_text():
        # Common text cleaning operations
        cleaned = text.strip()
        cleaned = " ".join(cleaned.split())  # Normalize whitespace
        cleaned = cleaned.lower()
        cleaned = cleaned.replace("test", "benchmark")
        # Remove special characters
        cleaned = re.sub(r"[^\w\s]", "", cleaned)
        # Truncate to a reasonable length
        return cleaned[:5000] if len(cleaned) > 5000 else cleaned

    result = benchmark(clean_text)
    assert "benchmark" in result
    assert "  " not in result


@pytest.mark.performance
@pytest.mark.benchmark(group="string")
def test_json_parsing_performance(benchmark):
    """Benchmark JSON parsing performance."""
    data = {
        "items": [
            {
                "id": i,
                "title": f"Item {i}",
                "description": "Lorem ipsum dolor sit amet " * 10,
                "tags": [f"tag{j}" for j in range(5)],
                "metadata": {
                    "created": f"2024-01-{i % 28 + 1:02d}",
                    "modified": f"2024-02-{i % 28 + 1:02d}",
                    "author": f"Author {i % 10}",
                    "stats": {
                        "views": i * 100,
                        "likes": i * 10,
                        "comments": i * 5,
                    },
                },
                "nested": {"level1": {"level2": {"level3": {"value": f"Deep value {i}"}}}},
            }
            for i in range(100)
        ],
        "pagination": {
            "page": 1,
            "per_page": 100,
            "total": 1000,
            "pages": 10,
        },
    }
    json_str = json.dumps(data)

    def parse_json():
        parsed = json.loads(json_str)
        # Simulate data extraction from parsed JSON
        extracted = []
        for item in parsed["items"]:
            extracted.append(
                {
                    "id": item["id"],
                    "title": item["title"],
                    "author": item["metadata"]["author"],
                    "views": item["metadata"]["stats"]["views"],
                    "deep_value": item["nested"]["level1"]["level2"]["level3"]["value"],
                }
            )
        return extracted

    result = benchmark(parse_json)
    assert len(result) == 100


@pytest.mark.performance
@pytest.mark.benchmark(group="regex")
def test_regex_performance(benchmark):
    """Benchmark regex operations commonly used in scraping."""
    # Generate realistic HTML content
    html_parts = []
    for i in range(100):
        html_parts.append(f"""
        <div class="product-{i}" id="item-{i}">
            <h2>Product Title {i}</h2>
            <span class="price">$99.{i % 100:02d}</span>
            <p>Posted on 2024-{i % 12 + 1:02d}-{i % 28 + 1:02d}</p>
            <a href="/product/{i}">View Details</a>
            <img src="/images/product-{i}.jpg" alt="Product {i}">
        </div>
        """)
    html = "".join(html_parts)

    # Common regex patterns for scraping
    patterns = {
        "headers": re.compile(r"<h\d>(.*?)</h\d>"),
        "classes": re.compile(r'class="([^"]*)"'),
        "ids": re.compile(r'id="([^"]*)"'),
        "dates": re.compile(r"\d{4}-\d{2}-\d{2}"),
        "prices": re.compile(r"\$[\d.]+"),
        "urls": re.compile(r'href="([^"]*)"'),
        "images": re.compile(r'<img[^>]+src="([^"]*)"[^>]*>'),
    }

    def run_regex():
        results = {}
        for name, pattern in patterns.items():
            matches = pattern.findall(html)
            results[name] = matches
        return results

    result = benchmark(run_regex)
    assert all(len(result[key]) > 0 for key in patterns)


@pytest.mark.performance
@pytest.mark.benchmark(group="memory")
def test_large_data_handling(benchmark):
    """Benchmark handling of large data structures."""

    def create_large_dataset():
        # Simulate large scraping result
        data = []
        for i in range(1000):
            data.append(
                {
                    "url": f"https://example.com/page{i}",
                    "status_code": 200,
                    "headers": {
                        "content-type": "text/html",
                        "content-length": str(i * 1000),
                        "server": "nginx",
                        "cache-control": "max-age=3600",
                    },
                    "content": "x" * 1000,  # 1KB per item
                    "extracted": {
                        "title": f"Title {i}",
                        "body": "Lorem ipsum dolor sit amet " * 50,
                        "metadata": {
                            "id": i,
                            "category": i % 10,
                            "tags": [f"tag{j}" for j in range(5)],
                        },
                        "links": [f"/link{j}" for j in range(10)],
                        "images": [f"/img{j}.jpg" for j in range(5)],
                    },
                    "timestamp": f"2024-01-{i % 28 + 1:02d}T12:00:00Z",
                }
            )
        return data

    dataset = benchmark(create_large_dataset)
    assert len(dataset) == 1000


@pytest.mark.performance
@pytest.mark.benchmark(group="cache")
def test_caching_performance(benchmark):
    """Benchmark caching operations."""
    call_count = 0

    @lru_cache(maxsize=128)
    def expensive_operation(n):
        nonlocal call_count
        call_count += 1
        # Simulate expensive parsing/processing
        result = 0
        for i in range(n * 100):
            result += i * i
            if i % 10 == 0:
                result = result // 2
        return result

    def test_cache():
        cache_results = []
        # First pass - cache misses
        for i in range(50):
            cache_results.append(expensive_operation(i % 10))
        # Second pass - cache hits
        for i in range(50):
            cache_results.append(expensive_operation(i % 10))
        # Third pass - mixed
        for i in range(25):
            cache_results.append(expensive_operation(i % 15))
        return cache_results, call_count

    results, count = benchmark(test_cache)
    assert len(results) == 125
    assert count <= 25  # Should cache repeated computations


@pytest.mark.performance
@pytest.mark.benchmark(group="cache")
def test_url_deduplication_performance(benchmark):
    """Benchmark URL deduplication for crawling."""
    # Generate URLs with duplicates
    urls = []
    for i in range(1000):
        urls.append(f"https://example.com/page{i % 100}")
        urls.append(f"https://example.com/article{i % 50}")
        urls.append(f"https://example.com/product{i % 200}")

    def deduplicate_urls():
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        return unique_urls

    result = benchmark(deduplicate_urls)
    assert len(result) < len(urls)
    assert len(result) == len(set(urls))


@pytest.mark.performance
@pytest.mark.benchmark(group="validation")
def test_data_validation_performance(benchmark):
    """Benchmark data validation operations."""
    # Generate data to validate
    items = []
    for i in range(500):
        items.append(
            {
                "id": i,
                "title": f"Item {i}" if i % 10 != 0 else None,
                "price": f"${i}.99" if i % 5 != 0 else "invalid",
                "url": f"https://example.com/item{i}" if i % 7 != 0 else "not-a-url",
                "email": f"user{i}@example.com" if i % 3 != 0 else "invalid-email",
                "date": f"2024-{i % 12 + 1:02d}-{i % 28 + 1:02d}",
            }
        )

    def validate_data():
        import re
        from urllib.parse import urlparse

        valid_items = []
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        price_pattern = re.compile(r"^\$\d+\.?\d*$")
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        for item in items:
            # Validate required fields
            if not item.get("title"):
                continue

            # Validate price format
            if not price_pattern.match(str(item.get("price", ""))):
                continue

            # Validate URL
            try:
                parsed_url = urlparse(item.get("url", ""))
                if not all([parsed_url.scheme, parsed_url.netloc]):
                    continue
            except (ValueError, TypeError):
                continue

            # Validate email
            if not email_pattern.match(item.get("email", "")):
                continue

            # Validate date
            if not date_pattern.match(item.get("date", "")):
                continue

            valid_items.append(item)

        return valid_items

    result = benchmark(validate_data)
    assert len(result) < len(items)
