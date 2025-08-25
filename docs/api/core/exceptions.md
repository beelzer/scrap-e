# Exceptions API

Scrap-E provides a comprehensive exception hierarchy for handling different types of errors that can occur during scraping operations.

## Exception Hierarchy

```
ScraperError (base)
├── ConnectionError
├── TimeoutError
├── ParsingError
├── AuthenticationError
├── ValidationError
├── ConfigurationError
└── RateLimitError
```

## Base Exception

::: scrap_e.core.exceptions.ScraperError

## Network Exceptions

### ConnectionError

::: scrap_e.core.exceptions.ConnectionError

**Use Cases:**

- DNS resolution failures
- Network unreachable errors
- Connection refused errors
- SSL/TLS handshake failures

**Example:**

```python
from scrap_e.core.exceptions import ConnectionError
from scrap_e.scrapers.web.http_scraper import HttpScraper

scraper = HttpScraper()

try:
    result = await scraper.scrape("https://unreachable-site.invalid")
except ConnectionError as e:
    print(f"Failed to connect: {e}")
    print(f"Error details: {e.details}")
```

### TimeoutError

::: scrap_e.core.exceptions.TimeoutError

**Use Cases:**

- Request timeouts
- Browser navigation timeouts
- Database query timeouts
- File operation timeouts

**Example:**

```python
from scrap_e.core.exceptions import TimeoutError
from scrap_e.core.config import WebScraperConfig

config = WebScraperConfig(default_timeout=5.0)
scraper = HttpScraper(config)

try:
    result = await scraper.scrape("https://very-slow-site.com")
except TimeoutError as e:
    print(f"Request timed out after {e.timeout} seconds")
```

## Parsing Exceptions

### ParsingError

::: scrap_e.core.exceptions.ParsingError

**Use Cases:**

- Invalid HTML structure
- Missing required elements
- XPath/CSS selector failures
- Data transformation errors

**Example:**

```python
from scrap_e.core.exceptions import ParsingError
from scrap_e.core.models import ExtractionRule

scraper = HttpScraper()
scraper.extraction_rules = [
    ExtractionRule(
        name="required_title",
        selector="h1.main-title",
        required=True
    )
]

try:
    result = await scraper.scrape("https://site-without-title.com")
except ParsingError as e:
    print(f"Failed to extract required data: {e}")
    print(f"Missing element: {e.details.get('selector')}")
```

## Authentication Exceptions

### AuthenticationError

::: scrap_e.core.exceptions.AuthenticationError

**Use Cases:**

- Invalid API keys
- Expired tokens
- Login failures
- Insufficient permissions

**Example:**

```python
from scrap_e.core.exceptions import AuthenticationError
from scrap_e.scrapers.api.rest_scraper import RestScraper

scraper = RestScraper()

try:
    result = await scraper.scrape(
        "https://api.example.com/protected",
        headers={"Authorization": "Bearer invalid-token"}
    )
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    print(f"Status code: {e.status_code}")
```

## Configuration Exceptions

### ConfigurationError

::: scrap_e.core.exceptions.ConfigurationError

**Use Cases:**

- Invalid configuration values
- Missing required settings
- Conflicting configuration options
- File permission issues

**Example:**

```python
from scrap_e.core.exceptions import ConfigurationError
from scrap_e.core.config import WebScraperConfig

try:
    config = WebScraperConfig(
        browser_type="invalid-browser",
        default_timeout=-1  # Invalid timeout
    )
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    print(f"Invalid field: {e.field}")
```

### ValidationError

::: scrap_e.core.exceptions.ValidationError

**Use Cases:**

- Invalid URLs
- Malformed data
- Schema validation failures
- Parameter validation errors

**Example:**

```python
from scrap_e.core.exceptions import ValidationError
from scrap_e.core.models import ExtractionRule

try:
    rule = ExtractionRule(
        name="",  # Empty name not allowed
        selector="h1"
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Invalid value: {e.value}")
```

## Rate Limiting Exceptions

### RateLimitError

::: scrap_e.core.exceptions.RateLimitError

**Use Cases:**

- API rate limit exceeded
- Server throttling responses
- Too many requests errors
- Temporary bans

**Example:**

```python
from scrap_e.core.exceptions import RateLimitError
import asyncio

scraper = HttpScraper()

try:
    result = await scraper.scrape("https://api.example.com/data")
except RateLimitError as e:
    print(f"Rate limited: {e}")
    print(f"Retry after: {e.retry_after} seconds")

    # Wait and retry
    await asyncio.sleep(e.retry_after)
    result = await scraper.scrape("https://api.example.com/data")
```

## Exception Attributes

All Scrap-E exceptions inherit common attributes from `ScraperError`:

### Common Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Human-readable error message |
| `details` | `dict[str, Any]` | Additional error context |
| `error_code` | `str \| None` | Machine-readable error code |
| `timestamp` | `datetime` | When the error occurred |
| `source` | `str \| None` | Source URL or identifier |

### Specific Attributes

#### TimeoutError

- `timeout: float` - The timeout value that was exceeded

#### ConnectionError

- `status_code: int | None` - HTTP status code if available
- `response_headers: dict` - Response headers if available

#### ParsingError

- `selector: str | None` - The CSS selector or XPath that failed
- `element_count: int` - Number of elements found (when expecting different count)

#### AuthenticationError

- `status_code: int` - HTTP authentication error status code
- `auth_method: str` - Authentication method that failed

#### RateLimitError

- `retry_after: int | None` - Seconds to wait before retrying
- `limit: int | None` - Rate limit that was exceeded
- `remaining: int | None` - Remaining requests in current window

## Error Context

All exceptions include contextual information to help with debugging:

```python
try:
    result = await scraper.scrape(url)
except ScraperError as e:
    print(f"Error: {e.message}")
    print(f"Time: {e.timestamp}")
    print(f"Source: {e.source}")
    print(f"Details: {e.details}")

    # Log structured error data
    logger.error(
        "Scraping failed",
        error_type=type(e).__name__,
        error_code=e.error_code,
        source=e.source,
        details=e.details
    )
```

## Custom Exception Handling

### Creating Custom Error Handlers

```python
from scrap_e.core.exceptions import ScraperError
from typing import Type, Callable
import logging

class ErrorHandler:
    def __init__(self):
        self.handlers: dict[Type[Exception], Callable] = {}
        self.logger = logging.getLogger(__name__)

    def register(self, exception_type: Type[Exception], handler: Callable):
        """Register a custom handler for an exception type."""
        self.handlers[exception_type] = handler

    async def handle(self, exception: Exception, context: dict = None):
        """Handle an exception using registered handlers."""
        exception_type = type(exception)

        if exception_type in self.handlers:
            return await self.handlers[exception_type](exception, context)

        # Default handling
        self.logger.error(f"Unhandled exception: {exception}")
        raise exception

# Usage
error_handler = ErrorHandler()

# Register custom handlers
error_handler.register(
    ConnectionError,
    lambda e, ctx: print(f"Network issue detected: {e}")
)

error_handler.register(
    RateLimitError,
    lambda e, ctx: asyncio.sleep(e.retry_after or 60)
)

# Use in scraping
try:
    result = await scraper.scrape(url)
except ScraperError as e:
    await error_handler.handle(e, {"url": url, "scraper": scraper})
```

### Exception Aggregation

For batch operations, collect and analyze multiple exceptions:

```python
from collections import defaultdict
from dataclasses import dataclass
from typing import List

@dataclass
class ErrorSummary:
    total_errors: int
    error_types: dict[str, int]
    most_common_error: str
    sample_errors: List[ScraperError]

def analyze_errors(exceptions: List[ScraperError]) -> ErrorSummary:
    """Analyze a collection of scraping errors."""
    error_counts = defaultdict(int)

    for exc in exceptions:
        error_type = type(exc).__name__
        error_counts[error_type] += 1

    most_common = max(error_counts.items(), key=lambda x: x[1])[0]

    return ErrorSummary(
        total_errors=len(exceptions),
        error_types=dict(error_counts),
        most_common_error=most_common,
        sample_errors=exceptions[:5]  # First 5 for debugging
    )

# Usage in batch operations
errors = []

for url in urls:
    try:
        result = await scraper.scrape(url)
    except ScraperError as e:
        errors.append(e)

if errors:
    summary = analyze_errors(errors)
    print(f"Total errors: {summary.total_errors}")
    print(f"Most common: {summary.most_common_error}")
    print("Error breakdown:", summary.error_types)
```

## Testing Exception Handling

### Unit Tests for Error Scenarios

```python
import pytest
from scrap_e.core.exceptions import ConnectionError, TimeoutError
from scrap_e.scrapers.web.http_scraper import HttpScraper

@pytest.mark.asyncio
async def test_connection_error_handling():
    scraper = HttpScraper()

    with pytest.raises(ConnectionError) as exc_info:
        await scraper.scrape("https://invalid-domain.invalid")

    assert "connection failed" in str(exc_info.value).lower()
    assert exc_info.value.details is not None

@pytest.mark.asyncio  
async def test_timeout_error_handling():
    config = WebScraperConfig(default_timeout=0.001)  # Very short timeout
    scraper = HttpScraper(config)

    with pytest.raises(TimeoutError) as exc_info:
        await scraper.scrape("https://httpbin.org/delay/5")

    assert exc_info.value.timeout == 0.001
```

### Mock Error Responses

```python
from unittest.mock import AsyncMock, patch
import httpx

@pytest.mark.asyncio
async def test_http_error_handling():
    scraper = HttpScraper()

    # Mock a 500 server error
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = httpx.HTTPStatusError(
            "Server Error",
            request=AsyncMock(),
            response=AsyncMock(status_code=500)
        )

        result = await scraper.scrape("https://example.com")
        assert not result.success
        assert "500" in result.error
```

## Best Practices

1. **Always catch specific exceptions first**, then fall back to general ones:

   ```python
   try:
       result = await scraper.scrape(url)
   except ConnectionError:
       # Handle network issues
       pass
   except TimeoutError:
       # Handle timeouts
       pass
   except ScraperError:
       # Handle other scraper errors
       pass
   ```

2. **Include context in error handling**:

   ```python
   try:
       result = await scraper.scrape(url)
   except ScraperError as e:
       logger.error(
           "Scraping failed",
           url=url,
           error=str(e),
           user_id=user_id,
           scraper_type=scraper.scraper_type.value
       )
   ```

3. **Use structured logging for error analysis**:

   ```python
   logger.error(
       "scrape_error",
       error_type=type(e).__name__,
       error_code=getattr(e, 'error_code', None),
       url=url,
       details=getattr(e, 'details', {})
   )
   ```

4. **Implement retry logic for transient errors**:

   ```python
   from tenacity import retry, stop_after_attempt, retry_if_exception_type

   @retry(
       stop=stop_after_attempt(3),
       retry=retry_if_exception_type((ConnectionError, TimeoutError))
   )
   async def scrape_with_retry(url: str):
       return await scraper.scrape(url)
   ```

For more practical examples of error handling, see the [Error Handling Guide](../../user-guide/error-handling.md).
