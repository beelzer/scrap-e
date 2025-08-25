# Contributing

Thank you for your interest in contributing to Scrap-E! This guide will help you get started with contributing to the project.

## Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up the development environment**
4. **Create a feature branch**
5. **Make your changes**
6. **Run tests and quality checks**
7. **Submit a pull request**

## Development Environment Setup

### Prerequisites

- Python 3.13 or higher
- Git
- UV (recommended) or pip
- Docker Desktop (optional, for testing)

### Clone and Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/scrap-e.git
cd scrap-e

# Add upstream remote
git remote add upstream https://github.com/beelzer/scrap-e.git

# Install with development dependencies
uv sync --dev

# Or with pip
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Install Playwright browsers
playwright install

# Verify setup
scrap-e doctor
```

### Development Dependencies

The development environment includes:

**Core Tools:**

- pytest for testing
- mypy for type checking
- ruff for linting and formatting
- pre-commit for git hooks

**Testing Tools:**

- pytest-asyncio for async testing
- pytest-cov for coverage
- pytest-benchmark for performance testing
- pytest-mock for mocking

**Quality Assurance:**

- bandit for security scanning
- safety for dependency vulnerability checks
- vulture for dead code detection

## Code Standards

### Python Style Guide

We follow strict code quality standards:

- **PEP 8** compliance enforced by ruff
- **Type hints** required for all functions and methods
- **Docstrings** required for all public functions and classes
- **Async/await** preferred over callbacks
- **Modern Python features** (Python 3.13+)

### Code Formatting

Formatting is handled automatically by ruff:

```bash
# Format code
ruff format

# Check and fix linting issues
ruff check --fix

# Type checking
mypy src
```

### Import Organization

Imports should be organized as follows:

```python
"""Module docstring."""

# Standard library
import asyncio
import json
from pathlib import Path
from typing import Any

# Third-party packages  
import httpx
from pydantic import BaseModel

# Local imports
from scrap_e.core.base_scraper import BaseScraper
from scrap_e.core.models import ScraperResult
```

### Naming Conventions

- **Classes**: PascalCase (`HttpScraper`, `ScraperConfig`)
- **Functions/Methods**: snake_case (`scrape_url`, `get_data`)
- **Variables**: snake_case (`user_agent`, `max_retries`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_TIMEOUT`, `MAX_WORKERS`)
- **Private**: Leading underscore (`_internal_method`)

### Documentation Standards

All public functions and classes must have docstrings:

```python
async def scrape_multiple(
    self,
    sources: list[str],
    max_concurrent: int | None = None,
    **kwargs: Any,
) -> list[ScraperResult[T]]:
    """
    Scrape multiple sources concurrently.

    Args:
        sources: List of sources to scrape
        max_concurrent: Maximum number of concurrent operations
        **kwargs: Additional arguments passed to each scrape operation

    Returns:
        List of ScraperResult objects

    Raises:
        ScraperError: If configuration is invalid
        ConnectionError: If network issues occur

    Example:
        ```python
        scraper = HttpScraper()
        results = await scraper.scrape_multiple([
            "https://site1.com",
            "https://site2.com"
        ])
        ```
    """
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scrap_e

# Run specific test categories
pytest -m "not slow"          # Skip slow tests
pytest -m integration         # Run integration tests only
pytest -m performance         # Run performance tests only

# Run tests in parallel
pytest -n auto
```

### Test Organization

Tests are organized by category:

```
tests/
├── unit/                    # Unit tests
│   ├── core/               # Core functionality tests
│   └── scrapers/           # Scraper-specific tests
├── integration/            # Integration tests
├── performance/            # Performance benchmarks
└── fixtures/               # Test fixtures and data
```

### Writing Tests

#### Unit Tests

```python
"""Test HTTP scraper functionality."""

import pytest
from scrap_e.scrapers.web import HttpScraper
from scrap_e.core.models import ExtractionRule


class TestHttpScraper:
    """Test suite for HttpScraper."""

    @pytest.fixture
    async def scraper(self) -> HttpScraper:
        """Create a test scraper instance."""
        return HttpScraper()

    async def test_basic_scraping(self, scraper: HttpScraper) -> None:
        """Test basic scraping functionality."""
        result = await scraper.scrape("https://httpbin.org/json")

        assert result.success
        assert result.data is not None
        assert result.data.status_code == 200
        assert "application/json" in result.data.headers.get("content-type", "")

    async def test_extraction_rules(self, scraper: HttpScraper) -> None:
        """Test data extraction with rules."""
        scraper.add_extraction_rule(ExtractionRule(
            name="title",
            selector="h1",
            required=True
        ))

        result = await scraper.scrape("https://example.com")

        assert result.success
        assert "title" in result.data.extracted_data
```

#### Integration Tests

```python
"""Integration tests for web scraping."""

import pytest
from scrap_e.scrapers.web import HttpScraper


@pytest.mark.integration
@pytest.mark.network
class TestWebScrapingIntegration:
    """Integration tests requiring network access."""

    async def test_real_website_scraping(self) -> None:
        """Test scraping a real website."""
        scraper = HttpScraper()

        result = await scraper.scrape("https://httpbin.org/headers")

        assert result.success
        assert result.data.status_code == 200
```

#### Performance Tests

```python
"""Performance tests and benchmarks."""

import pytest
from scrap_e.scrapers.web import HttpScraper


@pytest.mark.benchmark
class TestScrapingPerformance:
    """Performance benchmarks."""

    async def test_concurrent_scraping_performance(self, benchmark) -> None:
        """Benchmark concurrent scraping performance."""
        scraper = HttpScraper()
        urls = [f"https://httpbin.org/delay/{i}" for i in range(5)]

        result = await benchmark(scraper.scrape_multiple, urls)

        assert len(result) == 5
        assert all(r.success for r in result)
```

### Test Fixtures

Create reusable fixtures in `tests/fixtures/`:

```python
"""Common test fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_html() -> str:
    """Sample HTML content for testing."""
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Main Title</h1>
            <p class="content">Test content</p>
        </body>
    </html>
    """


@pytest.fixture
def temp_config_file(tmp_path: Path) -> Path:
    """Create a temporary configuration file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
    debug: true
    log_level: DEBUG
    default_timeout: 10.0
    """)
    return config_file
```

## Pull Request Process

### Before Submitting

1. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following code standards

3. **Run the full test suite:**

   ```bash
   pytest
   ```

4. **Run quality checks:**

   ```bash
   pre-commit run --all-files
   ```

5. **Update documentation** if needed

6. **Add/update tests** for your changes

### Submitting the PR

1. **Push your branch:**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a pull request** with:
   - **Clear title** describing the change
   - **Detailed description** explaining what and why
   - **Link to related issues**
   - **Screenshots** for UI changes
   - **Breaking changes** clearly marked

### PR Template

```markdown
## Description

Brief description of the changes.

## Type of Change

- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Added tests for new functionality
- [ ] Manual testing performed

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Performance impact considered

## Related Issues

Closes #(issue number)
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Address feedback** and update PR
4. **Final approval** and merge

## Types of Contributions

### Bug Fixes

1. **Check existing issues** first
2. **Create an issue** if one doesn't exist
3. **Include test cases** that reproduce the bug
4. **Fix the issue** with minimal changes
5. **Verify the fix** with tests

### New Features

1. **Discuss the feature** in an issue first
2. **Consider the API design** carefully
3. **Implement with tests**
4. **Update documentation**
5. **Consider backward compatibility**

### Documentation

1. **Use clear, concise language**
2. **Include code examples**
3. **Test code examples**
4. **Follow existing structure**
5. **Update navigation** if needed

### Performance Improvements

1. **Benchmark current performance**
2. **Implement improvements**
3. **Measure impact**
4. **Include benchmark tests**
5. **Document performance gains**

## Code Architecture

### Adding New Scrapers

When adding new scraper types:

1. **Inherit from BaseScraper**
2. **Implement required methods**
3. **Add configuration options**
4. **Create comprehensive tests**
5. **Update documentation**

Example structure:

```python
"""Custom scraper implementation."""

from typing import Any, AsyncIterator
from scrap_e.core.base_scraper import BaseScraper
from scrap_e.core.config import ScraperConfig
from scrap_e.core.models import ScraperType


class CustomScraper(BaseScraper[CustomData, CustomConfig]):
    """Custom scraper implementation."""

    def _get_default_config(self) -> CustomConfig:
        """Get default configuration."""
        return CustomConfig()

    @property
    def scraper_type(self) -> ScraperType:
        """Return scraper type."""
        return ScraperType.CUSTOM

    async def _initialize(self) -> None:
        """Initialize resources."""
        pass

    async def _cleanup(self) -> None:
        """Clean up resources."""
        pass

    async def _scrape(self, source: str, **kwargs: Any) -> CustomData:
        """Perform scraping."""
        # Implementation here
        pass

    async def _stream_scrape(self, source: str, chunk_size: int, **kwargs: Any) -> AsyncIterator[CustomData]:
        """Stream scraping implementation."""
        # Implementation here
        pass

    async def _validate_source(self, source: str, **kwargs: Any) -> None:
        """Validate source accessibility."""
        # Implementation here
        pass
```

## Issue Reporting

### Bug Reports

Include:

- **Environment details** (OS, Python version, package versions)
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Error messages and stack traces**
- **Minimal code example**
- **scrap-e doctor output**

### Feature Requests

Include:

- **Use case description**
- **Proposed API design**
- **Alternative solutions considered**
- **Implementation willingness**

### Security Issues

Report security vulnerabilities privately:

1. **Email**: <security@scrap-e.dev> (if available)
2. **GitHub Security**: Use GitHub's security advisory feature
3. **Do not** open public issues for security vulnerabilities

## Community Guidelines

### Code of Conduct

- **Be respectful** to all contributors
- **Welcome newcomers** and help them learn
- **Focus on technical merit**
- **Assume good intentions**
- **Resolve conflicts professionally**

### Communication

- **Use GitHub issues** for bugs and features
- **Use GitHub discussions** for questions and ideas
- **Be clear and concise** in communications
- **Provide context** for your requests
- **Follow up** on conversations

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

### Release Checklist

1. **Update version numbers**
2. **Update CHANGELOG.md**
3. **Run full test suite**
4. **Build documentation**
5. **Create release tag**
6. **Publish to PyPI**
7. **Update GitHub release**

## Getting Help

### Resources

- **Documentation**: Latest docs at `/docs`
- **Examples**: Check `/examples` directory
- **Tests**: See `/tests` for usage patterns
- **GitHub Issues**: Search existing issues first
- **GitHub Discussions**: For general questions

### Mentorship

New contributors can:

- **Find good first issues** labeled `good-first-issue`
- **Ask for guidance** in issues or discussions
- **Pair program** with experienced contributors
- **Join community calls** (if available)

## Recognition

Contributors are recognized through:

- **Git commit attribution**
- **CONTRIBUTORS.md file**
- **Release notes mentions**
- **GitHub contributor stats**

Thank you for contributing to Scrap-E! Your contributions help make web scraping accessible to everyone.
