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
    "BASIC_HTML",
    "COMPLEX_HTML",
    "EMPTY_HTML",
    "EXTRACTION_RULES",
    "FORM_HTML",
    "LARGE_HTML",
    "MALFORMED_HTML",
    "SAMPLE_CONFIGS",
    "SAMPLE_METADATA",
    "SAMPLE_URLS",
    "TABLE_HTML",
    "create_mock_response",
    "mock_http_error",
]
