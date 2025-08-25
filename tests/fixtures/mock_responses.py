"""Mock HTTP responses for testing."""

from typing import Any
from unittest.mock import MagicMock

import httpx


def create_mock_response(
    status_code: int = 200,
    content: str = "",
    headers: dict[str, str] | None = None,
    url: str = "https://example.com",
    json_data: dict[str, Any] | None = None,
) -> MagicMock:
    """Create a mock HTTP response.

    Args:
        status_code: HTTP status code
        content: Response text content
        headers: Response headers
        url: Response URL
        json_data: JSON response data

    Returns:
        Mock response object
    """
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.text = content
    mock_response.content = content.encode() if isinstance(content, str) else content
    mock_response.headers = headers or {"content-type": "text/html"}
    mock_response.url = url
    mock_response.raise_for_status = MagicMock()

    if json_data is not None:
        mock_response.json.return_value = json_data
        mock_response.headers["content-type"] = "application/json"

    # Add is_success property
    mock_response.is_success = 200 <= status_code < 300

    return mock_response


def mock_http_error(
    status_code: int = 404,
    message: str = "Not Found",
    url: str = "https://example.com",
) -> httpx.HTTPStatusError:
    """Create a mock HTTP error.

    Args:
        status_code: HTTP error status code
        message: Error message
        url: Request URL

    Returns:
        HTTPStatusError instance
    """
    response = create_mock_response(status_code=status_code, content=message, url=url)
    request = MagicMock()
    request.url = url

    return httpx.HTTPStatusError(
        message=f"{status_code} {message}",
        request=request,
        response=response,
    )


def create_redirect_response(
    location: str,
    status_code: int = 302,
    original_url: str = "https://example.com",
) -> MagicMock:
    """Create a mock redirect response.

    Args:
        location: Redirect location
        status_code: Redirect status code (301, 302, etc.)
        original_url: Original request URL

    Returns:
        Mock redirect response
    """
    return create_mock_response(
        status_code=status_code,
        headers={
            "location": location,
            "content-type": "text/html",
        },
        url=original_url,
    )


def create_streaming_response(
    chunks: list[str],
    status_code: int = 200,
    url: str = "https://example.com",
) -> MagicMock:
    """Create a mock streaming response.

    Args:
        chunks: List of content chunks
        status_code: HTTP status code
        url: Response URL

    Returns:
        Mock streaming response
    """
    mock_response = create_mock_response(status_code=status_code, url=url)

    def iter_lines():
        for chunk in chunks:
            yield chunk.encode()

    def iter_text():
        yield from chunks

    mock_response.iter_lines = iter_lines
    mock_response.iter_text = iter_text

    return mock_response
