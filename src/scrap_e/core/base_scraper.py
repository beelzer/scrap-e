"""Base scraper class that all scrapers inherit from."""

import asyncio
import builtins
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, TypeVar

import structlog
from pydantic import BaseModel

from scrap_e.core.config import ScraperConfig
from scrap_e.core.exceptions import ScraperError, TimeoutError
from scrap_e.core.models import ScraperMetadata, ScraperResult, ScraperStats, ScraperType

T = TypeVar("T", bound=BaseModel)
ConfigT = TypeVar("ConfigT", bound=ScraperConfig)


class BaseScraper[T: BaseModel, ConfigT: ScraperConfig](ABC):
    """Abstract base class for all scrapers."""

    def __init__(self, config: ConfigT | None = None) -> None:
        self.config = config or self._get_default_config()
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.stats = ScraperStats()
        self._session: Any | None = None
        self._start_time: float | None = None

    @abstractmethod
    def _get_default_config(self) -> ConfigT:
        """Get default configuration for the scraper."""
        ...

    @property
    @abstractmethod
    def scraper_type(self) -> ScraperType:
        """Return the type of this scraper."""
        ...

    @abstractmethod
    async def _initialize(self) -> None:
        """Initialize scraper resources (connections, sessions, etc.)."""
        ...

    @abstractmethod
    async def _cleanup(self) -> None:
        """Clean up scraper resources."""
        ...

    @abstractmethod
    async def _scrape(self, source: str, **kwargs: Any) -> T:
        """Perform the actual scraping operation."""
        ...

    async def scrape(self, source: str, **kwargs: Any) -> ScraperResult[T]:
        """
        Main public method to scrape data from a source.

        Args:
            source: The source to scrape from (URL, file path, connection string, etc.)
            **kwargs: Additional arguments specific to the scraper type

        Returns:
            ScraperResult containing the scraped data or error information
        """
        self._start_time = time.time()
        metadata = ScraperMetadata(
            scraper_type=self.scraper_type,
            source=source,
        )

        try:
            self.logger.info(
                "Starting scraping operation",
                source=source,
                scraper_type=self.scraper_type.value,
            )

            # Initialize if needed
            if self._session is None:
                await self._initialize()

            # Apply timeout if configured
            if self.config.default_timeout:
                try:
                    data = await asyncio.wait_for(
                        self._scrape(source, **kwargs),
                        timeout=self.config.default_timeout,
                    )
                except builtins.TimeoutError as e:
                    raise TimeoutError(
                        f"Scraping operation timed out after {self.config.default_timeout}s",
                        {"source": source, "timeout": self.config.default_timeout},
                    ) from e
            else:
                data = await self._scrape(source, **kwargs)

            # Update statistics
            self.stats.successful_requests += 1
            metadata.records_scraped = self._count_records(data)

            # Calculate duration
            duration = time.time() - self._start_time
            metadata.duration_seconds = duration
            self.stats.total_duration += duration

            self.logger.info(
                "Scraping completed successfully",
                source=source,
                duration=duration,
                records=metadata.records_scraped,
            )

            return ScraperResult(
                success=True,
                data=data,
                metadata=metadata,
            )

        except ScraperError as e:
            self.logger.error(
                "Scraping failed with known error",
                source=source,
                error=str(e),
                details=e.details,
            )
            self.stats.failed_requests += 1
            metadata.errors_count = 1

            if self._start_time:
                metadata.duration_seconds = time.time() - self._start_time

            return ScraperResult(
                success=False,
                error=str(e),
                metadata=metadata,
            )

        except Exception as e:
            self.logger.exception(
                "Scraping failed with unexpected error",
                source=source,
                error=str(e),
            )
            self.stats.failed_requests += 1
            metadata.errors_count = 1

            if self._start_time:
                metadata.duration_seconds = time.time() - self._start_time

            return ScraperResult(
                success=False,
                error=f"Unexpected error: {e!s}",
                metadata=metadata,
            )

    async def scrape_multiple(
        self,
        sources: list[str],
        max_concurrent: int | None = None,
        **kwargs: Any,
    ) -> list[ScraperResult[T]]:
        """
        Scrape multiple sources concurrently.

        Args:
            sources: List of sources to scrape
            max_concurrent: Maximum number of concurrent scraping operations
            **kwargs: Additional arguments passed to each scrape operation

        Returns:
            List of ScraperResult objects
        """
        max_concurrent = max_concurrent or self.config.concurrent_requests

        semaphore = asyncio.Semaphore(max_concurrent)

        async def scrape_with_semaphore(source: str) -> ScraperResult[T]:
            async with semaphore:
                return await self.scrape(source, **kwargs)

        tasks = [scrape_with_semaphore(source) for source in sources]
        return await asyncio.gather(*tasks)

    @asynccontextmanager
    async def session(self) -> AsyncIterator["BaseScraper[T, ConfigT]"]:
        """
        Context manager for scraping sessions.

        Usage:
            async with scraper.session() as s:
                result = await s.scrape("https://example.com")
        """
        try:
            await self._initialize()
            yield self
        finally:
            await self._cleanup()

    async def scrape_stream(
        self,
        source: str,
        chunk_size: int = 100,
        **kwargs: Any,
    ) -> AsyncIterator[T]:
        """
        Stream scraping results for large datasets.

        Args:
            source: The source to scrape from
            chunk_size: Number of records per chunk
            **kwargs: Additional arguments specific to the scraper type

        Yields:
            Chunks of scraped data
        """
        self.logger.info(
            "Starting stream scraping",
            source=source,
            chunk_size=chunk_size,
        )

        async for chunk in await self._stream_scrape(source, chunk_size, **kwargs):
            yield chunk

    @abstractmethod
    async def _stream_scrape(
        self,
        source: str,
        chunk_size: int,
        **kwargs: Any,
    ) -> AsyncIterator[T]:
        """Implementation of streaming scrape."""
        ...

    def _count_records(self, data: T) -> int:
        """Count the number of records in the scraped data."""
        if data is None:
            return 0
        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict):
            return 1
        if hasattr(data, "__len__"):
            return len(data)
        return 1

    async def validate(self, source: str, **kwargs: Any) -> bool:
        """
        Validate that a source can be scraped.

        Args:
            source: The source to validate
            **kwargs: Additional validation parameters

        Returns:
            True if the source is valid and accessible
        """
        try:
            # Quick validation without full scraping
            await self._validate_source(source, **kwargs)
            return True
        except Exception as e:
            self.logger.warning(
                "Source validation failed",
                source=source,
                error=str(e),
            )
            return False

    @abstractmethod
    async def _validate_source(self, source: str, **kwargs: Any) -> None:
        """Validate that a source is accessible."""
        ...

    def get_stats(self) -> ScraperStats:
        """Get current scraper statistics."""
        if self.stats.total_requests > 0:
            self.stats.average_response_time = self.stats.total_duration / self.stats.total_requests
        return self.stats

    def reset_stats(self) -> None:
        """Reset scraper statistics."""
        self.stats = ScraperStats()

    async def __aenter__(self) -> "BaseScraper[T, ConfigT]":
        """Async context manager entry."""
        await self._initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self._cleanup()


class BatchScraper(BaseScraper[T, ConfigT], ABC):
    """Base class for scrapers that support batch operations."""

    async def scrape_batch(
        self,
        sources: list[str],
        batch_size: int | None = None,
        **kwargs: Any,
    ) -> list[ScraperResult[T]]:
        """
        Scrape sources in batches.

        Args:
            sources: List of sources to scrape
            batch_size: Size of each batch
            **kwargs: Additional arguments

        Returns:
            List of results
        """
        batch_size = batch_size or self.config.batch_size
        results = []

        for i in range(0, len(sources), batch_size):
            batch = sources[i : i + batch_size]
            batch_results = await self._scrape_batch(batch, **kwargs)
            results.extend(batch_results)

        return results

    @abstractmethod
    async def _scrape_batch(
        self,
        sources: list[str],
        **kwargs: Any,
    ) -> list[ScraperResult[T]]:
        """Implementation of batch scraping."""
        ...


class PaginatedScraper(BaseScraper[T, ConfigT], ABC):
    """Base class for scrapers that support pagination."""

    async def scrape_all_pages(
        self,
        source: str,
        max_pages: int | None = None,
        **kwargs: Any,
    ) -> list[T]:
        """
        Scrape all pages from a paginated source.

        Args:
            source: The initial source
            max_pages: Maximum number of pages to scrape
            **kwargs: Additional arguments

        Returns:
            Combined data from all pages
        """
        max_pages = max_pages or self.config.pagination.max_pages
        all_data = []
        page = 1
        next_source = source

        while next_source and (max_pages is None or page <= max_pages):
            self.logger.info(f"Scraping page {page}", source=next_source)

            result = await self.scrape(next_source, **kwargs)
            if result.success and result.data:
                all_data.append(result.data)

            next_url = await self._get_next_page(next_source, result, page)
            if next_url is None:
                break
            next_source = next_url
            page += 1

        return all_data

    @abstractmethod
    async def _get_next_page(
        self,
        current_source: str,
        result: ScraperResult[T],
        page_number: int,
    ) -> str | None:
        """Get the source for the next page."""
        ...
