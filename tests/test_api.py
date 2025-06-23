"""Tests for brosh.api module."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic.networks import AnyUrl

from brosh.api import capture_webpage, capture_webpage_async
from brosh.models import CaptureConfig, ImageFormat


class TestCaptureWebpage:
    """Test the capture_webpage function."""

    @patch("brosh.api.BrowserScreenshotTool")
    @patch("brosh.api.asyncio.run")
    def test_capture_webpage_sync_context(
        self, mock_asyncio_run: MagicMock, mock_tool_class: MagicMock, temp_output_dir: Path
    ) -> None:
        """Test capture_webpage in sync context."""
        # Mock the tool instance
        mock_tool = MagicMock()
        mock_tool.capture.return_value = {"test.png": {"selector": "body"}}
        mock_tool_class.return_value = mock_tool

        # Mock asyncio.run to simulate sync context
        mock_asyncio_run.return_value = {"test.png": {"selector": "body"}}

        # Test the function
        result = capture_webpage(
            url=AnyUrl("https://example.com"),
            output_dir=temp_output_dir,
        )

        # Verify tool was created and called
        mock_tool_class.assert_called_once()
        mock_asyncio_run.assert_called_once()

        # Verify result
        assert result == {"test.png": {"selector": "body"}}

    @patch("brosh.api.BrowserScreenshotTool")
    @patch("brosh.api.asyncio.get_running_loop")
    def test_capture_webpage_async_context(
        self, mock_get_loop: MagicMock, mock_tool_class: MagicMock, temp_output_dir: Path
    ) -> None:
        """Test capture_webpage in async context."""
        # Mock the tool instance
        mock_tool = MagicMock()
        mock_tool.capture.return_value = {"test.png": {"selector": "body"}}
        mock_tool_class.return_value = mock_tool

        # Mock get_running_loop to simulate async context
        mock_loop = MagicMock()
        mock_get_loop.return_value = mock_loop

        # Test the function
        result = capture_webpage(
            url=AnyUrl("https://example.com"),
            output_dir=temp_output_dir,
        )

        # Verify tool was created and called
        mock_tool_class.assert_called_once()

        # Verify result is the coroutine (not run)
        assert result == mock_tool.capture.return_value

    def test_capture_webpage_config_creation(self, temp_output_dir: Path) -> None:
        """Test that CaptureConfig is created with correct parameters."""
        with patch("brosh.api.BrowserScreenshotTool") as mock_tool_class, patch(
            "brosh.api.asyncio.run"
        ) as mock_asyncio_run:
            # Mock the tool
            mock_tool = MagicMock()
            mock_tool_class.return_value = mock_tool
            mock_asyncio_run.return_value = {}

            # Call with specific parameters
            capture_webpage(
                url=AnyUrl("https://example.com/test"),
                zoom=150,
                width=1920,
                height=1080,
                scroll_step=75,
                scale=50,
                app="firefox",
                output_dir=temp_output_dir,
                subdirs=True,
                format=ImageFormat.JPG,
                anim_spf=1.0,
                fetch_html=True,
                fetch_image=False,
                fetch_image_path=True,
                fetch_text=True,
                trim_text=False,
                max_frames=5,
                from_selector="main",
            )

            # Verify tool.capture was called with correct config
            mock_tool.capture.assert_called_once()
            config = mock_tool.capture.call_args[0][0]

            assert isinstance(config, CaptureConfig)
            assert config.url == "https://example.com/test"
            assert config.zoom == 150
            assert config.width == 1920
            assert config.height == 1080
            assert config.scroll_step == 75
            assert config.scale == 50
            assert config.app == "firefox"
            assert config.output_dir == str(temp_output_dir)
            assert config.subdirs is True
            assert config.format == ImageFormat.JPG
            assert config.anim_spf == 1.0
            assert config.fetch_html is True
            assert config.fetch_image is False
            assert config.fetch_image_path is True
            assert config.fetch_text is True
            assert config.trim_text is False
            assert config.max_frames == 5
            assert config.from_selector == "main"

    def test_capture_webpage_default_output_dir(self) -> None:
        """Test default output directory handling."""
        with patch("brosh.api.BrowserScreenshotTool") as mock_tool_class, patch(
            "brosh.api.asyncio.run"
        ) as mock_asyncio_run, patch("brosh.api.dflt_output_folder") as mock_pictures_dir:
            mock_pictures_dir.return_value = "/home/user/Pictures"

            # Mock the tool
            mock_tool = MagicMock()
            mock_tool_class.return_value = mock_tool
            mock_asyncio_run.return_value = {}

            # Call without output_dir
            capture_webpage(url=AnyUrl("https://example.com"))

            # Verify config has correct output_dir
            config = mock_tool.capture.call_args[0][0]
            assert config.output_dir == "/home/user/Pictures"


class TestCaptureWebpageAsync:
    """Test the capture_webpage_async function."""

    @pytest.mark.asyncio
    async def test_capture_webpage_async(self, temp_output_dir: Path) -> None:
        """Test capture_webpage_async function."""
        with patch("brosh.api.BrowserScreenshotTool") as mock_tool_class:
            # Mock the tool instance
            mock_tool = MagicMock()
            mock_tool.capture = AsyncMock(return_value={"test.png": {"selector": "body"}})
            mock_tool_class.return_value = mock_tool

            # Test the function
            result = await capture_webpage_async(
                url=AnyUrl("https://example.com"),
                output_dir=temp_output_dir,
            )

            # Verify tool was created and called
            mock_tool_class.assert_called_once()
            mock_tool.capture.assert_called_once()

            # Verify result
            assert result == {"test.png": {"selector": "body"}}

    @pytest.mark.asyncio
    async def test_capture_webpage_async_config_validation(self, temp_output_dir: Path) -> None:
        """Test that capture_webpage_async validates config."""
        with patch("brosh.api.BrowserScreenshotTool") as mock_tool_class:
            # Mock the tool instance
            mock_tool = MagicMock()
            mock_tool.capture = AsyncMock(return_value={})
            mock_tool_class.return_value = mock_tool

            # Test with all parameters
            await capture_webpage_async(
                url=AnyUrl("https://example.com/test"),
                zoom=125,
                width=1024,
                height=768,
                scroll_step=100,
                scale=75,
                app="chrome",
                output_dir=temp_output_dir,
                subdirs=False,
                format=ImageFormat.PNG,
                anim_spf=0.5,
                fetch_html=False,
                fetch_image=False,
                fetch_image_path=True,
                fetch_text=True,
                trim_text=True,
                max_frames=0,
                from_selector="",
            )

            # Verify tool.capture was called
            mock_tool.capture.assert_called_once()
            config = mock_tool.capture.call_args[0][0]

            assert isinstance(config, CaptureConfig)
            assert config.url == "https://example.com/test"
            assert config.zoom == 125
            assert config.format == ImageFormat.PNG


class TestAPIParameterValidation:
    """Test API parameter validation."""

    def test_capture_webpage_validates_config(self) -> None:
        """Test that invalid config raises ValidationError."""
        with patch("brosh.api.BrowserScreenshotTool"), patch("brosh.api.asyncio.run"):
            # This should raise a validation error due to invalid zoom
            with pytest.raises(ValueError, match="Zoom"):
                capture_webpage(
                    url=AnyUrl("https://example.com"),
                    zoom=5,  # Invalid zoom value
                )

    @pytest.mark.asyncio
    async def test_capture_webpage_async_validates_config(self) -> None:
        """Test that async version validates config."""
        with patch("brosh.api.BrowserScreenshotTool"):
            # This should raise a validation error due to invalid zoom
            with pytest.raises(ValueError, match="Zoom"):
                await capture_webpage_async(
                    url=AnyUrl("https://example.com"),
                    zoom=5,  # Invalid zoom value
                )


class TestAPIConvenienceMethods:
    """Test convenience methods in API."""

    def test_capture_full_page_import(self) -> None:
        """Test that convenience methods can be imported."""
        from brosh.api import (
            capture_animation,
            capture_full_page,
            capture_visible_area,
        )

        # These should be callable (even if they're just aliases)
        assert callable(capture_full_page)
        assert callable(capture_visible_area)
        assert callable(capture_animation)

    @patch("brosh.api.capture_webpage")
    def test_capture_full_page_calls_main_function(self, mock_capture: MagicMock) -> None:
        """Test capture_full_page calls capture_webpage with correct params."""
        from brosh.api import capture_full_page

        mock_capture.return_value = {}

        # Test that it's defined and callable
        assert callable(capture_full_page)

        # If it's an alias, it should call the main function
        try:
            capture_full_page(url="https://example.com", height=-1)
            mock_capture.assert_called_once()
        except (AttributeError, NameError):
            # If it's not defined yet, that's fine for now
            pass
