"""Configuration management for the scraper framework."""

import json
import tempfile
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from scrap_e.core.models import (
    AuthType,
    CacheConfig,
    DataFormat,
    PaginationConfig,
    ProxyConfig,
    RateLimitConfig,
    RetryConfig,
    ScraperType,
)


class ScraperConfig(BaseSettings):
    """Main configuration for the scraper."""

    model_config = SettingsConfigDict(
        env_prefix="SCRAPER_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # General settings
    name: str = "universal-scraper"
    debug: bool = False
    log_level: str = "INFO"
    output_dir: Path = Path("./data")
    temp_dir: Path = Field(default_factory=lambda: Path(tempfile.gettempdir()) / "scraper")
    max_workers: int = 10
    async_enabled: bool = True

    # Default scraper type
    default_scraper_type: ScraperType = ScraperType.WEB_HTTP

    # Output settings
    output_format: DataFormat = DataFormat.JSON
    pretty_print: bool = True
    compress_output: bool = False

    # Network settings
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    default_timeout: float = 30.0
    verify_ssl: bool = True
    follow_redirects: bool = True
    max_redirects: int = 10

    # Rate limiting
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)

    # Retry configuration
    retry: RetryConfig = Field(default_factory=RetryConfig)

    # Cache configuration
    cache: CacheConfig = Field(default_factory=CacheConfig)

    # Proxy configuration
    proxy: ProxyConfig = Field(default_factory=ProxyConfig)

    # Pagination
    pagination: PaginationConfig = Field(default_factory=PaginationConfig)

    # Browser automation settings
    browser_headless: bool = True
    browser_type: str = "chromium"
    browser_viewport_width: int = 1920
    browser_viewport_height: int = 1080
    browser_timeout: float = 30.0
    browser_wait_until: str = "networkidle"
    browser_screenshot_on_error: bool = True

    # Database settings
    database_connection_timeout: float = 10.0
    database_query_timeout: float = 60.0
    database_pool_size: int = 5
    database_echo: bool = False

    # API settings
    api_base_url: str | None = None
    api_auth_type: AuthType = AuthType.NONE
    api_key: str | None = None
    api_secret: str | None = None

    # File processing settings
    file_encoding: str = "utf-8"
    file_chunk_size: int = 8192
    file_max_size_mb: int = 100

    # Redis settings (for caching and rate limiting)
    redis_url: str = "redis://localhost:6379/0"
    redis_password: str | None = None
    redis_ssl: bool = False

    # PostgreSQL settings
    postgres_url: str | None = None

    # MongoDB settings
    mongodb_url: str | None = None

    # Performance settings
    batch_size: int = 100
    concurrent_requests: int = 5
    memory_limit_mb: int = 512

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        return v.upper()

    @field_validator("output_dir", "temp_dir")
    @classmethod
    def ensure_directory_exists(cls, v: Path) -> Path:
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("browser_type")
    @classmethod
    def validate_browser_type(cls, v: str) -> str:
        valid_types = ["chromium", "firefox", "webkit"]
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid browser type. Must be one of {valid_types}")
        return v.lower()

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()

    @classmethod
    def from_file(cls, file_path: Path | str) -> "ScraperConfig":
        """Load configuration from a file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        content = file_path.read_text()

        if file_path.suffix in [".yaml", ".yml"]:
            data = yaml.safe_load(content)
        elif file_path.suffix == ".json":
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported configuration file format: {file_path.suffix}")

        return cls(**data)


class WebScraperConfig(ScraperConfig):
    """Configuration specific to web scraping."""

    # HTML parsing
    parser: str = "lxml"
    pretty_soup_features: str = "lxml"

    # JavaScript rendering
    enable_javascript: bool = True
    wait_for_selector: str | None = None
    wait_for_timeout: float = 10.0

    # Screenshots
    capture_screenshots: bool = False
    screenshot_format: str = "png"
    screenshot_quality: int = 85

    # Content extraction
    extract_links: bool = True
    extract_images: bool = True
    extract_metadata: bool = True

    # Browser-specific settings (override from ScraperConfig)
    headless: bool | None = None  # Alias for browser_headless
    browser_args: list[str] | None = None
    viewport_width: int | None = None  # Alias for browser_viewport_width
    viewport_height: int | None = None  # Alias for browser_viewport_height
    geolocation: dict[str, float] | None = None
    permissions: list[str] | None = None
    offline: bool = False


class APIScraperConfig(ScraperConfig):
    """Configuration specific to API scraping."""

    # Request defaults
    default_content_type: str = "application/json"
    default_accept: str = "application/json"

    # Response handling
    parse_json_automatically: bool = True
    validate_response_schema: bool = False

    # GraphQL specific
    graphql_endpoint: str | None = None
    graphql_ws_endpoint: str | None = None

    # WebSocket specific
    ws_ping_interval: float = 30.0
    ws_pong_timeout: float = 10.0
    ws_close_timeout: float = 10.0


class DatabaseScraperConfig(ScraperConfig):
    """Configuration specific to database scraping."""

    # Query settings
    fetch_size: int = 1000
    stream_results: bool = True
    use_server_side_cursors: bool = True

    # Connection pooling
    pool_pre_ping: bool = True
    pool_recycle: int = 3600

    # SQL specific
    sql_echo: bool = False
    sql_isolation_level: str | None = None

    # NoSQL specific
    nosql_read_preference: str = "primary"
    nosql_write_concern: int = 1
