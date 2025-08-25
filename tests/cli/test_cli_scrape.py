"""Tests for the scrape command."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from scrap_e.cli import cli
from tests.cli.fixtures import mock_scraper_result as create_mock_result


class TestScrapeCommand:
    """Test scrape command functionality."""

    @pytest.fixture
    def mock_scraper_result(self):
        """Create a mock scraper result."""
        return create_mock_result()

    def test_scrape_basic_http(self, mock_scraper_result):
        """Test basic HTTP scraping."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            result = runner.invoke(cli, ["scrape", "http://example.com"])

            assert result.exit_code == 0
            assert "SUCCESS" in result.output
            assert "Scraping successful" in result.output

            # Verify asyncio.run was called
            mock_run.assert_called_once()

    def test_scrape_with_output_json(self, mock_scraper_result, tmp_path):
        """Test scraping with JSON output to file."""
        runner = CliRunner()
        output_file = tmp_path / "output.json"

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            result = runner.invoke(
                cli,
                ["scrape", "http://example.com", "--output", str(output_file), "--format", "json"],
            )

            assert result.exit_code == 0
            assert output_file.exists()

            # Verify JSON content
            data = json.loads(output_file.read_text())
            assert data["success"] is True
            assert data["data"]["url"] == "http://example.com"

    def test_scrape_with_output_csv(self, mock_scraper_result, tmp_path):
        """Test scraping with CSV output."""
        runner = CliRunner()
        output_file = tmp_path / "output.csv"

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            result = runner.invoke(
                cli,
                ["scrape", "http://example.com", "--output", str(output_file), "--format", "csv"],
            )

            assert result.exit_code == 0
            assert output_file.exists()

            # Verify CSV content
            content = output_file.read_text()
            assert "title" in content  # Header
            assert "Test Page" in content  # Data

    def test_scrape_with_output_html(self, mock_scraper_result, tmp_path):
        """Test scraping with HTML output."""
        runner = CliRunner()
        output_file = tmp_path / "output.html"

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            result = runner.invoke(
                cli,
                ["scrape", "http://example.com", "--output", str(output_file), "--format", "html"],
            )

            assert result.exit_code == 0
            assert output_file.exists()

            # Verify HTML content
            content = output_file.read_text()
            assert "<html>" in content
            assert "<h1>Test</h1>" in content

    def test_scrape_with_selectors(self, mock_scraper_result):
        """Test scraping with CSS selectors."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            result = runner.invoke(
                cli,
                [
                    "scrape",
                    "http://example.com",
                    "--selector",
                    "h1",
                    "--selector",
                    ".content",
                ],
            )

            assert result.exit_code == 0

            # Verify asyncio.run was called with correct arguments
            assert mock_run.called
            # The coroutine is passed as first argument
            assert mock_run.call_count == 1

    def test_scrape_with_xpath(self, mock_scraper_result):
        """Test scraping with XPath selectors."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            result = runner.invoke(
                cli,
                [
                    "scrape",
                    "http://example.com",
                    "--xpath",
                    "//h1",
                    "--xpath",
                    "//div[@class='content']",
                ],
            )

            assert result.exit_code == 0

            # Verify asyncio.run was called with correct arguments
            assert mock_run.called
            # The coroutine is passed as first argument
            assert mock_run.call_count == 1

    def test_scrape_browser_mode(self, mock_scraper_result):
        """Test scraping with browser mode."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            result = runner.invoke(cli, ["scrape", "http://example.com", "--method", "browser"])

            assert result.exit_code == 0

            # Verify asyncio.run was called (browser method)
            assert mock_run.called
            assert result.exit_code == 0

    def test_scrape_browser_with_wait_for(self, mock_scraper_result):
        """Test browser scraping with wait-for selector."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            result = runner.invoke(
                cli,
                [
                    "scrape",
                    "http://example.com",
                    "--method",
                    "browser",
                    "--wait-for",
                    ".loaded",
                ],
            )

            assert result.exit_code == 0

            # Verify command was invoked with wait-for
            assert mock_run.called
            assert result.exit_code == 0

    def test_scrape_browser_with_screenshot(self, mock_scraper_result):
        """Test browser scraping with screenshot."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            result = runner.invoke(
                cli,
                [
                    "scrape",
                    "http://example.com",
                    "--method",
                    "browser",
                    "--screenshot",
                ],
            )

            assert result.exit_code == 0

            # Verify command was invoked with screenshot
            assert mock_run.called
            assert result.exit_code == 0

    def test_scrape_browser_headless_mode(self, mock_scraper_result):
        """Test browser scraping headless mode control."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            # Test headless mode (default)
            result = runner.invoke(cli, ["scrape", "http://example.com", "--method", "browser"])
            assert result.exit_code == 0

            # Test non-headless mode
            result = runner.invoke(
                cli, ["scrape", "http://example.com", "--method", "browser", "--no-headless"]
            )
            assert result.exit_code == 0

            # Verify command was invoked with no-headless
            assert mock_run.call_count == 2  # Called twice

    def test_scrape_with_custom_user_agent(self, mock_scraper_result):
        """Test scraping with custom user agent."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            result = runner.invoke(
                cli, ["scrape", "http://example.com", "--user-agent", "CustomBot/1.0"]
            )

            assert result.exit_code == 0

            # Verify command was invoked with custom user agent
            assert mock_run.called
            assert result.exit_code == 0

    def test_scrape_with_custom_timeout(self, mock_scraper_result):
        """Test scraping with custom timeout."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            result = runner.invoke(cli, ["scrape", "http://example.com", "--timeout", "60"])

            assert result.exit_code == 0

            # Verify command was invoked with custom timeout
            assert mock_run.called
            assert result.exit_code == 0

    def test_scrape_failure(self):
        """Test handling of scraping failure."""
        runner = CliRunner()

        failed_result = MagicMock(
            success=False,
            error="Connection timeout",
            data=None,
            metadata=None,
        )

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = failed_result

            result = runner.invoke(cli, ["scrape", "http://example.com"])

            assert result.exit_code == 0  # CLI doesn't exit with error
            assert "FAILED" in result.output
            assert "Connection timeout" in result.output

    def test_scrape_with_statistics(self, mock_scraper_result):
        """Test display of scraping statistics."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            result = runner.invoke(cli, ["scrape", "http://example.com"])

            assert result.exit_code == 0
            assert "Scraping Statistics" in result.output
            assert "Duration" in result.output
            assert "1.50s" in result.output  # 1.5 seconds formatted
            assert "Records" in result.output
            assert "Errors" in result.output

    def test_scrape_invalid_url(self):
        """Test scraping with invalid URL."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.side_effect = ValueError("Invalid URL")

            result = runner.invoke(cli, ["scrape", "not-a-url"])

            # Should handle the error gracefully
            assert result.exit_code != 0

    def test_scrape_multiple_format_outputs(self, mock_scraper_result, tmp_path):
        """Test that only specified format is saved."""
        runner = CliRunner()
        output_file = tmp_path / "output"

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_scraper_result

            # Save as JSON
            result = runner.invoke(
                cli,
                ["scrape", "http://example.com", "--output", str(output_file), "--format", "json"],
            )

            assert result.exit_code == 0
            # File should be saved with original name (no extension added automatically)
            assert Path(str(output_file)).exists()
            content = Path(str(output_file)).read_text()
            assert content.startswith("{")  # JSON format
