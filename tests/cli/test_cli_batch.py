"""Tests for the batch command."""

import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from scrap_e.cli import cli


class TestBatchCommand:
    """Test batch command functionality."""

    @pytest.fixture
    def mock_batch_results(self):
        """Create mock batch scraping results."""
        return [
            MagicMock(
                success=True,
                data=MagicMock(
                    url="http://example1.com",
                    content="<html><body>Page 1</body></html>",
                    status_code=200,
                    headers={},
                ),
                error=None,
                model_dump=lambda **kwargs: {
                    "success": True,
                    "data": {
                        "url": "http://example1.com",
                        "content": "<html><body>Page 1</body></html>",
                        "status_code": 200,
                    },
                },
            ),
            MagicMock(
                success=True,
                data=MagicMock(
                    url="http://example2.com",
                    content="<html><body>Page 2</body></html>",
                    status_code=200,
                    headers={},
                ),
                error=None,
                model_dump=lambda **kwargs: {
                    "success": True,
                    "data": {
                        "url": "http://example2.com",
                        "content": "<html><body>Page 2</body></html>",
                        "status_code": 200,
                    },
                },
            ),
            MagicMock(
                success=False,
                error="Connection failed",
                data=None,
            ),
        ]

    def test_batch_basic(self, mock_batch_results):
        """Test basic batch scraping."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_batch_results

            result = runner.invoke(
                cli, ["batch", "http://example1.com", "http://example2.com", "http://example3.com"]
            )

            assert result.exit_code == 0
            assert "Scraping 3 URLs" in result.output
            assert "SUCCESS Count: 2" in result.output
            assert "FAILED Count: 1" in result.output

    def test_batch_with_concurrent_limit(self, mock_batch_results):
        """Test batch scraping with concurrent limit."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_batch_results

            result = runner.invoke(
                cli,
                [
                    "batch",
                    "http://example1.com",
                    "http://example2.com",
                    "--concurrent",
                    "2",
                ],
            )

            assert result.exit_code == 0
            assert "2 concurrent requests" in result.output

            # Verify command executed successfully
            assert mock_run.called

    def test_batch_with_output_directory(self, mock_batch_results, tmp_path):
        """Test batch scraping with output directory."""
        runner = CliRunner()
        output_dir = tmp_path / "batch_output"

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_batch_results

            result = runner.invoke(
                cli,
                [
                    "batch",
                    "http://example1.com",
                    "http://example2.com",
                    "http://example3.com",
                    "--output-dir",
                    str(output_dir),
                ],
            )

            assert result.exit_code == 0
            assert output_dir.exists()

            # Check that successful results were saved
            result_files = list(output_dir.glob("result_*.json"))
            assert len(result_files) == 2  # Only successful results saved

            # Verify content of saved files
            with result_files[0].open() as f:
                data = json.load(f)
                assert data["success"] is True

    def test_batch_with_method_browser(self, mock_batch_results):
        """Test batch scraping with browser method."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_batch_results

            result = runner.invoke(
                cli,
                [
                    "batch",
                    "http://example1.com",
                    "http://example2.com",
                    "--method",
                    "browser",
                ],
            )

            assert result.exit_code == 0

            # Verify command executed with browser method
            assert mock_run.called

    def test_batch_no_urls(self):
        """Test batch command without URLs."""
        runner = CliRunner()

        result = runner.invoke(cli, ["batch"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_batch_single_url(self, mock_batch_results):
        """Test batch command with single URL."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = [mock_batch_results[0]]

            result = runner.invoke(cli, ["batch", "http://example.com"])

            assert result.exit_code == 0
            assert "Scraping 1 URLs" in result.output

    def test_batch_all_failed(self):
        """Test batch scraping when all URLs fail."""
        runner = CliRunner()

        failed_results = [
            MagicMock(success=False, error="Error 1", data=None),
            MagicMock(success=False, error="Error 2", data=None),
        ]

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = failed_results

            result = runner.invoke(cli, ["batch", "http://example1.com", "http://example2.com"])

            assert result.exit_code == 0
            assert "SUCCESS Count: 0" in result.output
            assert "FAILED Count: 2" in result.output

    def test_batch_large_concurrent_limit(self, mock_batch_results):
        """Test batch scraping with large concurrent limit."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_batch_results

            result = runner.invoke(
                cli,
                [
                    "batch",
                    "http://example1.com",
                    "http://example2.com",
                    "--concurrent",
                    "100",
                ],
            )

            assert result.exit_code == 0
            assert "100 concurrent requests" in result.output

    def test_batch_invalid_concurrent_value(self):
        """Test batch command with invalid concurrent value."""
        runner = CliRunner()

        result = runner.invoke(cli, ["batch", "http://example.com", "--concurrent", "not-a-number"])

        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_batch_output_dir_creation(self, mock_batch_results, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        runner = CliRunner()
        output_dir = tmp_path / "new" / "nested" / "dir"

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_batch_results

            result = runner.invoke(
                cli,
                [
                    "batch",
                    "http://example.com",
                    "--output-dir",
                    str(output_dir),
                ],
            )

            assert result.exit_code == 0
            assert output_dir.exists()
            assert "Results saved to" in result.output

    def test_batch_mixed_url_formats(self, mock_batch_results):
        """Test batch command with various URL formats."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_batch_results

            result = runner.invoke(
                cli,
                [
                    "batch",
                    "http://example.com",
                    "https://secure.example.com",
                    "example.com/page",  # URL without protocol
                ],
            )

            assert result.exit_code == 0
            assert "Scraping 3 URLs" in result.output

    def test_batch_with_debug_mode(self, mock_batch_results):
        """Test batch command with debug mode enabled."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = mock_batch_results

            result = runner.invoke(cli, ["--debug", "batch", "http://example.com"])

            assert result.exit_code == 0
            # Debug mode should be propagated to config

    def test_batch_empty_results(self):
        """Test batch command with empty results."""
        runner = CliRunner()

        with patch("scrap_e.cli.asyncio.run") as mock_run:
            mock_run.return_value = []

            result = runner.invoke(cli, ["batch", "http://example.com"])

            assert result.exit_code == 0
            assert "SUCCESS Count: 0" in result.output
            assert "FAILED Count: 0" in result.output
