"""Scraper implementations for various data sources."""

from scrap_e.scrapers.web.browser_scraper import BrowserScraper
from scrap_e.scrapers.web.http_scraper import HttpScraper

__all__ = [
    "BrowserScraper",
    "HttpScraper",
]
