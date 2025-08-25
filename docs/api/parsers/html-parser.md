# HTML Parser API

The HTML Parser provides advanced HTML parsing capabilities with multiple backend support for efficient data extraction.

## Overview

The `HtmlParser` class offers a unified interface for HTML parsing using different backends:
- **BeautifulSoup** - Python-native, feature-rich
- **lxml** - C-based, high performance  
- **selectolax** - Fastest CSS selector engine (optional)

## Class Reference

::: scrap_e.scrapers.web.parser.HtmlParser

## Usage Examples

### Basic Parsing

```python
from scrap_e.scrapers.web.parser import HtmlParser

html_content = """
<html>
<head><title>Example Page</title></head>
<body>
    <h1 class="main-title">Welcome</h1>
    <p class="content">This is a paragraph.</p>
    <div class="articles">
        <article id="1">First Article</article>
        <article id="2">Second Article</article>
    </div>
</body>
</html>
"""

# Create parser instance
parser = HtmlParser(html_content, parser_type="lxml")

# Access different parser backends
soup = parser.soup  # BeautifulSoup instance
lxml_tree = parser.lxml_tree  # lxml instance
selectolax_tree = parser.selectolax_tree  # selectolax instance (if available)
```

### Extraction Rules

The parser works with `ExtractionRule` objects to define how data should be extracted:

```python
from scrap_e.core.models import ExtractionRule

# CSS Selector extraction
title_rule = ExtractionRule(
    name="title",
    selector="h1.main-title",
    attribute="text"  # Extract text content
)

# Extract multiple elements
articles_rule = ExtractionRule(
    name="articles",
    selector="article",
    multiple=True,
    attribute="id"  # Extract id attribute
)

# XPath extraction
xpath_rule = ExtractionRule(
    name="content",
    xpath="//p[@class='content']/text()"
)

# Regex extraction
regex_rule = ExtractionRule(
    name="numbers",
    regex=r'\d+',
    multiple=True
)

# Extract data using rules
title = parser.extract_with_rule(title_rule)
articles = parser.extract_with_rule(articles_rule)
content = parser.extract_with_rule(xpath_rule)
numbers = parser.extract_with_rule(regex_rule)

print(f"Title: {title}")          # Title: Welcome
print(f"Articles: {articles}")    # Articles: ['1', '2']
print(f"Content: {content}")      # Content: This is a paragraph.
```

### Advanced Extraction

#### Required Fields and Defaults

```python
# Required field - raises ParsingError if not found
required_rule = ExtractionRule(
    name="required_title",
    selector="h1.missing-class",
    required=True
)

# With default value
optional_rule = ExtractionRule(
    name="optional_subtitle",
    selector="h2.subtitle",
    default="No subtitle"
)

try:
    title = parser.extract_with_rule(required_rule)
except ParsingError as e:
    print(f"Required field missing: {e}")

subtitle = parser.extract_with_rule(optional_rule)  # Returns "No subtitle"
```

#### Attribute Extraction

```python
# Extract different attributes
link_rule = ExtractionRule(
    name="links",
    selector="a",
    attribute="href",
    multiple=True
)

image_rule = ExtractionRule(
    name="image_src",
    selector="img.hero",
    attribute="src"
)

data_rule = ExtractionRule(
    name="data_id",
    selector="div.widget",
    attribute="data-id"
)

# Extract custom attributes
links = parser.extract_with_rule(link_rule)
image_src = parser.extract_with_rule(image_rule)
data_id = parser.extract_with_rule(data_rule)
```

#### JSON-LD Extraction

```python
html_with_json = """
<html>
<head>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "How to Parse HTML",
        "author": {"name": "John Doe"},
        "datePublished": "2024-01-15"
    }
    </script>
</head>
<body>...</body>
</html>
"""

parser = HtmlParser(html_with_json)

# Extract JSON-LD data
json_rule = ExtractionRule(
    name="article_data",
    json_path="$.headline"  # JSONPath expression
)

headline = parser.extract_with_rule(json_rule)
print(f"Headline: {headline}")  # Headline: How to Parse HTML
```

### Performance Considerations

Different backends have different performance characteristics:

```python
import time
from scrap_e.scrapers.web.parser import HtmlParser

large_html = "<html>" + "<p>content</p>" * 10000 + "</html>"

# BeautifulSoup - Most features, slower
start = time.time()
parser_bs = HtmlParser(large_html, parser_type="html.parser")
soup_time = time.time() - start

# lxml - Fast and feature-rich
start = time.time()
parser_lxml = HtmlParser(large_html, parser_type="lxml")
lxml_time = time.time() - start

print(f"BeautifulSoup: {soup_time:.3f}s")
print(f"lxml: {lxml_time:.3f}s")

# selectolax - Fastest for CSS selectors
if parser_lxml.selectolax_tree:
    start = time.time()
    selectolax_results = parser_lxml.selectolax_tree.css("p")
    selectolax_time = time.time() - start
    print(f"selectolax: {selectolax_time:.3f}s")
```

### Custom Transform Functions

Apply custom transformations to extracted data:

```python
from scrap_e.core.models import ExtractionRule

def clean_price(value: str) -> float:
    """Convert price string to float."""
    if not value:
        return 0.0
    # Remove currency symbols and convert
    price_str = re.sub(r'[^\d.]', '', value)
    return float(price_str) if price_str else 0.0

def normalize_url(value: str, base_url: str) -> str:
    """Convert relative URL to absolute."""
    from urllib.parse import urljoin
    return urljoin(base_url, value)

# Example HTML with prices
html_content = """
<div class="products">
    <div class="product">
        <span class="price">$19.99</span>
        <a href="/product/1">Product 1</a>
    </div>
    <div class="product">
        <span class="price">€25.00</span>
        <a href="/product/2">Product 2</a>
    </div>
</div>
"""

parser = HtmlParser(html_content)

# Extract and transform prices
price_rule = ExtractionRule(
    name="prices",
    selector=".price",
    multiple=True,
    transform="custom"  # Will be processed by scraper
)

# Extract and transform URLs
url_rule = ExtractionRule(
    name="product_urls",
    selector=".product a",
    attribute="href",
    multiple=True,
    transform="to_absolute_url"  # Built-in transform
)

prices = parser.extract_with_rule(price_rule)
urls = parser.extract_with_rule(url_rule)
```

## Backend Comparison

### BeautifulSoup

**Advantages:**
- Pure Python, always available
- Excellent error handling
- Rich API for tree manipulation
- Great for complex parsing tasks

**Disadvantages:**
- Slower than C-based parsers
- Memory overhead for large documents

**Best for:** Complex parsing, data cleaning, error-prone HTML

### lxml

**Advantages:**
- Fast C-based implementation
- Full XPath support
- Good balance of speed and features
- Memory efficient

**Disadvantages:**
- External C dependency
- Stricter HTML parsing

**Best for:** High-performance parsing, XPath queries, large documents

### selectolax

**Advantages:**
- Fastest CSS selector performance
- Very low memory footprint
- Simple, focused API

**Disadvantages:**
- Limited feature set
- CSS selectors only (no XPath)
- Optional dependency

**Best for:** High-volume CSS selector extraction, performance-critical applications

## Error Handling

The parser provides detailed error information:

```python
from scrap_e.core.exceptions import ParsingError

html_content = "<html><body><p>Test</p></body></html>"
parser = HtmlParser(html_content)

try:
    # This will fail because the element doesn't exist
    rule = ExtractionRule(
        name="missing_element",
        selector=".nonexistent",
        required=True
    )

    result = parser.extract_with_rule(rule)

except ParsingError as e:
    print(f"Parsing failed: {e}")
    print(f"Rule name: {e.details.get('rule_name')}")
    print(f"Selector: {e.details.get('selector')}")
```

## Best Practices

### 1. Choose the Right Backend

```python
# For maximum compatibility
parser = HtmlParser(html, parser_type="html.parser")

# For performance with well-formed HTML
parser = HtmlParser(html, parser_type="lxml")

# For malformed HTML that needs fixing
parser = HtmlParser(html, parser_type="html5lib")
```

### 2. Use Specific Selectors

```python
# Good - specific selector
good_rule = ExtractionRule(
    name="product_title",
    selector="h1.product-title"
)

# Less efficient - overly broad selector
broad_rule = ExtractionRule(
    name="title",
    selector="h1"  # Might match multiple elements
)
```

### 3. Handle Missing Data Gracefully

```python
# Always provide defaults for optional fields
rule = ExtractionRule(
    name="optional_field",
    selector=".may-not-exist",
    default="N/A",
    required=False
)
```

### 4. Optimize for Performance

```python
# Cache parser instances for repeated use
class CachedParser:
    def __init__(self):
        self._parsers = {}

    def get_parser(self, html_content: str) -> HtmlParser:
        content_hash = hash(html_content)
        if content_hash not in self._parsers:
            self._parsers[content_hash] = HtmlParser(html_content)
        return self._parsers[content_hash]

# Use selectolax for CSS-only extraction at scale
if HtmlParser(html).selectolax_tree:
    # Use fast selectolax backend
    pass
```

### 5. Test with Real-World HTML

```python
import pytest
from scrap_e.scrapers.web.parser import HtmlParser

def test_parser_with_malformed_html():
    """Test parser handles real-world malformed HTML."""
    malformed_html = "<html><body><p>Unclosed paragraph<div>Nested incorrectly</body></html>"

    parser = HtmlParser(malformed_html, parser_type="html5lib")  # More forgiving

    rule = ExtractionRule(name="text", selector="p")
    result = parser.extract_with_rule(rule)

    assert result == "Unclosed paragraph"
```

The HTML Parser is a core component that powers all HTML-based data extraction in Scrap-E, providing flexibility and performance for various scraping scenarios.
