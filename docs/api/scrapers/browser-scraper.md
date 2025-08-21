# Browser Scraper

API reference for the browser-based scraper implementation.

!!! info "Coming Soon"
    This documentation section is currently under development. Please check back soon for detailed API reference.

## Overview

The `BrowserScraper` class provides functionality for scraping JavaScript-heavy websites using browser automation.

## Class Reference

```python
class BrowserScraper(BaseScraper):
    """Browser-based web scraper implementation."""

    # Detailed API documentation coming soon...
```

## Key Features

- Headless and headed browser modes
- JavaScript execution
- Screenshot capture
- PDF generation
- Element interaction (clicking, typing)
- Page navigation
- Cookie and local storage management
- Multiple browser engine support

## Methods

- `navigate()` - Navigate to URL
- `wait_for_element()` - Wait for element to appear
- `click_element()` - Click on element
- `type_text()` - Type text into input
- `take_screenshot()` - Capture screenshot
- `execute_script()` - Execute JavaScript

## Browser Engines

- Chromium (default)
- Firefox
- WebKit

## Usage Examples

Comprehensive usage examples will be available soon.

## See Also

- [Base Scraper](../core/base-scraper.md)
- [HTTP Scraper](http-scraper.md)
