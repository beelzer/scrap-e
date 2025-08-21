# Scrap-E Documentation

Welcome to **Scrap-E**, a universal data scraper for Web, APIs, databases, and files.

## Overview

Scrap-E is a powerful and flexible Python library designed to simplify data extraction from various sources. Whether you need to scrape websites, consume APIs, query databases, or process files, Scrap-E provides a unified interface and robust toolset to get the job done efficiently.

## Key Features

- **🌐 Web Scraping**: Support for both HTTP-based scraping and browser automation
- **🔌 API Integration**: Built-in support for REST, GraphQL, and WebSocket APIs
- **🗄️ Database Connectivity**: Connect and extract data from SQL and NoSQL databases
- **📁 File Processing**: Parse and extract data from various file formats (CSV, JSON, XML, PDF, etc.)
- **⚡ Async Support**: Built on async/await for high-performance concurrent operations
- **🔧 Extensible**: Easy to extend with custom scrapers and processors
- **🛡️ Robust Error Handling**: Comprehensive error handling and retry mechanisms
- **📊 Data Validation**: Built-in data validation using Pydantic models

## Quick Example

```python
from scrap_e.scrapers.web import HttpScraper
from scrap_e.core.models import ExtractionRule

# Create a scraper instance
scraper = HttpScraper()

# Define extraction rules
scraper.add_extraction_rule(
    ExtractionRule(
        name="title",
        selector="h1",
        required=True
    )
)

# Scrape data
async def main():
    result = await scraper.scrape("https://example.com")
    if result.success:
        print(result.data.extracted_data)

# Run the scraper
import asyncio
asyncio.run(main())
```

## Installation

Install Scrap-E using pip:

```bash
pip install scrap-e
```

Or with optional dependencies for specific features:

```bash
# For browser automation
pip install scrap-e[browser]

# For development
pip install scrap-e[dev]
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
