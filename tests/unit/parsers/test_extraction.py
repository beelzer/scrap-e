"""Tests for content extraction methods."""

from scrap_e.core.models import ExtractionRule
from scrap_e.scrapers.web.parser import HtmlParser
from tests.fixtures import COMPLEX_HTML, FORM_HTML, TABLE_HTML


class TestMetadataExtraction:
    """Test metadata extraction methods."""

    def test_extract_basic_metadata(self):
        """Test basic metadata extraction from HTML."""
        html = """
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
            <meta name="keywords" content="test, parser">
            <meta property="og:title" content="OG Title">
            <meta property="og:description" content="OG Description">
        </head>
        <body></body>
        </html>
        """
        parser = HtmlParser(html)
        metadata = parser.extract_metadata()

        assert metadata["title"] == "Test Page"
        assert metadata["description"] == "Test description"
        assert "keywords" in metadata
        assert metadata.get("og:title") == "OG Title"

    def test_extract_complex_metadata(self):
        """Test metadata extraction from complex HTML."""
        parser = HtmlParser(COMPLEX_HTML)
        metadata = parser.extract_metadata()

        assert metadata["title"] == "Complex Test Page"
        assert metadata["description"] == "A complex test page"
        assert "test" in metadata.get("keywords", "").lower()

    def test_extract_json_ld(self):
        """Test JSON-LD extraction."""
        html = """
        <html>
            <head>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org",
                    "@type": "Product",
                    "name": "Product Name",
                    "price": {
                        "@type": "MonetaryAmount",
                        "value": "99.99",
                        "currency": "USD"
                    }
                }
                </script>
            </head>
            <body>Content</body>
        </html>
        """
        parser = HtmlParser(html)

        # Extract with JSON path to name
        rule = ExtractionRule(name="product_name", json_path="name")
        result = parser.extract_with_rule(rule)
        assert result == "Product Name"

        # Extract nested value
        rule_nested = ExtractionRule(name="price_value", json_path="price.value")
        result = parser.extract_with_rule(rule_nested)
        assert result == "99.99"

        # Extract currency
        rule_currency = ExtractionRule(name="currency", json_path="price.currency")
        result = parser.extract_with_rule(rule_currency)
        assert result == "USD"

    def test_extract_invalid_json_ld(self):
        """Test extraction with invalid JSON-LD."""
        html = """
        <html>
            <head>
                <script type="application/ld+json">
                {invalid json}
                </script>
            </head>
        </html>
        """
        parser = HtmlParser(html)

        rule = ExtractionRule(name="schema", json_path="", default={})
        result = parser.extract_with_rule(rule)
        assert result == {}


class TestContentExtraction:
    """Test various content extraction methods."""

    def test_extract_links(self):
        """Test link extraction from HTML."""
        html = """
        <html>
        <body>
            <a href="http://example.com">External Link</a>
            <a href="/internal">Internal Link</a>
            <a href="#anchor">Anchor Link</a>
            <a>Link without href</a>
            <a href="mailto:test@example.com">Email Link</a>
            <a href="tel:+123456789">Phone Link</a>
        </body>
        </html>
        """
        parser = HtmlParser(html)
        links = parser.extract_links()

        assert len(links) >= 2
        assert any(link["url"] == "http://example.com" for link in links)
        assert any(link["url"] == "/internal" for link in links)

        # Check link structure
        external_link = next((link for link in links if "example.com" in link["url"]), None)
        assert external_link is not None
        assert external_link["text"] == "External Link"

    def test_extract_images(self):
        """Test image extraction from HTML."""
        html = """
        <html>
        <body>
            <img src="/image1.jpg" alt="Test Image" title="Image Title">
            <img src="http://example.com/image2.png" alt="External Image">
            <img src="data:image/png;base64,..." alt="Data URI">
            <img alt="No source">
            <picture>
                <source srcset="/image3.webp" type="image/webp">
                <img src="/image3.jpg" alt="Picture Element">
            </picture>
        </body>
        </html>
        """
        parser = HtmlParser(html)
        images = parser.extract_images()

        assert len(images) >= 2
        assert any(img["src"] == "/image1.jpg" for img in images)
        assert any("image2.png" in img["src"] for img in images)

        # Check image attributes
        first_img = next((img for img in images if img["src"] == "/image1.jpg"), None)
        assert first_img is not None
        assert first_img["alt"] == "Test Image"

    def test_extract_tables(self):
        """Test table extraction from HTML."""
        parser = HtmlParser(TABLE_HTML)
        tables = parser.extract_tables()

        assert len(tables) == 1
        table = tables[0]

        # Check headers were extracted
        assert len(table) >= 3  # Header + at least 2 rows

        # Verify table content structure
        for row in table:
            if isinstance(row, list):
                assert len(row) == 3  # Name, Age, Email columns

    def test_extract_forms(self):
        """Test form extraction."""
        parser = HtmlParser(FORM_HTML)

        # Extract form elements
        form = parser.soup.find("form")
        assert form is not None
        assert form["action"] == "/submit"
        assert form["method"] == "post"

        # Extract input fields
        inputs = form.find_all("input")
        assert len(inputs) >= 3

        # Extract select options
        select = form.find("select")
        assert select is not None
        options = select.find_all("option")
        assert len(options) == 3

    def test_extract_structured_data(self):
        """Test structured data extraction."""
        parser = HtmlParser(COMPLEX_HTML)
        data = parser.extract_structured_data()

        # Check structure
        assert isinstance(data, dict)
        assert "metadata" in data
        assert "links" in data
        assert "images" in data
        assert "tables" in data

        # Check metadata was extracted
        assert data["metadata"]["title"] == "Complex Test Page"

        # Check links were extracted
        assert len(data["links"]) > 0
        assert any("/about" in link["url"] for link in data["links"])


class TestRegexExtraction:
    """Test regular expression extraction."""

    def test_extract_with_regex(self):
        """Test extraction using regular expressions."""
        html = """
        <html>
            <body>
                Price: $99.99
                Email: test@example.com
                Phone: 123-456-7890
                URL: https://example.com/page
            </body>
        </html>
        """
        parser = HtmlParser(html)

        # Single match with group
        rule = ExtractionRule(name="price", regex=r"Price: \$(\d+\.\d+)")
        result = parser.extract_with_rule(rule)
        assert result == "99.99"

        # Single match without group
        rule_no_group = ExtractionRule(name="email", regex=r"[a-z]+@[a-z]+\.[a-z]+")
        result = parser.extract_with_rule(rule_no_group)
        assert result == "test@example.com"

        # Multiple matches
        rule_multi = ExtractionRule(name="numbers", regex=r"\d+", multiple=True)
        result = parser.extract_with_rule(rule_multi)
        assert "99" in result
        assert "123" in result

        # No match with default
        rule_default = ExtractionRule(name="missing", regex=r"NotFound", default="N/A")
        result = parser.extract_with_rule(rule_default)
        assert result == "N/A"

    def test_extract_complex_patterns(self):
        """Test extraction with complex regex patterns."""
        html = """
        <body>
            Date: 2024-01-15
            Time: 14:30:00
            IP: 192.168.1.1
            Version: v2.1.3
            Code: ABC-123-XYZ
        </body>
        """
        parser = HtmlParser(html)

        # Date pattern
        date_rule = ExtractionRule(name="date", regex=r"\d{4}-\d{2}-\d{2}")
        result = parser.extract_with_rule(date_rule)
        assert result == "2024-01-15"

        # IP pattern
        ip_rule = ExtractionRule(name="ip", regex=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        result = parser.extract_with_rule(ip_rule)
        assert result == "192.168.1.1"

        # Version pattern with group
        version_rule = ExtractionRule(name="version", regex=r"v(\d+\.\d+\.\d+)")
        result = parser.extract_with_rule(version_rule)
        assert result == "2.1.3"


class TestAttributeExtraction:
    """Test element attribute extraction."""

    def test_extract_attributes(self):
        """Test extracting element attributes."""
        html = """
        <html>
            <body>
                <a href="/page1" title="Link 1" class="nav-link">Click here</a>
                <img src="/image.jpg" alt="Image description" width="100" height="200">
                <input type="text" name="username" value="john" required>
            </body>
        </html>
        """
        parser = HtmlParser(html)

        # Extract href attribute
        rule = ExtractionRule(name="link", selector="a", attribute="href")
        result = parser.extract_with_rule(rule)
        assert result == "/page1"

        # Extract title attribute
        rule_title = ExtractionRule(name="link_title", selector="a", attribute="title")
        result = parser.extract_with_rule(rule_title)
        assert result == "Link 1"

        # Extract img dimensions
        rule_width = ExtractionRule(name="img_width", selector="img", attribute="width")
        result = parser.extract_with_rule(rule_width)
        assert result == "100"

        # Extract input value
        rule_value = ExtractionRule(name="username", selector="input", attribute="value")
        result = parser.extract_with_rule(rule_value)
        assert result == "john"

    def test_extract_data_attributes(self):
        """Test extracting data-* attributes."""
        html = """
        <div data-id="123" data-name="test" data-config='{"key": "value"}'>
            Content
        </div>
        """
        parser = HtmlParser(html)

        # Extract data-id
        rule = ExtractionRule(name="id", selector="div", attribute="data-id")
        result = parser.extract_with_rule(rule)
        assert result == "123"

        # Extract data-config (JSON string)
        rule_config = ExtractionRule(name="config", selector="div", attribute="data-config")
        result = parser.extract_with_rule(rule_config)
        assert '{"key": "value"}' in result
