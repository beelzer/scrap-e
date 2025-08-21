"""Basic usage examples for Scrap-E."""

import asyncio

from scrap_e.core.models import ExtractionRule
from scrap_e.scrapers.web.browser_scraper import BrowserScraper
from scrap_e.scrapers.web.http_scraper import HttpScraper


async def example_http_scraping():
    """Example of basic HTTP scraping."""
    print("=== HTTP Scraping Example ===")

    # Create scraper instance
    scraper = HttpScraper()

    # Add extraction rules
    scraper.add_extraction_rule(
        ExtractionRule(
            name="title",
            selector="h1",
            required=False,
        )
    )

    scraper.add_extraction_rule(
        ExtractionRule(
            name="paragraphs",
            selector="p",
            multiple=True,
            required=False,
        )
    )

    # Scrape a website
    result = await scraper.scrape("https://example.com")

    if result.success:
        print(f"Status: {result.data.status_code}")
        print(f"URL: {result.data.url}")
        if result.data.extracted_data:
            print(f"Title: {result.data.extracted_data.get('title')}")
            paragraphs = result.data.extracted_data.get("paragraphs", [])
            print(f"Found {len(paragraphs)} paragraphs")
    else:
        print(f"Error: {result.error}")


async def example_browser_scraping():
    """Example of browser-based scraping for JavaScript sites."""
    print("\n=== Browser Scraping Example ===")

    # Create browser scraper
    scraper = BrowserScraper()
    scraper.config.browser_headless = True

    # Scrape with browser
    result = await scraper.scrape("https://example.com", wait_for_selector="h1", screenshot=True)

    if result.success:
        print(f"Title: {result.data.title}")
        print(f"URL: {result.data.url}")
        if result.data.screenshot:
            print(f"Screenshot captured: {len(result.data.screenshot)} bytes")
    else:
        print(f"Error: {result.error}")


async def example_multiple_urls():
    """Example of scraping multiple URLs concurrently."""
    print("\n=== Multiple URLs Example ===")

    scraper = HttpScraper()

    urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://httpbin.org/json",
    ]

    # Scrape multiple URLs with max 2 concurrent requests
    results = await scraper.scrape_multiple(urls, max_concurrent=2)

    for i, result in enumerate(results):
        if result.success:
            print(f"URL {i + 1}: SUCCESS - Status {result.data.status_code}")
        else:
            print(f"URL {i + 1}: FAILED - {result.error}")


async def example_with_extraction():
    """Example with custom extraction rules."""
    print("\n=== Custom Extraction Example ===")

    scraper = HttpScraper()

    # Scrape with inline extraction rules
    result = await scraper.scrape(
        "https://httpbin.org/html",
        extraction_rules=[
            ExtractionRule(
                name="title",
                selector="h1",
                required=False,
            ),
            ExtractionRule(
                name="author",
                selector="span.author",
                default="Unknown",
                required=False,
            ),
            ExtractionRule(
                name="links",
                selector="a",
                attribute="href",
                multiple=True,
                required=False,
            ),
        ],
    )

    if result.success and result.data.extracted_data:
        print("Extracted data:")
        for key, value in result.data.extracted_data.items():
            if isinstance(value, list):
                print(f"  {key}: {len(value)} items")
            else:
                print(f"  {key}: {value}")


async def main():
    """Run all examples."""
    await example_http_scraping()
    await example_browser_scraping()
    await example_multiple_urls()
    await example_with_extraction()

    print("\n=== Examples Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
