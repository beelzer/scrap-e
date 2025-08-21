"""Performance benchmark tests for scrap-e."""

import random
import string

import pytest

from scrap_e.core.models import ExtractionRule
from scrap_e.scrapers.web.http_scraper import HttpScraper
from scrap_e.scrapers.web.parser import HtmlParser


def generate_html(size: str = "small") -> str:
    """Generate HTML content of varying sizes for benchmarking."""
    if size == "small":
        # ~1KB HTML
        return """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Test Header</h1>
            <div class="content">
                <p>Simple paragraph with some text.</p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                    <li>Item 3</li>
                </ul>
            </div>
        </body>
        </html>
        """
    if size == "medium":
        # ~10KB HTML
        items = []
        for i in range(100):
            items.append(f"""
                <article class="post-{i}">
                    <h2>Article Title {i}</h2>
                    <p class="meta">Posted on 2024-{i % 12 + 1:02d}-{i % 28 + 1:02d}</p>
                    <div class="content">
                        <p>{''.join(random.choices(string.ascii_letters + ' ', k=200))}</p>
                    </div>
                    <div class="tags">
                        <span class="tag">tag{i % 5}</span>
                        <span class="tag">category{i % 3}</span>
                    </div>
                </article>
            """)
        return f"""
        <html>
        <head><title>Medium Test Page</title></head>
        <body>
            <header><h1>Blog Posts</h1></header>
            <main>{''.join(items)}</main>
            <footer>Copyright 2024</footer>
        </body>
        </html>
        """
    # large
    # ~100KB HTML
    rows = []
    for i in range(1000):
        cells = "".join(f"<td>Cell {i}-{j}</td>" for j in range(10))
        rows.append(f"<tr>{cells}</tr>")
    return f"""
        <html>
        <head><title>Large Test Page</title></head>
        <body>
            <h1>Data Table</h1>
            <table>
                <thead>
                    <tr>{''.join(f'<th>Column {i}</th>' for i in range(10))}</tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </body>
        </html>
        """


@pytest.mark.performance
@pytest.mark.benchmark(group="parser")
def test_parser_initialization_speed(benchmark):
    """Benchmark HTML parser initialization."""
    html = generate_html("small")

    def init_parser():
        return HtmlParser(html)

    parser = benchmark(init_parser)
    assert parser.soup is not None


@pytest.mark.performance
@pytest.mark.benchmark(group="parser")
def test_parser_small_html_parsing(benchmark):
    """Benchmark parsing small HTML documents."""
    html = generate_html("small")

    def parse_html():
        parser = HtmlParser(html)
        return parser.soup.find_all("p")

    result = benchmark(parse_html)
    assert len(result) > 0


@pytest.mark.performance
@pytest.mark.benchmark(group="parser")
def test_parser_medium_html_parsing(benchmark):
    """Benchmark parsing medium HTML documents."""
    html = generate_html("medium")

    def parse_html():
        parser = HtmlParser(html)
        return parser.soup.find_all("article")

    result = benchmark(parse_html)
    assert len(result) == 100


@pytest.mark.performance
@pytest.mark.benchmark(group="parser")
def test_parser_large_html_parsing(benchmark):
    """Benchmark parsing large HTML documents."""
    html = generate_html("large")

    def parse_html():
        parser = HtmlParser(html)
        return parser.soup.find_all("tr")

    result = benchmark(parse_html)
    assert len(result) > 0


@pytest.mark.performance
@pytest.mark.benchmark(group="parser")
def test_parser_css_selector_performance(benchmark):
    """Benchmark CSS selector performance."""
    html = generate_html("medium")
    parser = HtmlParser(html)

    def select_elements():
        return parser.soup.select("article.post-50 .content p")

    result = benchmark(select_elements)
    assert result is not None


@pytest.mark.performance
@pytest.mark.benchmark(group="parser")
def test_parser_xpath_performance(benchmark):
    """Benchmark XPath selector performance using lxml."""
    html = generate_html("medium")

    def xpath_select():
        from lxml import etree

        tree = etree.HTML(html)
        return tree.xpath("//article[@class='post-50']//p")

    result = benchmark(xpath_select)
    assert result is not None


@pytest.mark.performance
@pytest.mark.benchmark(group="extraction")
def test_metadata_extraction_performance(benchmark):
    """Benchmark metadata extraction."""
    html = """
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="Test description">
        <meta name="keywords" content="test, benchmark, performance">
        <meta property="og:title" content="OG Title">
        <meta property="og:description" content="OG Description">
        <meta property="og:image" content="https://example.com/image.jpg">
    </head>
    <body><h1>Content</h1></body>
    </html>
    """

    def extract_metadata():
        parser = HtmlParser(html)
        return parser.extract_metadata()

    metadata = benchmark(extract_metadata)
    assert metadata["title"] == "Test Page"


@pytest.mark.performance
@pytest.mark.benchmark(group="extraction")
def test_link_extraction_performance(benchmark):
    """Benchmark link extraction."""
    links = []
    for i in range(100):
        links.append(f'<a href="/page{i}">Link {i}</a>')

    html = f"""
    <html>
    <body>
        <nav>{''.join(links[:50])}</nav>
        <main>{''.join(links[50:])}</main>
    </body>
    </html>
    """

    def extract_links():
        parser = HtmlParser(html)
        return parser.extract_links("https://example.com")

    result = benchmark(extract_links)
    assert len(result) == 100


@pytest.mark.performance
@pytest.mark.benchmark(group="extraction")
def test_image_extraction_performance(benchmark):
    """Benchmark image extraction."""
    images = []
    for i in range(50):
        images.append(f'<img src="/image{i}.jpg" alt="Image {i}" />')

    html = f"""
    <html>
    <body>
        <div class="gallery">
            {''.join(images)}
        </div>
    </body>
    </html>
    """

    def extract_images():
        parser = HtmlParser(html)
        return parser.extract_images("https://example.com")

    result = benchmark(extract_images)
    assert len(result) == 50


@pytest.mark.performance
@pytest.mark.benchmark(group="extraction")
def test_rule_based_extraction_performance(benchmark):
    """Benchmark rule-based data extraction."""
    html = generate_html("medium")
    parser = HtmlParser(html)

    rules = [
        ExtractionRule(name="title", selector="h1", required=False),
        ExtractionRule(name="articles", selector="article", multiple=True, required=False),
        ExtractionRule(name="tags", selector=".tag", multiple=True, required=False),
    ]

    def extract_with_rules():
        results = {}
        for rule in rules:
            results[rule.name] = parser.extract_with_rule(rule)
        return results

    result = benchmark(extract_with_rules)
    assert "title" in result
    assert "articles" in result
    assert "tags" in result


@pytest.mark.performance
@pytest.mark.benchmark(group="scraper")
@pytest.mark.asyncio
async def test_http_scraper_initialization_performance(benchmark):
    """Benchmark HTTP scraper initialization."""

    def init_scraper():
        return HttpScraper()

    scraper = benchmark(init_scraper)
    assert scraper is not None


@pytest.mark.performance
@pytest.mark.benchmark(group="scraper")
@pytest.mark.asyncio
async def test_http_request_building_performance(benchmark):
    """Benchmark HTTP request building."""
    scraper = HttpScraper()

    def build_request():
        return scraper._build_request(
            "https://example.com/page",
            headers={"Custom-Header": "Value"},
            params={"page": 1, "limit": 100},
            cookies={"session": "abc123"},
        )

    request = benchmark(build_request)
    assert request.url


@pytest.mark.performance
@pytest.mark.benchmark(group="scraper")
def test_concurrent_scraping_setup(benchmark):
    """Benchmark setup for concurrent scraping operations."""
    urls = [f"https://example.com/page{i}" for i in range(100)]

    def setup_batch():
        scraper = HttpScraper()
        scraper.config.concurrent_requests = 10
        return [(url, {}) for url in urls]

    batch = benchmark(setup_batch)
    assert len(batch) == 100


@pytest.mark.performance
@pytest.mark.benchmark(group="string")
def test_string_manipulation_performance(benchmark):
    """Benchmark string manipulation operations common in scraping."""
    text = "  This is a TEST string with    MIXED case and   extra  spaces.  " * 100

    def clean_text():
        # Common text cleaning operations
        result = text.strip()
        result = " ".join(result.split())  # Normalize whitespace
        result = result.lower()
        return result.replace("test", "benchmark")

    result = benchmark(clean_text)
    assert "benchmark" in result
    assert "  " not in result


@pytest.mark.performance
@pytest.mark.benchmark(group="string")
def test_json_parsing_performance(benchmark):
    """Benchmark JSON parsing performance."""
    import json

    data = {
        "items": [
            {
                "id": i,
                "title": f"Item {i}",
                "description": "Lorem ipsum" * 10,
                "tags": [f"tag{j}" for j in range(5)],
                "metadata": {
                    "created": f"2024-01-{i % 28 + 1:02d}",
                    "modified": f"2024-02-{i % 28 + 1:02d}",
                    "author": f"Author {i % 10}",
                },
            }
            for i in range(100)
        ]
    }
    json_str = json.dumps(data)

    def parse_json():
        return json.loads(json_str)

    result = benchmark(parse_json)
    assert len(result["items"]) == 100


@pytest.mark.performance
@pytest.mark.benchmark(group="regex")
def test_regex_performance(benchmark):
    """Benchmark regex operations commonly used in scraping."""
    import re

    html = generate_html("medium")

    # Common regex patterns for scraping
    patterns = [
        r"<h\d>(.*?)</h\d>",  # Headers
        r'class="([^"]*)"',  # Class attributes
        r"\d{4}-\d{2}-\d{2}",  # Dates
        r"post-\d+",  # IDs
    ]

    def run_regex():
        results = []
        for pattern in patterns:
            matches = re.findall(pattern, html)
            results.extend(matches)
        return results

    result = benchmark(run_regex)
    assert len(result) > 0


@pytest.mark.performance
@pytest.mark.benchmark(group="memory")
def test_large_data_handling(benchmark):
    """Benchmark handling of large data structures."""

    def create_large_dataset():
        # Simulate large scraping result
        data = []
        for i in range(1000):
            data.append(
                {
                    "url": f"https://example.com/page{i}",
                    "content": "x" * 1000,  # 1KB per item
                    "extracted": {
                        "title": f"Title {i}",
                        "body": "Lorem ipsum" * 50,
                        "metadata": {"id": i, "category": i % 10},
                    },
                }
            )
        return data

    dataset = benchmark(create_large_dataset)
    assert len(dataset) == 1000


@pytest.mark.performance
@pytest.mark.benchmark(group="cache")
def test_caching_performance(benchmark):
    """Benchmark caching operations."""
    from functools import lru_cache

    call_count = 0

    @lru_cache(maxsize=128)
    def expensive_operation(n):
        nonlocal call_count
        call_count += 1
        # Simulate expensive parsing
        return sum(i * i for i in range(n))

    def test_cache():
        results = []
        # First pass - cache misses
        for i in range(50):
            results.append(expensive_operation(i % 10))
        # Second pass - cache hits
        for i in range(50):
            results.append(expensive_operation(i % 10))
        return results, call_count

    results, count = benchmark(test_cache)
    assert len(results) == 100
    assert count <= 10  # Should only compute unique values
