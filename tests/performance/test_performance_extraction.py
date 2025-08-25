"""Performance benchmark tests for data extraction operations."""

import json
import random
import string

import pytest

from scrap_e.core.models import ExtractionRule
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
        <meta property="og:url" content="https://example.com">
        <meta property="og:type" content="website">
        <meta name="author" content="Test Author">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="robots" content="index, follow">
        <meta http-equiv="content-type" content="text/html; charset=utf-8">
    </head>
    <body><h1>Content</h1></body>
    </html>
    """

    def extract_metadata():
        parser = HtmlParser(html)
        return parser.extract_metadata()

    metadata = benchmark(extract_metadata)
    assert metadata["title"] == "Test Page"
    assert "description" in metadata
    assert "og:title" in metadata


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
        <nav>{"".join(links[:50])}</nav>
        <main>{"".join(links[50:])}</main>
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
            {"".join(images)}
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
        ExtractionRule(name="dates", selector=".meta", multiple=True, required=False),
        ExtractionRule(name="content", selector=".content p", multiple=True, required=False),
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
@pytest.mark.benchmark(group="extraction")
def test_complex_extraction_performance(benchmark):
    """Benchmark complex data extraction with nested structures."""
    html = generate_html("medium")
    parser = HtmlParser(html)

    def complex_extraction():
        results = []
        for article in parser.soup.find_all("article")[:20]:
            item = {
                "title": article.find("h2").get_text(strip=True) if article.find("h2") else None,
                "date": article.find("p", class_="meta").get_text(strip=True)
                if article.find("p", class_="meta")
                else None,
                "content": article.find("div", class_="content").get_text(strip=True)
                if article.find("div", class_="content")
                else None,
                "tags": [
                    tag.get_text(strip=True) for tag in article.find_all("span", class_="tag")
                ],
            }
            results.append(item)
        return results

    result = benchmark(complex_extraction)
    assert len(result) == 20
    assert all("title" in item for item in result)


@pytest.mark.performance
@pytest.mark.benchmark(group="extraction")
def test_attribute_extraction_performance(benchmark):
    """Benchmark extracting attributes from elements."""
    html = f"""
    <html>
    <body>
        {"".join(f'<div id="item-{i}" class="item type-{i % 5}" data-value="{i}" data-category="cat-{i % 10}">Item {i}</div>' for i in range(100))}
    </body>
    </html>
    """
    parser = HtmlParser(html)

    def extract_attributes():
        results = []
        for elem in parser.soup.find_all("div", class_="item"):
            results.append(
                {
                    "id": elem.get("id"),
                    "class": elem.get("class"),
                    "data-value": elem.get("data-value"),
                    "data-category": elem.get("data-category"),
                    "text": elem.get_text(strip=True),
                }
            )
        return results

    result = benchmark(extract_attributes)
    assert len(result) == 100


@pytest.mark.performance
@pytest.mark.benchmark(group="extraction")
def test_table_extraction_performance(benchmark):
    """Benchmark extracting data from HTML tables."""
    html = generate_html("large")
    parser = HtmlParser(html)

    def extract_table_data():
        table = parser.soup.find("table")
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        rows = []
        for tr in table.find_all("tr")[:100]:  # First 100 rows
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if cells:
                rows.append(cells)
        return {"headers": headers, "rows": rows}

    result = benchmark(extract_table_data)
    assert len(result["headers"]) == 10
    assert (
        len(result["rows"]) >= 99
    )  # Should have at least 99 rows (might be 100 or 99 depending on parsing)


@pytest.mark.performance
@pytest.mark.benchmark(group="extraction")
def test_form_data_extraction_performance(benchmark):
    """Benchmark extracting form data."""
    forms = []
    for i in range(20):
        forms.append(f"""
        <form id="form-{i}" action="/submit-{i}" method="post">
            <input type="text" name="field1-{i}" value="value1">
            <input type="email" name="field2-{i}" value="test@example.com">
            <select name="field3-{i}">
                <option value="opt1">Option 1</option>
                <option value="opt2" selected>Option 2</option>
            </select>
            <textarea name="field4-{i}">Text content</textarea>
            <button type="submit">Submit</button>
        </form>
        """)

    html = f"""
    <html>
    <body>
        {"".join(forms)}
    </body>
    </html>
    """
    parser = HtmlParser(html)

    def extract_forms():
        results: list[dict] = []
        for form in parser.soup.find_all("form"):
            form_data: dict = {
                "id": form.get("id"),
                "action": form.get("action"),
                "method": form.get("method"),
                "fields": [],
            }
            for input_elem in form.find_all(["input", "select", "textarea"]):
                field: dict = {
                    "name": input_elem.get("name"),
                    "type": input_elem.get("type", input_elem.name),
                    "value": input_elem.get("value"),
                }
                form_data["fields"].append(field)
            results.append(form_data)
        return results

    result = benchmark(extract_forms)
    assert len(result) == 20


@pytest.mark.performance
@pytest.mark.benchmark(group="extraction")
def test_structured_data_extraction_performance(benchmark):
    """Benchmark extracting structured data (JSON-LD, microdata)."""
    html = """
    <html>
    <head>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Product Name",
            "description": "Product description",
            "price": "99.99",
            "priceCurrency": "USD"
        }
        </script>
    </head>
    <body>
        <div itemscope itemtype="https://schema.org/Person">
            <span itemprop="name">John Doe</span>
            <span itemprop="jobTitle">Software Engineer</span>
        </div>
    </body>
    </html>
    """

    def extract_structured():
        parser = HtmlParser(html)
        results = {
            "json_ld": [],
            "microdata": [],
        }

        # Extract JSON-LD
        for script in parser.soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                results["json_ld"].append(data)
            except (json.JSONDecodeError, TypeError, AttributeError):
                pass

        # Extract microdata
        for elem in parser.soup.find_all(attrs={"itemscope": True}):
            item = {"type": elem.get("itemtype"), "properties": {}}
            for prop in elem.find_all(attrs={"itemprop": True}):
                item["properties"][prop.get("itemprop")] = prop.get_text(strip=True)
            results["microdata"].append(item)

        return results

    result = benchmark(extract_structured)
    assert len(result["json_ld"]) > 0
    assert len(result["microdata"]) > 0


@pytest.mark.performance
@pytest.mark.benchmark(group="extraction")
def test_parallel_extraction_simulation(benchmark):
    """Benchmark simulated parallel extraction operations."""
    html = generate_html("medium")
    parser = HtmlParser(html)

    def parallel_extraction():
        # Simulate extracting different data types in parallel
        return {
            "links": parser.extract_links("https://example.com"),
            "images": parser.extract_images("https://example.com"),
            "metadata": parser.extract_metadata(),
            "articles": [a.get_text(strip=True)[:50] for a in parser.soup.find_all("article")[:10]],
            "tags": [t.get_text(strip=True) for t in parser.soup.find_all(".tag")],
        }

    result = benchmark(parallel_extraction)
    assert all(key in result for key in ["links", "images", "metadata", "articles", "tags"])
