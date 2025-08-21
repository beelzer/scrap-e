"""HTML parsing utilities for web scraping."""

import json
import re
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from lxml import html

if TYPE_CHECKING:
    from selectolax.parser import HTMLParser

try:
    from selectolax.parser import HTMLParser

    SELECTOLAX_AVAILABLE = True
except ImportError:
    SELECTOLAX_AVAILABLE = False

from scrap_e.core.exceptions import ParsingError
from scrap_e.core.models import ExtractionRule


class HtmlParser:
    """Advanced HTML parser with multiple backend support."""

    def __init__(self, html_content: str, parser_type: str = "lxml") -> None:
        self.html_content = html_content
        self.parser_type = parser_type
        self._soup: BeautifulSoup | None = None
        self._lxml_tree: Any | None = None
        self._selectolax_tree: Any | None = None

    @property
    def soup(self) -> BeautifulSoup:
        """Get BeautifulSoup parser instance."""
        if self._soup is None:
            self._soup = BeautifulSoup(self.html_content, self.parser_type)
        return self._soup

    @property
    def lxml_tree(self) -> Any:
        """Get lxml parser instance."""
        if self._lxml_tree is None:
            self._lxml_tree = html.fromstring(self.html_content)
        return self._lxml_tree

    @property
    def selectolax_tree(self) -> Any | None:
        """Get selectolax parser instance."""
        if not SELECTOLAX_AVAILABLE:
            return None
        if self._selectolax_tree is None:
            self._selectolax_tree = HTMLParser(self.html_content)
        return self._selectolax_tree

    def extract_with_rule(self, rule: ExtractionRule) -> Any:
        """
        Extract data using an extraction rule.

        Args:
            rule: Extraction rule to apply

        Returns:
            Extracted data based on the rule
        """
        try:
            if rule.selector:
                return self._extract_css(rule)
            if rule.xpath:
                return self._extract_xpath(rule)
            if rule.regex:
                return self._extract_regex(rule)
            if rule.json_path:
                return self._extract_json(rule)
            raise ParsingError(f"No extraction method specified in rule: {rule.name}")
        except Exception as e:
            if rule.required:
                raise ParsingError(f"Failed to extract required field '{rule.name}': {e!s}") from e
            return rule.default

    def _extract_css(self, rule: ExtractionRule) -> Any:
        """Extract using CSS selector."""
        if rule.selector is None:
            return rule.default
        if rule.multiple:
            elements = self.soup.select(rule.selector)
            return [self._extract_element_data(el, rule) for el in elements]
        element = self.soup.select_one(rule.selector)
        if element:
            return self._extract_element_data(element, rule)
        return rule.default

    def _extract_xpath(self, rule: ExtractionRule) -> Any:
        """Extract using XPath."""
        results = self.lxml_tree.xpath(rule.xpath)

        if not results:
            return rule.default

        if rule.multiple:
            return [self._process_xpath_result(r, rule) for r in results]
        return self._process_xpath_result(results[0], rule)

    def _extract_regex(self, rule: ExtractionRule) -> Any:
        """Extract using regular expression."""
        if rule.regex is None:
            return rule.default
        pattern = re.compile(rule.regex)

        if rule.multiple:
            matches = pattern.findall(self.html_content)
            return matches if matches else rule.default
        match = pattern.search(self.html_content)
        return (
            match.group(1)
            if match and match.groups()
            else (match.group(0) if match else rule.default)
        )

    def _extract_json(self, rule: ExtractionRule) -> Any:
        """Extract JSON-LD or inline JSON data."""
        # Look for JSON-LD scripts
        json_scripts = self.soup.find_all("script", type="application/ld+json")

        for script in json_scripts:
            try:
                data = json.loads(script.string)
                # Apply JSON path if specified
                if rule.json_path:
                    result = self._apply_json_path(data, rule.json_path)
                    if result is None:
                        continue  # Try next JSON script
                    return result
                return data
            except json.JSONDecodeError:
                continue

        return rule.default

    def _extract_element_data(self, element: Tag, rule: ExtractionRule) -> Any:
        """Extract data from a BeautifulSoup element."""
        value = element.get(rule.attribute) if rule.attribute else element.get_text(strip=True)

        if rule.transform:
            value = self._apply_transform(value, rule.transform)

        return value

    def _process_xpath_result(self, result: Any, rule: ExtractionRule) -> Any:
        """Process XPath result."""
        if isinstance(result, str):
            value = result
        elif hasattr(result, "text"):
            value = result.get(rule.attribute) if rule.attribute else result.text
        else:
            value = str(result)

        if rule.transform:
            value = self._apply_transform(value, rule.transform)

        return value

    def _apply_transform(self, value: Any, transform: str) -> Any:
        """Apply transformation to extracted value."""
        # String transformations
        if transform in {"strip", "lower", "upper"} and isinstance(value, str):
            return getattr(value, transform)()

        # Type conversions
        if transform == "int":
            try:
                return int(re.sub(r"[^\d-]", "", str(value)))
            except ValueError:
                return 0
        if transform == "float":
            try:
                return float(re.sub(r"[^\d.-]", "", str(value)))
            except ValueError:
                return 0.0
        if transform == "bool":
            return bool(value)

        return value

    def _apply_json_path(self, data: dict[str, Any], path: str) -> Any:
        """Apply JSON path to extract nested data."""
        keys = path.split(".")
        result = data

        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)  # type: ignore[assignment]
            elif isinstance(result, list) and key.isdigit():
                idx = int(key)
                result = result[idx] if idx < len(result) else None
            else:
                return None

            if result is None:
                return None

        return result

    def extract_metadata(self) -> dict[str, Any]:
        """Extract common metadata from HTML."""
        metadata: dict[str, Any] = {
            "title": None,
            "description": None,
            "keywords": None,
            "author": None,
            "language": None,
            "canonical_url": None,
            "og_data": {},
            "twitter_data": {},
            "schema_data": [],
        }

        # Title
        title_tag = self.soup.find("title")
        if title_tag:
            metadata["title"] = title_tag.get_text(strip=True)

        # Meta tags
        for meta in self.soup.find_all("meta"):
            name = meta.get("name", "").lower()
            property = meta.get("property", "").lower()
            content = meta.get("content", "")

            if name == "description":
                metadata["description"] = content
            elif name == "keywords":
                metadata["keywords"] = content
            elif name == "author":
                metadata["author"] = content
            elif property.startswith("og:"):
                metadata["og_data"][property] = content
            elif name.startswith("twitter:"):
                metadata["twitter_data"][name] = content

        # Language
        html_tag = self.soup.find("html")
        if html_tag and isinstance(html_tag, Tag):
            metadata["language"] = html_tag.get("lang")

        # Canonical URL
        canonical = self.soup.find("link", rel="canonical")
        if canonical and isinstance(canonical, Tag):
            metadata["canonical_url"] = canonical.get("href")

        # Schema.org data
        json_scripts = self.soup.find_all("script", type="application/ld+json")
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                metadata["schema_data"].append(data)
            except json.JSONDecodeError:
                continue

        return metadata

    def extract_links(self, absolute_url: str | None = None) -> list[dict[str, str]]:
        """Extract all links from HTML."""
        links = []
        for link in self.soup.find_all("a", href=True):
            href = link["href"]
            if absolute_url:
                href = urljoin(absolute_url, href)

            links.append(
                {
                    "url": href,
                    "text": link.get_text(strip=True),
                    "title": link.get("title", ""),
                }
            )

        return links

    def extract_images(self, absolute_url: str | None = None) -> list[dict[str, str]]:
        """Extract all images from HTML."""
        images = []
        for img in self.soup.find_all("img"):
            src = img.get("src", "")
            if absolute_url and src:
                src = urljoin(absolute_url, src)

            images.append(
                {
                    "src": src,
                    "alt": img.get("alt", ""),
                    "title": img.get("title", ""),
                    "width": img.get("width", ""),
                    "height": img.get("height", ""),
                }
            )

        return images

    def extract_forms(self) -> list[dict[str, Any]]:
        """Extract form data from HTML."""
        forms = []

        for form in self.soup.find_all("form"):
            form_data = {
                "action": form.get("action", ""),
                "method": form.get("method", "get").lower(),
                "id": form.get("id"),
                "inputs": [],
            }

            # Extract all input fields
            for input_elem in form.find_all(["input", "select", "textarea"]):
                input_data = {
                    "type": (
                        input_elem.get("type", "text")
                        if input_elem.name == "input"
                        else input_elem.name
                    ),
                    "name": input_elem.get("name"),
                    "id": input_elem.get("id"),
                    "value": input_elem.get("value"),
                    "placeholder": input_elem.get("placeholder"),
                    "required": input_elem.get("required") is not None,
                }

                # For select elements, get options
                if input_elem.name == "select":
                    options = [
                        {
                            "value": option.get("value", option.text),
                            "text": option.text,
                        }
                        for option in input_elem.find_all("option")
                    ]
                    input_data["options"] = options

                form_data["inputs"].append(input_data)

            forms.append(form_data)

        return forms

    def extract_table(self, selector: str) -> dict[str, Any] | None:
        """Extract table data from HTML."""
        table = self.soup.select_one(selector)
        if not table:
            return None

        return self._parse_table(table)

    def extract_all_tables(self) -> list[dict[str, Any]]:
        """Extract all tables from HTML."""
        return [self._parse_table(table) for table in self.soup.find_all("table")]

    def _parse_table(self, table: Tag) -> dict[str, Any]:
        """Parse a table element into structured data."""
        headers = []
        rows = []

        # Extract headers
        thead = table.find("thead")
        if thead:
            header_row = thead.find("tr")
            if header_row and isinstance(header_row, Tag):
                headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
        else:
            # Try to find headers in first row
            first_row = table.find("tr")
            if first_row and isinstance(first_row, Tag) and first_row.find("th"):
                headers = [th.get_text(strip=True) for th in first_row.find_all("th")]

        # Extract rows
        tbody = table.find("tbody") or table
        if isinstance(tbody, Tag):
            for tr in tbody.find_all("tr"):
                # Skip header row if it contains th elements
                if tr.find("th") and not tbody:
                    continue
                row = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if row:  # Only add non-empty rows
                    rows.append(row)

        return {"headers": headers, "rows": rows}

    def clean_text(self, text: str | None) -> str:
        """Clean and normalize text."""
        if text is None:
            return ""

        # Replace multiple whitespaces with single space
        text = re.sub(r"\s+", " ", text)
        # Strip leading/trailing whitespace
        return text.strip()

    def extract_tables(self) -> list[list[dict[str, Any]]]:
        """Extract all tables as structured data."""
        tables = []

        for table in self.soup.find_all("table"):
            headers = []
            rows = []

            # Extract headers
            thead = table.find("thead")
            if thead:
                header_row = thead.find("tr")
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]

            # If no thead, try first row
            if not headers:
                first_row = table.find("tr")
                if first_row:
                    potential_headers = first_row.find_all("th")
                    if potential_headers:
                        headers = [th.get_text(strip=True) for th in potential_headers]

            # Extract rows
            tbody = table.find("tbody") or table
            for tr in tbody.find_all("tr"):
                cells = tr.find_all(["td", "th"])
                if headers and len(cells) == len(headers):
                    row: dict[str, Any] | list[Any] = {
                        headers[i]: cell.get_text(strip=True) for i, cell in enumerate(cells)
                    }
                else:
                    row = [cell.get_text(strip=True) for cell in cells]

                if row:
                    rows.append(row)

            if rows:
                tables.append(rows)

        return tables

    def extract_structured_data(self) -> dict[str, Any]:
        """Extract all structured data from the page."""
        return {
            "metadata": self.extract_metadata(),
            "links": self.extract_links(),
            "images": self.extract_images(),
            "tables": self.extract_tables(),
        }
