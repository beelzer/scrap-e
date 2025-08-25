"""Core functionality for Scrap-E universal scraper."""

from scrap_e.core.base_scraper import BaseScraper
from scrap_e.core.config import ScraperConfig, WebScraperConfig
from scrap_e.core.exceptions import (
    AuthenticationError,
    ConnectionError,
    ParsingError,
    RateLimitError,
    ScraperError,
    TimeoutError,
    ValidationError,
)
from scrap_e.core.models import (
    CacheConfig,
    ExtractionRule,
    RateLimitConfig,
    RetryConfig,
    ScraperMetadata,
    ScraperResult,
)

__all__ = [
    # Exceptions
    "AuthenticationError",
    # Base classes
    "BaseScraper",
    # Configuration
    "CacheConfig",
    "ConnectionError",
    # Models
    "ExtractionRule",
    "ParsingError",
    "RateLimitConfig",
    "RateLimitError",
    "RetryConfig",
    "ScraperConfig",
    "ScraperError",
    "ScraperMetadata",
    "ScraperResult",
    "TimeoutError",
    "ValidationError",
    "WebScraperConfig",
]
