# Installation

## Requirements

- Python 3.13 or higher
- pip package manager

## Basic Installation

Install Scrap-E using pip:

```bash
pip install scrap-e
```

## Installation from Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/beelzer/scrap-e.git
cd scrap-e
pip install -e .
```

## Optional Dependencies

Scrap-E offers optional dependencies for specific features:

### Browser Automation

For Playwright-based browser automation:

```bash
# Install playwright browsers
playwright install
```

### Development Tools

For development and testing:

```bash
pip install -e ".[dev]"
```

This includes:
- pytest for testing
- mypy for type checking
- ruff for linting
- black for code formatting
- pre-commit hooks

### Documentation

For building documentation:

```bash
pip install -e ".[docs]"
```

## Verify Installation

Check that Scrap-E is installed correctly:

```python
import scrap_e
print(scrap_e.__version__)
```

Or from the command line:

```bash
scrap-e --version
```

## Next Steps

- Read the [Quick Start Guide](quickstart.md) to create your first scraper
- Learn about [Configuration](configuration.md) options
- Explore the [User Guide](../user-guide/web-scraping.md) for detailed examples
