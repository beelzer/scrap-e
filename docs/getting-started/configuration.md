# Configuration

Comprehensive configuration guide for customizing Scrap-E behavior.

## Configuration Methods

Scrap-E supports multiple configuration methods in order of precedence:

1. **Direct instantiation** (highest priority)
2. **Environment variables**  
3. **Configuration files** (.env, YAML, JSON)
4. **Default values** (lowest priority)

## Configuration Classes

### Base Configuration

The `ScraperConfig` class provides settings for all scrapers:

```python
from scrap_e.core.config import ScraperConfig

config = ScraperConfig(
    debug=True,
    log_level="DEBUG",
    default_timeout=30.0,
    concurrent_requests=10,
    user_agent="My Custom Bot 1.0"
)
```

### Web Scraper Configuration

For web scraping, use `WebScraperConfig` with additional web-specific settings:

```python
from scrap_e.core.config import WebScraperConfig

config = WebScraperConfig(
    # Base settings
    debug=False,
    default_timeout=30.0,

    # Web-specific settings
    browser_headless=True,
    enable_javascript=True,
    capture_screenshots=False,
    extract_links=True,
    extract_images=True,
    extract_metadata=True
)
```

## Core Configuration Options

### General Settings

```python
config = ScraperConfig(
    # Application settings
    name="my-scraper",
    debug=False,
    log_level="INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # Output settings
    output_dir="./data",
    temp_dir="./temp",
    output_format="JSON",  # JSON, CSV, PARQUET, EXCEL
    pretty_print=True,
    compress_output=False,

    # Performance settings
    max_workers=10,
    concurrent_requests=5,
    batch_size=100,
    memory_limit_mb=512
)
```

### Network Settings

```python
config = ScraperConfig(
    # HTTP settings
    default_timeout=30.0,
    verify_ssl=True,
    follow_redirects=True,
    max_redirects=10,

    # User agent
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",

    # Rate limiting
    rate_limit=RateLimitConfig(
        enabled=True,
        requests_per_second=10.0,
        burst_size=20
    ),

    # Retry configuration
    retry=RetryConfig(
        enabled=True,
        max_attempts=3,
        initial_delay=1.0,
        max_delay=60.0,
        exponential_base=2.0
    )
)
```

### Browser Configuration

```python
config = WebScraperConfig(
    # Browser type and mode
    browser_type="chromium",  # chromium, firefox, webkit
    browser_headless=True,

    # Viewport and rendering
    browser_viewport_width=1920,
    browser_viewport_height=1080,
    browser_wait_until="networkidle",  # load, domcontentloaded, networkidle

    # Screenshots and PDFs
    capture_screenshots=True,
    screenshot_format="png",  # png, jpeg
    screenshot_quality=85,

    # JavaScript and interactions
    enable_javascript=True,
    wait_for_timeout=10.0,
    browser_timeout=30.0,

    # Error handling
    browser_screenshot_on_error=True
)
```

## Environment Variables

Configure Scrap-E using environment variables with the `SCRAPER_` prefix:

### Core Settings
```bash
# Application
export SCRAPER_DEBUG=true
export SCRAPER_LOG_LEVEL=DEBUG
export SCRAPER_OUTPUT_DIR=/path/to/output
export SCRAPER_TEMP_DIR=/path/to/temp

# Performance
export SCRAPER_MAX_WORKERS=20
export SCRAPER_CONCURRENT_REQUESTS=10
export SCRAPER_BATCH_SIZE=100
```

### Network Settings
```bash
# HTTP
export SCRAPER_DEFAULT_TIMEOUT=45
export SCRAPER_USER_AGENT="My Custom Scraper 1.0"
export SCRAPER_VERIFY_SSL=true
export SCRAPER_FOLLOW_REDIRECTS=true

# Rate limiting
export SCRAPER_RATE_LIMIT__ENABLED=true
export SCRAPER_RATE_LIMIT__REQUESTS_PER_SECOND=5.0
```

### Browser Settings
```bash
# Browser configuration
export SCRAPER_BROWSER_TYPE=firefox
export SCRAPER_BROWSER_HEADLESS=false
export SCRAPER_BROWSER_VIEWPORT_WIDTH=1366
export SCRAPER_BROWSER_VIEWPORT_HEIGHT=768

# Screenshots
export SCRAPER_CAPTURE_SCREENSHOTS=true
export SCRAPER_SCREENSHOT_FORMAT=jpeg
export SCRAPER_SCREENSHOT_QUALITY=90
```

### Database Settings
```bash
# PostgreSQL
export SCRAPER_POSTGRES_URL=postgresql://user:pass@localhost:5432/db

# MongoDB
export SCRAPER_MONGODB_URL=mongodb://localhost:27017/scraper

# Redis
export SCRAPER_REDIS_URL=redis://localhost:6379/0
export SCRAPER_REDIS_PASSWORD=secret
```

## Configuration Files

### YAML Configuration

Create a `config.yaml` file:

```yaml
# config.yaml
debug: false
log_level: INFO
output_dir: ./data
default_timeout: 30.0

# Rate limiting
rate_limit:
  enabled: true
  requests_per_second: 10.0
  burst_size: 20

# Retry settings
retry:
  enabled: true
  max_attempts: 3
  initial_delay: 1.0

# Browser settings
browser_headless: true
browser_type: chromium
capture_screenshots: false

# Cache settings
cache:
  enabled: true
  ttl_seconds: 3600
  max_size_mb: 100
```

Load the configuration:

```python
from scrap_e.core.config import ScraperConfig

config = ScraperConfig.from_file("config.yaml")
```

### JSON Configuration

```json
{
  "debug": false,
  "log_level": "INFO",
  "output_dir": "./data",
  "default_timeout": 30.0,
  "rate_limit": {
    "enabled": true,
    "requests_per_second": 10.0,
    "burst_size": 20
  },
  "browser_headless": true,
  "capture_screenshots": false
}
```

### .env File

Create a `.env` file in your project root:

```bash
# .env
SCRAPER_DEBUG=false
SCRAPER_LOG_LEVEL=INFO
SCRAPER_OUTPUT_DIR=./data
SCRAPER_DEFAULT_TIMEOUT=30.0
SCRAPER_BROWSER_HEADLESS=true
SCRAPER_RATE_LIMIT__ENABLED=true
SCRAPER_RATE_LIMIT__REQUESTS_PER_SECOND=10.0
```

## Advanced Configuration

### Pagination Settings

```python
from scrap_e.core.models import PaginationConfig

config = WebScraperConfig(
    pagination=PaginationConfig(
        enabled=True,
        max_pages=50,
        page_param="page",
        page_size=20,
        next_page_selector="a.next-page",
        stop_condition="No more results"
    )
)
```

### Proxy Configuration

```python
from scrap_e.core.models import ProxyConfig

config = ScraperConfig(
    proxy=ProxyConfig(
        enabled=True,
        proxy_list=[
            "http://proxy1:8080",
            "http://proxy2:8080"
        ],
        rotation_enabled=True,
        authentication={"username": "user", "password": "pass"}
    )
)
```

### Cache Configuration

```python
from scrap_e.core.models import CacheConfig

config = ScraperConfig(
    cache=CacheConfig(
        enabled=True,
        backend="redis",  # memory, redis, file
        ttl_seconds=7200,
        max_size_mb=500,
        cache_key_prefix="scraper"
    )
)
```

## Specialized Configurations

### API Scraper Configuration

```python
from scrap_e.core.config import APIScraperConfig

config = APIScraperConfig(
    # Base settings
    default_timeout=30.0,

    # API-specific
    api_base_url="https://api.example.com",
    api_auth_type="bearer",
    api_key="your-api-key",
    default_content_type="application/json",

    # GraphQL
    graphql_endpoint="/graphql",

    # WebSocket
    ws_ping_interval=30.0,
    ws_pong_timeout=10.0
)
```

### Database Scraper Configuration

```python
from scrap_e.core.config import DatabaseScraperConfig

config = DatabaseScraperConfig(
    # Connection settings
    database_connection_timeout=10.0,
    database_query_timeout=300.0,
    database_pool_size=5,

    # Query settings
    fetch_size=1000,
    stream_results=True,
    use_server_side_cursors=True,

    # SQL specific
    sql_echo=False,  # Log all SQL queries
    sql_isolation_level="READ_COMMITTED"
)
```

## Performance Tuning

### High-Performance Configuration

```python
config = WebScraperConfig(
    # Concurrent processing
    concurrent_requests=20,
    max_workers=16,
    batch_size=200,

    # Connection optimization  
    default_timeout=15.0,

    # Caching
    cache=CacheConfig(
        enabled=True,
        backend="redis",
        ttl_seconds=3600,
        max_size_mb=1000
    ),

    # Rate limiting (be respectful)
    rate_limit=RateLimitConfig(
        enabled=True,
        requests_per_second=50.0,
        burst_size=100
    ),

    # Memory management
    memory_limit_mb=2048
)
```

### Low-Resource Configuration

```python
config = WebScraperConfig(
    # Conservative settings
    concurrent_requests=2,
    max_workers=2,
    batch_size=10,

    # Longer timeouts for stability
    default_timeout=60.0,

    # Minimal caching
    cache=CacheConfig(
        enabled=True,
        backend="memory",
        ttl_seconds=300,
        max_size_mb=50
    ),

    # Conservative rate limiting
    rate_limit=RateLimitConfig(
        enabled=True,
        requests_per_second=1.0
    ),

    memory_limit_mb=128
)
```

## Configuration Validation

Scrap-E validates configuration automatically:

```python
try:
    config = ScraperConfig(
        log_level="INVALID",  # Will raise ValidationError
        default_timeout=-5    # Will raise ValidationError
    )
except ValidationError as e:
    print(f"Configuration error: {e}")
```

## Configuration Examples

### Production Web Scraping

```python
config = WebScraperConfig(
    debug=False,
    log_level="WARNING",
    output_dir="/var/log/scraper",

    # Robust settings
    default_timeout=45.0,
    concurrent_requests=10,

    # Browser settings
    browser_headless=True,
    browser_screenshot_on_error=True,

    # Error handling
    retry=RetryConfig(
        enabled=True,
        max_attempts=5,
        initial_delay=2.0,
        exponential_base=2.0
    ),

    # Caching for performance
    cache=CacheConfig(
        enabled=True,
        backend="redis",
        ttl_seconds=7200
    )
)
```

### Development and Testing

```python
config = WebScraperConfig(
    debug=True,
    log_level="DEBUG",

    # Fast settings for development
    default_timeout=10.0,
    concurrent_requests=2,

    # Browser settings
    browser_headless=False,  # See browser for debugging
    capture_screenshots=True,

    # Minimal caching
    cache=CacheConfig(enabled=False),

    # No rate limiting for testing
    rate_limit=RateLimitConfig(enabled=False)
)
```

## Best Practices

1. **Use environment variables** for sensitive data (API keys, passwords)
2. **Start with conservative settings** and increase concurrency gradually
3. **Enable caching** for repeated scraping of the same sources
4. **Set appropriate timeouts** based on target site performance
5. **Respect rate limits** to avoid being blocked
6. **Use configuration files** for complex setups
7. **Validate configuration** in development to catch errors early

## Next Steps

- Learn about [extraction rules](../user-guide/extraction-rules.md)
- Explore [web scraping techniques](../user-guide/web-scraping.md)
- Check out [API scraping](../user-guide/api-scraping.md) patterns
- Review [performance optimization](../user-guide/performance.md) tips
