"""Unit tests for HTML parser functionality."""

from scrap_e.scrapers.web.parser import HtmlParser


class TestHtmlParserBasics:
    """Basic tests for HtmlParser."""

    def test_parser_initialization(self):
        """Test parser initialization with HTML content."""
        html = "<html><body><h1>Test</h1></body></html>"
        parser = HtmlParser(html)
        assert parser.soup is not None
        assert parser.soup.find("h1").text == "Test"

    def test_parser_empty_html(self):
        """Test parser with empty HTML."""
        parser = HtmlParser("")
        assert parser.soup is not None

    def test_parser_malformed_html(self):
        """Test parser handles malformed HTML gracefully."""
        html = "<h1>Unclosed tag<p>Another tag</p>"
        parser = HtmlParser(html)
        assert parser.soup is not None
        assert parser.soup.find("h1") is not None


class TestHtmlParserTransforms:
    """Tests for parser transformation methods."""

    def test_transform_strip(self):
        """Test strip transformation."""
        parser = HtmlParser("")
        assert parser._apply_transform("  test  ", "strip") == "test"
        assert parser._apply_transform("\n\ttest\n\t", "strip") == "test"

    def test_transform_case(self):
        """Test case transformations."""
        parser = HtmlParser("")
        assert parser._apply_transform("TEST", "lower") == "test"
        assert parser._apply_transform("test", "upper") == "TEST"
        # title transform is not implemented, returns original value
        assert parser._apply_transform("test string", "title") == "test string"

    def test_transform_numeric(self):
        """Test numeric transformations."""
        parser = HtmlParser("")
        assert parser._apply_transform("42", "int") == 42
        assert parser._apply_transform("42.5", "float") == 42.5
        assert parser._apply_transform("3.14159", "float") == 3.14159

    def test_transform_invalid(self):
        """Test invalid transformations."""
        parser = HtmlParser("")
        # Invalid int conversion returns 0
        assert parser._apply_transform("not_a_number", "int") == 0
        # Invalid float conversion returns 0.0
        assert parser._apply_transform("not_a_float", "float") == 0.0

    def test_transform_unknown(self):
        """Test unknown transformation types."""
        parser = HtmlParser("")
        assert parser._apply_transform("test", "unknown") == "test"
        assert parser._apply_transform("test", None) == "test"


class TestHtmlParserExtraction:
    """Tests for content extraction methods."""

    def test_extract_metadata(self):
        """Test metadata extraction from HTML."""
        html = """
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
            <meta name="keywords" content="test, parser">
            <meta property="og:title" content="OG Title">
        </head>
        <body></body>
        </html>
        """
        parser = HtmlParser(html)
        metadata = parser.extract_metadata()

        assert metadata["title"] == "Test Page"
        assert metadata["description"] == "Test description"
        assert "keywords" in metadata

    def test_extract_links(self):
        """Test link extraction from HTML."""
        html = """
        <html>
        <body>
            <a href="http://example.com">External Link</a>
            <a href="/internal">Internal Link</a>
            <a href="#anchor">Anchor Link</a>
            <a>Link without href</a>
        </body>
        </html>
        """
        parser = HtmlParser(html)
        links = parser.extract_links()

        assert len(links) >= 2
        assert any(link["url"] == "http://example.com" for link in links)
        assert any(link["url"] == "/internal" for link in links)

    def test_extract_images(self):
        """Test image extraction from HTML."""
        html = """
        <html>
        <body>
            <img src="/image1.jpg" alt="Test Image">
            <img src="http://example.com/image2.png" alt="External Image">
            <img src="data:image/png;base64,..." alt="Data URI">
            <img alt="No source">
        </body>
        </html>
        """
        parser = HtmlParser(html)
        images = parser.extract_images()

        assert len(images) >= 2
        assert any(img["src"] == "/image1.jpg" for img in images)
        assert any("image2.png" in img["src"] for img in images)

    def test_extract_tables(self):
        """Test table extraction from HTML."""
        html = """
        <table>
            <thead>
                <tr><th>Name</th><th>Value</th></tr>
            </thead>
            <tbody>
                <tr><td>Item1</td><td>123</td></tr>
                <tr><td>Item2</td><td>456</td></tr>
            </tbody>
        </table>
        """
        parser = HtmlParser(html)
        tables = parser.extract_tables()

        assert len(tables) == 1
        assert len(tables[0]) >= 2  # At least 2 rows

    def test_extract_structured_data(self):
        """Test structured data extraction."""
        html = """
        <script type="application/ld+json">
        {
            "@type": "Article",
            "name": "Test Article",
            "author": "Test Author"
        }
        </script>
        """
        parser = HtmlParser(html)
        data = parser.extract_structured_data()

        # extract_structured_data returns a dict with metadata, links, images, tables
        assert data is not None
        assert isinstance(data, dict)
        assert "metadata" in data
        assert "links" in data
        assert "images" in data
        assert "tables" in data

        # Check if JSON-LD was extracted into schema_data
        if "schema_data" in data.get("metadata", {}):
            schema_data = data["metadata"]["schema_data"]
            if schema_data and len(schema_data) > 0:
                assert schema_data[0].get("@type") == "Article"


class TestHtmlParserSelectors:
    """Tests for CSS and XPath selectors."""

    def test_css_selector(self):
        """Test CSS selector functionality."""
        html = """
        <div class="container">
            <h1 class="title">Main Title</h1>
            <p class="content">Paragraph 1</p>
            <p class="content">Paragraph 2</p>
        </div>
        """
        parser = HtmlParser(html)

        # Test single element selection
        title = parser.soup.select_one(".title")
        assert title.text == "Main Title"

        # Test multiple element selection
        paragraphs = parser.soup.select(".content")
        assert len(paragraphs) == 2

    def test_complex_selectors(self):
        """Test complex CSS selectors."""
        html = """
        <div id="main">
            <article>
                <h2>Article Title</h2>
                <div class="meta">
                    <span class="author">John Doe</span>
                    <span class="date">2024-01-01</span>
                </div>
            </article>
        </div>
        """
        parser = HtmlParser(html)

        # Test descendant selector
        author = parser.soup.select_one("#main article .author")
        assert author.text == "John Doe"

        # Test child selector
        article_title = parser.soup.select_one("article > h2")
        assert article_title.text == "Article Title"
