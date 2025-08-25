"""Shared test fixtures and data for scrap-e tests."""

from .html_samples import (
    BASIC_HTML,
    COMPLEX_HTML,
    EMPTY_HTML,
    FORM_HTML,
    LARGE_HTML,
    MALFORMED_HTML,
    TABLE_HTML,
)
from .mock_responses import create_mock_response, mock_http_error
from .test_data import (
    EXTRACTION_RULES,
    SAMPLE_CONFIGS,
    SAMPLE_METADATA,
    SAMPLE_URLS,
)

__all__ = [
    # HTML samples
    "BASIC_HTML",
    "COMPLEX_HTML",
    "EMPTY_HTML",
    "FORM_HTML",
    "LARGE_HTML",
    "MALFORMED_HTML",
    "TABLE_HTML",
    # Mock responses
    "create_mock_response",
    "mock_http_error",
    # Test data
    "EXTRACTION_RULES",
    "SAMPLE_CONFIGS",
    "SAMPLE_METADATA",
    "SAMPLE_URLS",
]
