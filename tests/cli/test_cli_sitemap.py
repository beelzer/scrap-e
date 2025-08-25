"""Tests for the sitemap command."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from scrap_e.cli import cli


class TestSitemapCommand:
    """Test sitemap command functionality."""

    @pytest.fixture
    def mock_sitemap_urls(self):
        """Create mock sitemap URLs."""
        return [
            "http://example.com/page1",
            "http://example.com/page2",
            "http://example.com/page3",
            "http://example.com/blog/post1",
            "http://example.com/blog/post2",
        ]

    def test_sitemap_extract_urls(self, mock_sitemap_urls):
        """Test extracting URLs from sitemap."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_sitemap_urls

            result = runner.invoke(cli, ["sitemap", "http://example.com/sitemap.xml"])

            assert result.exit_code == 0
            assert "Extracting URLs from sitemap" in result.output
            assert "Found 5 URLs" in result.output
            assert "http://example.com/page1" in result.output

    def test_sitemap_save_urls_to_file(self, mock_sitemap_urls, tmp_path):
        """Test saving extracted URLs to file."""
        runner = CliRunner()
        output_file = tmp_path / "urls.txt"

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_sitemap_urls

            result = runner.invoke(
                cli, ["sitemap", "http://example.com/sitemap.xml", "--output", str(output_file)]
            )

            assert result.exit_code == 0
            assert output_file.exists()

            # Verify file content
            content = output_file.read_text()
            for url in mock_sitemap_urls:
                assert url in content

            assert "URLs saved to" in result.output

    def test_sitemap_display_limited_urls(self):
        """Test that only first 10 URLs are displayed."""
        runner = CliRunner()

        # Create more than 10 URLs
        many_urls = [f"http://example.com/page{i}" for i in range(20)]

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = many_urls

            result = runner.invoke(cli, ["sitemap", "http://example.com/sitemap.xml"])

            assert result.exit_code == 0
            assert "Found 20 URLs" in result.output
            assert "and 10 more" in result.output

            # Check first 10 are shown
            for i in range(10):
                assert f"page{i}" in result.output

            # Check 11th is not shown
            assert "page10" not in result.output

    def test_sitemap_with_scrape_flag(self, mock_sitemap_urls):
        """Test sitemap with --scrape flag to scrape all URLs."""
        runner = CliRunner()

        # Mock scraping results
        mock_scrape_results = [
            MagicMock(success=True, data=MagicMock(), error=None),
            MagicMock(success=True, data=MagicMock(), error=None),
            MagicMock(success=False, data=None, error="Failed"),
            MagicMock(success=True, data=MagicMock(), error=None),
            MagicMock(success=True, data=MagicMock(), error=None),
        ]

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            # First call extracts URLs, second call scrapes them
            mock_run.side_effect = [mock_sitemap_urls, mock_scrape_results]

            result = runner.invoke(cli, ["sitemap", "http://example.com/sitemap.xml", "--scrape"])

            assert result.exit_code == 0
            assert "Found 5 URLs" in result.output
            assert "Scraping 5 URLs" in result.output
            assert "Successfully scraped 4/5 URLs" in result.output

    def test_sitemap_with_scrape_and_output(self, mock_sitemap_urls, tmp_path):
        """Test sitemap with both --scrape and --output flags."""
        runner = CliRunner()
        output_file = tmp_path / "urls.txt"

        mock_scrape_results = [
            MagicMock(success=True, data=MagicMock(), error=None) for _ in mock_sitemap_urls
        ]

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.side_effect = [mock_sitemap_urls, mock_scrape_results]

            result = runner.invoke(
                cli,
                [
                    "sitemap",
                    "http://example.com/sitemap.xml",
                    "--scrape",
                    "--output",
                    str(output_file),
                ],
            )

            assert result.exit_code == 0
            assert output_file.exists()
            assert "URLs saved to" in result.output
            assert "Successfully scraped 5/5 URLs" in result.output

    def test_sitemap_empty_result(self):
        """Test sitemap with no URLs found."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = []

            result = runner.invoke(cli, ["sitemap", "http://example.com/sitemap.xml"])

            assert result.exit_code == 0
            assert "Found 0 URLs" in result.output

    def test_sitemap_invalid_url(self):
        """Test sitemap with invalid URL."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.side_effect = ValueError("Invalid URL")

            result = runner.invoke(cli, ["sitemap", "not-a-url"])

            assert result.exit_code != 0

    def test_sitemap_network_error(self):
        """Test sitemap with network error."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.side_effect = ConnectionError("Network error")

            result = runner.invoke(cli, ["sitemap", "http://example.com/sitemap.xml"])

            assert result.exit_code != 0

    def test_sitemap_scrape_all_failed(self, mock_sitemap_urls):
        """Test sitemap scraping when all URLs fail."""
        runner = CliRunner()

        mock_scrape_results = [
            MagicMock(success=False, data=None, error="Failed") for _ in mock_sitemap_urls
        ]

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.side_effect = [mock_sitemap_urls, mock_scrape_results]

            result = runner.invoke(cli, ["sitemap", "http://example.com/sitemap.xml", "--scrape"])

            assert result.exit_code == 0
            assert "Successfully scraped 0/5 URLs" in result.output

    def test_sitemap_malformed_xml(self):
        """Test sitemap with malformed XML."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            # Return some URLs despite malformed XML (parser might be forgiving)
            mock_run.return_value = ["http://example.com/page1"]

            result = runner.invoke(cli, ["sitemap", "http://example.com/bad-sitemap.xml"])

            assert result.exit_code == 0
            assert "Found 1 URLs" in result.output

    def test_sitemap_gzip_compressed(self, mock_sitemap_urls):
        """Test sitemap with gzipped sitemap."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_sitemap_urls

            result = runner.invoke(cli, ["sitemap", "http://example.com/sitemap.xml.gz"])

            assert result.exit_code == 0
            assert "Found 5 URLs" in result.output

    def test_sitemap_index(self):
        """Test sitemap index (sitemap of sitemaps)."""
        runner = CliRunner()

        # Simulate URLs from multiple sitemaps
        all_urls = [
            "http://example.com/page1",
            "http://example.com/page2",
            "http://example.com/blog/post1",
            "http://example.com/products/item1",
        ]

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = all_urls

            result = runner.invoke(cli, ["sitemap", "http://example.com/sitemap_index.xml"])

            assert result.exit_code == 0
            assert "Found 4 URLs" in result.output

    def test_sitemap_with_debug_mode(self, mock_sitemap_urls):
        """Test sitemap command with debug mode."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_sitemap_urls

            result = runner.invoke(cli, ["--debug", "sitemap", "http://example.com/sitemap.xml"])

            assert result.exit_code == 0
            assert "Found 5 URLs" in result.output

    def test_sitemap_missing_argument(self):
        """Test sitemap command without URL argument."""
        runner = CliRunner()

        result = runner.invoke(cli, ["sitemap"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output
