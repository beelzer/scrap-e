# Quick Start

This guide will help you create your first scraper with Scrap-E.

## Basic Web Scraping

### HTTP Scraper Example

The simplest way to scrape a website is using the `HttpScraper`:

```python
import asyncio
from scrap_e.scrapers.web import HttpScraper

async def scrape_website():
    # Create scraper instance
    scraper = HttpScraper()

    # Scrape a webpage
    result = await scraper.scrape("https://example.com")

    if result.success:
        print(f"Status: {result.data.status_code}")
        print(f"Content length: {len(result.data.content)}")
        print(f"Title: {result.data.metadata.get('title')}")

    # Clean up resources
    await scraper.cleanup()

# Run the scraper
asyncio.run(scrape_website())
```

### Extracting Specific Data

Use extraction rules to target specific elements:

```python
from scrap_e.core.models import ExtractionRule

async def extract_data():
    scraper = HttpScraper()

    # Add extraction rules
    scraper.add_extraction_rule(
        ExtractionRule(
            name="headline",
            selector="h1.main-title",
            required=True
        )
    )

    scraper.add_extraction_rule(
        ExtractionRule(
            name="paragraphs",
            selector="p.content",
            multiple=True  # Extract all matching elements
        )
    )

    result = await scraper.scrape("https://example.com")

    if result.success:
        data = result.data.extracted_data
        print(f"Headline: {data.get('headline')}")
        print(f"Found {len(data.get('paragraphs', []))} paragraphs")

    await scraper.cleanup()

asyncio.run(extract_data())
```

## Browser-Based Scraping

For JavaScript-heavy sites, use the `BrowserScraper`:

```python
from scrap_e.scrapers.web import BrowserScraper

async def scrape_with_browser():
    scraper = BrowserScraper()

    # Wait for specific element to load
    result = await scraper.scrape(
        "https://example.com",
        wait_for="div.dynamic-content",
        screenshot=True  # Take a screenshot
    )

    if result.success:
        print(f"Page title: {result.data.metadata.get('title')}")
        if result.data.screenshot:
            print("Screenshot captured!")

    await scraper.cleanup()

asyncio.run(scrape_with_browser())
```

## Handling Multiple Pages

Scrape multiple pages concurrently:

```python
async def scrape_multiple():
    scraper = HttpScraper()

    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3"
    ]

    results = await scraper.scrape_multiple(urls)

    for result in results:
        if result.success:
            print(f"Scraped: {result.data.url}")
        else:
            print(f"Failed: {result.error}")

    await scraper.cleanup()

asyncio.run(scrape_multiple())
```

## Error Handling

Proper error handling ensures robust scraping:

```python
from scrap_e.core.exceptions import ScraperError, ConnectionError

async def safe_scraping():
    scraper = HttpScraper()

    try:
        result = await scraper.scrape("https://example.com")

        if result.success:
            process_data(result.data)
        else:
            print(f"Scraping failed: {result.error}")

    except ConnectionError as e:
        print(f"Connection error: {e}")
    except ScraperError as e:
        print(f"Scraper error: {e}")
    finally:
        await scraper.cleanup()

def process_data(data):
    # Process your scraped data here
    pass

asyncio.run(safe_scraping())
```

## Next Steps

- Learn about [Configuration](configuration.md) options
- Explore [Web Scraping](../user-guide/web-scraping.md) in depth
- Check out [API Scraping](../user-guide/api-scraping.md)
- See the [API Reference](../api/core/base-scraper.md) for detailed documentation
