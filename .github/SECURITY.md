# Security Policy

## Supported Versions

Currently supported versions for security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do NOT Create a Public Issue

Security vulnerabilities should not be reported through public GitHub issues.

### 2. Contact Us Privately

Please send a detailed report to: security@scrap-e.dev

Or use GitHub's private vulnerability reporting:
https://github.com/beelzer/scrap-e/security/advisories/new

Include the following information:
- Type of vulnerability
- Full path of source file(s) related to the issue
- Location of affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue

### 3. Response Timeline

- We will acknowledge receipt within 48 hours
- We will provide a detailed response within 7 days
- We will work on a fix and coordinate disclosure

## Security Best Practices for Users

### When Using Scrap-E

1. **Validate Input Sources**
   - Always validate URLs and connection strings
   - Use allow-lists for trusted domains
   - Sanitize user input before scraping

2. **Handle Credentials Securely**
   - Never hardcode credentials in code
   - Use environment variables or secure vaults
   - Rotate credentials regularly

3. **Rate Limiting**
   - Always enable rate limiting to avoid overwhelming targets
   - Respect robots.txt and terms of service

4. **Data Handling**
   - Be cautious with scraped data
   - Validate and sanitize extracted content
   - Don't execute scraped JavaScript or code

### Example Secure Configuration

```python
from scrap_e import HttpScraper
from scrap_e.core.config import WebScraperConfig
import os

# Use environment variables for sensitive data
config = WebScraperConfig(
    # Security settings
    verify_ssl=True,
    follow_redirects=True,
    max_redirects=5,

    # Rate limiting
    rate_limit={
        "enabled": True,
        "requests_per_second": 1,
    },

    # Timeouts to prevent hanging
    default_timeout=30,
)

# Validate URLs before scraping
allowed_domains = ["example.com", "trusted-site.org"]

def is_safe_url(url: str) -> bool:
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    return any(domain.endswith(allowed) for allowed in allowed_domains)

# Use the scraper safely
scraper = HttpScraper(config)
url = "https://example.com/data"

if is_safe_url(url):
    result = await scraper.scrape(url)
```

## Known Security Considerations

### Web Scraping
- Be aware of XSS risks when parsing HTML
- Don't execute JavaScript from untrusted sources
- Validate SSL certificates (enabled by default)

### Database Connections
- Use parameterized queries
- Limit database user permissions
- Use connection pooling with limits

### File Processing
- Validate file types before processing
- Set maximum file size limits
- Scan for malware if processing user uploads

## Security Updates

Security updates will be released as patch versions (e.g., 0.1.1, 0.1.2).

To stay updated:
1. Watch this repository for security advisories
2. Keep dependencies updated: `uv sync --upgrade`
3. Subscribe to release notifications

## Disclosure Policy

- Security issues will be disclosed after a fix is available
- We will credit researchers who report valid issues
- A security advisory will be published for high-severity issues
