"""Unit tests for data models."""

from pydantic import BaseModel

from scrap_e.core.models import (
    ExtractionRule,
    ScraperMetadata,
    ScraperResult,
    ScraperType,
)


class DataModelForTesting(BaseModel):
    """Test data model."""

    content: str
    value: int = 0


class TestExtractionRule:
    """Tests for ExtractionRule model."""

    def test_extraction_rule_creation(self):
        """Test extraction rule creation with basic fields."""
        rule = ExtractionRule(name="test", selector="h1", required=False)
        assert rule.name == "test"
        assert rule.selector == "h1"
        assert rule.required is False

    def test_extraction_rule_defaults(self):
        """Test extraction rule default values."""
        rule = ExtractionRule(name="test", selector="h1")
        assert rule.required is False  # Default should be False
        assert rule.transform is None
        assert rule.multiple is False


class TestScraperMetadata:
    """Tests for ScraperMetadata model."""

    def test_scraper_metadata_creation(self):
        """Test scraper metadata creation."""
        metadata = ScraperMetadata(
            scraper_type=ScraperType.WEB_HTTP,
            source="http://test.com",
            records_scraped=10,
        )
        assert metadata.scraper_type == ScraperType.WEB_HTTP
        assert metadata.source == "http://test.com"
        assert metadata.records_scraped == 10

    def test_scraper_metadata_optional_fields(self):
        """Test scraper metadata with optional fields."""
        metadata = ScraperMetadata(
            scraper_type=ScraperType.WEB_BROWSER,
            source="http://example.com",
        )
        assert metadata.scraper_type == ScraperType.WEB_BROWSER
        assert metadata.source == "http://example.com"
        assert metadata.records_scraped == 0  # Default value


class TestScraperResult:
    """Tests for ScraperResult model."""

    def test_scraper_result_success(self):
        """Test successful scraper result."""
        metadata = ScraperMetadata(scraper_type=ScraperType.WEB_HTTP, source="http://test.com")
        result = ScraperResult(success=True, data={"test": "data"}, metadata=metadata)
        assert result.success is True
        assert result.data == {"test": "data"}
        assert result.metadata == metadata
        assert result.error is None

    def test_scraper_result_failure(self):
        """Test failed scraper result."""
        metadata = ScraperMetadata(scraper_type=ScraperType.WEB_HTTP, source="http://test.com")
        result = ScraperResult(
            success=False, data=None, metadata=metadata, error="Connection timeout"
        )
        assert result.success is False
        assert result.data is None
        assert result.error == "Connection timeout"


class TestCustomModels:
    """Tests for custom data models."""

    def test_custom_model_creation(self):
        """Test custom model instantiation."""
        model = DataModelForTesting(content="test content", value=42)
        assert model.content == "test content"
        assert model.value == 42

    def test_custom_model_defaults(self):
        """Test custom model with default values."""
        model = DataModelForTesting(content="test")
        assert model.content == "test"
        assert model.value == 0  # Default value
