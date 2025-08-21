"""Web scraping modules."""

from scrap_e.scrapers.web.browser_scraper import BrowserScraper
from scrap_e.scrapers.web.http_scraper import HttpScraper
from scrap_e.scrapers.web.parser import HtmlParser

__all__ = [
    "BrowserScraper",
    "HtmlParser",
    "HttpScraper",
]
