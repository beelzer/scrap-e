"""Command-line interface for Scrap-E universal scraper."""

import asyncio
import csv
import json
import sys
from io import StringIO
from pathlib import Path
from typing import Any

import click
import structlog
from rich.console import Console
from rich.table import Table

from scrap_e import __version__
from scrap_e.core.config import ScraperConfig, WebScraperConfig
from scrap_e.core.models import ExtractionRule
from scrap_e.scrapers.web.browser_scraper import BrowserScraper
from scrap_e.scrapers.web.http_scraper import HttpScraper

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

console = Console()
logger = structlog.get_logger()


@click.group()
@click.version_option(version=__version__, prog_name="scrap-e")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Enable debug mode",
)
@click.pass_context
def cli(ctx: click.Context, config: str | None, debug: bool) -> None:
    """Scrap-E: Universal Data Scraper - Web, APIs, Databases, Files."""
    ctx.ensure_object(dict)

    # Load configuration
    if config:
        ctx.obj["config"] = ScraperConfig.from_file(config)
    else:
        ctx.obj["config"] = ScraperConfig(debug=debug)

    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            (structlog.dev.ConsoleRenderer() if debug else structlog.processors.JSONRenderer()),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


@cli.command()
@click.argument("url")
@click.option(
    "--method",
    "-m",
    type=click.Choice(["http", "browser"]),
    default="http",
    help="Scraping method to use",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "csv", "html"]),
    default="json",
    help="Output format",
)
@click.option(
    "--selector",
    "-s",
    multiple=True,
    help="CSS selector for data extraction (can be used multiple times)",
)
@click.option(
    "--xpath",
    "-x",
    multiple=True,
    help="XPath for data extraction (can be used multiple times)",
)
@click.option(
    "--wait-for",
    help="Wait for selector (browser mode only)",
)
@click.option(
    "--screenshot",
    is_flag=True,
    help="Capture screenshot (browser mode only)",
)
@click.option(
    "--headless/--no-headless",
    default=True,
    help="Run browser in headless mode",
)
@click.option(
    "--user-agent",
    help="Custom user agent string",
)
@click.option(
    "--timeout",
    type=int,
    default=30,
    help="Request timeout in seconds",
)
@click.pass_context
def scrape(
    ctx: click.Context,
    url: str,
    method: str,
    output: str | None,
    format: str,
    selector: tuple[str, ...],
    xpath: tuple[str, ...],
    wait_for: str | None,
    screenshot: bool,
    headless: bool,
    user_agent: str | None,
    timeout: int,
) -> None:
    """Scrape data from a URL."""
    config = ctx.obj["config"]

    # Update config with CLI options
    if user_agent:
        config.user_agent = user_agent
    config.default_timeout = timeout
    config.browser_headless = headless

    # Create extraction rules
    extraction_rules = []
    for i, sel in enumerate(selector):
        extraction_rules.append(
            ExtractionRule(
                name=f"selector_{i}",
                selector=sel,
                multiple=True,
            )
        )
    for i, xp in enumerate(xpath):
        extraction_rules.append(
            ExtractionRule(
                name=f"xpath_{i}",
                xpath=xp,
                multiple=True,
            )
        )

    # Run scraping
    console.print(f"Scraping {url}...")

    result = asyncio.run(
        _scrape_url(
            url=url,
            method=method,
            config=config,
            extraction_rules=extraction_rules,
            wait_for=wait_for,
            screenshot=screenshot,
        )
    )

    # Handle result
    if result.success:
        console.print("[green]SUCCESS[/green] Scraping successful!")

        # Format output
        if format == "json":
            output_data = json.dumps(result.model_dump(), indent=2, default=str)
        elif format == "csv":
            # Simple CSV conversion for extracted data
            if result.data and result.data.extracted_data:
                buffer = StringIO()
                writer = csv.DictWriter(buffer, fieldnames=result.data.extracted_data.keys())
                writer.writeheader()
                writer.writerow(result.data.extracted_data)
                output_data = buffer.getvalue()
            else:
                output_data = "No data extracted"
        else:  # html
            output_data = result.data.content if result.data else ""

        # Save or print output
        if output:
            Path(output).write_text(output_data)
            console.print(f"[green]OK[/green] Output saved to {output}")
        else:
            console.print(output_data)

        # Show statistics
        if result.metadata:
            table = Table(title="Scraping Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Duration", f"{result.metadata.duration_seconds:.2f}s")
            table.add_row("Records", str(result.metadata.records_scraped))
            table.add_row("Errors", str(result.metadata.errors_count))

            console.print(table)
    else:
        console.print(f"[red]FAILED[/red] Scraping failed: {result.error}")


async def _scrape_url(
    url: str,
    method: str,
    config: ScraperConfig,
    extraction_rules: list[ExtractionRule],
    wait_for: str | None = None,
    screenshot: bool = False,
) -> Any:
    """Async function to scrape a URL."""
    # Convert base config to WebScraperConfig
    web_config = WebScraperConfig(**config.model_dump())

    if method == "browser":
        scraper = BrowserScraper(web_config)
        scraper.extraction_rules = extraction_rules

        kwargs = {}
        if wait_for:
            kwargs["wait_for_selector"] = wait_for
        if screenshot:
            kwargs["screenshot"] = True

        return await scraper.scrape(url, **kwargs)
    scraper = HttpScraper(web_config)
    scraper.extraction_rules = extraction_rules
    return await scraper.scrape(url)


@cli.command()
@click.argument("urls", nargs=-1, required=True)
@click.option(
    "--method",
    "-m",
    type=click.Choice(["http", "browser"]),
    default="http",
    help="Scraping method to use",
)
@click.option(
    "--concurrent",
    "-c",
    type=int,
    default=5,
    help="Number of concurrent requests",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    help="Output directory for results",
)
@click.pass_context
def batch(
    ctx: click.Context,
    urls: tuple[str, ...],
    method: str,
    concurrent: int,
    output_dir: str | None,
) -> None:
    """Scrape multiple URLs in batch."""
    config = ctx.obj["config"]
    config.concurrent_requests = concurrent

    console.print(f"Scraping {len(urls)} URLs with {concurrent} concurrent requests...")

    # Run batch scraping
    results = asyncio.run(_batch_scrape(list(urls), method, config))

    # Process results
    success_count = sum(1 for r in results if r.success)
    failed_count = len(results) - success_count

    console.print(f"[green]SUCCESS[/green] Count: {success_count}")
    console.print(f"[red]FAILED[/red] Count: {failed_count}")

    # Save results if output directory specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for i, result in enumerate(results):
            if result.success:
                file_path = output_path / f"result_{i}.json"
                file_path.write_text(json.dumps(result.model_dump(), indent=2, default=str))

        console.print(f"[green]OK[/green] Results saved to {output_dir}")


async def _batch_scrape(urls: list[str], method: str, config: ScraperConfig) -> list[Any]:
    """Async function to scrape multiple URLs."""
    # Convert base config to WebScraperConfig
    web_config = WebScraperConfig(**config.model_dump())

    scraper = BrowserScraper(web_config) if method == "browser" else HttpScraper(web_config)

    async with scraper.session() as s:
        return await s.scrape_multiple(urls)


@cli.command()
@click.argument("sitemap_url")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file for URLs",
)
@click.option(
    "--scrape",
    is_flag=True,
    help="Scrape all URLs from sitemap",
)
@click.pass_context
def sitemap(
    ctx: click.Context,
    sitemap_url: str,
    output: str | None,
    scrape: bool,
) -> None:
    """Extract and optionally scrape URLs from a sitemap."""
    config = ctx.obj["config"]

    console.print(f"Extracting URLs from sitemap: {sitemap_url}")

    # Extract URLs from sitemap
    urls = asyncio.run(_extract_sitemap(sitemap_url, config))

    console.print(f"[green]OK[/green] Found {len(urls)} URLs")

    # Save URLs if output specified
    if output:
        Path(output).write_text("\n".join(urls))
        console.print(f"[green]OK[/green] URLs saved to {output}")
    else:
        for url in urls[:10]:  # Show first 10
            console.print(f"  • {url}")
        if len(urls) > 10:
            console.print(f"  ... and {len(urls) - 10} more")

    # Scrape all URLs if requested
    if scrape:
        console.print(f"Scraping {len(urls)} URLs...")
        results = asyncio.run(_batch_scrape(urls, "http", config))

        success_count = sum(1 for r in results if r.success)
        console.print(f"[green]OK[/green] Successfully scraped {success_count}/{len(urls)} URLs")


async def _extract_sitemap(sitemap_url: str, config: ScraperConfig) -> list[str]:
    """Extract URLs from a sitemap."""
    # Convert base config to WebScraperConfig
    web_config = WebScraperConfig(**config.model_dump())

    scraper = HttpScraper(web_config)
    return await scraper.scrape_sitemap(sitemap_url)


@cli.command()
@click.option(
    "--host",
    default="127.0.0.1",
    help="API server host",
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="API server port",
)
@click.pass_context
def serve(ctx: click.Context, host: str, port: int) -> None:  # noqa: ARG001
    """Start the Scrap-E API server."""
    console.print(f"Starting API server on {host}:{port}")
    console.print("[yellow]API server not yet implemented[/yellow]")
    # TODO: Implement FastAPI server


@cli.command()
def doctor() -> None:
    """Check system dependencies and configuration."""
    console.print("[bold]Scrap-E System Check[/bold]\n")

    checks = []

    # Check Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    checks.append(("Python Version", py_version, sys.version_info >= (3, 13)))

    # Check important packages
    packages = [
        "httpx",
        "beautifulsoup4",
        "playwright",
        "pandas",
        "pydantic",
    ]

    for package in packages:
        try:
            __import__(package)
            checks.append((f"Package: {package}", "Installed", True))
        except ImportError:
            checks.append((f"Package: {package}", "Not installed", False))

    # Check browser drivers
    if sync_playwright:
        try:
            with sync_playwright() as p:
                for browser in ["chromium", "firefox", "webkit"]:
                    try:
                        getattr(p, browser).launch(headless=True).close()
                        checks.append((f"Browser: {browser}", "Available", True))
                    except Exception:
                        checks.append((f"Browser: {browser}", "Not available", False))
        except Exception:
            checks.append(("Playwright browsers", "Not configured", False))
    else:
        checks.append(("Playwright", "Not installed", False))

    # Display results
    table = Table(title="System Check Results")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Result", style="white")

    for component, status, success in checks:
        result_icon = "[green]OK[/green]" if success else "[red]FAIL[/red]"
        table.add_row(component, status, result_icon)

    console.print(table)

    # Overall status
    if all(check[2] for check in checks):
        console.print("\n[green]OK[/green] All checks passed! Scrap-E is ready to use.")
    else:
        console.print(
            "\n[yellow]WARNING[/yellow] Some checks failed. Run 'uv sync' to install missing dependencies."
        )


def main() -> None:
    """Main entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
