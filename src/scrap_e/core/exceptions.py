"""Custom exceptions for the scraper framework."""

from typing import Any


class ScraperError(Exception):
    """Base exception for all scraper errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(ScraperError):
    """Raised when there's a configuration issue."""


class ConnectionError(ScraperError):
    """Raised when connection to target fails."""


class AuthenticationError(ScraperError):
    """Raised when authentication fails."""


class RateLimitError(ScraperError):
    """Raised when rate limit is exceeded."""


class ParsingError(ScraperError):
    """Raised when data parsing fails."""


class ValidationError(ScraperError):
    """Raised when data validation fails."""


class TimeoutError(ScraperError):
    """Raised when operation times out."""


class RetryError(ScraperError):
    """Raised when all retry attempts are exhausted."""


class CacheError(ScraperError):
    """Raised when cache operations fail."""


class ExtractionError(ScraperError):
    """Raised when data extraction fails."""
