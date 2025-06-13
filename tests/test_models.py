"""Tests for brosh.models module."""

from datetime import datetime
from pathlib import Path

import pytest

from brosh.models import (
    CaptureConfig,
    CaptureFrame,
    CaptureResult,
    ImageFormat,
    MCPImageContent,
    MCPTextContent,
    MCPToolResult,
)


class TestImageFormat:
    """Test the ImageFormat enum."""

    def test_mime_type_property(self) -> None:
        """Test that mime_type property returns correct MIME types."""
        assert ImageFormat.PNG.mime_type == "image/png"
        assert ImageFormat.JPG.mime_type == "image/jpeg"
        assert ImageFormat.APNG.mime_type == "image/apng"

    def test_file_extension_property(self) -> None:
        """Test that file_extension property returns correct extensions."""
        assert ImageFormat.PNG.file_extension == ".png"
        assert ImageFormat.JPG.file_extension == ".jpg"
        assert ImageFormat.APNG.file_extension == ".apng"

    def test_from_mime_type_valid(self) -> None:
        """Test creating ImageFormat from valid MIME types."""
        assert ImageFormat.from_mime_type("image/png") == ImageFormat.PNG
        assert ImageFormat.from_mime_type("image/jpeg") == ImageFormat.JPG
        assert ImageFormat.from_mime_type("image/jpg") == ImageFormat.JPG
        assert ImageFormat.from_mime_type("image/apng") == ImageFormat.APNG

    def test_from_mime_type_invalid(self) -> None:
        """Test error handling for invalid MIME types."""
        with pytest.raises(ValueError, match="Unsupported MIME type"):
            ImageFormat.from_mime_type("image/gif")

    def test_from_extension_valid(self) -> None:
        """Test creating ImageFormat from valid file extensions."""
        assert ImageFormat.from_extension(".png") == ImageFormat.PNG
        assert ImageFormat.from_extension("png") == ImageFormat.PNG
        assert ImageFormat.from_extension(".jpg") == ImageFormat.JPG
        assert ImageFormat.from_extension("jpg") == ImageFormat.JPG
        assert ImageFormat.from_extension(".jpeg") == ImageFormat.JPG
        assert ImageFormat.from_extension("jpeg") == ImageFormat.JPG
        assert ImageFormat.from_extension(".apng") == ImageFormat.APNG

    def test_from_extension_case_insensitive(self) -> None:
        """Test that extension parsing is case-insensitive."""
        assert ImageFormat.from_extension(".PNG") == ImageFormat.PNG
        assert ImageFormat.from_extension(".JPG") == ImageFormat.JPG

    def test_from_extension_invalid(self) -> None:
        """Test error handling for invalid file extensions."""
        with pytest.raises(ValueError, match="Unsupported file extension"):
            ImageFormat.from_extension(".gif")


class TestCaptureFrame:
    """Test the CaptureFrame dataclass."""

    def test_capture_frame_creation(self) -> None:
        """Test creating a CaptureFrame with required fields."""
        frame = CaptureFrame(
            image_bytes=b"test_image_data",
            scroll_position_y=100,
            page_height=2000,
            viewport_height=800,
            active_selector="main",
        )

        assert frame.image_bytes == b"test_image_data"
        assert frame.scroll_position_y == 100
        assert frame.page_height == 2000
        assert frame.viewport_height == 800
        assert frame.active_selector == "main"
        assert frame.visible_html is None
        assert frame.visible_text is None
        assert frame.timestamp is None

    def test_capture_frame_with_optional_fields(self) -> None:
        """Test creating a CaptureFrame with all fields."""
        from datetime import timezone

        timestamp = datetime.now(tz=timezone.utc)
        frame = CaptureFrame(
            image_bytes=b"test_image_data",
            scroll_position_y=100,
            page_height=2000,
            viewport_height=800,
            active_selector="main",
            visible_html="<div>Test</div>",
            visible_text="Test content",
            timestamp=timestamp,
        )

        assert frame.visible_html == "<div>Test</div>"
        assert frame.visible_text == "Test content"
        assert frame.timestamp == timestamp


class TestCaptureConfig:
    """Test the CaptureConfig class."""

    def test_capture_config_creation_minimal(self) -> None:
        """Test creating CaptureConfig with minimal required fields."""
        config = CaptureConfig(url="https://example.com")

        assert config.url == "https://example.com"
        assert config.width == 0
        assert config.height == 0
        assert config.zoom == 100
        assert config.format == ImageFormat.PNG
        assert config.trim_text is True  # Default value

    def test_capture_config_creation_full(self, temp_output_dir: Path) -> None:
        """Test creating CaptureConfig with all fields."""
        config = CaptureConfig(
            url="https://example.com/test",
            width=1920,
            height=1080,
            zoom=125,
            scroll_step=75,
            scale=150,
            format=ImageFormat.JPG,
            app="firefox",
            output_dir=str(temp_output_dir),
            subdirs=True,
            anim_spf=0.8,
            fetch_html=True,
            fetch_image=False,
            fetch_image_path=True,
            fetch_text=True,
            trim_text=False,
            max_frames=10,
            from_selector="main",
        )

        assert config.url == "https://example.com/test"
        assert config.width == 1920
        assert config.height == 1080
        assert config.zoom == 125
        assert config.scroll_step == 75
        assert config.scale == 150
        assert config.format == ImageFormat.JPG
        assert config.app == "firefox"
        assert config.output_dir == str(temp_output_dir)
        assert config.subdirs is True
        assert config.anim_spf == 0.8
        assert config.fetch_html is True
        assert config.fetch_image is False
        assert config.fetch_image_path is True
        assert config.fetch_text is True
        assert config.trim_text is False
        assert config.max_frames == 10
        assert config.from_selector == "main"

    def test_capture_config_validation_zoom(self) -> None:
        """Test CaptureConfig zoom validation."""
        # Valid zoom values
        config = CaptureConfig(url="https://example.com", zoom=50)
        config.validate()

        config = CaptureConfig(url="https://example.com", zoom=200)
        config.validate()

        # Invalid zoom values
        with pytest.raises(ValueError, match="Zoom must be between 10 and 500"):
            config = CaptureConfig(url="https://example.com", zoom=5)
            config.validate()

        with pytest.raises(ValueError, match="Zoom must be between 10 and 500"):
            config = CaptureConfig(url="https://example.com", zoom=600)
            config.validate()

    def test_capture_config_validation_scroll_step(self) -> None:
        """Test CaptureConfig scroll_step validation."""
        # Valid scroll_step values
        config = CaptureConfig(url="https://example.com", scroll_step=50)
        config.validate()

        config = CaptureConfig(url="https://example.com", scroll_step=150)
        config.validate()

        # Invalid scroll_step values
        with pytest.raises(ValueError, match="Scroll step must be between 10 and 200"):
            config = CaptureConfig(url="https://example.com", scroll_step=5)
            config.validate()

        with pytest.raises(ValueError, match="Scroll step must be between 10 and 200"):
            config = CaptureConfig(url="https://example.com", scroll_step=250)
            config.validate()

    def test_capture_config_validation_scale(self) -> None:
        """Test CaptureConfig scale validation."""
        # Valid scale values
        config = CaptureConfig(url="https://example.com", scale=25)
        config.validate()

        config = CaptureConfig(url="https://example.com", scale=150)
        config.validate()

        # Invalid scale values
        with pytest.raises(ValueError, match="Scale must be between 10 and 200"):
            config = CaptureConfig(url="https://example.com", scale=5)
            config.validate()

        with pytest.raises(ValueError, match="Scale must be between 10 and 200"):
            config = CaptureConfig(url="https://example.com", scale=250)
            config.validate()

    def test_capture_config_validation_height(self) -> None:
        """Test CaptureConfig height validation."""
        # Valid height values
        config = CaptureConfig(url="https://example.com", height=0)
        config.validate()

        config = CaptureConfig(url="https://example.com", height=-1)
        config.validate()

        config = CaptureConfig(url="https://example.com", height=1080)
        config.validate()

        # Invalid height values
        with pytest.raises(ValueError, match="Height must be -1, 0, or positive"):
            config = CaptureConfig(url="https://example.com", height=-5)
            config.validate()

    def test_capture_config_validation_anim_spf(self) -> None:
        """Test CaptureConfig anim_spf validation."""
        # Valid anim_spf values
        config = CaptureConfig(url="https://example.com", anim_spf=0.1)
        config.validate()

        config = CaptureConfig(url="https://example.com", anim_spf=5.0)
        config.validate()

        # Invalid anim_spf values
        with pytest.raises(ValueError, match="Animation SPF must be between 0.1 and 10.0"):
            config = CaptureConfig(url="https://example.com", anim_spf=0.05)
            config.validate()

        with pytest.raises(ValueError, match="Animation SPF must be between 0.1 and 10.0"):
            config = CaptureConfig(url="https://example.com", anim_spf=15.0)
            config.validate()


class TestCaptureResult:
    """Test the CaptureResult class."""

    def test_capture_result_creation(self, temp_output_dir: Path) -> None:
        """Test creating a CaptureResult."""
        from datetime import timezone

        frames = {str(temp_output_dir / "test.png"): {"selector": "main", "text": "Test content"}}

        result = CaptureResult(
            frames=frames,
            format=ImageFormat.PNG,
            total_frames=1,
            capture_time=datetime.now(tz=timezone.utc),
        )

        assert result.frames == frames
        assert result.format == ImageFormat.PNG
        assert result.total_frames == 1
        assert isinstance(result.capture_time, datetime)


class TestMCPModels:
    """Test MCP-related model classes."""

    def test_mcp_text_content(self) -> None:
        """Test MCPTextContent creation."""
        content = MCPTextContent(text="Test content")

        assert content.type == "text"
        assert content.text == "Test content"

    def test_mcp_image_content(self) -> None:
        """Test MCPImageContent creation."""
        content = MCPImageContent(data="base64_encoded_data", mime_type="image/png")

        assert content.type == "image"
        assert content.data == "base64_encoded_data"
        assert content.mime_type == "image/png"

    def test_mcp_tool_result(self) -> None:
        """Test MCPToolResult creation."""
        text_content = MCPTextContent(text="Test content")
        image_content = MCPImageContent(data="base64_data", mime_type="image/png")

        result = MCPToolResult(content=[text_content, image_content])

        assert len(result.content) == 2
        assert result.content[0] == text_content
        assert result.content[1] == image_content

    def test_mcp_tool_result_empty(self) -> None:
        """Test MCPToolResult creation with empty content."""
        result = MCPToolResult(content=[])

        assert len(result.content) == 0
