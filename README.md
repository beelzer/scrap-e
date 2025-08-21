# 🕷️ Scrap-E

<div align="center">

[![CI/CD Pipeline](https://github.com/beelzer/scrap-e/actions/workflows/ci.yml/badge.svg)](https://github.com/beelzer/scrap-e/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/beelzer/scrap-e/branch/main/graph/badge.svg?token=YOUR_TOKEN)](https://codecov.io/gh/beelzer/scrap-e)
[![Python Version](https://img.shields.io/pypi/pyversions/scrap-e)](https://pypi.org/project/scrap-e/)
[![PyPI - Version](https://img.shields.io/pypi/v/scrap-e)](https://pypi.org/project/scrap-e/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Documentation Status](https://readthedocs.org/projects/scrap-e/badge/?version=latest)](https://scrap-e.readthedocs.io/en/latest/?badge=latest)

[![Downloads](https://pepy.tech/badge/scrap-e)](https://pepy.tech/project/scrap-e)
[![Downloads/Month](https://pepy.tech/badge/scrap-e/month)](https://pepy.tech/project/scrap-e)
[![Downloads/Week](https://pepy.tech/badge/scrap-e/week)](https://pepy.tech/project/scrap-e)
[![GitHub stars](https://img.shields.io/github/stars/beelzer/scrap-e?style=social)](https://github.com/beelzer/scrap-e/stargazers)

**A blazingly fast, universal data scraper for the modern web**

[Documentation](https://beelzer.github.io/scrap-e/) | [PyPI](https://pypi.org/project/scrap-e/) | [Issues](https://github.com/beelzer/scrap-e/issues) | [Discussions](https://github.com/beelzer/scrap-e/discussions)

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

### Using pip

```bash
pip install scrap-e
```

### Using uv (recommended)

```bash
uv pip install scrap-e
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/beelzer/scrap-e.git
cd scrap-e

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Optional Dependencies

```bash
# For browser automation
pip install scrap-e[browser]

# For database support
pip install scrap-e[database]

# For API features
pip install scrap-e[api]

# Install everything
pip install scrap-e[all]
```

## 🚀 Quick Start

### Basic Web Scraping

```python
from scrap_e import Scraper

# Simple HTTP scraping
scraper = Scraper()
data = await scraper.get("https://example.com")
print(data.text)

# Extract structured data
products = await scraper.get(
    "https://shop.example.com/products",
    parser="css",
    extract={
        "products": {
            "selector": ".product-card",
            "multiple": True,
            "fields": {
                "name": ".product-name",
                "price": ".product-price",
                "image": {"selector": "img", "attr": "src"}
            }
        }
    }
)
```

### Browser Automation

```python
from scrap_e import BrowserScraper

# Scrape JavaScript-rendered content
async with BrowserScraper() as scraper:
    # Navigate and wait for content
    await scraper.goto("https://spa.example.com")
    await scraper.wait_for_selector(".dynamic-content")

    # Interact with the page
    await scraper.click("#load-more")
    await scraper.type("#search", "python")

    # Extract data
    results = await scraper.extract({
        "results": {
            "selector": ".search-result",
            "multiple": True
        }
    })
```

### API Integration

```python
from scrap_e import APIClient

# REST API
api = APIClient(base_url="https://api.example.com")
users = await api.get("/users", params={"page": 1})

# GraphQL
graphql = APIClient(base_url="https://graphql.example.com")
query = """
    query GetUser($id: ID!) {
        user(id: $id) {
            name
            email
        }
    }
"""
user = await graphql.post("/graphql", json={
    "query": query,
    "variables": {"id": "123"}
})
```

### Database Operations

```python
from scrap_e import DatabaseScraper

# SQL databases
async with DatabaseScraper("postgresql://user:pass@localhost/db") as db:
    results = await db.query("SELECT * FROM products WHERE price < :price", price=100)

# MongoDB
async with DatabaseScraper("mongodb://localhost:27017/shop") as db:
    products = await db.collection("products").find({"inStock": True}).to_list()
```

## 🔧 Configuration

Scrap-E uses environment variables and configuration files for settings:

```python
# config.py
from scrap_e import Config

config = Config(
    # Scraping settings
    user_agent="Mozilla/5.0 ...",
    timeout=30,
    retries=3,
    retry_delay=1,

    # Concurrency
    max_concurrent_requests=10,
    rate_limit=100,  # requests per minute

    # Caching
    cache_enabled=True,
    cache_ttl=3600,  # 1 hour

    # Logging
    log_level="INFO",
    log_format="json",
)
```

### Environment Variables

```bash
# .env file
SCRAPE_USER_AGENT="Custom User Agent"
SCRAPE_TIMEOUT=60
SCRAPE_RETRIES=5
SCRAPE_CACHE_DIR="/tmp/scrape_cache"
SCRAPE_LOG_LEVEL="DEBUG"
```

## 📊 Advanced Usage

### Custom Parsers

```python
from scrap_e import Parser, register_parser

@register_parser("custom")
class CustomParser(Parser):
    def parse(self, content: str) -> dict:
        # Your parsing logic here
        return parsed_data

# Use custom parser
scraper = Scraper()
data = await scraper.get("https://example.com", parser="custom")
```

### Pipeline Processing

```python
from scrap_e import Pipeline, Processor

class CleanProcessor(Processor):
    def process(self, item):
        # Clean and validate data
        return cleaned_item

class SaveProcessor(Processor):
    async def process(self, item):
        # Save to database
        await db.save(item)
        return item

# Create pipeline
pipeline = Pipeline([
    CleanProcessor(),
    SaveProcessor(),
])

# Process scraped data
async for item in scraper.scrape_many(urls):
    await pipeline.process(item)
```

### Distributed Scraping

```python
from scrap_e import DistributedScraper
from scrap_e.queue import RedisQueue

# Setup distributed scraping with Redis
queue = RedisQueue("redis://localhost:6379")
scraper = DistributedScraper(queue=queue, workers=10)

# Add URLs to queue
await scraper.add_urls(urls)

# Start distributed scraping
await scraper.run()
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
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`make test && make lint`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Quality

We maintain high code quality standards:

- **Testing**: Minimum 80% code coverage
- **Linting**: Ruff (linting, formatting & import sorting), MyPy
- **Security**: Bandit, Safety, pip-audit
- **Documentation**: All public APIs documented
- **Type Hints**: Full type annotations

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Scrap-E is built on the shoulders of giants:

- [httpx](https://github.com/encode/httpx) - Modern HTTP client
- [Playwright](https://playwright.dev/) - Browser automation
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database toolkit
- [structlog](https://www.structlog.org/) - Structured logging

## 💬 Support

- 📧 Email: support@scrap-e.dev
- 💬 [Discussions](https://github.com/beelzer/scrap-e/discussions)
- 🐛 [Issue Tracker](https://github.com/beelzer/scrap-e/issues)
- 📚 [Documentation](https://beelzer.github.io/scrap-e/)
- 🐦 Twitter: [@scrape_dev](https://twitter.com/scrape_dev)

## 🏆 Sponsors

Special thanks to our sponsors who make this project possible:

<!-- Add sponsor logos/links here -->

---

<div align="center">
Made with ❤️ by the Scrap-E Team
</div>
