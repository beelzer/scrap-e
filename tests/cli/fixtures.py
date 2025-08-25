"""Shared fixtures and utilities for CLI tests."""

from unittest.mock import MagicMock


def mock_scraper_result(success=True, data=None, error=None, metadata=None):
    """Create a mock scraper result."""
    if data is None and success:
        data = MagicMock(
            url="http://example.com",
            content="<html><body><h1>Test</h1></body></html>",
            status_code=200,
            headers={},
            extracted_data={"title": "Test Page"},
        )

    if metadata is None and success:
        metadata = MagicMock(
            duration_seconds=1.5,
            records_scraped=1,
            errors_count=0,
        )

    result = MagicMock(
        success=success,
        data=data,
        error=error,
        metadata=metadata,
        model_dump=lambda **kwargs: {
            "success": success,
            "data": {
                "url": getattr(data, "url", None),
                "content": getattr(data, "content", None),
                "status_code": getattr(data, "status_code", None),
                "headers": getattr(data, "headers", {}),
                "extracted_data": getattr(data, "extracted_data", None),
            }
            if data
            else None,
            "error": error,
            "metadata": {
                "duration_seconds": getattr(metadata, "duration_seconds", 0),
                "records_scraped": getattr(metadata, "records_scraped", 0),
                "errors_count": getattr(metadata, "errors_count", 0),
            }
            if metadata
            else None,
        },
    )
    return result  # noqa: RET504


def mock_async_run_handler(return_value):
    """Create a mock handler for asyncio.run that properly handles coroutines."""

    def _handler(coro, *args, **kwargs):
        # If it's a coroutine, just return the mock value
        # This prevents the "coroutine was never awaited" warning
        return return_value

    return _handler
