# Contributing to Scrap-E

Thank you for your interest in contributing to Scrap-E! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Use the bug report template
3. Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages and stack traces

### Suggesting Features

1. Check existing feature requests
2. Use the feature request template
3. Explain the use case and benefits
4. Provide code examples if possible

### Submitting Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Install development dependencies**:
   ```bash
   uv sync --extra dev
   ```
3. **Make your changes**:
   - Follow the existing code style
   - Add/update tests as needed
   - Update documentation if required
4. **Run quality checks**:
   ```bash
   # Format code
   uv run ruff format src/ tests/

   # Lint code
   uv run ruff check src/ tests/

   # Type checking
   uv run mypy src/

   # Run tests
   uv run pytest

   # Check coverage
   uv run pytest --cov=scrap_e
   ```
5. **Commit your changes**:
   - Use clear, descriptive commit messages
   - Follow conventional commit format: `type: description`
   - Types: feat, fix, docs, style, refactor, test, chore
6. **Push to your fork** and submit a pull request
7. **Fill out the PR template** completely

## Development Setup

### Prerequisites

- Python 3.13+
- uv package manager
- Docker (optional, for containerized testing)

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/beelzer/scrap-e.git
   cd scrap-e
   ```

2. Install dependencies:
   ```bash
   uv sync --extra dev
   ```

3. Set up pre-commit hooks (optional):
   ```bash
   uv run pre-commit install
   ```

4. Run tests to verify setup:
   ```bash
   uv run pytest
   ```

## Code Style Guidelines

### Python Code

- Follow PEP 8 with a line length of 100 characters
- Use type hints for all function signatures
- Use docstrings for all public functions and classes
- Prefer f-strings for string formatting
- Use async/await for I/O operations

### Imports

- Group imports: standard library, third-party, local
- Sort imports alphabetically within groups
- Use absolute imports for project modules

### Example Code Style

```python
"""Module docstring explaining purpose."""

from typing import Any

import httpx
from pydantic import BaseModel

from scrap_e.core.exceptions import ScraperError


class ExampleScraper(BaseModel):
    """Class docstring with description."""

    url: str
    timeout: float = 30.0

    async def scrape(self, source: str) -> dict[str, Any]:
        """
        Scrape data from a source.

        Args:
            source: The source to scrape from

        Returns:
            Dictionary containing scraped data

        Raises:
            ScraperError: If scraping fails
        """
        # Implementation here
        pass
```

## Testing Guidelines

### Writing Tests

- Place tests in `tests/` directory
- Mirror the source code structure
- Use pytest fixtures for common setup
- Test both success and failure cases
- Use mocks for external dependencies

### Test Example

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

from scrap_e.scrapers.web.http_scraper import HttpScraper


@pytest.mark.asyncio
async def test_scraper_success():
    """Test successful scraping."""
    scraper = HttpScraper()

    # Mock external dependencies
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Test</body></html>"

    with patch.object(scraper, "_make_request", return_value=mock_response):
        result = await scraper.scrape("https://example.com")

        assert result.success is True
        assert result.data is not None
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def function(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Longer description if needed, explaining behavior,
    assumptions, and important details.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative

    Example:
        >>> function("test", 42)
        True
    """
```

### Updating Documentation

- Update README.md for significant changes
- Add docstrings for new modules and functions
- Update examples/ directory with usage examples
- Consider adding to docs/ for complex features

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a pull request with version bump
4. After merge, tag the release
5. Build and publish to PyPI (maintainers only)

## Getting Help

- Open an issue for bugs or questions
- Start a discussion for general questions
- Check existing issues and discussions first

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).
