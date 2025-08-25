"""Core HTML parser functionality tests."""

from scrap_e.scrapers.web.parser import HtmlParser
from tests.fixtures import EMPTY_HTML, MALFORMED_HTML


class TestHtmlParserCore:
    """Test core parser functionality."""

    def test_parser_initialization(self):
        """Test parser initialization with HTML content."""
        html = "<html><body><h1>Test</h1></body></html>"
        parser = HtmlParser(html)
        assert parser.soup is not None
        assert parser.soup.find("h1").text == "Test"

    def test_parser_with_parser_type(self):
        """Test parser initialization with different parser types."""
        html = "<html><body>Test</body></html>"

        # Test with lxml parser
        parser = HtmlParser(html, "lxml")
        assert parser.soup is not None
        assert parser.soup.name == "[document]"

        # Test lazy loading of lxml tree
        tree = parser.lxml_tree
        assert tree is not None

    def test_parser_empty_html(self):
        """Test parser with empty HTML."""
        parser = HtmlParser(EMPTY_HTML)
        assert parser.soup is not None

    def test_parser_malformed_html(self):
        """Test parser handles malformed HTML gracefully."""
        parser = HtmlParser(MALFORMED_HTML)
        assert parser.soup is not None
        # BeautifulSoup should fix the malformed HTML
        assert parser.soup.find("p") is not None

    def test_parser_with_fixtures(self, basic_html):
        """Test parser with fixture HTML."""
        parser = HtmlParser(basic_html)
        assert parser.soup is not None
        title = parser.soup.find("title")
        assert title is not None
        assert title.text == "Test Page"

    def test_parser_text_extraction(self):
        """Test text extraction from HTML."""
        html = """
        <html>
            <body>
                <div>
                    <p>Paragraph 1</p>
                    <p>Paragraph 2</p>
                </div>
            </body>
        </html>
        """
        parser = HtmlParser(html)
        text = parser.soup.get_text(strip=True)
        assert "Paragraph 1" in text
        assert "Paragraph 2" in text

    def test_parser_encoding(self):
        """Test parser handles different encodings."""
        html_with_special = "<html><body><p>Special chars: é à ü</p></body></html>"
        parser = HtmlParser(html_with_special)
        assert parser.soup is not None
        text = parser.soup.find("p").text
        assert "é" in text
        assert "à" in text
        assert "ü" in text
