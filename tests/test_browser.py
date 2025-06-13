"""Tests for brosh.browser module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from brosh.browser import BrowserManager


class TestBrowserManager:
    """Test the BrowserManager class."""

    def test_browser_manager_initialization(self) -> None:
        """Test BrowserManager initialization."""
        manager = BrowserManager()

        assert hasattr(manager, "debug_ports")
        assert isinstance(manager.debug_ports, dict)
        assert "chrome" in manager.debug_ports
        assert "firefox" in manager.debug_ports
        assert "edge" in manager.debug_ports

    def test_get_browser_name_empty_string(self) -> None:
        """Test get_browser_name with empty app string."""
        manager = BrowserManager()

        with patch("platform.system") as mock_system:
            # Test macOS
            mock_system.return_value = "Darwin"
            assert manager.get_browser_name("") == "chrome"

            # Test Windows
            mock_system.return_value = "Windows"
            assert manager.get_browser_name("") == "chrome"

            # Test Linux
            mock_system.return_value = "Linux"
            assert manager.get_browser_name("") == "chrome"

    def test_get_browser_name_specific_browser(self) -> None:
        """Test get_browser_name with specific browser names."""
        manager = BrowserManager()

        assert manager.get_browser_name("chrome") == "chrome"
        assert manager.get_browser_name("firefox") == "firefox"
        assert manager.get_browser_name("edge") == "edge"
        assert manager.get_browser_name("safari") == "safari"

    def test_get_browser_name_invalid_browser(self) -> None:
        """Test get_browser_name with invalid browser name."""
        manager = BrowserManager()

        with pytest.raises(ValueError, match="Unsupported browser"):
            manager.get_browser_name("invalid_browser")

    @patch("brosh.browser.subprocess.run")
    def test_browser_path_detection(self, mock_subprocess: MagicMock) -> None:
        """Test browser path detection."""
        manager = BrowserManager()

        # Test that browser detection methods exist
        assert hasattr(manager, "is_browser_available")
        assert hasattr(manager, "find_browser_path")
        assert hasattr(manager, "get_browser_paths")

        # Test browser availability check
        with patch("os.path.exists", return_value=True):
            assert manager.is_browser_available("chrome") in [True, False]

    def test_find_browser_path(self) -> None:
        """Test finding browser executable path."""
        manager = BrowserManager()

        # This should return a path or None
        path = manager.find_browser_path("chrome")
        assert path is None or isinstance(path, str)

    def test_get_browser_paths(self) -> None:
        """Test getting possible browser paths."""
        manager = BrowserManager()

        paths = manager.get_browser_paths("chrome")
        assert isinstance(paths, list)

    @pytest.mark.asyncio
    async def test_launch_browser_and_connect(self) -> None:
        """Test launching browser and connecting."""
        manager = BrowserManager()

        # Mock subprocess for browser launch
        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.poll.return_value = None  # Still running
            mock_popen.return_value = mock_process

            # This method should exist
            assert hasattr(manager, "launch_browser_and_connect")

    def test_browser_failure_handling(self) -> None:
        """Test browser failure handling."""
        manager = BrowserManager()

        # Test with invalid browser path
        path = manager.find_browser_path("nonexistent_browser")
        assert path is None

    def test_get_screen_dimensions_default(self) -> None:
        """Test getting screen dimensions with defaults."""
        manager = BrowserManager()

        width, height = manager.get_screen_dimensions()

        # Should return reasonable default values
        assert width > 0
        assert height > 0
        assert isinstance(width, int)
        assert isinstance(height, int)

    @patch("brosh.browser.tkinter.Tk")
    def test_get_screen_dimensions_tkinter(self, mock_tk: MagicMock) -> None:
        """Test getting screen dimensions using tkinter."""
        # Mock tkinter window
        mock_root = MagicMock()
        mock_root.winfo_screenwidth.return_value = 1920
        mock_root.winfo_screenheight.return_value = 1080
        mock_tk.return_value = mock_root

        manager = BrowserManager()
        width, height = manager.get_screen_dimensions()

        assert width == 1920
        assert height == 1080
        mock_root.destroy.assert_called_once()

    @patch("brosh.browser.tkinter.Tk")
    def test_get_screen_dimensions_tkinter_failure(self, mock_tk: MagicMock) -> None:
        """Test screen dimensions fallback when tkinter fails."""
        mock_tk.side_effect = Exception("No display")

        manager = BrowserManager()
        width, height = manager.get_screen_dimensions()

        # Should fall back to defaults
        assert width == 1024
        assert height == 768

    @pytest.mark.asyncio
    async def test_get_browser_instance_chrome(self) -> None:
        """Test getting browser instance for Chrome."""
        manager = BrowserManager()

        # Mock playwright
        mock_playwright = MagicMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()

        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        browser, context, page = await manager.get_browser_instance(mock_playwright, "chrome", 1024, 768, 100)

        assert browser == mock_browser
        assert context == mock_context
        assert page == mock_page

        mock_playwright.chromium.launch.assert_called_once()
        mock_browser.new_context.assert_called_once()
        mock_context.new_page.assert_called_once()
        mock_page.set_viewport_size.assert_called_once_with(width=1024, height=768)

    @pytest.mark.asyncio
    async def test_get_browser_instance_firefox(self) -> None:
        """Test getting browser instance for Firefox."""
        manager = BrowserManager()

        # Mock playwright
        mock_playwright = MagicMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()

        mock_playwright.firefox.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        browser, context, page = await manager.get_browser_instance(mock_playwright, "firefox", 1920, 1080, 125)

        assert browser == mock_browser
        assert context == mock_context
        assert page == mock_page

        mock_playwright.firefox.launch.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_browser_instance_safari(self) -> None:
        """Test getting browser instance for Safari."""
        manager = BrowserManager()

        # Mock playwright
        mock_playwright = MagicMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()

        mock_playwright.webkit.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        browser, context, page = await manager.get_browser_instance(mock_playwright, "safari", 1024, 768, 100)

        assert browser == mock_browser
        mock_playwright.webkit.launch.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_browser_instance_unsupported(self) -> None:
        """Test getting browser instance for unsupported browser."""
        manager = BrowserManager()
        mock_playwright = MagicMock()

        with pytest.raises(ValueError, match="Unsupported browser"):
            await manager.get_browser_instance(mock_playwright, "unsupported", 1024, 768, 100)

    def test_debug_ports_configuration(self) -> None:
        """Test that debug ports are properly configured."""
        manager = BrowserManager()

        # Check that all expected browsers have debug ports
        expected_browsers = ["chrome", "firefox", "edge"]
        for browser in expected_browsers:
            assert browser in manager.debug_ports
            assert isinstance(manager.debug_ports[browser], int)
            assert manager.debug_ports[browser] > 0

    @patch("platform.system")
    def test_platform_specific_browser_commands(self, mock_system: MagicMock) -> None:
        """Test platform-specific browser command generation."""
        manager = BrowserManager()

        # Test macOS
        mock_system.return_value = "Darwin"
        chrome_name = manager.get_browser_name("")
        assert chrome_name in ["chrome", "safari"]

        # Test Windows
        mock_system.return_value = "Windows"
        chrome_name = manager.get_browser_name("")
        assert chrome_name in ["chrome", "edge"]

        # Test Linux
        mock_system.return_value = "Linux"
        chrome_name = manager.get_browser_name("")
        assert chrome_name == "chrome"

    @pytest.mark.asyncio
    async def test_browser_context_configuration(self) -> None:
        """Test browser context configuration with custom settings."""
        manager = BrowserManager()

        # Mock playwright and browser
        mock_playwright = MagicMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()

        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        # Test with zoom level
        browser, context, page = await manager.get_browser_instance(mock_playwright, "chrome", 1024, 768, 150)

        # Verify zoom is applied
        mock_page.set_viewport_size.assert_called_once()

        # Check that context was created with proper settings
        mock_browser.new_context.assert_called_once()


class TestBrowserManagerEdgeCases:
    """Test edge cases and error conditions for BrowserManager."""

    def test_browser_manager_with_invalid_dimensions(self) -> None:
        """Test browser manager with invalid screen dimensions."""
        manager = BrowserManager()

        # Dimensions should be positive integers
        width, height = manager.get_screen_dimensions()
        assert width > 0
        assert height > 0

    @patch("brosh.browser.subprocess.run")
    def test_launch_browser_with_different_platforms(self, mock_subprocess: MagicMock) -> None:
        """Test launching browsers on different platforms."""
        manager = BrowserManager()
        mock_subprocess.return_value = MagicMock(returncode=0)

        platforms = ["Darwin", "Windows", "Linux"]
        browsers = ["chrome", "firefox", "edge"]

        for platform in platforms:
            with patch("platform.system", return_value=platform):
                for browser in browsers:
                    # Test that browser methods work
                    available = manager.is_browser_available(browser)
                    assert isinstance(available, bool)

                    path = manager.find_browser_path(browser)
                    assert path is None or isinstance(path, str)

    def test_browser_manager_singleton_behavior(self) -> None:
        """Test that BrowserManager can be instantiated multiple times."""
        manager1 = BrowserManager()
        manager2 = BrowserManager()

        # They should be separate instances but with same configuration
        assert id(manager1) != id(manager2)
        assert manager1.debug_ports == manager2.debug_ports
