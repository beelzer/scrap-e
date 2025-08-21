"""Quick test of the scraper functionality."""

import asyncio

from scrap_e.core.models import ExtractionRule
from scrap_e.scrapers.web.http_scraper import HttpScraper


async def test_example_com():
    """Test scraping example.com."""
    print("Testing Scrap-E with example.com...")

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

    scraper.add_extraction_rule(
        ExtractionRule(
            name="links",
            selector="a",
            attribute="href",
            multiple=True,
            required=False,
        )
    )

    # Scrape the website
    result = await scraper.scrape("https://example.com")

    if result.success:
        print(f"\nSuccess! Scraped: {result.data.url}")
        print(f"Status Code: {result.data.status_code}")
        print(f"Duration: {result.metadata.duration_seconds:.2f}s")

        if result.data.extracted_data:
            print("\nExtracted Data:")
            for key, value in result.data.extracted_data.items():
                if isinstance(value, list):
                    print(f"  {key}: {len(value)} items found")
                    if value and len(value) <= 3:
                        for item in value:
                            print(f"    - {item}")
                else:
                    print(f"  {key}: {value}")

        if result.data.metadata:
            print("\nPage Metadata:")
            print(f"  Title: {result.data.metadata.get('title')}")
            print(f"  Language: {result.data.metadata.get('language')}")
    else:
        print(f"Error: {result.error}")

    # Clean up
    await scraper._cleanup()


if __name__ == "__main__":
    print("=" * 50)
    print("Scrap-E Universal Scraper Test")
    print("=" * 50)
    asyncio.run(test_example_com())
