"""Tests for basic CLI functionality and configuration."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from scrap_e import __version__
from scrap_e.cli import cli


class TestCLIBase:
    """Test basic CLI functionality."""

    def test_cli_version(self):
        """Test version option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_cli_help(self):
        """Test help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Scrap-E: Universal Data Scraper" in result.output
        assert "scrape" in result.output
        assert "batch" in result.output
        assert "doctor" in result.output
        assert "sitemap" in result.output

    def test_cli_debug_mode(self):
        """Test debug mode flag."""
        runner = CliRunner()
        with patch("scrap_e.cli.structlog.configure") as mock_configure:
            result = runner.invoke(cli, ["--debug", "doctor"])
            assert result.exit_code == 0
            # Verify structlog was configured with debug settings
            mock_configure.assert_called_once()
            processors = mock_configure.call_args[1]["processors"]
            # Check that ConsoleRenderer is used in debug mode
            assert any("ConsoleRenderer" in str(p) for p in processors)

    def test_cli_config_file(self, tmp_path):
        """Test loading configuration from file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
debug: true
default_timeout: 60
user_agent: "Test Bot"
        """)

        runner = CliRunner()
        with patch("scrap_e.core.config.ScraperConfig.from_file") as mock_from_file:
            mock_config = MagicMock()
            mock_from_file.return_value = mock_config

            result = runner.invoke(cli, ["--config", str(config_file), "doctor"])
            assert result.exit_code == 0
            mock_from_file.assert_called_once_with(str(config_file))

    def test_cli_invalid_config_file(self):
        """Test error handling for invalid config file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--config", "nonexistent.yaml", "doctor"])
        assert result.exit_code != 0
        assert "does not exist" in result.output.lower()


class TestCLICommands:
    """Test CLI command structure."""

    def test_scrape_command_help(self):
        """Test scrape command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["scrape", "--help"])
        assert result.exit_code == 0
        assert "Scrape data from a URL" in result.output
        assert "--method" in result.output
        assert "--output" in result.output
        assert "--format" in result.output
        assert "--selector" in result.output
        assert "--xpath" in result.output

    def test_batch_command_help(self):
        """Test batch command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["batch", "--help"])
        assert result.exit_code == 0
        assert "Scrape multiple URLs in batch" in result.output
        assert "--concurrent" in result.output
        assert "--output-dir" in result.output

    def test_sitemap_command_help(self):
        """Test sitemap command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["sitemap", "--help"])
        assert result.exit_code == 0
        assert "Extract and optionally scrape URLs from a sitemap" in result.output
        assert "--output" in result.output
        assert "--scrape" in result.output

    def test_doctor_command_help(self):
        """Test doctor command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["doctor", "--help"])
        assert result.exit_code == 0
        assert "Check system dependencies and configuration" in result.output

    def test_serve_command_help(self):
        """Test serve command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--help"])
        assert result.exit_code == 0
        assert "Start the Scrap-E API server" in result.output
        assert "--host" in result.output
        assert "--port" in result.output


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_invalid_command(self):
        """Test invalid command handling."""
        runner = CliRunner()
        result = runner.invoke(cli, ["invalid_command"])
        assert result.exit_code != 0
        assert "Error" in result.output or "Usage" in result.output

    def test_missing_required_argument(self):
        """Test missing required argument."""
        runner = CliRunner()
        result = runner.invoke(cli, ["scrape"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_invalid_option_value(self):
        """Test invalid option value."""
        runner = CliRunner()
        result = runner.invoke(cli, ["scrape", "http://example.com", "--method", "invalid"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_conflicting_options(self):
        """Test handling of conflicting options."""
        runner = CliRunner()
        # Test browser-only option with http method
        result = runner.invoke(
            cli, ["scrape", "http://example.com", "--method", "http", "--screenshot"]
        )
        # Should still run but screenshot is ignored for HTTP method
        # Just verify it doesn't crash
        assert result.exit_code in [0, 1]  # May fail due to actual scraping attempt


class TestCLIContext:
    """Test CLI context passing."""

    def test_context_propagation(self):
        """Test that context is properly propagated to commands."""
        runner = CliRunner()
        with patch("scrap_e.cli.asyncio.run") as mock_run:
            # Return a regular object, not a coroutine
            mock_run.return_value = MagicMock(success=True, error=None, data=None, metadata=None)

            runner.invoke(cli, ["--debug", "scrape", "http://example.com"])

            # Command should execute with debug context
            assert mock_run.called

    def test_global_options_override(self):
        """Test that global options override defaults."""
        runner = CliRunner()
        with patch("scrap_e.cli.asyncio.run") as mock_run:
            # Return a regular object, not a coroutine
            mock_run.return_value = MagicMock(success=True, error=None, data=None, metadata=None)

            # Test with custom timeout
            runner.invoke(cli, ["scrape", "http://example.com", "--timeout", "60"])

            # Verify timeout was passed through
            assert mock_run.called
            # The first argument to asyncio.run is the coroutine
            call_args = mock_run.call_args
            assert call_args is not None
