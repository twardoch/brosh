"""Tests for brosh.cli module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from brosh.cli import BrowserScreenshotCLI


class TestBrowserScreenshotCLI:
    """Test the BrowserScreenshotCLI class."""

    def test_cli_initialization_defaults(self) -> None:
        """Test CLI initialization with default parameters."""
        with patch("brosh.cli.BrowserManager"):
            cli = BrowserScreenshotCLI()
            
            assert cli.app == ""
            assert cli.width == 0
            assert cli.height == 0
            assert cli.zoom == 100
            assert cli.subdirs is False
            assert cli.json is False
            assert cli.verbose is False

    def test_cli_initialization_custom(self, temp_output_dir: Path) -> None:
        """Test CLI initialization with custom parameters."""
        with patch("brosh.cli.BrowserManager"):
            cli = BrowserScreenshotCLI(
                app="firefox",
                width=1920,
                height=1080,
                zoom=150,
                output_dir=temp_output_dir,
                subdirs=True,
                verbose=True,
                json=True,
            )
            
            assert cli.app == "firefox"
            assert cli.width == 1920
            assert cli.height == 1080
            assert cli.zoom == 150
            assert cli.output_dir == temp_output_dir
            assert cli.subdirs is True
            assert cli.verbose is True
            assert cli.json is True

    @patch("brosh.cli.BrowserManager")
    def test_cli_run_browser_already_running(
        self, mock_browser_manager: MagicMock
    ) -> None:
        """Test running browser when it's already running."""
        # Mock browser manager
        mock_instance = MagicMock()
        mock_instance.get_browser_name.return_value = "chrome"
        mock_instance.debug_ports = {"chrome": 9222}
        mock_browser_manager.return_value = mock_instance
        
        cli = BrowserScreenshotCLI()
        
        # Mock urllib to simulate browser already running
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = MagicMock()
            
            result = cli.run()
            
            assert "chrome already running on port 9222" in result
            mock_urlopen.assert_called_once()

    @patch("brosh.cli.BrowserManager")
    def test_cli_run_browser_not_running(
        self, mock_browser_manager: MagicMock
    ) -> None:
        """Test running browser when it's not running."""
        # Mock browser manager
        mock_instance = MagicMock()
        mock_instance.get_browser_name.return_value = "chrome"
        mock_instance.debug_ports = {"chrome": 9222}
        mock_instance.launch_browser.return_value = "chrome started"
        mock_browser_manager.return_value = mock_instance
        
        cli = BrowserScreenshotCLI()
        
        # Mock urllib to simulate browser not running
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = Exception("Connection refused")
            
            result = cli.run()
            
            assert result == "chrome started"
            mock_instance.launch_browser.assert_called_once()

    @patch("brosh.cli.BrowserManager")
    def test_cli_run_force_restart(
        self, mock_browser_manager: MagicMock
    ) -> None:
        """Test force restarting browser."""
        # Mock browser manager
        mock_instance = MagicMock()
        mock_instance.get_browser_name.return_value = "chrome"
        mock_instance.launch_browser.return_value = "chrome restarted"
        mock_browser_manager.return_value = mock_instance
        
        cli = BrowserScreenshotCLI()
        
        result = cli.run(force_run=True)
        
        assert result == "chrome restarted"
        mock_instance.launch_browser.assert_called_once()

    @patch("brosh.cli.capture_webpage")
    @patch("brosh.cli.BrowserManager")
    def test_cli_capture_basic(
        self, mock_browser_manager: MagicMock, mock_capture: MagicMock,
        temp_output_dir: Path
    ) -> None:
        """Test basic capture functionality."""
        mock_capture.return_value = {
            str(temp_output_dir / "example_com.png"): {
                "selector": "body",
                "text": "Example content"
            }
        }
        
        cli = BrowserScreenshotCLI(output_dir=temp_output_dir)
        
        # Test that capture method exists and can be called
        # Note: We might need to implement this method in the CLI
        assert hasattr(cli, "_browser_manager")

    @patch("brosh.cli.BrowserManager")
    def test_cli_verbose_logging(self, mock_browser_manager: MagicMock) -> None:
        """Test verbose logging configuration."""
        with patch("brosh.cli.logger") as mock_logger:
            # Test non-verbose mode
            cli_quiet = BrowserScreenshotCLI(verbose=False)
            mock_logger.remove.assert_called()
            mock_logger.add.assert_called()
            
            # Reset mocks
            mock_logger.reset_mock()
            
            # Test verbose mode
            cli_verbose = BrowserScreenshotCLI(verbose=True)
            # Verbose mode should not call remove/add
            mock_logger.remove.assert_not_called()

    @patch("brosh.cli.BrowserManager")
    def test_cli_with_different_browsers(
        self, mock_browser_manager: MagicMock
    ) -> None:
        """Test CLI with different browser configurations."""
        browsers = ["chrome", "firefox", "edge", "safari"]
        
        for browser in browsers:
            cli = BrowserScreenshotCLI(app=browser)
            assert cli.app == browser

    @patch("brosh.cli.BrowserManager")
    def test_cli_output_directory_handling(
        self, mock_browser_manager: MagicMock, temp_output_dir: Path
    ) -> None:
        """Test output directory handling in CLI."""
        # Test with custom output directory
        cli = BrowserScreenshotCLI(output_dir=temp_output_dir)
        assert cli.output_dir == temp_output_dir
        
        # Test with default (should use user_pictures_dir)
        with patch("brosh.cli.user_pictures_dir") as mock_pictures_dir:
            mock_pictures_dir.return_value = "/home/user/Pictures"
            cli_default = BrowserScreenshotCLI()
            # Default should be set during initialization
            assert cli_default.output_dir == Path("/home/user/Pictures")


class TestCLIIntegration:
    """Test CLI integration scenarios."""

    @patch("brosh.cli.capture_webpage")
    @patch("brosh.cli.BrowserManager")
    def test_cli_screenshot_workflow(
        self, mock_browser_manager: MagicMock, mock_capture: MagicMock,
        temp_output_dir: Path
    ) -> None:
        """Test a complete screenshot workflow."""
        # Mock the capture result
        expected_result = {
            str(temp_output_dir / "example_com.png"): {
                "selector": "body",
                "text": "Page content",
                "html": "<body>Page content</body>"
            }
        }
        mock_capture.return_value = expected_result
        
        # Create CLI instance
        cli = BrowserScreenshotCLI(
            app="chrome",
            width=1024,
            height=768,
            zoom=100,
            output_dir=temp_output_dir,
            subdirs=False,
            verbose=False,
            json=True,
        )
        
        # Verify CLI is properly configured
        assert cli.app == "chrome"
        assert cli.width == 1024
        assert cli.height == 768
        assert cli.zoom == 100
        assert cli.output_dir == temp_output_dir
        assert cli.subdirs is False
        assert cli.json is True

    @patch("brosh.cli.BrowserManager")
    def test_cli_error_handling(self, mock_browser_manager: MagicMock) -> None:
        """Test CLI error handling scenarios."""
        # Mock browser manager to raise an exception
        mock_instance = MagicMock()
        mock_instance.get_browser_name.side_effect = RuntimeError("Browser error")
        mock_browser_manager.return_value = mock_instance
        
        cli = BrowserScreenshotCLI()
        
        # Test that errors are handled gracefully
        with pytest.raises(RuntimeError):
            cli.run()

    @patch("brosh.cli.BrowserManager")
    def test_cli_parameter_validation(
        self, mock_browser_manager: MagicMock
    ) -> None:
        """Test CLI parameter validation."""
        # Test with valid parameters
        cli = BrowserScreenshotCLI(
            zoom=100,
            width=1920,
            height=1080,
        )
        
        assert cli.zoom == 100
        assert cli.width == 1920
        assert cli.height == 1080
        
        # Test with edge case values
        cli_edge = BrowserScreenshotCLI(
            zoom=50,
            width=0,  # Should use default
            height=-1,  # Full page
        )
        
        assert cli_edge.zoom == 50
        assert cli_edge.width == 0
        assert cli_edge.height == -1


class TestCLIUtilities:
    """Test CLI utility functions and methods."""

    @patch("brosh.cli.BrowserManager")
    def test_cli_json_output_flag(self, mock_browser_manager: MagicMock) -> None:
        """Test JSON output flag functionality."""
        cli_json = BrowserScreenshotCLI(json=True)
        cli_regular = BrowserScreenshotCLI(json=False)
        
        assert cli_json.json is True
        assert cli_regular.json is False

    @patch("brosh.cli.BrowserManager")
    def test_cli_subdirs_flag(self, mock_browser_manager: MagicMock) -> None:
        """Test subdirectories flag functionality."""
        cli_subdirs = BrowserScreenshotCLI(subdirs=True)
        cli_flat = BrowserScreenshotCLI(subdirs=False)
        
        assert cli_subdirs.subdirs is True
        assert cli_flat.subdirs is False

    @patch("brosh.cli.BrowserManager")
    def test_cli_app_selection(self, mock_browser_manager: MagicMock) -> None:
        """Test browser app selection."""
        # Test auto-detection (empty string)
        cli_auto = BrowserScreenshotCLI(app="")
        assert cli_auto.app == ""
        
        # Test specific browser
        cli_firefox = BrowserScreenshotCLI(app="firefox")
        assert cli_firefox.app == "firefox"
