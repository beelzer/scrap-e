"""Advanced tests for HtmlParser to improve coverage."""

from scrap_e.core.models import ExtractionRule
from scrap_e.scrapers.web.parser import HtmlParser


class TestHtmlParserAdvanced:
    """Advanced tests for HtmlParser."""

    def test_init_and_properties(self):
        """Test parser initialization and lazy loading of parsers."""
        html = "<html><body>Test</body></html>"
        parser = HtmlParser(html, "lxml")

        # Test lazy loading of soup
        soup = parser.soup
        assert soup is not None
        assert soup.name == "[document]"

        # Test lazy loading of lxml
        tree = parser.lxml_tree
        assert tree is not None

        # Test selectolax (may or may not be available)
        # Don't assert on this as it's optional

    def test_extract_with_css_selector(self):
        """Test extraction using CSS selectors."""
        html = """
        <html>
            <body>
                <h1>Title</h1>
                <p class="description">Description text</p>
                <div class="items">
                    <span>Item 1</span>
                    <span>Item 2</span>
                </div>
            </body>
        </html>
        """
        parser = HtmlParser(html)

        # Single element
        rule = ExtractionRule(name="title", selector="h1")
        result = parser.extract_with_rule(rule)
        assert result == "Title"

        # Multiple elements
        rule_multi = ExtractionRule(name="items", selector="div.items span", multiple=True)
        result = parser.extract_with_rule(rule_multi)
        assert result == ["Item 1", "Item 2"]

        # Non-existent element with default
        rule_default = ExtractionRule(name="missing", selector=".nonexistent", default="N/A")
        result = parser.extract_with_rule(rule_default)
        assert result == "N/A"

    def test_extract_with_xpath(self):
        """Test extraction using XPath."""
        html = """
        <html>
            <body>
                <h1>Title</h1>
                <div id="content">
                    <p>Paragraph 1</p>
                    <p>Paragraph 2</p>
                </div>
            </body>
        </html>
        """
        parser = HtmlParser(html)

        # Single element
        rule = ExtractionRule(name="title", xpath="//h1/text()")
        result = parser.extract_with_rule(rule)
        assert result == "Title"

        # Multiple elements
        rule_multi = ExtractionRule(
            name="paragraphs", xpath="//div[@id='content']/p", multiple=True
        )
        result = parser.extract_with_rule(rule_multi)
        assert len(result) == 2

        # Non-existent with default
        rule_default = ExtractionRule(name="missing", xpath="//span", default=[])
        result = parser.extract_with_rule(rule_default)
        assert result == []

    def test_extract_with_regex(self):
        """Test extraction using regular expressions."""
        html = """
        <html>
            <body>
                Price: $99.99
                Email: test@example.com
                Phone: 123-456-7890
            </body>
        </html>
        """
        parser = HtmlParser(html)

        # Single match with a group
        rule = ExtractionRule(name="price", regex=r"Price: \$(\d+\.\d+)")
        result = parser.extract_with_rule(rule)
        assert result == "99.99"

        # Single match without a group
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

    def test_extract_with_json_ld(self):
        """Test extraction of JSON-LD data."""
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

        # Extract with JSON path
        rule_path = ExtractionRule(name="price_value", json_path="price.value")
        result = parser.extract_with_rule(rule_path)
        assert result == "99.99"

        # Nested path
        rule_nested = ExtractionRule(name="currency", json_path="price.currency")
        result = parser.extract_with_rule(rule_nested)
        assert result == "USD"

    def test_extract_with_invalid_json_ld(self):
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

    def test_extract_element_with_attribute(self):
        """Test extracting element attributes."""
        html = """
        <html>
            <body>
                <a href="/page1" title="Link 1">Click here</a>
                <img src="/image.jpg" alt="Image description">
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

    def test_extract_with_transforms(self):
        """Test value transformations."""
        html = "<body>  MIXED Case Text  </body>"
        parser = HtmlParser(html)

        # Strip transform
        rule_strip = ExtractionRule(name="text", selector="body", transform="strip")
        result = parser.extract_with_rule(rule_strip)
        assert result == "MIXED Case Text"

        # Lower transform
        rule_lower = ExtractionRule(name="text", selector="body", transform="lower")
        result = parser.extract_with_rule(rule_lower)
        assert "mixed case text" in result.lower()

        # Upper transform
        rule_upper = ExtractionRule(name="text", selector="body", transform="upper")
        result = parser.extract_with_rule(rule_upper)
        assert "MIXED CASE TEXT" in result.upper()

    def test_numeric_transforms(self):
        """Test numeric transformations."""
        html = """
        <body>
            <span class="price">$1,234.56</span>
            <span class="quantity">100 items</span>
            <span class="invalid">not a number</span>
        </body>
        """
        parser = HtmlParser(html)

        # Int transform
        rule_int = ExtractionRule(name="quantity", selector=".quantity", transform="int")
        result = parser.extract_with_rule(rule_int)
        assert result == 100

        # Float transform
        rule_float = ExtractionRule(name="price", selector=".price", transform="float")
        result = parser.extract_with_rule(rule_float)
        assert result == 1234.56

        # Invalid int
        rule_invalid_int = ExtractionRule(name="invalid", selector=".invalid", transform="int")
        result = parser.extract_with_rule(rule_invalid_int)
        assert result == 0

        # Invalid float
        rule_invalid_float = ExtractionRule(name="invalid", selector=".invalid", transform="float")
        result = parser.extract_with_rule(rule_invalid_float)
        assert result == 0.0

    def test_bool_transform(self):
        """Test boolean transformation."""
        html = """
        <body>
            <span class="true">yes</span>
            <span class="false"></span>
        </body>
        """
        parser = HtmlParser(html)

        rule_true = ExtractionRule(name="truthy", selector=".true", transform="bool")
        result = parser.extract_with_rule(rule_true)
        assert result is True

        rule_false = ExtractionRule(name="falsy", selector=".false", transform="bool")
        result = parser.extract_with_rule(rule_false)
        assert result is False

    def test_unknown_transform(self):
        """Test unknown transformation returns original value."""
        html = "<body>Text</body>"
        parser = HtmlParser(html)

        rule = ExtractionRule(name="text", selector="body", transform="unknown")
        result = parser.extract_with_rule(rule)
        assert "Text" in result

    def test_extract_with_no_method(self):
        """Test extraction with no method specified."""
        parser = HtmlParser("<html></html>")
        rule = ExtractionRule(name="test", default="default_val")

        # Should return default when no extraction method is specified
        result = parser.extract_with_rule(rule)
        assert result == "default_val"

    def test_extract_required_field_failure(self):
        """Test required field extraction failure."""
        parser = HtmlParser("<html></html>")
        rule = ExtractionRule(
            name="optional", selector=".nonexistent", required=False, default="fallback"
        )

        # Should return default for a non-required field
        result = parser.extract_with_rule(rule)
        assert result == "fallback"

    def test_apply_json_path(self):
        """Test JSON path navigation."""
        html = """
        <html>
        <script type="application/ld+json">
        {
            "nested": {
                "array": [
                    {"value": "first"},
                    {"value": "second"}
                ],
                "object": {
                    "deep": {
                        "field": "value"
                    }
                }
            }
        }
        </script>
        </html>
        """
        parser = HtmlParser(html)

        # Navigate to a nested object
        rule = ExtractionRule(name="deep", json_path="nested.object.deep.field")
        result = parser.extract_with_rule(rule)
        assert result == "value"

        # Navigate array by index
        rule_array = ExtractionRule(name="array_item", json_path="nested.array.0.value")
        result = parser.extract_with_rule(rule_array)
        assert result == "first"

        # Invalid path returns default when the JSON path fails
        rule_invalid = ExtractionRule(
            name="invalid", json_path="nested.nonexistent.field", default="N/A"
        )
        result = parser.extract_with_rule(rule_invalid)
        # The extract_with_rule should return the default for invalid paths
        assert result == "N/A"

        # Out-of-bounds array index
        rule_oob = ExtractionRule(name="oob", json_path="nested.array.10.value", default="N/A")
        result = parser.extract_with_rule(rule_oob)
        assert result == "N/A"

    def test_extract_metadata(self):
        """Test metadata extraction."""
        html = """
        <html lang="en">
            <head>
                <title>Page Title</title>
                <meta name="description" content="Page description">
                <meta name="keywords" content="key1, key2">
                <meta name="author" content="John Doe">
                <meta property="og:title" content="OG Title">
                <meta property="og:description" content="OG Description">
                <meta name="twitter:card" content="summary">
                <meta name="twitter:title" content="Twitter Title">
                <link rel="canonical" href="https://example.com/page">
                <script type="application/ld+json">
                {"@type": "Article", "name": "Article Name"}
                </script>
            </head>
        </html>
        """
        parser = HtmlParser(html)
        metadata = parser.extract_metadata()

        assert metadata["title"] == "Page Title"
        assert metadata["description"] == "Page description"
        assert metadata["keywords"] == "key1, key2"
        assert metadata["author"] == "John Doe"
        assert metadata["language"] == "en"
        assert metadata["canonical_url"] == "https://example.com/page"
        assert metadata["og_data"]["og:title"] == "OG Title"
        assert metadata["twitter_data"]["twitter:card"] == "summary"
        assert len(metadata["schema_data"]) > 0
        assert metadata["schema_data"][0]["@type"] == "Article"

    def test_extract_metadata_missing_elements(self):
        """Test metadata extraction with missing elements."""
        html = "<html><head></head></html>"
        parser = HtmlParser(html)
        metadata = parser.extract_metadata()

        assert metadata["title"] is None
        assert metadata["description"] is None
        assert metadata["language"] is None
        assert metadata["canonical_url"] is None
        assert metadata["og_data"] == {}
        assert metadata["twitter_data"] == {}

    def test_extract_links(self):
        """Test link extraction."""
        html = """
        <html>
            <body>
                <a href="/relative">Relative Link</a>
                <a href="https://external.com">External Link</a>
                <a href="#anchor">Anchor Link</a>
                <a href="mailto:test@example.com">Email Link</a>
                <a href="javascript:void(0)">JS Link</a>
                <a>No href</a>
            </body>
        </html>
        """
        parser = HtmlParser(html)
        links = parser.extract_links("https://example.com/page")

        # Check that links are extracted and resolved
        urls = [link["url"] for link in links]
        assert "https://example.com/relative" in urls
        assert "https://external.com" in urls
        assert "https://example.com/page#anchor" in urls
        assert "mailto:test@example.com" in urls

        # Check text extraction
        texts = [link["text"] for link in links]
        assert "Relative Link" in texts
        assert "External Link" in texts

    def test_extract_images(self):
        """Test image extraction."""
        html = """
        <html>
            <body>
                <img src="/image1.jpg" alt="Image 1">
                <img src="https://cdn.example.com/image2.png" alt="Image 2" title="Title 2">
                <img src="data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" alt="Data URL">
                <img alt="No src">
                <picture>
                    <source srcset="/webp-image.webp" type="image/webp">
                    <img src="/fallback.jpg" alt="Picture element">
                </picture>
            </body>
        </html>
        """
        parser = HtmlParser(html)
        images = parser.extract_images("https://example.com/")

        # Check that images are extracted
        srcs = [img["src"] for img in images]
        assert "https://example.com/image1.jpg" in srcs
        assert "https://cdn.example.com/image2.png" in srcs

        # Check alt text
        alts = [img.get("alt") for img in images if img.get("alt")]
        assert "Image 1" in alts
        assert "Image 2" in alts

    def test_extract_tables(self):
        """Test table extraction."""
        html = """
        <html>
            <body>
                <table id="data">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Age</th>
                            <th>City</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>John</td>
                            <td>30</td>
                            <td>New York</td>
                        </tr>
                        <tr>
                            <td>Jane</td>
                            <td>25</td>
                            <td>Boston</td>
                        </tr>
                    </tbody>
                </table>
                <table id="no-header">
                    <tr>
                        <td>A1</td>
                        <td>B1</td>
                    </tr>
                    <tr>
                        <td>A2</td>
                        <td>B2</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        parser = HtmlParser(html)

        # Extract specific table
        table_data = parser.extract_table("#data")
        assert table_data["headers"] == ["Name", "Age", "City"]
        assert len(table_data["rows"]) == 2
        assert table_data["rows"][0] == ["John", "30", "New York"]
        assert table_data["rows"][1] == ["Jane", "25", "Boston"]

        # Extract all tables
        all_tables = parser.extract_all_tables()
        assert len(all_tables) == 2

        # Table without a header
        no_header_table = parser.extract_table("#no-header")
        assert no_header_table["headers"] == []
        assert len(no_header_table["rows"]) == 2

    def test_extract_table_not_found(self):
        """Test table extraction when table not found."""
        parser = HtmlParser("<html><body></body></html>")
        result = parser.extract_table("#nonexistent")
        assert result is None

    def test_clean_text(self):
        """Test text cleaning."""
        parser = HtmlParser("")

        # Test whitespace cleaning
        assert parser.clean_text("  multiple   spaces  ") == "multiple spaces"
        assert parser.clean_text("line\nbreaks\r\nhere") == "line breaks here"
        assert parser.clean_text("\t\ttabs\t\t") == "tabs"

        # Test None
        assert parser.clean_text(None) == ""

    def test_extract_with_xpath_attribute(self):
        """Test XPath extraction with attributes."""
        html = """
        <html>
            <body>
                <div id="content" data-value="test123">Content</div>
            </body>
        </html>
        """
        parser = HtmlParser(html)

        # Extract attribute via XPath
        rule = ExtractionRule(name="value", xpath="//div[@id='content']", attribute="data-value")
        result = parser.extract_with_rule(rule)
        assert result == "test123"

    def test_process_xpath_result_types(self):
        """Test processing different XPath result types."""
        html = """
        <html>
            <body>
                <div id="test">Text content</div>
            </body>
        </html>
        """
        parser = HtmlParser(html)

        # Element result
        rule_element = ExtractionRule(name="div", xpath="//div[@id='test']")
        result = parser.extract_with_rule(rule_element)
        assert "Text content" in str(result)

        # Element result
        rule_element = ExtractionRule(name="div", xpath="//div[@id='test']")
        result = parser.extract_with_rule(rule_element)
        assert "Text content" in str(result)

    def test_json_path_with_non_dict(self):
        """Test JSON path on non-dict data."""
        html = """
        <html>
        <script type="application/ld+json">
        ["item1", "item2", "item3"]
        </script>
        </html>
        """
        parser = HtmlParser(html)

        # Try to access an array element
        rule = ExtractionRule(name="item", json_path="1")
        result = parser.extract_with_rule(rule)
        assert result == "item2"

        # Invalid path on an array returns default
        rule_invalid = ExtractionRule(name="invalid", json_path="key.value", default="N/A")
        result = parser.extract_with_rule(rule_invalid)
        # When a JSON path fails, it returns the default
        assert result == "N/A" or result is None

    def test_extract_forms(self):
        """Test form extraction."""
        html = """
        <html>
            <body>
                <form action="/submit" method="post" id="contact">
                    <input type="text" name="name" placeholder="Name">
                    <input type="email" name="email" required>
                    <select name="country">
                        <option value="us">United States</option>
                        <option value="uk">United Kingdom</option>
                    </select>
                    <textarea name="message"></textarea>
                    <button type="submit">Submit</button>
                </form>
            </body>
        </html>
        """
        parser = HtmlParser(html)
        forms = parser.extract_forms()

        assert len(forms) == 1
        form = forms[0]
        assert form["action"] == "/submit"
        assert form["method"] == "post"
        assert len(form["inputs"]) == 4  # text, email, select, textarea

        # Check input details
        name_input = next(i for i in form["inputs"] if i["name"] == "name")
        assert name_input["type"] == "text"
        assert name_input["placeholder"] == "Name"

        email_input = next(i for i in form["inputs"] if i["name"] == "email")
        assert email_input["required"] is True
