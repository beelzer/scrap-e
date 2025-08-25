# 🕷️ Scrap-E

<div align="center">

[![CI/CD Pipeline](https://github.com/beelzer/scrap-e/actions/workflows/ci.yml/badge.svg)](https://github.com/beelzer/scrap-e/actions/workflows/ci.yml)
[![Documentation](https://github.com/beelzer/scrap-e/actions/workflows/docs.yml/badge.svg)](https://github.com/beelzer/scrap-e/actions/workflows/docs.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

[![GitHub stars](https://img.shields.io/github/stars/beelzer/scrap-e?style=social)](https://github.com/beelzer/scrap-e/stargazers)

**A blazingly fast, universal data scraper for the modern web**

[Documentation](https://beelzer.github.io/scrap-e/) | [Issues](https://github.com/beelzer/scrap-e/issues) | [Discussions](https://github.com/beelzer/scrap-e/discussions)

</div>

---

## ✨ Features

Scrap-E is a powerful, modern data scraping framework that handles everything from simple web pages to complex APIs and databases. Built with Python 3.13+ and designed for speed, reliability, and ease of use.

### 🚀 Core Capabilities

- **🌐 Web Scraping**
  - HTTP/HTTPS with session management and retry logic
  - Browser automation with Playwright (Chrome, Firefox, WebKit)
  - JavaScript rendering and dynamic content handling
  - Automatic encoding detection and response parsing
  - Built-in rate limiting and politeness delays

- **🔌 API Integration**
  - REST API client with automatic retries
  - GraphQL query support
  - WebSocket connections for real-time data
  - OAuth 1.0/2.0 authentication flows
  - Automatic pagination handling

- **🗄️ Database Connectivity**
  - PostgreSQL, MySQL, SQLite support via SQLAlchemy
  - MongoDB integration for NoSQL operations
  - Redis for caching and queue management
  - Async database operations with asyncpg
  - Connection pooling and transaction management

- **📁 File Processing**
  - Excel, CSV, JSON, XML, YAML parsing
  - PDF text extraction and analysis
  - Word document processing
  - Image metadata extraction
  - Large file streaming support

### 🛡️ Advanced Features

- **Concurrent Processing**: Async/await support for massive parallelization
- **Smart Caching**: Disk-based caching with TTL support
- **Error Recovery**: Automatic retries with exponential backoff
- **Data Validation**: Pydantic models for type safety
- **Extensible Pipeline**: Plugin architecture for custom processors
- **Monitoring**: Built-in metrics and structured logging
- **Security**: Proxy support, custom headers, certificate validation

## 📦 Installation

### Using uv (recommended)

```bash
uv add scrap-e  # When available on PyPI
```

### Using pip

```bash
pip install scrap-e  # When available on PyPI
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/beelzer/scrap-e.git
cd scrap-e

# Install with development dependencies
uv sync --dev
# or
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Install Playwright browsers (for web scraping)
playwright install

# Verify setup
scrap-e doctor
```

### Post-Installation Setup

```bash
# For browser automation, install Playwright browsers
playwright install

# Verify your installation
scrap-e doctor
```

## 🚀 Quick Start

### Command Line Interface

```bash
# Basic web scraping
scrap-e scrape https://example.com -o output.json

# Browser-based scraping with JavaScript rendering
scrap-e scrape https://example.com --method browser --wait-for ".content"

# Extract specific data with CSS selectors
scrap-e scrape https://example.com -s ".article-title" -s ".article-body"

# Batch scraping multiple URLs
scrap-e batch url1.com url2.com url3.com --concurrent 5 -o results/

# Extract URLs from sitemap
scrap-e sitemap https://example.com/sitemap.xml --scrape
```

### Python API - Basic Web Scraping

```python
from scrap_e.scrapers.web.http_scraper import HttpScraper
from scrap_e.core.config import WebScraperConfig
from scrap_e.core.models import ExtractionRule
import asyncio

async def main():
    # Configure scraper
    config = WebScraperConfig(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        default_timeout=30.0,
        concurrent_requests=5
    )

    # Create HTTP scraper
    scraper = HttpScraper(config)

    # Add extraction rules
    scraper.extraction_rules = [
        ExtractionRule(
            name="title",
            selector="h1.title",
            required=True
        ),
        ExtractionRule(
            name="products",
            selector=".product-card",
            multiple=True
        )
    ]

    # Scrape data
    result = await scraper.scrape("https://example.com")
    if result.success and result.data.extracted_data:
        print(result.data.extracted_data)

# Run the scraper
asyncio.run(main())
```

### Browser Automation

```python
from scrap_e.scrapers.web.browser_scraper import BrowserScraper
from scrap_e.core.config import WebScraperConfig
import asyncio

async def browser_scrape():
    # Configure browser scraper
    config = WebScraperConfig(
        browser_headless=True,
        browser_type="chromium",
        browser_viewport_width=1920,
        browser_viewport_height=1080
    )

    # Create browser scraper
    scraper = BrowserScraper(config)

    # Scrape JavaScript-rendered content
    result = await scraper.scrape(
        "https://spa.example.com",
        wait_for_selector=".dynamic-content",
        capture_screenshot=True
    )

    if result.success:
        print(f"Page title: {result.data.title}")
        print(f"Content loaded: {len(result.data.content)} bytes")
        if result.data.screenshot:
            print(f"Screenshot captured: {len(result.data.screenshot)} bytes")

    # Clean up
    await scraper._cleanup()

asyncio.run(browser_scrape())
```

### Concurrent Scraping

```python
from scrap_e.scrapers.web.http_scraper import HttpScraper
import asyncio

async def scrape_multiple():
    # Scrape multiple URLs concurrently
    scraper = HttpScraper()
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3"
    ]

    # Use built-in concurrent scraping
    results = await scraper.scrape_multiple(urls, max_concurrent=3)

    for result in results:
        if result.success:
            print(f"{result.data.url}: {result.metadata.duration_seconds:.2f}s")
        else:
            print(f"Failed: {result.error}")

    # Clean up
    await scraper._cleanup()

asyncio.run(scrape_multiple())
```

## 🔧 Configuration

Scrap-E supports multiple configuration methods:

### Configuration File (YAML)

```yaml
# config.yaml
scraper:
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  timeout: 30
  retries: 3
  concurrent_requests: 10

browser:
  headless: true
  type: chromium
  viewport:
    width: 1920
    height: 1080

cache:
  enabled: true
  ttl: 3600
  directory: ".cache/scrap-e"
```

### Environment Variables

```bash
# .env file
SCRAPER_USER_AGENT="Custom User Agent"
SCRAPER_DEFAULT_TIMEOUT=60
SCRAPER_MAX_RETRIES=5
SCRAPER_CONCURRENT_REQUESTS=10
SCRAPER_BROWSER_HEADLESS=true
SCRAPER_CACHE_ENABLED=true
```

### Python Configuration

```python
from scrap_e.core.config import ScraperConfig, WebScraperConfig

# Base configuration
config = ScraperConfig(
    debug=True,
    user_agent="Custom UA",
    default_timeout=30,
    max_retries=3
)

# Web-specific configuration
web_config = WebScraperConfig(
    **config.model_dump(),
    concurrent_requests=10,
    rate_limit_calls=100,
    rate_limit_period=60,
    browser_type="chromium",
    browser_headless=True
)
```

## 📊 Advanced Usage

### Custom Extraction Rules

```python
from scrap_e.core.models import ExtractionRule
from scrap_e.scrapers.web.http_scraper import HttpScraper
import asyncio

async def extract_complex_data():
    # Define complex extraction rules
    rules = [
        ExtractionRule(
            name="price",
            selector=".price",
            default=0.0,
            required=False
        ),
        ExtractionRule(
            name="availability",
            xpath="//span[@class='stock']/@data-available",
            default="unknown"
        ),
        ExtractionRule(
            name="images",
            selector="img.product-image",
            attribute="src",
            multiple=True
        )
    ]

    scraper = HttpScraper()
    scraper.extraction_rules = rules

    result = await scraper.scrape("https://example.com/product")

    if result.success and result.data.extracted_data:
        data = result.data.extracted_data
        print(f"Price: {data.get('price')}")
        print(f"Available: {data.get('availability')}")
        print(f"Images: {len(data.get('images', []))}")

    await scraper._cleanup()

asyncio.run(extract_complex_data())
```

### Session Management

```python
from scrap_e.scrapers.web.http_scraper import HttpScraper
import asyncio

async def session_example():
    scraper = HttpScraper()

    # Use session context manager for automatic cleanup
    async with scraper.session() as session:
        # All requests in this block share the same session
        # Cookies and connection pooling are maintained

        result1 = await session.scrape("https://example.com/page1")
        result2 = await session.scrape("https://example.com/page2")
        result3 = await session.scrape("https://example.com/page3")

        print(f"Scraped {len([r for r in [result1, result2, result3] if r.success])} pages")

    # Session automatically cleaned up here

asyncio.run(session_example())
```

### Error Handling & Retries

```python
from scrap_e.core.config import WebScraperConfig
from scrap_e.core.exceptions import ScraperError, ConnectionError
from scrap_e.scrapers.web.http_scraper import HttpScraper
import asyncio

async def robust_scraping():
    config = WebScraperConfig(
        default_timeout=30.0,
        concurrent_requests=3
    )

    scraper = HttpScraper(config)

    try:
        # Scrape with built-in retry logic
        result = await scraper.scrape("https://example.com")

        if result.success:
            print(f"Success: {result.data.url}")
            print(f"Duration: {result.metadata.duration_seconds:.2f}s")
        else:
            print(f"Scraping failed: {result.error}")

    except ConnectionError as e:
        print(f"Connection failed: {e}")
    except ScraperError as e:
        print(f"Scraper error: {e}")
    finally:
        await scraper._cleanup()

asyncio.run(robust_scraping())
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scrap_e --cov-report=html

# Run specific test file
pytest tests/test_http_scraper.py

# Run with verbose output
pytest -v

# Run in parallel
pytest -n auto
```

## 📖 Documentation

Full documentation is available at [https://beelzer.github.io/scrap-e/](https://beelzer.github.io/scrap-e/)

### Building Documentation Locally

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/scrap-e.git
   cd scrap-e
   ```
3. Install development dependencies:
   ```bash
   uv sync --dev
   pre-commit install
   playwright install
   ```
4. Create a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
5. Make your changes and run tests:
   ```bash
   make test
   make lint
   make type-check
   ```
6. Commit your changes:
   ```bash
   git commit -m 'Add amazing feature'
   ```
7. Push to your fork and open a Pull Request

### Testing

We use pytest with parallel execution for fast test runs:

```bash
# Run all tests (parallel by default)
make test

# Run tests with maximum parallelization
make test-fast

# Run specific test suites
make test-unit        # Unit tests only
make test-integration # Integration tests
make test-performance # Performance benchmarks

# Run tests with coverage
make test-cov

# Watch tests (auto-rerun on changes)
make test-watch
```

**Performance Optimization**: Tests run in parallel using pytest-xdist, providing 2-4x speedup on multi-core systems. The configuration automatically uses all available CPU cores.

### Code Quality

We maintain high code quality standards:

- **Testing**: Comprehensive test suite with parallel execution
- **Type Safety**: Full type annotations with strict MyPy checking
- **Linting**: Ruff for fast, comprehensive linting and formatting
- **Security**: Bandit, Safety, pip-audit for vulnerability scanning
- **Documentation**: All public APIs documented with examples
- **Pre-commit**: Automated checks before every commit
- **CI/CD**: GitHub Actions for continuous integration

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Scrap-E is built with these excellent libraries:

- [httpx](https://github.com/encode/httpx) - Modern async HTTP client
- [Playwright](https://playwright.dev/) - Cross-browser automation
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML/XML parsing
- [selectolax](https://github.com/rushter/selectolax) - Fast HTML parsing
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation using Python type hints
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [structlog](https://www.structlog.org/) - Structured logging
- [Click](https://click.palletsprojects.com/) - Command line interface
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output

## 💬 Support

- 💬 [Discussions](https://github.com/beelzer/scrap-e/discussions) - Ask questions and share ideas
- 🐛 [Issue Tracker](https://github.com/beelzer/scrap-e/issues) - Report bugs and request features
- 📚 [Documentation](https://beelzer.github.io/scrap-e/) - Comprehensive guides and API reference

---

<div align="center">
Made with ❤️ by the Scrap-E Team
</div>
