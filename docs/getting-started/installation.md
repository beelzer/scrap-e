# Installation

## System Requirements

- **Python**: 3.13 or higher (required for modern async features)
- **Operating System**: Windows 11, macOS, or Linux
- **Memory**: Minimum 2GB RAM (4GB+ recommended for browser automation)
- **Disk Space**: 500MB for basic installation, 2GB+ for full development setup

## Installation Methods

### From PyPI (Production Use)

When Scrap-E is published to PyPI:

```bash
pip install scrap-e
```

### From Source (Current Development)

For the latest features and development:

```bash
# Clone the repository
git clone https://github.com/beelzer/scrap-e.git
cd scrap-e

# Install with uv (recommended)
uv sync --dev

# Or install with pip
pip install -e ".[dev]"
```

## Post-Installation Setup

After installing Scrap-E, complete the setup with these steps:

### 1. Install Pre-commit Hooks (Development)

```bash
pre-commit install
```

### 2. Install Playwright Browsers (Required for Browser Scraping)

```bash
playwright install
```

This installs Chromium, Firefox, and WebKit browsers for automated scraping.

### 3. Verify Installation

```bash
scrap-e doctor
```

This command checks your system configuration and reports any issues.

## Optional Dependencies

### Browser Automation

Scrap-E supports multiple browser engines via Playwright:

```bash
# Install specific browsers
playwright install chromium
playwright install firefox
playwright install webkit
```

### Database Support

For database scraping, install additional drivers:

```bash
# PostgreSQL
pip install asyncpg psycopg2-binary

# MySQL
pip install aiomysql pymysql

# MongoDB
pip install motor pymongo

# Redis
pip install redis aioredis
```

### File Processing

For advanced file processing capabilities:

```bash
# PDF processing
pip install pypdf pymupdf

# Excel files
pip install openpyxl xlrd

# Image processing with OCR
pip install pillow pytesseract
```

## Development Dependencies

The full development environment includes:

```bash
pip install -e ".[dev]"
```

This includes:

**Testing Tools:**
- pytest, pytest-asyncio, pytest-cov
- pytest-benchmark for performance testing
- pytest-mock for mocking

**Code Quality:**
- ruff for linting and formatting
- mypy for type checking
- pre-commit for git hooks
- bandit for security scanning

**Documentation:**
- mkdocs-material for documentation
- mkdocstrings for API docs

## Environment Variables

Configure Scrap-E using environment variables:

```bash
# Core settings
export SCRAPER_DEBUG=true
export SCRAPER_LOG_LEVEL=INFO
export SCRAPER_OUTPUT_DIR=/path/to/output

# Browser settings
export SCRAPER_BROWSER_TYPE=chromium
export SCRAPER_BROWSER_HEADLESS=true

# Database connections
export SCRAPER_POSTGRES_URL=postgresql://user:pass@host:5432/db
export SCRAPER_MONGODB_URL=mongodb://localhost:27017/db
export SCRAPER_REDIS_URL=redis://localhost:6379/0
```

## Docker Installation

Run Scrap-E in a containerized environment:

```bash
# Build the Docker image
docker build -t scrap-e .

# Run with Docker Compose
docker-compose up -d
```

The Docker setup includes all dependencies and browsers pre-installed.

## Verification

### Basic Verification

```python
import scrap_e
print(f"Scrap-E version: {scrap_e.__version__}")

# Test HTTP scraping
import asyncio
from scrap_e.scrapers.web import HttpScraper

async def test():
    scraper = HttpScraper()
    result = await scraper.scrape("https://httpbin.org/json")
    print("HTTP scraping:", "✓" if result.success else "✗")

asyncio.run(test())
```

### CLI Verification

```bash
# Check version
scrap-e --version

# System diagnostic
scrap-e doctor

# Test scraping
scrap-e scrape https://httpbin.org/json
```

### Browser Scraping Verification

```bash
# Test browser functionality
scrap-e scrape https://example.com --method browser --screenshot
```

## Troubleshooting

### Common Issues

**Playwright not found:**
```bash
playwright install
```

**Permission errors on Windows:**
```bash
# Run as administrator or use:
pip install --user scrap-e
```

**Browser automation fails:**
```bash
# Install system dependencies (Linux)
sudo apt-get install libnss3 libatk-bridge2.0-0 libxss1 libasound2

# Or use our Docker image
docker run --rm scrap-e scrap-e doctor
```

### Getting Help

If you encounter issues:

1. Run `scrap-e doctor` for diagnostic information
2. Check the [troubleshooting guide](../user-guide/troubleshooting.md)
3. Search [GitHub issues](https://github.com/beelzer/scrap-e/issues)
4. Create a new issue with diagnostic output

## Next Steps

- Read the [Quick Start Guide](quickstart.md) to create your first scraper
- Learn about [Configuration](configuration.md) options
- Explore the [User Guide](../user-guide/web-scraping.md) for detailed examples
- Check out the [CLI documentation](../user-guide/cli.md) for command-line usage
