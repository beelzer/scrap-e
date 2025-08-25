# CLI Usage

Scrap-E provides a powerful command-line interface for quick scraping tasks and automation. The CLI supports all major scraping operations with simple, intuitive commands.

## Installation Verification

Before using the CLI, verify your installation:

```bash
# Check version
scrap-e --version

# System diagnostic
scrap-e doctor
```

## Basic Commands

### scrape

The main command for scraping individual URLs:

```bash
# Basic scraping
scrap-e scrape https://example.com

# Save to file
scrap-e scrape https://example.com -o output.json

# Use browser mode for JavaScript rendering
scrap-e scrape https://example.com --method browser

# Extract specific data with CSS selectors
scrap-e scrape https://example.com -s "h1" -s ".content"

# Extract with XPath
scrap-e scrape https://example.com -x "//h1" -x "//p[@class='content']"
```

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--method` | `-m` | Scraping method (http/browser) | http |
| `--output` | `-o` | Output file path | stdout |
| `--format` | `-f` | Output format (json/csv/html) | json |
| `--selector` | `-s` | CSS selector (repeatable) | None |
| `--xpath` | `-x` | XPath expression (repeatable) | None |
| `--wait-for` | | Wait for selector (browser only) | None |
| `--screenshot` | | Capture screenshot (browser only) | False |
| `--headless/--no-headless` | | Browser headless mode | True |
| `--user-agent` | | Custom user agent | Default |
| `--timeout` | | Request timeout in seconds | 30 |

#### Examples

**Extract article titles and content:**
```bash
scrap-e scrape https://news.example.com \
  -s "h2.article-title" \
  -s ".article-content" \
  -o articles.json
```

**Browser scraping with screenshot:**
```bash
scrap-e scrape https://spa.example.com \
  --method browser \
  --wait-for ".dynamic-content" \
  --screenshot \
  -o spa_data.json
```

**Custom user agent and timeout:**
```bash
scrap-e scrape https://api.example.com \
  --user-agent "Custom Bot 1.0" \
  --timeout 60 \
  -o api_data.json
```

### batch

Scrape multiple URLs concurrently:

```bash
# Basic batch scraping
scrap-e batch https://site1.com https://site2.com https://site3.com

# Control concurrency
scrap-e batch url1 url2 url3 --concurrent 10

# Save results to directory
scrap-e batch url1 url2 url3 --output-dir results/

# Browser batch scraping
scrap-e batch url1 url2 url3 --method browser --concurrent 5
```

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--method` | `-m` | Scraping method (http/browser) | http |
| `--concurrent` | `-c` | Number of concurrent requests | 5 |
| `--output-dir` | `-o` | Output directory for results | None |

#### Examples

**High-concurrency scraping:**
```bash
scrap-e batch \
  https://example.com/page1 \
  https://example.com/page2 \
  https://example.com/page3 \
  --concurrent 20 \
  --output-dir scraped_pages/
```

**Browser batch with controlled rate:**
```bash
scrap-e batch \
  https://spa1.com \
  https://spa2.com \
  https://spa3.com \
  --method browser \
  --concurrent 2
```

### sitemap

Extract URLs from sitemaps and optionally scrape them:

```bash
# Extract URLs from sitemap
scrap-e sitemap https://example.com/sitemap.xml

# Save URLs to file
scrap-e sitemap https://example.com/sitemap.xml -o urls.txt

# Extract and scrape all URLs
scrap-e sitemap https://example.com/sitemap.xml --scrape
```

#### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Output file for URLs |
| `--scrape` | | Scrape all URLs from sitemap |

#### Examples

**Extract sitemap URLs:**
```bash
scrap-e sitemap https://blog.example.com/sitemap.xml -o blog_urls.txt
```

**Full sitemap scraping:**
```bash
scrap-e sitemap https://shop.example.com/sitemap.xml --scrape
```

### doctor

System diagnostics and health check:

```bash
scrap-e doctor
```

This command checks:
- Python version compatibility
- Required packages installation
- Browser drivers availability
- System dependencies
- Configuration validity

**Sample output:**
```
Scrap-E System Check

Component                Status              Result
Python Version           3.13.0              ✓ OK
Package: httpx           Installed           ✓ OK
Package: playwright      Installed           ✓ OK
Browser: chromium        Available           ✓ OK
Browser: firefox         Available           ✓ OK
Browser: webkit          Not available       ✗ FAIL

⚠ WARNING Some checks failed. Run 'playwright install webkit' to install missing browsers.
```

### serve

Start the API server (when implemented):

```bash
# Start on default host/port
scrap-e serve

# Custom host and port
scrap-e serve --host 0.0.0.0 --port 8080
```

## Configuration

### Global Options

Available for all commands:

| Option | Description | Default |
|--------|-------------|---------|
| `--config` | Path to configuration file | None |
| `--debug/--no-debug` | Enable debug mode | False |

### Configuration File

Use a configuration file for consistent settings:

```yaml
# config.yaml
debug: true
user_agent: "Custom Scraper Bot 1.0"
timeout: 60
concurrent_requests: 10
browser_headless: true
output_format: json
```

Then use it:

```bash
scrap-e --config config.yaml scrape https://example.com
```

### Environment Variables

Configure via environment variables:

```bash
export SCRAPER_USER_AGENT="Custom Bot"
export SCRAPER_DEFAULT_TIMEOUT=60
export SCRAPER_BROWSER_HEADLESS=true
export SCRAPER_DEBUG=true

scrap-e scrape https://example.com
```

## Output Formats

### JSON (Default)

Complete scraping result with metadata:

```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "status_code": 200,
    "content": "...",
    "extracted_data": {
      "title": "Example Page",
      "content": ["paragraph 1", "paragraph 2"]
    }
  },
  "metadata": {
    "scraper_type": "web_http",
    "duration_seconds": 1.23,
    "records_scraped": 1
  }
}
```

### CSV

Tabular format for extracted data:

```csv
title,content_0,content_1
"Example Page","paragraph 1","paragraph 2"
```

### HTML

Raw HTML content:

```html
<!DOCTYPE html>
<html>
<head><title>Example Page</title></head>
<body>...</body>
</html>
```

## Advanced Usage

### Complex Extraction

```bash
# Multiple selectors with custom output
scrap-e scrape https://ecommerce.example.com \
  -s ".product-title" \
  -s ".product-price" \
  -s ".product-description" \
  -s ".product-image" \
  --format json \
  -o products.json
```

### Rate-Limited Scraping

```bash
# Gentle scraping with low concurrency
scrap-e batch \
  https://api.example.com/page1 \
  https://api.example.com/page2 \
  https://api.example.com/page3 \
  --concurrent 1 \
  --timeout 30
```

### Browser Automation

```bash
# Full browser automation with screenshot
scrap-e scrape https://app.example.com/dashboard \
  --method browser \
  --wait-for "[data-loaded='true']" \
  --screenshot \
  --no-headless \
  -o dashboard.json
```

## Error Handling

The CLI provides detailed error information:

```bash
# Verbose error reporting
scrap-e --debug scrape https://invalid-url.com
```

**Common exit codes:**
- `0`: Success
- `1`: General error
- `2`: Configuration error
- `3`: Network error
- `4`: Parsing error

## Performance Tips

1. **Adjust concurrency** based on target server capacity
2. **Use appropriate timeouts** for different types of sites
3. **Choose the right method** - HTTP for static content, Browser for SPAs
4. **Use selectors efficiently** - specific selectors are faster
5. **Save to files** to avoid terminal buffer limits with large outputs

## Integration Examples

### Shell Scripts

```bash
#!/bin/bash
# bulk_scraper.sh

urls=(
  "https://site1.com"
  "https://site2.com"
  "https://site3.com"
)

for url in "${urls[@]}"; do
  echo "Scraping $url..."
  scrap-e scrape "$url" -o "output_$(basename "$url").json"
done
```

### Cron Jobs

```bash
# Daily sitemap scraping
0 2 * * * /usr/local/bin/scrap-e sitemap https://news.example.com/sitemap.xml --scrape
```

### Pipeline Usage

```bash
# Extract URLs and pipe to batch scraper
scrap-e sitemap https://example.com/sitemap.xml -o - | \
  head -10 | \
  xargs scrap-e batch --concurrent 5
```

## Troubleshooting

**Command not found:**
```bash
# Ensure scrap-e is in PATH
which scrap-e

# Or run directly
python -m scrap_e.cli
```

**Browser automation fails:**
```bash
# Check browser installation
scrap-e doctor

# Install missing browsers
playwright install
```

**Memory issues with large sites:**
```bash
# Reduce concurrency
scrap-e batch urls... --concurrent 2

# Use streaming for large datasets
# (Feature planned for future release)
```

For more detailed troubleshooting, see the [Error Handling Guide](error-handling.md).
