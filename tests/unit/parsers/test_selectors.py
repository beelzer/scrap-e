"""Tests for CSS and XPath selectors."""

from scrap_e.core.models import ExtractionRule
from scrap_e.scrapers.web.parser import HtmlParser
from tests.fixtures import COMPLEX_HTML


class TestCSSSelectors:
    """Test CSS selector functionality."""

    def test_css_selector_basic(self):
        """Test basic CSS selector functionality."""
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

    def test_css_selector_with_extraction_rule(self):
        """Test CSS selector with extraction rules."""
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

    def test_complex_css_selectors(self):
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

    def test_css_attribute_selectors(self):
        """Test CSS attribute selectors."""
        html = """
        <div>
            <input type="text" name="username">
            <input type="password" name="password">
            <button type="submit">Submit</button>
            <a href="/page" target="_blank">Link</a>
        </div>
        """
        parser = HtmlParser(html)

        # Attribute existence
        links = parser.soup.select("a[target]")
        assert len(links) == 1

        # Attribute value
        password_input = parser.soup.select_one("input[type='password']")
        assert password_input["name"] == "password"

        # Multiple attributes
        submit = parser.soup.select_one("button[type='submit']")
        assert submit.text == "Submit"

    def test_css_pseudo_selectors(self):
        """Test CSS pseudo-selectors."""
        html = """
        <ul>
            <li>First</li>
            <li>Second</li>
            <li>Third</li>
            <li>Fourth</li>
        </ul>
        """
        parser = HtmlParser(html)

        # First child
        first = parser.soup.select_one("li:first-child")
        assert first.text == "First"

        # Last child
        last = parser.soup.select_one("li:last-child")
        assert last.text == "Fourth"

        # Nth child
        second = parser.soup.select_one("li:nth-child(2)")
        assert second.text == "Second"


class TestXPathSelectors:
    """Test XPath selector functionality."""

    def test_xpath_basic(self):
        """Test basic XPath extraction."""
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

        # Single element text
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

    def test_xpath_attributes(self):
        """Test XPath attribute extraction."""
        html = """
        <div>
            <a href="/page1" title="Page 1">Link 1</a>
            <a href="/page2" title="Page 2">Link 2</a>
            <img src="/image.jpg" alt="Test Image">
        </div>
        """
        parser = HtmlParser(html)

        # Extract attribute directly
        rule = ExtractionRule(name="links", xpath="//a/@href", multiple=True)
        result = parser.extract_with_rule(rule)
        assert "/page1" in result
        assert "/page2" in result

        # Extract with condition
        rule_cond = ExtractionRule(name="page2_title", xpath="//a[@href='/page2']/@title")
        result = parser.extract_with_rule(rule_cond)
        assert result == "Page 2"

    def test_xpath_complex_queries(self):
        """Test complex XPath queries."""
        parser = HtmlParser(COMPLEX_HTML)

        # Following sibling
        rule = ExtractionRule(
            name="after_h2", xpath="//h2[text()='Section 1']/following-sibling::p"
        )
        result = parser.extract_with_rule(rule)
        assert "Content for section 1" in str(result)

        # Parent navigation
        rule_parent = ExtractionRule(
            name="article_content",
            xpath="//h1[@id='main-title']/parent::article//p[@class='description']",
        )
        result = parser.extract_with_rule(rule_parent)
        assert "complex test page" in str(result).lower()

        # Contains text
        rule_contains = ExtractionRule(name="views", xpath="//span[contains(text(), 'Views')]")
        result = parser.extract_with_rule(rule_contains)
        assert "Views" in str(result)

    def test_xpath_with_namespaces(self):
        """Test XPath with XML namespaces."""
        xml_html = """
        <html xmlns="http://www.w3.org/1999/xhtml">
            <body>
                <div>Regular content</div>
                <custom:element xmlns:custom="http://example.com/custom">
                    Custom content
                </custom:element>
            </body>
        </html>
        """
        parser = HtmlParser(xml_html)

        # Regular XPath should still work
        rule = ExtractionRule(name="div", xpath="//div")
        result = parser.extract_with_rule(rule)
        assert "Regular content" in str(result)
