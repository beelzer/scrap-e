"""Performance benchmark tests for HTML parser operations."""

import random
import string

import pytest
from lxml import etree

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
                        <p>{"".join(random.choices(string.ascii_letters + " ", k=200))}</p>
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
            <main>{"".join(items)}</main>
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
                    <tr>{"".join(f"<th>Column {i}</th>" for i in range(10))}</tr>
                </thead>
                <tbody>
                    {"".join(rows)}
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
        tree = etree.HTML(html)
        return tree.xpath("//article[@class='post-50']//p")

    result = benchmark(xpath_select)
    assert result is not None


@pytest.mark.performance
@pytest.mark.benchmark(group="parser")
def test_parser_find_vs_select_performance(benchmark):
    """Compare the performance of find methods vs. CSS selectors."""
    html = generate_html("medium")
    parser = HtmlParser(html)

    def find_method():
        return parser.soup.find_all("article", class_=lambda x: x and "post-" in x)

    result = benchmark(find_method)
    assert len(result) == 100


@pytest.mark.performance
@pytest.mark.benchmark(group="parser")
def test_parser_nested_element_navigation(benchmark):
    """Benchmark navigating nested elements."""
    html = generate_html("medium")
    parser = HtmlParser(html)

    def navigate_nested():
        results = []
        for article in parser.soup.find_all("article")[:10]:
            title = article.find("h2")
            content = article.find("div", class_="content")
            tags = article.find_all("span", class_="tag")
            results.append({"title": title, "content": content, "tags": tags})
        return results

    result = benchmark(navigate_nested)
    assert len(result) == 10


@pytest.mark.performance
@pytest.mark.benchmark(group="parser")
def test_parser_attribute_access_performance(benchmark):
    """Benchmark attribute access patterns."""
    html = generate_html("medium")
    parser = HtmlParser(html)

    def access_attributes():
        results = []
        for elem in parser.soup.find_all(class_=True)[:50]:
            results.append(
                {
                    "class": elem.get("class"),
                    "id": elem.get("id"),
                    "text": elem.get_text(strip=True)[:20],
                }
            )
        return results

    result = benchmark(access_attributes)
    assert len(result) == 50


@pytest.mark.performance
@pytest.mark.benchmark(group="parser")
def test_parser_text_extraction_performance(benchmark):
    """Benchmark text extraction from HTML."""
    html = generate_html("large")
    parser = HtmlParser(html)

    def extract_text():
        return parser.soup.get_text().strip()

    result = benchmark(extract_text)
    assert len(result) > 0


@pytest.mark.performance
@pytest.mark.benchmark(group="parser")
def test_parser_multiple_selector_types(benchmark):
    """Benchmark using multiple selector types together."""
    html = generate_html("medium")
    parser = HtmlParser(html)

    def mixed_selectors():
        return {
            "css_select": len(parser.soup.select(".tag")),
            "find_all": len(parser.soup.find_all("article")),
            "find": parser.soup.find("h1"),
            "descendants": sum(1 for _ in parser.soup.descendants),
        }

    result = benchmark(mixed_selectors)
    assert "css_select" in result
    assert "find_all" in result
