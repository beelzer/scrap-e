# CLI Commands API

The Scrap-E command-line interface provides powerful tools for scraping operations. This reference documents all available commands and their options.

## Main Command

### scrap-e

The root command with global options available to all subcommands.

```bash
scrap-e [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

#### Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `--version` | Show version and exit | - |
| `--config PATH` | Path to configuration file | None |
| `--debug/--no-debug` | Enable debug mode | False |
| `--help` | Show help message | - |

#### Configuration

Global configuration affects all commands:

```bash
# Using configuration file
scrap-e --config scraper.yaml scrape https://example.com

# Debug mode for detailed logging
scrap-e --debug scrape https://example.com
```

## Commands

### scrape

Scrape data from a single URL.

```bash
scrap-e scrape URL [OPTIONS]
```

#### Arguments

- `URL` - The URL to scrape (required)

#### Options

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--method` | `-m` | Choice | Scraping method: `http`, `browser` | `http` |
| `--output` | `-o` | Path | Output file path | stdout |
| `--format` | `-f` | Choice | Output format: `json`, `csv`, `html` | `json` |
| `--selector` | `-s` | Text | CSS selector (repeatable) | None |
| `--xpath` | `-x` | Text | XPath expression (repeatable) | None |
| `--wait-for` | | Text | Wait for selector (browser only) | None |
| `--screenshot` | | Flag | Capture screenshot (browser only) | False |
| `--headless/--no-headless` | | Flag | Browser headless mode | True |
| `--user-agent` | | Text | Custom user agent string | Default UA |
| `--timeout` | | Integer | Request timeout in seconds | 30 |

#### Examples

**Basic scraping:**
```bash
scrap-e scrape https://example.com
```

**Extract specific data:**
```bash
scrap-e scrape https://news.example.com \
  --selector "h2.headline" \
  --selector ".article-summary" \
  --output articles.json
```

**Browser scraping with JavaScript:**
```bash
scrap-e scrape https://spa.example.com \
  --method browser \
  --wait-for ".dynamic-content" \
  --screenshot \
  --output spa_data.json
```

**XPath extraction:**
```bash
scrap-e scrape https://example.com \
  --xpath "//h1/text()" \
  --xpath "//p[@class='content']/text()" \
  --format csv
```

#### Return Codes

- `0` - Success
- `1` - Scraping failed
- `2` - Invalid arguments
- `3` - Network error
- `4` - Parsing error

### batch

Scrape multiple URLs concurrently.

```bash
scrap-e batch URL [URL ...] [OPTIONS]
```

#### Arguments

- `URL` - One or more URLs to scrape (required, multiple allowed)

#### Options

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--method` | `-m` | Choice | Scraping method: `http`, `browser` | `http` |
| `--concurrent` | `-c` | Integer | Number of concurrent requests | 5 |
| `--output-dir` | `-o` | Path | Output directory for results | None |

#### Examples

**Basic batch scraping:**
```bash
scrap-e batch \
  https://example.com/page1 \
  https://example.com/page2 \
  https://example.com/page3
```

**High concurrency with output directory:**
```bash
scrap-e batch \
  https://site1.com \
  https://site2.com \
  https://site3.com \
  --concurrent 10 \
  --output-dir scraped_results/
```

**Browser batch scraping:**
```bash
scrap-e batch \
  https://app1.example.com \
  https://app2.example.com \
  --method browser \
  --concurrent 2
```

#### Output Structure

When using `--output-dir`, files are saved as:
- `result_0.json` - First URL result
- `result_1.json` - Second URL result
- etc.

#### Performance Considerations

- Default concurrency is 5 to be respectful to target servers
- Increase `--concurrent` for better performance if the target supports it
- Browser method is slower but handles JavaScript-heavy sites
- Monitor network usage and adjust concurrency accordingly

### sitemap

Extract URLs from XML sitemaps and optionally scrape them.

```bash
scrap-e sitemap SITEMAP_URL [OPTIONS]
```

#### Arguments

- `SITEMAP_URL` - URL of the XML sitemap (required)

#### Options

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--output` | `-o` | Path | Output file for extracted URLs |
| `--scrape` | | Flag | Scrape all URLs from sitemap |

#### Examples

**Extract URLs from sitemap:**
```bash
scrap-e sitemap https://example.com/sitemap.xml
```

**Save URLs to file:**
```bash
scrap-e sitemap https://blog.example.com/sitemap.xml \
  --output blog_urls.txt
```

**Extract and scrape all URLs:**
```bash
scrap-e sitemap https://shop.example.com/sitemap.xml --scrape
```

#### Sitemap Support

Supports standard XML sitemap formats:
- Regular sitemaps (`<urlset>`)
- Sitemap index files (`<sitemapindex>`)
- Nested sitemaps (automatically resolved)

#### Output Format

**URL extraction only:**
```
https://example.com/page1
https://example.com/page2
https://example.com/page3
```

**With scraping (`--scrape` flag):**
- Console output shows scraping progress
- Results are not saved unless combined with `--output-dir` from batch command

### doctor

System diagnostics and health check.

```bash
scrap-e doctor
```

#### No Options

This command takes no additional options.

#### Checks Performed

1. **Python Version** - Verifies Python 3.13+ compatibility
2. **Package Dependencies** - Checks installation of required packages:
   - httpx (HTTP client)
   - beautifulsoup4 (HTML parsing)
   - playwright (Browser automation)
   - pandas (Data processing)
   - pydantic (Data validation)
3. **Browser Drivers** - Tests browser availability:
   - Chromium
   - Firefox  
   - WebKit
4. **System Dependencies** - Verifies system-level requirements

#### Example Output

```
Scrap-E System Check

Component                Status              Result
Python Version           3.13.0              ✓ OK
Package: httpx           Installed           ✓ OK
Package: beautifulsoup4  Installed           ✓ OK
Package: playwright      Installed           ✓ OK
Package: pandas          Installed           ✓ OK
Package: pydantic        Installed           ✓ OK
Browser: chromium        Available           ✓ OK
Browser: firefox         Available           ✓ OK
Browser: webkit          Not available       ✗ FAIL

⚠ WARNING Some checks failed. Run 'playwright install webkit' to install missing browsers.
```

#### Return Codes

- `0` - All checks passed
- `1` - Some checks failed (warnings)
- `2` - Critical failures (cannot operate)

#### Troubleshooting

Based on doctor output:

```bash
# Install missing browsers
playwright install

# Install missing packages
pip install beautifulsoup4 pandas

# Fix Python version
pyenv install 3.13.0
pyenv local 3.13.0
```

### serve

Start the Scrap-E API server (planned feature).

```bash
scrap-e serve [OPTIONS]
```

#### Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--host` | Text | API server host | 127.0.0.1 |
| `--port` | Integer | API server port | 8000 |

#### Examples

**Start server on default host/port:**
```bash
scrap-e serve
```

**Custom host and port:**
```bash
scrap-e serve --host 0.0.0.0 --port 8080
```

#### Current Status

This command is a placeholder for future API server functionality. Currently displays:
```
Starting API server on 127.0.0.1:8000
⚠ WARNING API server not yet implemented
```

## Configuration Files

### YAML Configuration

```yaml
# scraper.yaml
debug: true
user_agent: "Custom Scraper Bot 1.0"
default_timeout: 60
concurrent_requests: 10

browser:
  headless: true
  type: chromium
  viewport:
    width: 1920
    height: 1080

output:
  format: json
  pretty_print: true
```

Use with any command:
```bash
scrap-e --config scraper.yaml scrape https://example.com
```

### Environment Variables

Set configuration via environment variables:

```bash
export SCRAPER_USER_AGENT="Custom Bot 1.0"
export SCRAPER_DEFAULT_TIMEOUT=60
export SCRAPER_BROWSER_HEADLESS=true
export SCRAPER_DEBUG=true
```

Variables are automatically loaded by all commands.

## Output Formats

### JSON Format

Default format with complete metadata:

```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "status_code": 200,
    "headers": {...},
    "content": "<!DOCTYPE html>...",
    "extracted_data": {
      "title": "Page Title",
      "links": ["url1", "url2"]
    },
    "metadata": {...}
  },
  "metadata": {
    "scraper_type": "web_http",
    "source": "https://example.com",
    "timestamp": "2024-01-15T10:30:00Z",
    "duration_seconds": 1.23,
    "records_scraped": 1,
    "errors_count": 0
  }
}
```

### CSV Format

Tabular format for extracted data:

```csv
url,title,status_code,content_length
https://example.com,"Example Page",200,15420
```

### HTML Format

Raw HTML content:

```html
<!DOCTYPE html>
<html>
<head><title>Example Page</title></head>
<body>
  <h1>Welcome</h1>
  <p>Content here...</p>
</body>
</html>
```

## Error Handling

### Common Error Messages

**Invalid URL:**
```
Error: Invalid URL format: 'not-a-url'
```

**Network timeout:**
```
Error: Request timed out after 30 seconds
URL: https://very-slow-site.com
```

**Missing selector:**
```
Error: No elements found for selector: '.nonexistent'
URL: https://example.com
```

**Browser not available:**
```
Error: Browser 'chromium' not found
Run 'scrap-e doctor' to check browser installation
```

### Debug Mode

Enable debug mode for detailed error information:

```bash
scrap-e --debug scrape https://problematic-site.com
```

Debug output includes:
- HTTP request/response headers
- Full exception tracebacks
- Parser backend selection
- Performance timing information

## Integration Examples

### Shell Scripting

```bash
#!/bin/bash
# bulk_scraper.sh

URLS=(
    "https://example.com/page1"
    "https://example.com/page2"
    "https://example.com/page3"
)

echo "Starting bulk scraping..."

for url in "${URLS[@]}"; do
    filename="output_$(basename "$url" | tr '/' '_').json"
    echo "Scraping $url -> $filename"

    if scrap-e scrape "$url" --output "$filename"; then
        echo "✓ Success: $url"
    else
        echo "✗ Failed: $url"
    fi
done

echo "Bulk scraping complete!"
```

### Cron Jobs

```bash
# Crontab entry for daily scraping
0 2 * * * /usr/local/bin/scrap-e sitemap https://news.example.com/sitemap.xml --scrape > /var/log/scraper.log 2>&1

# Weekly full site scraping
0 1 * * 0 /usr/local/bin/scrap-e batch $(cat /home/user/urls.txt) --output-dir /data/scraped/$(date +\%Y-\%m-\%d)/
```

### CI/CD Pipeline

```yaml
# .github/workflows/scraping.yml
name: Daily Data Collection

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install Scrap-E
        run: |
          pip install scrap-e
          playwright install chromium

      - name: Verify Installation
        run: scrap-e doctor

      - name: Scrape Data
        run: |
          scrap-e batch \
            https://api.example.com/data \
            https://feeds.example.com/rss \
            --output-dir data/$(date +%Y-%m-%d) \
            --concurrent 5

      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: scraped-data
          path: data/
```

## Performance Guidelines

### Concurrency Settings

| Scenario | Recommended Concurrency | Notes |
|----------|--------------------------|-------|
| Small API | 1-2 | Respect rate limits |
| Public website | 3-5 | Be respectful |
| Internal service | 10-20 | Based on capacity |
| Bulk processing | 20-50 | Monitor resources |

### Memory Usage

- HTTP method: ~5MB per concurrent request
- Browser method: ~50-100MB per concurrent request
- Factor in target response sizes
- Use `--output-dir` for large batches to avoid memory accumulation

### Network Considerations

- Default timeout (30s) works for most sites
- Increase timeout for slow APIs: `--timeout 120`
- Use `--user-agent` to identify your scraper
- Implement delays between requests if needed (future feature)

For more detailed usage examples, see the [CLI Usage Guide](../../user-guide/cli-usage.md).
