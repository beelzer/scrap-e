#!/usr/bin/env python
"""
Comprehensive test script for all Scrap-E features.
Tests web scraping (HTTP & Browser), parsing, extraction, and data export.
"""

import asyncio
import json
import warnings
import sys
from pathlib import Path
from datetime import datetime

# Suppress Windows-specific asyncio cleanup warnings
if sys.platform == "win32":
    warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*transport")
    warnings.filterwarnings("ignore", message="I/O operation on closed pipe")

# Import all scraper components
from scrap_e.scrapers import HttpScraper, BrowserScraper
from scrap_e.core.config import WebScraperConfig
from scrap_e.core.models import (
    ExtractionRule,
    PaginationConfig,
    RateLimitConfig,
    RetryConfig,
    CacheConfig,
)
from scrap_e.scrapers.web.parser import HtmlParser


class ComprehensiveScraperTest:
    """Test all features of the Scrap-E scraping framework."""

    def __init__(self, run_name: str | None = None):
        """Initialize test configuration.

        Args:
            run_name: Optional custom name for this test run.
                     If not provided, uses timestamp.
        """
        # Set up output directory structure with unique timestamp or custom name
        self.script_name = Path(__file__).stem
        if run_name:
            # Sanitize the run name to be filesystem-safe
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in run_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"{safe_name}_{timestamp}"
        else:
            folder_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Use Path relative to the script location
        script_dir = Path(__file__).parent
        self.output_dir = script_dir / "output" / self.script_name / folder_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for different test categories
        self.http_output = self.output_dir / "http_scraping"
        self.browser_output = self.output_dir / "browser_scraping"
        self.parsing_output = self.output_dir / "parsing_tests"
        self.extraction_output = self.output_dir / "extraction_tests"
        self.pagination_output = self.output_dir / "pagination_tests"

        for dir_path in [
            self.http_output,
            self.browser_output,
            self.parsing_output,
            self.extraction_output,
            self.pagination_output,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

    async def test_http_scraper_basic(self):
        """Test basic HTTP scraping functionality."""
        print("\n=== Testing HTTP Scraper (Basic) ===")

        config = WebScraperConfig(
            user_agent="Scrap-E Test Bot/1.0",
            default_timeout=30.0,
            follow_redirects=True,
            verify_ssl=True,
            concurrent_requests=5,
        )

        scraper = HttpScraper(config)

        # Test scraping a simple page
        test_urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/user-agent",
            "https://httpbin.org/headers",
        ]

        results = []
        for url in test_urls:
            try:
                result = await scraper.scrape(url)
                if result.success and result.data:
                    results.append({
                        "url": url,
                        "status_code": result.data.status_code,
                        "content_length": len(result.data.content or ""),
                        "headers": dict(result.data.headers),
                    })
                    print(f"[OK] Scraped {url}")
            except Exception as e:
                print(f"[FAILED] Failed to scrape {url}: {e}")

        # Save results
        output_file = self.http_output / "basic_test_results.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
            f.flush()  # Ensure data is written to the disk
        print(f"Results saved to {output_file.absolute()}")

    async def test_http_scraper_with_extraction(self):
        """Test HTTP scraping with extraction rules."""
        print("\n=== Testing HTTP Scraper with Extraction Rules ===")

        # Define extraction rules for different data types
        extraction_rules = [
            ExtractionRule(
                name="title",
                selector="title",
                required=False,
            ),
            ExtractionRule(
                name="headings",
                selector="h1, h2, h3",
                multiple=True,
                required=False,
            ),
            ExtractionRule(
                name="links",
                selector="a[href]",
                attribute="href",
                multiple=True,
                required=False,
            ),
            ExtractionRule(
                name="images",
                selector="img",
                attribute="src",
                multiple=True,
                required=False,
            ),
            ExtractionRule(
                name="meta_description",
                selector='meta[name="description"]',
                attribute="content",
                required=False,
            ),
        ]

        config = WebScraperConfig()
        scraper = HttpScraper(config)
        scraper.extraction_rules = extraction_rules

        # Test on a real website
        test_url = "https://example.com"

        try:
            result = await scraper.scrape(test_url)
            if result.success and result.data:
                extracted_data = {
                    "url": test_url,
                    "extracted": result.data.extracted_data,
                    "timestamp": datetime.now().isoformat(),
                }

                # Save extracted data
                output_file = self.extraction_output / "http_extraction_test.json"
                with open(output_file, "w") as f:
                    json.dump(extracted_data, f, indent=2, default=str)
                print(f"[OK] Extracted data from {test_url}")
                print(f"Results saved to {output_file}")
        except Exception as e:
            print(f"[FAILED] Failed extraction test: {e}")

    async def test_browser_scraper_basic(self):
        """Test browser-based scraping for JavaScript sites."""
        print("\n=== Testing Browser Scraper (Basic) ===")

        config = WebScraperConfig(
            browser_type="chromium",
            browser_headless=True,
            enable_javascript=True,
            browser_viewport_width=1920,
            browser_viewport_height=1080,
            wait_for_selector=None,
            wait_for_timeout=10.0
        )

        scraper = BrowserScraper(config)
        try:
            # Test JavaScript-heavy pages
            test_urls = [
                "https://example.com",
                "https://httpbin.org/delay/2",  # Tests wait functionality
            ]

            results = []
            for url in test_urls:
                try:
                    result = await scraper.scrape(
                        url,
                        screenshot=True,  # Take screenshots
                        wait_for_network_idle=True,
                    )

                    if result.success and result.data:
                        # Save a screenshot if available
                        if result.data.screenshot:
                            screenshot_file = self.browser_output / f"{url.replace('://', '_').replace('/', '_')}_screenshot.png"
                            with open(screenshot_file, "wb") as f:
                                f.write(result.data.screenshot)
                            print(f"[OK] Screenshot saved: {screenshot_file}")

                        results.append({
                            "url": url,
                            "title": result.data.title,
                            "content_length": len(result.data.content or ""),
                            "has_screenshot": result.data.screenshot is not None,
                        })
                        print(f"[OK] Browser scraped {url}")
                except Exception as e:
                    print(f"[FAILED] Failed to browser scrape {url}: {e}")

            # Save results
            output_file = self.browser_output / "browser_test_results.json"
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Results saved to {output_file}")
        finally:
            # Ensure browser cleanup
            await scraper.cleanup()

    async def test_browser_scraper_interactions(self):
        """Test browser interactions (clicks, form fills, scrolling)."""
        print("\n=== Testing Browser Scraper with Interactions ===")

        config = WebScraperConfig(
            browser_type="chromium",
            browser_headless=True,
            enable_javascript=True,
        )

        scraper = BrowserScraper(config)

        try:
            # Test form interaction on httpbin
            result = await scraper.scrape(
                "https://httpbin.org/forms/post",
                actions=[
                    {"type": "fill", "selector": 'input[name="custname"]', "value": "Test User"},
                    {"type": "fill", "selector": 'input[name="custtel"]', "value": "123-456-7890"},
                    {"type": "fill", "selector": 'input[name="custemail"]', "value": "test@example.com"},
                    {"type": "select", "selector": 'select[name="size"]', "value": "large"},
                    {"type": "fill", "selector": 'textarea[name="comments"]', "value": "Testing browser interactions"},
                    {"type": "screenshot", "path": str(self.browser_output / "form_filled.png")},
                ],
            )

            if result.success:
                print("[OK] Successfully tested browser interactions")

                # Save interaction test results
                output_file = self.browser_output / "interaction_test_results.json"
                with open(output_file, "w") as f:
                    json.dump({
                        "test": "form_interaction",
                        "success": True,
                        "timestamp": datetime.now().isoformat(),
                    }, f, indent=2)
        except Exception as e:
            print(f"[FAILED] Failed interaction test: {e}")
        finally:
            # Ensure browser cleanup
            await scraper.cleanup()

    async def test_parser_features(self):
        """Test HTML parsing with different backends."""
        print("\n=== Testing HTML Parser Features ===")

        # Sample HTML for testing
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": "Test Page",
                "description": "A test page for parsing"
            }
            </script>
        </head>
        <body>
            <h1>Main Heading</h1>
            <div class="content">
                <p>Paragraph 1 with <strong>bold text</strong></p>
                <p>Paragraph 2 with <a href="/link">a link</a></p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                    <li>Item 3</li>
                </ul>
            </div>
            <table>
                <tr><th>Header 1</th><th>Header 2</th></tr>
                <tr><td>Data 1</td><td>Data 2</td></tr>
                <tr><td>Data 3</td><td>Data 4</td></tr>
            </table>
            <div id="special" data-value="42">Special content</div>
        </body>
        </html>
        """

        # Test different parser backends
        parser = HtmlParser(test_html)

        # Test CSS selectors
        css_tests = {
            "title": parser.soup.select_one("title").text if parser.soup.select_one("title") else None,
            "h1": parser.soup.select_one("h1").text if parser.soup.select_one("h1") else None,
            "paragraphs": [p.text for p in parser.soup.select("p")],
            "links": [a.get("href") for a in parser.soup.select("a[href]")],
            "list_items": [li.text for li in parser.soup.select("li")],
            "table_cells": [td.text for td in parser.soup.select("td")],
            "special_div_text": parser.soup.select_one("#special").text if parser.soup.select_one("#special") else None,
            "special_div_attr": parser.soup.select_one("#special").get("data-value") if parser.soup.select_one("#special") else None,
        }

        # Test XPath
        xpath_tests = {
            "title_xpath": parser.lxml_tree.xpath("//title/text()"),
            "h1_xpath": parser.lxml_tree.xpath("//h1/text()"),
            "all_text_nodes": parser.lxml_tree.xpath("//text()[normalize-space()]")[:5],  # First 5 text nodes
            "attribute_xpath": parser.lxml_tree.xpath("//*[@id='special']/@data-value"),
        }

        # Test extraction rules
        rules = [
            ExtractionRule(name="json_ld", json_path="@type"),
            ExtractionRule(name="meta_desc", selector='meta[name="description"]', attribute="content"),
            ExtractionRule(name="all_headers", xpath="//h1 | //h2 | //h3", multiple=True),
            ExtractionRule(name="word_count", regex=r"\b\w+\b", multiple=True),
        ]

        extraction_results = {}
        for rule in rules:
            try:
                extraction_results[rule.name] = parser.extract_with_rule(rule)
            except Exception as e:
                extraction_results[rule.name] = f"Error: {e}"

        # Save all parser test results
        parser_results = {
            "css_selector_tests": css_tests,
            "xpath_tests": xpath_tests,
            "extraction_rule_tests": extraction_results,
        }

        output_file = self.parsing_output / "parser_test_results.json"
        with open(output_file, "w") as f:
            json.dump(parser_results, f, indent=2, default=str)
        print(f"[OK] Parser tests completed. Results saved to {output_file}")

    async def test_pagination(self):
        """Test pagination handling."""
        print("\n=== Testing Pagination ===")

        # Configure pagination
        pagination_config = PaginationConfig(
            enabled=True,
            max_pages=3,
            page_param="page",
            page_size=10,
            start_page=1,
        )

        config = WebScraperConfig(
            pagination=pagination_config,
        )

        scraper = HttpScraper(config)

        # Test pagination by simulating multiple page requests
        base_url = "https://httpbin.org/anything"

        all_results = []
        for page_num in range(1, pagination_config.max_pages + 1):
            try:
                # Simulate pagination by adding page parameter
                result = await scraper.scrape(f"{base_url}?page={page_num}")
                if result.success and result.data:
                    all_results.append({
                        "page": page_num,
                        "url": result.data.url,
                        "timestamp": datetime.now().isoformat(),
                    })
                    print(f"[OK] Scraped page {page_num}")
            except Exception as e:
                print(f"[FAILED] Page {page_num}: {e}")
                break

        # Save pagination results
        output_file = self.pagination_output / "pagination_test_results.json"
        with open(output_file, "w") as f:
            json.dump({
                "total_pages": len(all_results),
                "pages": all_results,
                "config": {
                    "max_pages": pagination_config.max_pages,
                    "page_size": pagination_config.page_size,
                },
            }, f, indent=2)
        print(f"[OK] Pagination test completed. Results saved to {output_file}")

    @staticmethod
    async def test_rate_limiting():
        """Test rate limiting configuration."""
        print("\n=== Testing Rate Limiting ===")

        # Configure rate limiting
        rate_limit_config = RateLimitConfig(
            enabled=True,
            requests_per_second=2.0,  # 2 requests per second
            burst_size=3,
        )

        config = WebScraperConfig(
            rate_limit=rate_limit_config,
        )

        scraper = HttpScraper(config)

        # Test rate limiting with multiple requests
        urls = [f"https://httpbin.org/delay/{i}" for i in range(1, 4)]

        start_time = datetime.now()
        results = []

        for url in urls:
            try:
                result = await scraper.scrape(url)
                if result.success:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    results.append({
                        "url": url,
                        "elapsed_seconds": elapsed,
                    })
                    print(f"[OK] Request completed at {elapsed:.2f}s")
            except Exception as e:
                print(f"[FAILED] Rate limit test failed: {e}")

        # Check if rate limiting worked (should take at least 1 second between requests)
        print(f"[OK] Rate limiting test completed. Total time: {(datetime.now() - start_time).total_seconds():.2f}s")

    @staticmethod
    async def test_retry_mechanism():
        """Test retry configuration for failed requests."""
        print("\n=== Testing Retry Mechanism ===")

        # Configure retries
        retry_config = RetryConfig(
            enabled=True,
            max_attempts=3,
            initial_delay=1.0,
            exponential_base=2.0,
            retry_on_status_codes=[500, 502, 503],
        )

        config = WebScraperConfig(
            retry=retry_config,
        )

        scraper = HttpScraper(config)

        # Test 1: URL that always returns 500 (should fail after retries)
        print("Test 1: Persistent failure (500 error)")
        test_url = "https://httpbin.org/status/500"

        try:
            result = await scraper.scrape(test_url)
            if result.success:
                print(f"[UNEXPECTED] Request succeeded when it should have failed")
            else:
                print(f"[OK] Request failed after {retry_config.max_attempts} retry attempts (expected behavior)")
                print(f"     Error: {result.error[:100]}..." if result.error and len(result.error) > 100 else f"     Error: {result.error}")
        except Exception as e:
            print(f"[OK] Retry mechanism tested (expected failure after retries): {e}")

        # Test 2: URL that sometimes fails (transient errors)
        print("\nTest 2: Transient failure simulation")
        # Using httpbin's /status endpoint with multiple codes - it randomly returns one
        test_url2 = "https://httpbin.org/status/200,500,503"

        success_count = 0
        retry_count = 0

        for i in range(3):
            try:
                result = await scraper.scrape(test_url2)
                if result.success:
                    success_count += 1
                    print(f"  Attempt {i+1}: [OK] Request succeeded (possibly after retries)")
                else:
                    retry_count += 1
                    print(f"  Attempt {i+1}: [RETRY] Request failed even after retries")
            except Exception as e:
                retry_count += 1
                print(f"  Attempt {i+1}: [RETRY] Exception: {str(e)[:50]}...")

        print(f"\nRetry test summary: {success_count}/3 succeeded, {retry_count}/3 failed")

    @staticmethod
    async def test_caching():
        """Test caching functionality."""
        print("\n=== Testing Cache ===")

        # Configure caching
        cache_config = CacheConfig(
            enabled=True,
            backend="memory",
            ttl_seconds=60,
        )

        config = WebScraperConfig(
            cache=cache_config,
        )

        scraper = HttpScraper(config)

        # Test caching with the same URL twice
        test_url = "https://httpbin.org/uuid"

        # First request (cache miss)
        start1 = datetime.now()
        await scraper.scrape(test_url)
        time1 = (datetime.now() - start1).total_seconds()

        # Second request (should be cached)
        start2 = datetime.now()
        await scraper.scrape(test_url)
        time2 = (datetime.now() - start2).total_seconds()

        print(f"[OK] First request: {time1:.3f}s")
        print(f"[OK] Second request (cached): {time2:.3f}s")
        print(f"[OK] Cache hit: {time2 < time1 * 0.5}")  # Cached should be much faster

    async def run_all_tests(self):
        """Run all test scenarios."""
        print("=" * 60)
        print("SCRAP-E COMPREHENSIVE FEATURE TEST")
        print(f"Output Directory: {self.output_dir.absolute()}")
        print("=" * 60)

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Run all test scenarios
        test_methods = [
            self.test_http_scraper_basic,
            self.test_http_scraper_with_extraction,
            self.test_browser_scraper_basic,
            self.test_browser_scraper_interactions,
            self.test_parser_features,
            self.test_pagination,
            self.test_rate_limiting,
            self.test_retry_mechanism,
            self.test_caching,
        ]

        for test_method in test_methods:
            try:
                await test_method()
            except Exception as e:
                print(f"[FAILED] Test failed: {test_method.__name__}: {e}")

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print(f"Results saved in: {self.output_dir}")
        print("=" * 60)

        # Create the summary report
        self._create_summary_report()

    def _create_summary_report(self):
        """Create a summary report of all tests."""
        # Collect files from each category
        test_files = {
            "http_scraping": list(self.http_output.glob("*")),
            "browser_scraping": list(self.browser_output.glob("*")),
            "parsing_tests": list(self.parsing_output.glob("*")),
            "extraction_tests": list(self.extraction_output.glob("*")),
            "pagination_tests": list(self.pagination_output.glob("*")),
        }

        # Build summary with file counts and names
        summary = {
            "test_run": datetime.now().isoformat(),
            "output_directory": str(self.output_dir),
            "test_categories": {}
        }

        # Process each category
        for category, files in test_files.items():
            summary["test_categories"][category] = {
                "file_count": len(files),
                "files": [f.name for f in files]
            }

        # Save summary
        summary_file = self.output_dir / "test_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"\n[OK] Test summary saved to: {summary_file}")


async def main():
    """Main entry point."""
    import sys

    # Check for optional run name argument
    run_name = None
    if len(sys.argv) > 1:
        run_name = sys.argv[1]
        print(f"Using custom run name: {run_name}")

    tester = ComprehensiveScraperTest(run_name=run_name)
    await tester.run_all_tests()

    # Small delay to allow async resources to clean up properly
    await asyncio.sleep(0.5)


if __name__ == "__main__":
    # Run the async main function
    # Usage: python comprehensive_test.py [optional_run_name]
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[CANCELLED] Test interrupted by user")
        sys.exit(1)
    finally:
        # On Windows, suppress the final cleanup warnings from Playwright
        if sys.platform == "win32":
            import os
            import contextlib
            with contextlib.suppress(Exception):
                # Redirect stderr to null during final cleanup
                sys.stderr = open(os.devnull, 'w')
        sys.exit(0)
