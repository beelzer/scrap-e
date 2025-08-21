"""Pydantic models for data validation and serialization."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, ValidationInfo, field_validator

T = TypeVar("T")


class ScraperType(str, Enum):
    """Types of scrapers available."""

    WEB_HTTP = "web_http"
    WEB_BROWSER = "web_browser"
    API_REST = "api_rest"
    API_GRAPHQL = "api_graphql"
    API_WEBSOCKET = "api_websocket"
    DATABASE_SQL = "database_sql"
    DATABASE_NOSQL = "database_nosql"
    FILE_CSV = "file_csv"
    FILE_JSON = "file_json"
    FILE_XML = "file_xml"
    FILE_EXCEL = "file_excel"
    FILE_PDF = "file_pdf"


class DataFormat(str, Enum):
    """Output data formats."""

    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    EXCEL = "excel"
    SQL = "sql"
    MONGODB = "mongodb"


class RequestMethod(str, Enum):
    """HTTP request methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthType(str, Enum):
    """Authentication types."""

    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    COOKIES = "cookies"
    JWT = "jwt"


class ScraperMetadata(BaseModel):
    """Metadata for scraping operations."""

    model_config = ConfigDict(extra="allow")

    scraper_type: ScraperType
    source: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    duration_seconds: float | None = None
    records_scraped: int = 0
    errors_count: int = 0
    warnings: list[str] = Field(default_factory=list)
    tags: dict[str, Any] = Field(default_factory=dict)


class ScraperResult[T](BaseModel):
    """Generic result container for scraped data."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool
    data: T | None = None
    error: str | None = None
    metadata: ScraperMetadata
    raw_response: Any | None = Field(default=None, exclude=True)


class HttpRequest(BaseModel):
    """HTTP request configuration."""

    url: HttpUrl
    method: RequestMethod = RequestMethod.GET
    headers: dict[str, str] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    data: dict[str, Any] | str | None = None
    json_data: dict[str, Any] | None = None
    timeout: float = 30.0
    follow_redirects: bool = True
    verify_ssl: bool = True
    proxies: dict[str, str] | None = None
    cookies: dict[str, str] | None = None
    auth_type: AuthType = AuthType.NONE
    auth_credentials: dict[str, str] | None = None

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Timeout must be positive")
        if v > 300:
            raise ValueError("Timeout cannot exceed 300 seconds")
        return v


class DatabaseConnection(BaseModel):
    """Database connection configuration."""

    host: str
    port: int
    database: str
    username: str | None = None
    password: str | None = None
    driver: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)
    pool_size: int = 5
    max_overflow: int = 10
    timeout: float = 30.0


class ExtractionRule(BaseModel):
    """Rule for extracting data from sources."""

    name: str
    selector: str | None = None
    xpath: str | None = None
    regex: str | None = None
    json_path: str | None = None
    attribute: str | None = None
    transform: str | None = None
    default: Any = None
    required: bool = False
    multiple: bool = False

    @field_validator("selector", "xpath", "regex", "json_path")
    @classmethod
    def validate_extraction_method(cls, v: str | None, info: ValidationInfo) -> str | None:
        if v is None:
            return v
        field_name = info.field_name
        if field_name in ["selector", "xpath"] and not v.strip():
            raise ValueError(f"{field_name} cannot be empty")
        return v


class PaginationConfig(BaseModel):
    """Configuration for handling pagination."""

    enabled: bool = False
    max_pages: int | None = None
    page_param: str = "page"
    page_size_param: str = "page_size"
    page_size: int = 100
    start_page: int = 1
    next_page_selector: str | None = None
    next_page_url_pattern: str | None = None
    stop_condition: str | None = None


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""

    enabled: bool = True
    requests_per_second: float = 10.0
    requests_per_minute: int | None = None
    requests_per_hour: int | None = None
    burst_size: int = 10
    retry_after_header: str = "Retry-After"


class CacheConfig(BaseModel):
    """Cache configuration."""

    enabled: bool = True
    backend: str = "memory"
    ttl_seconds: int = 3600
    max_size_mb: int = 100
    cache_key_prefix: str = "scraper"
    serialize_format: str = "pickle"


class RetryConfig(BaseModel):
    """Retry configuration."""

    enabled: bool = True
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_status_codes: list[int] = Field(default_factory=lambda: [429, 500, 502, 503, 504])


class ProxyConfig(BaseModel):
    """Proxy configuration."""

    enabled: bool = False
    proxy_list: list[str] = Field(default_factory=list)
    rotation_enabled: bool = True
    authentication: dict[str, str] | None = None
    test_url: HttpUrl | None = None


class ScraperStats(BaseModel):
    """Statistics for scraping operations."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_bytes: int = 0
    total_duration: float = 0.0
    average_response_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    retries: int = 0
    rate_limited: int = 0
