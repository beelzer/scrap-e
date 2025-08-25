# Web Scraping Guide

Comprehensive guide to web scraping with Scrap-E's HTTP and browser-based scrapers.

## Overview

Scrap-E provides two main approaches to web scraping:

- **HttpScraper**: Fast, lightweight scraping using HTTP requests
- **BrowserScraper**: Full browser automation for JavaScript-heavy sites

Choose based on your target website's complexity and requirements.

## HTTP Scraping

### Basic HTTP Scraping

The `HttpScraper` is ideal for static websites and APIs:

```python
import asyncio
from scrap_e.scrapers.web.http_scraper import HttpScraper

async def basic_scraping():
    scraper = HttpScraper()

    result = await scraper.scrape("https://httpbin.org/json")

    if result.success:
        print(f"Status: {result.data.status_code}")
        print(f"Content: {result.data.content}")
        print(f"Headers: {result.data.headers}")

    await scraper._cleanup()

asyncio.run(basic_scraping())
```

### Data Extraction with Rules

Extract specific data using CSS selectors, XPath, or regular expressions:

```python
from scrap_e.core.models import ExtractionRule
from scrap_e.scrapers.web.http_scraper import HttpScraper

async def extract_with_rules():
    scraper = HttpScraper()

    # Add extraction rules
    scraper.extraction_rules = [
        ExtractionRule(
            name="title",
            selector="h1.main-title",
            required=True
        ),
        ExtractionRule(
            name="articles",
            selector="article.post",
            multiple=True,
            attribute="data-id"
        ),
        ExtractionRule(
            name="email",
            regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            multiple=True
        )
    ]

    result = await scraper.scrape("https://example-blog.com")

    if result.success and result.data.extracted_data:
        data = result.data.extracted_data
        print(f"Title: {data.get('title')}")
        print(f"Articles: {len(data.get('articles', []))}")
        print(f"Emails found: {data.get('email', [])}")

    await scraper._cleanup()

asyncio.run(extract_with_rules())
```

### Session Management and Cookies

Maintain session state across requests:

```python
async def session_scraping():
    scraper = HttpScraper()

    urls = [
        "https://httpbin.org/cookies/set/session_id/abc123",
        "https://httpbin.org/cookies",
        "https://httpbin.org/headers"
    ]

    # Scrape with session persistence
    results = await scraper.scrape_with_session(
        urls,
        initial_cookies={"user_pref": "dark_mode"}
    )

    for i, result in enumerate(results):
        if result.success:
            print(f"Request {i+1}: {result.data.url}")

asyncio.run(session_scraping())
```

### Custom Headers and Authentication

Handle authentication and custom headers:

```python
async def authenticated_scraping():
    scraper = HttpScraper()

    # Custom headers
    headers = {
        "Authorization": "Bearer your-token-here",
        "User-Agent": "MyBot 1.0",
        "Accept": "application/json"
    }

    # Scrape with authentication
    result = await scraper.scrape(
        "https://api.example.com/protected",
        headers=headers,
        method="POST",
        json={"query": "search term"}
    )

    if result.success:
        print(f"Protected data: {result.data.content}")

asyncio.run(authenticated_scraping())
```

### Handling Forms and POST Requests

Submit forms and handle POST requests:

```python
async def form_submission():
    scraper = HttpScraper()

    # Login form submission
    login_data = {
        "username": "user@example.com",
        "password": "secure_password",
        "remember_me": "1"
    }

    result = await scraper.scrape(
        "https://example.com/login",
        method="POST",
        data=login_data
    )

    if result.success and result.data.status_code == 200:
        print("Login successful!")

        # Use cookies from login for subsequent requests
        cookies = {}
        set_cookie = result.data.headers.get("set-cookie", "")
        for cookie in set_cookie.split(","):
            if "=" in cookie:
                key, value = cookie.split("=", 1)
                cookies[key.strip()] = value.split(";")[0].strip()

        # Access protected page
        protected_result = await scraper.scrape(
            "https://example.com/dashboard",
            cookies=cookies
        )

asyncio.run(form_submission())
```

## Browser Scraping

### Basic Browser Automation

Use `BrowserScraper` for JavaScript-heavy sites:

```python
from scrap_e.scrapers.web import BrowserScraper

async def browser_scraping():
    scraper = BrowserScraper()

    result = await scraper.scrape(
        "https://spa-example.com",
        wait_for_selector=".dynamic-content",
        screenshot=True
    )

    if result.success:
        print(f"Title: {result.data.title}")
        print(f"Content loaded: {len(result.data.content)}")

        # Save screenshot
        if result.data.screenshot:
            with open("page_screenshot.png", "wb") as f:
                f.write(result.data.screenshot)

asyncio.run(browser_scraping())
```

### Page Interactions

Interact with page elements:

```python
async def interactive_scraping():
    scraper = BrowserScraper()

    interactions = [
        {"action": "fill", "selector": "#search-input", "value": "Python scraping"},
        {"action": "click", "selector": "#search-button"},
        {"action": "wait", "time": 2},
        {"action": "click", "selector": ".result-item:first-child"}
    ]

    result = await scraper.interact_and_scrape(
        "https://search-example.com",
        interactions=interactions
    )

    if result.success:
        print(f"Final page: {result.data.url}")

asyncio.run(interactive_scraping())
```

### Infinite Scroll Pages

Handle infinite scroll and dynamic loading:

```python
async def infinite_scroll_scraping():
    scraper = BrowserScraper()

    result = await scraper.scrape_infinite_scroll(
        "https://infinite-scroll-example.com",
        max_scrolls=5,
        wait_between_scrolls=2
    )

    if result.success:
        print(f"Final content length: {len(result.data.content)}")

asyncio.run(infinite_scroll_scraping())
```

### Single Page Applications (SPAs)

Navigate through SPA routes:

```python
async def spa_scraping():
    scraper = BrowserScraper()

    routes = ["#/home", "#/products", "#/about", "#/contact"]

    results = await scraper.scrape_spa(
        "https://spa-example.com",
        routes=routes,
        wait_after_navigation=1
    )

    for i, result in enumerate(results):
        print(f"Route {i}: {result.url} - Title: {result.title}")

asyncio.run(spa_scraping())
```

## Advanced Techniques

### Concurrent Scraping

Scrape multiple URLs concurrently:

```python
async def concurrent_scraping():
    scraper = HttpScraper()

    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/json",
        "https://httpbin.org/headers"
    ]

    # Concurrent scraping with session management
    async with scraper.session() as s:
        results = await s.scrape_multiple(
            urls,
            max_concurrent=3
        )

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")

asyncio.run(concurrent_scraping())
```

### Pagination Handling

Automatically follow pagination:

```python
from scrap_e.core.config import WebScraperConfig
from scrap_e.core.models import PaginationConfig

async def paginated_scraping():
    config = WebScraperConfig(
        pagination=PaginationConfig(
            enabled=True,
            max_pages=5,
            next_page_selector="a.next-page",
            stop_condition="No more results"
        )
    )

    scraper = HttpScraper(config)

    # Extract data from each page
    scraper.add_extraction_rule(ExtractionRule(
        name="items",
        selector=".item",
        multiple=True
    ))

    results = await scraper.scrape_paginated("https://example.com/page1")

    all_items = []
    for result in results:
        if result.success and result.data.extracted_data:
            all_items.extend(result.data.extracted_data.get("items", []))

    print(f"Total items collected: {len(all_items)}")

asyncio.run(paginated_scraping())
```

### Sitemap Processing

Extract and scrape URLs from sitemaps:

```python
async def sitemap_scraping():
    scraper = HttpScraper()

    # Extract URLs from sitemap
    urls = await scraper.scrape_sitemap("https://example.com/sitemap.xml")
    print(f"Found {len(urls)} URLs in sitemap")

    # Scrape first 10 URLs
    sample_urls = urls[:10]
    results = await scraper.scrape_multiple(sample_urls)

    for result in results:
        if result.success:
            print(f"✓ {result.data.url}")
        else:
            print(f"✗ {result.error}")

asyncio.run(sitemap_scraping())
```

### Stream Scraping

Process large responses in chunks:

```python
async def stream_scraping():
    scraper = HttpScraper()

    async for chunk in scraper.scrape_stream(
        "https://large-file-example.com/data.html",
        chunk_size=1024
    ):
        # Process each chunk as it arrives
        print(f"Processed chunk: {len(chunk.content)} bytes")

asyncio.run(stream_scraping())
```

## Error Handling and Resilience

### Retry Logic and Error Recovery

```python
from scrap_e.core.config import WebScraperConfig
from scrap_e.core.models import RetryConfig
from scrap_e.core.exceptions import ScraperError, ConnectionError

async def resilient_scraping():
    config = WebScraperConfig(
        retry=RetryConfig(
            enabled=True,
            max_attempts=3,
            initial_delay=1.0,
            exponential_base=2.0
        )
    )

    scraper = HttpScraper(config)

    try:
        result = await scraper.scrape("https://unreliable-site.com")

        if result.success:
            print("Scraping successful after retries")
        else:
            print(f"Scraping failed: {result.error}")

    except ConnectionError as e:
        print(f"Connection error: {e}")
    except ScraperError as e:
        print(f"Scraper error: {e}")

asyncio.run(resilient_scraping())
```

### Rate Limiting and Politeness

```python
from scrap_e.core.models import RateLimitConfig

async def polite_scraping():
    config = WebScraperConfig(
        rate_limit=RateLimitConfig(
            enabled=True,
            requests_per_second=2.0,
            burst_size=5
        )
    )

    scraper = HttpScraper(config)

    urls = [f"https://example.com/page{i}" for i in range(10)]

    # Rate limiting is applied automatically
    results = await scraper.scrape_multiple(urls)

    print(f"Scraped {len(results)} URLs with rate limiting")

asyncio.run(polite_scraping())
```

## Performance Optimization

### Caching

Enable response caching:

```python
from scrap_e.core.models import CacheConfig

async def cached_scraping():
    config = WebScraperConfig(
        cache=CacheConfig(
            enabled=True,
            backend="memory",
            ttl_seconds=300,
            max_size_mb=100
        )
    )

    scraper = HttpScraper(config)

    # First request - fetched from server
    result1 = await scraper.scrape("https://example.com")
    print(f"First request: {result1.metadata.duration_seconds:.2f}s")

    # Second request - served from cache (much faster)
    result2 = await scraper.scrape("https://example.com")
    print(f"Cached request: {result2.metadata.duration_seconds:.2f}s")

asyncio.run(cached_scraping())
```

### Connection Pooling

Optimize for high-volume scraping:

```python
async def high_volume_scraping():
    config = WebScraperConfig(
        concurrent_requests=20,
        default_timeout=15.0,
        max_workers=10
    )

    scraper = HttpScraper(config)

    # Generate many URLs
    urls = [f"https://httpbin.org/delay/{i%3}" for i in range(100)]

    import time
    start_time = time.time()

    results = await scraper.scrape_multiple(urls)

    duration = time.time() - start_time
    successful = sum(1 for r in results if r.success)

    print(f"Scraped {successful}/{len(urls)} URLs in {duration:.2f}s")
    print(f"Rate: {successful/duration:.1f} URLs/second")

asyncio.run(high_volume_scraping())
```

## Best Practices

### 1. Choose the Right Scraper

- **HttpScraper**: Static sites, APIs, fast scraping
- **BrowserScraper**: SPAs, JavaScript-heavy sites, complex interactions

### 2. Respect Robots.txt

```python
async def check_robots():
    scraper = HttpScraper()

    # Check robots.txt before scraping
    robots_result = await scraper.scrape("https://example.com/robots.txt")

    if robots_result.success:
        robots_content = robots_result.data.content
        if "Disallow: /" in robots_content:
            print("Site disallows scraping")
            return

    # Proceed with scraping
    result = await scraper.scrape("https://example.com")

asyncio.run(check_robots())
```

### 3. Use Appropriate User Agents

```python
config = WebScraperConfig(
    user_agent="MyBot 1.0 (+https://mysite.com/bot)"
)
```

### 4. Handle Errors Gracefully

```python
async def safe_scraping():
    scraper = HttpScraper()

    urls = ["https://example.com", "https://invalid-url.xyz"]

    for url in urls:
        try:
            result = await scraper.scrape(url)
            if result.success:
                print(f"✓ {url}")
            else:
                print(f"✗ {url}: {result.error}")
        except Exception as e:
            print(f"✗ {url}: Unexpected error: {e}")

asyncio.run(safe_scraping())
```

### 5. Monitor Performance

```python
async def monitored_scraping():
    scraper = HttpScraper()

    # Scrape some URLs
    urls = [f"https://httpbin.org/delay/{i}" for i in range(5)]
    await scraper.scrape_multiple(urls)

    # Check statistics
    stats = scraper.get_stats()
    print(f"Total requests: {stats.total_requests}")
    print(f"Successful: {stats.successful_requests}")
    print(f"Failed: {stats.failed_requests}")
    print(f"Average response time: {stats.average_response_time:.2f}s")

asyncio.run(monitored_scraping())
```

## Common Patterns

### News Article Scraping

```python
async def scrape_news():
    scraper = HttpScraper()

    scraper.add_extraction_rule(ExtractionRule(
        name="headline",
        selector="h1.headline, h1.title",
        required=True
    ))

    scraper.add_extraction_rule(ExtractionRule(
        name="author",
        selector=".author, .byline",
    ))

    scraper.add_extraction_rule(ExtractionRule(
        name="publish_date",
        selector="time[datetime], .publish-date",
        attribute="datetime"
    ))

    scraper.add_extraction_rule(ExtractionRule(
        name="content",
        selector=".article-body, .content",
        multiple=True
    ))

    result = await scraper.scrape("https://news-site.com/article")

    if result.success:
        article = result.data.extracted_data
        print(f"Title: {article['headline']}")
        print(f"Author: {article['author']}")
        print(f"Date: {article['publish_date']}")
        print(f"Paragraphs: {len(article['content'])}")

asyncio.run(scrape_news())
```

### E-commerce Product Data

```python
async def scrape_products():
    scraper = BrowserScraper()  # E-commerce sites often use JavaScript

    scraper.add_extraction_rule(ExtractionRule(
        name="name",
        selector="h1.product-title",
        required=True
    ))

    scraper.add_extraction_rule(ExtractionRule(
        name="price",
        selector=".price .current",
        transform="float"
    ))

    scraper.add_extraction_rule(ExtractionRule(
        name="rating",
        selector=".rating",
        attribute="data-rating"
    ))

    scraper.add_extraction_rule(ExtractionRule(
        name="reviews",
        selector=".review",
        multiple=True
    ))

    scraper.add_extraction_rule(ExtractionRule(
        name="images",
        selector=".product-image img",
        attribute="src",
        multiple=True
    ))

    result = await scraper.scrape("https://shop.example.com/product/123")

    if result.success:
        product = result.data.extracted_data
        print(f"Product: {product['name']}")
        print(f"Price: ${product['price']}")
        print(f"Rating: {product['rating']}/5")
        print(f"Reviews: {len(product['reviews'])}")
        print(f"Images: {len(product['images'])}")

asyncio.run(scrape_products())
```

## Troubleshooting

### Common Issues

1. **JavaScript Not Loading**: Use `BrowserScraper` instead of `HttpScraper`
2. **Rate Limiting**: Reduce `requests_per_second` in configuration
3. **Timeouts**: Increase `default_timeout` for slow sites
4. **Memory Usage**: Enable streaming for large responses
5. **Blocked Requests**: Use different user agents and proxies

### Debug Mode

```python
from scrap_e.core.config import WebScraperConfig

config = WebScraperConfig(
    debug=True,
    log_level="DEBUG",
    browser_headless=False,  # See browser in action
    browser_screenshot_on_error=True
)

scraper = BrowserScraper(config)
# Detailed logs and error screenshots will be generated
```

## Next Steps

- Explore [API scraping](api-scraping.md) for REST and GraphQL APIs
- Learn about [database scraping](database-scraping.md) for direct data access
- Check out [file processing](file-processing.md) for local file extraction
- Review [performance optimization](performance.md) techniques
