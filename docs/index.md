# Scrap-E Documentation

Welcome to **Scrap-E**, a universal data scraper for Web, APIs, databases, and files.

## Overview

Scrap-E is a powerful and flexible Python library designed to simplify data extraction from various sources. Built with modern Python (3.13+) and async/await patterns, Scrap-E provides a unified interface for scraping websites, consuming APIs, querying databases, and processing files.

## Key Features

- **🌐 Web Scraping**: HTTP-based scraping with `HttpScraper` and JavaScript-heavy sites with `BrowserScraper` (Playwright)
- **🔌 API Integration**: REST, GraphQL, and WebSocket API support with built-in authentication
- **🗄️ Database Connectivity**: SQL (PostgreSQL, MySQL, SQLite) and NoSQL (MongoDB, Redis) database extraction
- **📁 File Processing**: CSV, JSON, XML, PDF, Excel, and other file format parsing
- **⚡ High Performance**: Async/await architecture with concurrent request handling and connection pooling
- **🔧 Extensible Architecture**: Modular design with pluggable scrapers and configurable pipelines
- **🛡️ Production Ready**: Comprehensive error handling, retry mechanisms, rate limiting, and caching
- **📊 Data Validation**: Pydantic models for type safety and data validation
- **🖥️ CLI Interface**: Command-line tool for quick scraping and batch operations
- **📈 Monitoring**: Built-in statistics, logging, and performance metrics

## Architecture

Scrap-E is built around several core concepts:

- **Base Scrapers**: Abstract foundation supporting different data sources
- **Specialized Scrapers**: HTTP, Browser, API, Database, and File scrapers
- **Configuration System**: Flexible settings with environment variable support
- **Result Models**: Structured data containers with metadata and error handling
- **Extraction Rules**: Declarative data extraction using selectors, XPath, and JSONPath

## Quick Examples

### HTTP Web Scraping

```python
import asyncio
from scrap_e.scrapers.web.http_scraper import HttpScraper
from scrap_e.core.models import ExtractionRule

async def scrape_web():
    scraper = HttpScraper()

    # Add extraction rules
    scraper.extraction_rules = [
        ExtractionRule(
            name="title",
            selector="h1",
            required=True
        ),
        ExtractionRule(
            name="articles",
            selector="article",
            multiple=True
        )
    ]

    # Scrape with session management
    async with scraper.session() as s:
        result = await s.scrape("https://example.com")
        if result.success and result.data.extracted_data:
            print(f"Title: {result.data.extracted_data['title']}")
            print(f"Found {len(result.data.extracted_data['articles'])} articles")

asyncio.run(scrape_web())
```

### Browser Automation

```python
from scrap_e.scrapers.web.browser_scraper import BrowserScraper

async def scrape_spa():
    scraper = BrowserScraper()

    result = await scraper.scrape(
        "https://spa-example.com",
        wait_for_selector=".dynamic-content",
        capture_screenshot=True
    )

    if result.success:
        print(f"Page title: {result.data.title}")
        if result.data.screenshot:
            with open("screenshot.png", "wb") as f:
                f.write(result.data.screenshot)

    await scraper._cleanup()

asyncio.run(scrape_spa())
```

### CLI Usage

```bash
# Simple scraping
scrap-e scrape https://example.com --selector "h1" --selector ".content"

# Batch scraping
scrap-e batch https://site1.com https://site2.com --concurrent 10

# Sitemap extraction and scraping
scrap-e sitemap https://example.com/sitemap.xml --scrape

# System check
scrap-e doctor
```

## Installation

### From PyPI (when released)

```bash
pip install scrap-e
```

### From Source (Development)

```bash
git clone https://github.com/beelzer/scrap-e.git
cd scrap-e
uv sync --dev
```

### Post-Installation Setup

After installation, run these commands to complete setup:

```bash
# Install pre-commit hooks (development)
pre-commit install

# Install Playwright browsers (for browser scraping)
playwright install

# Verify installation
scrap-e doctor
```

## Documentation Structure

- **[Getting Started](getting-started/installation.md)**: Installation, configuration, and your first scraper
- **[User Guide](user-guide/web-scraping.md)**: Detailed guides for different scraping scenarios
- **[API Reference](api/core/base-scraper.md)**: Complete API documentation
- **[Contributing](contributing.md)**: How to contribute to the project

## Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/beelzer/scrap-e/issues)
- **Documentation**: You're reading it!
- **Examples**: Check the [examples directory](https://github.com/beelzer/scrap-e/tree/master/examples) in the repository

## License

Scrap-E is released under the MIT License. See the [LICENSE](https://github.com/beelzer/scrap-e/blob/master/LICENSE) file for details.
