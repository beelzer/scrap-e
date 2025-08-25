# Error Handling

Scrap-E provides comprehensive error handling to help you build robust scraping applications. This guide covers the exception hierarchy, common error scenarios, and best practices for handling failures gracefully.

## Exception Hierarchy

Scrap-E uses a structured exception hierarchy based on `ScraperError`:

```python
from scrap_e.core.exceptions import (
    ScraperError,        # Base exception
    ConnectionError,     # Network-related errors
    ParsingError,        # HTML/data parsing errors
    TimeoutError,        # Timeout-related errors
    AuthenticationError, # Authentication failures
    ValidationError,     # Data validation errors
    ConfigurationError,  # Configuration issues
    RateLimitError,      # Rate limiting errors
)
```

### Base Exception: ScraperError

All Scrap-E exceptions inherit from `ScraperError`:

```python
from scrap_e.core.exceptions import ScraperError

try:
    result = await scraper.scrape(url)
except ScraperError as e:
    print(f"Scraping failed: {e}")
    print(f"Error details: {e.details}")
    print(f"Error code: {e.error_code}")
```

## Common Error Types

### Connection Errors

Network-related issues like DNS failures, connection timeouts, or unreachable servers:

```python
from scrap_e.core.exceptions import ConnectionError
from scrap_e.scrapers.web.http_scraper import HttpScraper

async def handle_connection_errors():
    scraper = HttpScraper()

    try:
        result = await scraper.scrape("https://unreachable-site.com")
    except ConnectionError as e:
        print(f"Connection failed: {e}")
        # Log the error and try alternative approach
        logger.warning(f"Failed to connect to {url}: {e}")

        # Maybe try a different URL or proxy
        await try_with_proxy(scraper, url)
```

### Timeout Errors

When operations exceed configured timeout limits:

```python
from scrap_e.core.exceptions import TimeoutError
from scrap_e.core.config import WebScraperConfig

async def handle_timeouts():
    config = WebScraperConfig(default_timeout=10.0)
    scraper = HttpScraper(config)

    try:
        result = await scraper.scrape("https://very-slow-site.com")
    except TimeoutError as e:
        print(f"Request timed out: {e}")

        # Retry with longer timeout
        config.default_timeout = 60.0
        scraper = HttpScraper(config)
        result = await scraper.scrape("https://very-slow-site.com")
```

### Parsing Errors

Issues with HTML parsing or data extraction:

```python
from scrap_e.core.exceptions import ParsingError
from scrap_e.core.models import ExtractionRule

async def handle_parsing_errors():
    scraper = HttpScraper()
    scraper.extraction_rules = [
        ExtractionRule(
            name="title",
            selector="h1.main-title",
            required=True  # This will cause ParsingError if not found
        )
    ]

    try:
        result = await scraper.scrape("https://example.com")
    except ParsingError as e:
        print(f"Failed to parse content: {e}")

        # Try with fallback selector
        scraper.extraction_rules = [
            ExtractionRule(
                name="title",
                selector="h1, .title, #title",  # Multiple fallback selectors
                required=False
            )
        ]
        result = await scraper.scrape("https://example.com")
```

### Rate Limit Errors

When hitting API or server rate limits:

```python
from scrap_e.core.exceptions import RateLimitError
import asyncio

async def handle_rate_limits():
    scraper = HttpScraper()

    try:
        result = await scraper.scrape("https://api.example.com/data")
    except RateLimitError as e:
        print(f"Rate limited: {e}")

        # Wait for the suggested retry period
        if hasattr(e, 'retry_after'):
            await asyncio.sleep(e.retry_after)
        else:
            await asyncio.sleep(60)  # Default wait

        # Retry the request
        result = await scraper.scrape("https://api.example.com/data")
```

## Error Recovery Patterns

### Retry Logic

Implement exponential backoff for transient failures:

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from scrap_e.core.exceptions import ConnectionError, TimeoutError

class RobustScraper:
    def __init__(self):
        self.scraper = HttpScraper()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def scrape_with_retry(self, url: str):
        try:
            return await self.scraper.scrape(url)
        except (ConnectionError, TimeoutError) as e:
            print(f"Retry attempt failed: {e}")
            raise  # Re-raise to trigger retry

# Usage
scraper = RobustScraper()
result = await scraper.scrape_with_retry("https://flaky-site.com")
```

### Fallback Strategies

Use multiple approaches when primary method fails:

```python
from scrap_e.scrapers.web.http_scraper import HttpScraper
from scrap_e.scrapers.web.browser_scraper import BrowserScraper

async def scrape_with_fallback(url: str):
    # Try HTTP first (faster)
    http_scraper = HttpScraper()
    try:
        result = await http_scraper.scrape(url)
        if result.success:
            return result
    except ScraperError as e:
        print(f"HTTP scraping failed: {e}")

    # Fallback to browser scraping
    browser_scraper = BrowserScraper()
    try:
        result = await browser_scraper.scrape(url)
        return result
    except ScraperError as e:
        print(f"Browser scraping also failed: {e}")
        raise
```

### Graceful Degradation

Continue operation with partial results when possible:

```python
async def scrape_with_degradation(urls: list[str]):
    scraper = HttpScraper()
    results = []
    errors = []

    for url in urls:
        try:
            result = await scraper.scrape(url)
            if result.success:
                results.append(result)
            else:
                errors.append(f"{url}: {result.error}")
        except ScraperError as e:
            errors.append(f"{url}: {e}")
            continue  # Continue with other URLs

    # Log summary
    print(f"Successfully scraped {len(results)}/{len(urls)} URLs")
    if errors:
        print(f"Errors encountered: {len(errors)}")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")

    return results, errors
```

## Validation and Data Quality

### Input Validation

Validate URLs and parameters before scraping:

```python
from scrap_e.core.exceptions import ValidationError
from urllib.parse import urlparse

def validate_url(url: str) -> str:
    """Validate and normalize URL."""
    if not url:
        raise ValidationError("URL cannot be empty")

    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"

    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValidationError(f"Invalid URL format: {url}")

    return url

async def safe_scrape(url: str):
    try:
        validated_url = validate_url(url)
        scraper = HttpScraper()
        return await scraper.scrape(validated_url)
    except ValidationError as e:
        print(f"URL validation failed: {e}")
        return None
```

### Result Validation

Validate scraped data quality:

```python
from pydantic import BaseModel, ValidationError as PydanticValidationError
from typing import List, Optional

class ProductData(BaseModel):
    title: str
    price: Optional[float] = None
    description: str
    in_stock: bool = True

async def scrape_and_validate(url: str):
    scraper = HttpScraper()
    scraper.extraction_rules = [
        ExtractionRule(name="title", selector=".product-title"),
        ExtractionRule(name="price", selector=".price"),
        ExtractionRule(name="description", selector=".description"),
        ExtractionRule(name="in_stock", selector=".stock-status"),
    ]

    result = await scraper.scrape(url)

    if not result.success:
        return None

    try:
        # Validate extracted data structure
        product = ProductData(**result.data.extracted_data)
        return product
    except PydanticValidationError as e:
        print(f"Data validation failed: {e}")
        # Log data quality issue
        logger.warning(f"Invalid product data from {url}: {e}")
        return None
```

## Logging and Monitoring

### Structured Logging

Use structured logging for better error tracking:

```python
import structlog
from scrap_e.core.exceptions import ScraperError

logger = structlog.get_logger()

async def logged_scrape(url: str, user_id: str = None):
    scraper = HttpScraper()

    try:
        logger.info(
            "Starting scrape operation",
            url=url,
            user_id=user_id,
            scraper_type="http"
        )

        result = await scraper.scrape(url)

        if result.success:
            logger.info(
                "Scrape completed successfully",
                url=url,
                status_code=result.data.status_code,
                content_length=len(result.data.content or ""),
                duration=result.metadata.duration_seconds
            )
        else:
            logger.error(
                "Scrape failed",
                url=url,
                error=result.error,
                user_id=user_id
            )

        return result

    except ScraperError as e:
        logger.exception(
            "Scraper exception occurred",
            url=url,
            error_type=type(e).__name__,
            error_details=getattr(e, 'details', None),
            user_id=user_id
        )
        raise
```

### Health Monitoring

Monitor scraper health and performance:

```python
from dataclasses import dataclass, field
from typing import Dict
import time

@dataclass
class ScraperHealth:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    error_counts: Dict[str, int] = field(default_factory=dict)
    last_error: Optional[str] = None
    last_error_time: Optional[float] = None

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    def record_success(self):
        self.total_requests += 1
        self.successful_requests += 1

    def record_error(self, error: Exception):
        self.total_requests += 1
        self.failed_requests += 1

        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        self.last_error = str(error)
        self.last_error_time = time.time()

class MonitoredScraper:
    def __init__(self):
        self.scraper = HttpScraper()
        self.health = ScraperHealth()

    async def scrape(self, url: str):
        try:
            result = await self.scraper.scrape(url)

            if result.success:
                self.health.record_success()
            else:
                self.health.record_error(Exception(result.error))

            return result

        except Exception as e:
            self.health.record_error(e)
            raise

    def get_health_report(self) -> dict:
        return {
            "success_rate": f"{self.health.success_rate:.2%}",
            "total_requests": self.health.total_requests,
            "error_breakdown": self.health.error_counts,
            "last_error": self.health.last_error,
            "last_error_time": self.health.last_error_time
        }
```

## Best Practices

### 1. Always Use Context Managers

Ensure proper resource cleanup:

```python
async def proper_resource_management():
    # Good: Using session context manager
    scraper = HttpScraper()
    async with scraper.session() as session:
        result = await session.scrape("https://example.com")
    # Resources automatically cleaned up
```

### 2. Set Appropriate Timeouts

Configure timeouts based on expected response times:

```python
from scrap_e.core.config import WebScraperConfig

# For fast APIs
fast_config = WebScraperConfig(default_timeout=10.0)

# For slower web scraping
slow_config = WebScraperConfig(default_timeout=60.0)

# For batch operations
batch_config = WebScraperConfig(default_timeout=30.0, concurrent_requests=5)
```

### 3. Implement Circuit Breakers

Prevent cascade failures with circuit breakers:

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout)
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def can_execute(self) -> bool:
        if self.state == "closed":
            return True

        if self.state == "open":
            if datetime.now() - self.last_failure_time > self.timeout:
                self.state = "half-open"
                return True
            return False

        # half-open state
        return True

    def record_success(self):
        self.failure_count = 0
        self.state = "closed"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"

class CircuitBreakerScraper:
    def __init__(self):
        self.scraper = HttpScraper()
        self.circuit_breaker = CircuitBreaker()

    async def scrape(self, url: str):
        if not self.circuit_breaker.can_execute():
            raise ScraperError("Circuit breaker is open")

        try:
            result = await self.scraper.scrape(url)
            if result.success:
                self.circuit_breaker.record_success()
            else:
                self.circuit_breaker.record_failure()
            return result
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise
```

### 4. Use Bulk Error Handling

For batch operations, collect and analyze errors:

```python
from collections import defaultdict

async def batch_scrape_with_analysis(urls: list[str]):
    scraper = HttpScraper()
    results = []
    error_analysis = defaultdict(list)

    for url in urls:
        try:
            result = await scraper.scrape(url)
            results.append(result)
        except ScraperError as e:
            error_type = type(e).__name__
            error_analysis[error_type].append(url)

    # Analyze error patterns
    for error_type, failed_urls in error_analysis.items():
        print(f"{error_type}: {len(failed_urls)} URLs failed")
        if len(failed_urls) > 10:
            print(f"  High failure rate for {error_type} - investigate server issues")

    return results, dict(error_analysis)
```

## CLI Error Handling

The CLI provides detailed error reporting:

```bash
# Enable debug mode for detailed errors
scrap-e --debug scrape https://problematic-site.com

# Check system health before scraping
scrap-e doctor
```

**Common CLI errors and solutions:**

- **Browser not found**: Run `playwright install`
- **Permission denied**: Check file permissions for output directory
- **Network timeout**: Increase timeout with `--timeout 60`
- **Memory issues**: Reduce concurrency with `--concurrent 2`

## Error Recovery Examples

### Website Changes

Handle structural changes in target websites:

```python
async def adaptive_scraping(url: str):
    scraper = HttpScraper()

    # Try current selectors first
    current_rules = [
        ExtractionRule(name="title", selector="h1.current-title")
    ]
    scraper.extraction_rules = current_rules

    result = await scraper.scrape(url)

    if result.success and result.data.extracted_data.get('title'):
        return result

    # Fallback to previous selectors
    fallback_rules = [
        ExtractionRule(name="title", selector="h1.old-title, .legacy-title, h1")
    ]
    scraper.extraction_rules = fallback_rules

    return await scraper.scrape(url)
```

This comprehensive error handling approach ensures your Scrap-E applications are robust and reliable in production environments.
