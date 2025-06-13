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
    def test_cli_run_browser_already_running(self, mock_browser_manager: MagicMock) -> None:
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
    @patch("brosh.cli.subprocess.Popen")
    def test_cli_run_browser_not_running(self, mock_popen: MagicMock, mock_browser_manager: MagicMock) -> None:
        """Test `run` command when browser is not running."""
        mock_instance = mock_browser_manager.return_value
        mock_instance.get_browser_name.return_value = "chrome"
        mock_instance.find_browser_path.return_value = "/path/to/chrome"
        mock_instance.get_browser_args.return_value = ["--remote-debugging-port=9222"]

        cli = BrowserScreenshotCLI()
        with patch("urllib.request.urlopen", side_effect=Exception("no connection")):
            result = cli.run()
            assert "Started chrome" in result
            mock_popen.assert_called_once()

    @patch("brosh.cli.BrowserManager")
    @patch("brosh.cli.subprocess.Popen")
    def test_cli_run_force_restart(self, mock_popen: MagicMock, mock_browser_manager: MagicMock) -> None:
        """Test `run` command with `force_run` flag."""
        mock_instance = mock_browser_manager.return_value
        mock_instance.get_browser_name.return_value = "chrome"
        mock_instance.find_browser_path.return_value = "/path/to/chrome"
        mock_instance.get_browser_args.return_value = ["--remote-debugging-port=9222"]
        cli = BrowserScreenshotCLI()
        with patch("urllib.request.urlopen"), patch.object(cli, "quit", return_value=None) as mock_quit:
            result = cli.run(force_run=True)
            mock_quit.assert_called_once()
            assert "Started chrome" in result
            mock_popen.assert_called_once()

    @patch("brosh.cli.capture_webpage")
    def test_cli_capture_basic(self, mock_capture: MagicMock, temp_output_dir: Path) -> None:
        """Test basic capture functionality."""
        mock_capture.return_value = {str(temp_output_dir / "test.png"): {"selector": "body", "text": "..."}}
        cli = BrowserScreenshotCLI(output_dir=str(temp_output_dir))
        result = cli.shot("http://example.com")
        assert result
        mock_capture.assert_called_once()

    @patch("brosh.cli.capture_webpage")
    def test_cli_with_different_browsers(self, mock_capture: MagicMock, temp_output_dir: Path) -> None:
        """Test CLI with different browser selections."""
        for browser in ["chrome", "edge", "safari"]:
            cli = BrowserScreenshotCLI(app=browser, output_dir=str(temp_output_dir))
            cli.shot("http://example.com")
            mock_capture.assert_called_once()
            if "app" in mock_capture.call_args.kwargs:
                assert mock_capture.call_args.kwargs["app"] == browser
            mock_capture.reset_mock()

    @patch("platformdirs.user_pictures_dir")
    def test_cli_output_directory_handling(self, mock_user_pictures_dir: MagicMock, temp_output_dir: Path) -> None:
        """Test output directory handling in CLI."""
        mock_user_pictures_dir.return_value = "/home/user/Pictures"
        cli_default = BrowserScreenshotCLI()
        # Check that the output_dir is based on the mocked pictures directory
        assert str(cli_default.output_dir).endswith("Pictures/brosh")

        cli_custom = BrowserScreenshotCLI(output_dir=str(temp_output_dir))
        assert Path(cli_custom.output_dir) == temp_output_dir

    @patch("brosh.cli.BrowserManager")
    def test_cli_verbose_logging(self, mock_browser_manager: MagicMock) -> None:
        """Test verbose logging configuration."""
        with patch("brosh.cli.logger") as mock_logger:
            # Test non-verbose mode
            BrowserScreenshotCLI(verbose=False)
            mock_logger.remove.assert_called()
            mock_logger.add.assert_called()

            # Reset mocks
            mock_logger.reset_mock()

            # Test verbose mode
            BrowserScreenshotCLI(verbose=True)
            # Verbose mode should not call remove/add
            mock_logger.remove.assert_not_called()

    @patch("brosh.cli.BrowserManager")
    def test_cli_with_different_browsers(self, mock_browser_manager: MagicMock) -> None:
        """Test CLI with different browser configurations."""
        browsers = ["chrome", "firefox", "edge", "safari"]

        for browser in browsers:
            cli = BrowserScreenshotCLI(app=browser)
            assert cli.app == browser


class TestCLIIntegration:
    """Test CLI integration scenarios."""

    @patch("brosh.cli.capture_webpage")
    @patch("brosh.cli.BrowserManager")
    def test_cli_screenshot_workflow(
        self, mock_browser_manager: MagicMock, mock_capture: MagicMock, temp_output_dir: Path
    ) -> None:
        """Test a complete screenshot workflow."""
        # Mock the capture result
        expected_result = {
            str(temp_output_dir / "example_com.png"): {
                "selector": "body",
                "text": "Page content",
                "html": "<body>Page content</body>",
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
    def test_cli_parameter_validation(self, mock_browser_manager: MagicMock) -> None:
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
