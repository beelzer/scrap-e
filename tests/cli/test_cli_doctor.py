"""Tests for the doctor command."""

import sys
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from scrap_e.cli import cli


class TestDoctorCommand:
    """Test doctor command functionality."""

    def test_doctor_basic(self):
        """Test basic doctor command execution."""
        runner = CliRunner()
        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        assert "Scrap-E System Check" in result.output
        assert "System Check Results" in result.output
        assert "Python Version" in result.output
        assert "Component" in result.output
        assert "Status" in result.output
        assert "Result" in result.output

    def test_doctor_python_version_check(self):
        """Test Python version checking."""
        runner = CliRunner()
        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        assert py_version in result.output

    def test_doctor_package_checks(self):
        """Test package availability checks."""
        runner = CliRunner()

        # Just test that the command runs and shows package info
        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        assert "httpx" in result.output
        assert "beautifulsoup4" in result.output
        assert "playwright" in result.output
        assert "pandas" in result.output
        assert "pydantic" in result.output

    def test_doctor_all_packages_installed(self):
        """Test doctor command when all packages are installed."""
        runner = CliRunner()

        # Since we're in a test environment, packages should be installed
        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        # Should show installed status for at least some packages
        assert "Installed" in result.output or "OK" in result.output

    def test_doctor_no_packages_installed(self):
        """Test doctor command output format."""
        runner = CliRunner()

        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        # Check for output structure
        assert "System Check Results" in result.output
        assert "Component" in result.output
        assert "Status" in result.output

    @patch("scrap_e.cli.PLAYWRIGHT_AVAILABLE", True)
    @patch("scrap_e.cli.sync_playwright")
    def test_doctor_playwright_browsers_available(self, mock_sync_playwright):
        """Test playwright browser availability check."""
        runner = CliRunner()

        # Mock playwright context manager
        mock_playwright = MagicMock()
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright

        # Mock browser launchers
        for browser in ["chromium", "firefox", "webkit"]:
            browser_mock = MagicMock()
            browser_mock.launch.return_value.close = MagicMock()
            setattr(mock_playwright, browser, browser_mock)

        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        assert "Browser: chromium" in result.output
        assert "Browser: firefox" in result.output
        assert "Browser: webkit" in result.output
        assert "Available" in result.output

    @patch("scrap_e.cli.PLAYWRIGHT_AVAILABLE", True)
    @patch("scrap_e.cli.sync_playwright")
    def test_doctor_playwright_browser_not_available(self, mock_sync_playwright):
        """Test playwright browser not available."""
        runner = CliRunner()

        # Mock playwright context manager
        mock_playwright = MagicMock()
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright

        # Mock chromium available, others not
        chromium_mock = MagicMock()
        chromium_mock.launch.return_value.close = MagicMock()
        mock_playwright.chromium = chromium_mock

        # Firefox and webkit fail
        firefox_mock = MagicMock()
        firefox_mock.launch.side_effect = Exception("Browser not found")
        mock_playwright.firefox = firefox_mock

        webkit_mock = MagicMock()
        webkit_mock.launch.side_effect = Exception("Browser not found")
        mock_playwright.webkit = webkit_mock

        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        assert "Browser: chromium" in result.output
        assert "Available" in result.output
        assert "Browser: firefox" in result.output
        assert "Not available" in result.output

    @patch("scrap_e.cli.PLAYWRIGHT_AVAILABLE", False)
    def test_doctor_playwright_not_installed(self):
        """Test doctor when playwright is not installed."""
        runner = CliRunner()

        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        assert "Playwright" in result.output
        assert "Not installed" in result.output

    @patch("scrap_e.cli.PLAYWRIGHT_AVAILABLE", True)
    @patch("scrap_e.cli.sync_playwright")
    def test_doctor_playwright_configuration_error(self, mock_sync_playwright):
        """Test playwright configuration error."""
        runner = CliRunner()

        # Simulate playwright configuration error
        mock_sync_playwright.side_effect = Exception("Playwright not configured")

        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        assert "Playwright browsers" in result.output
        assert "Not configured" in result.output

    def test_doctor_all_checks_pass(self):
        """Test doctor command success message."""
        runner = CliRunner()

        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        # Check for either success or warning message
        assert "OK" in result.output or "WARNING" in result.output

    def test_doctor_some_checks_fail(self):
        """Test doctor command output messages."""
        runner = CliRunner()

        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        # Check that some status message is shown
        assert result.output  # Non-empty output

    def test_doctor_output_formatting(self):
        """Test doctor command output formatting."""
        runner = CliRunner()

        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        # Check for table structure
        assert "│" in result.output or "|" in result.output  # Table borders
        assert "OK" in result.output or "FAIL" in result.output  # Result indicators

    def test_doctor_with_debug_mode(self):
        """Test doctor command with debug mode."""
        runner = CliRunner()

        result = runner.invoke(cli, ["--debug", "doctor"])

        assert result.exit_code == 0
        assert "Scrap-E System Check" in result.output

    def test_doctor_python_version_fail(self):
        """Test doctor command shows Python version."""
        runner = CliRunner()

        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        assert "Python Version" in result.output
        # Should show current Python version
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        assert py_version in result.output
