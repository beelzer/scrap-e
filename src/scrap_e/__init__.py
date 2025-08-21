"""
Scrap-E: Universal Data Scraper
Web, APIs, Databases, Files - All in one powerful scraping framework
"""

from importlib.metadata import version

try:
    __version__ = version("scrap-e")
except Exception:
    __version__ = "0.1.0"

from scrap_e.core.base_scraper import BaseScraper
from scrap_e.core.config import ScraperConfig
from scrap_e.core.exceptions import ScraperError
from scrap_e.core.models import ScraperResult

__all__ = [
    "BaseScraper",
    "ScraperConfig",
    "ScraperError",
    "ScraperResult",
    "__version__",
]
