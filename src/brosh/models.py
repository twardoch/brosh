#!/usr/bin/env python3
# this_file: src/brosh/models.py

"""Data models and enums for the brosh package."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Literal

from platformdirs import user_pictures_dir
from pydantic import BaseModel, Field
from pydantic.networks import AnyUrl


class ImageFormat(str, Enum):
    """Supported image output formats.

    Used in:
    - __init__.py
    - api.py
    - cli.py
    - mcp.py
    - tool.py
    """

    PNG = "png"
    JPG = "jpg"
    APNG = "apng"

    @property
    def mime_type(self) -> str:
        """Get the MIME type for this image format."""
        mime_types = {
            self.PNG: "image/png",
            self.JPG: "image/jpeg",
            self.APNG: "image/apng",
        }
        return mime_types[self]

    @property
    def file_extension(self) -> str:
        """Get the file extension for this image format."""
        extensions = {
            self.PNG: ".png",
            self.JPG: ".jpg",
            self.APNG: ".apng",
        }
        return extensions[self]

    @classmethod
    def from_mime_type(cls, mime_type: str) -> "ImageFormat":
        """Create an ImageFormat from a MIME type."""
        mime_map = {
            "image/png": cls.PNG,
            "image/jpeg": cls.JPG,
            "image/jpg": cls.JPG,
            "image/apng": cls.APNG,
        }
        if mime_type not in mime_map:
            msg = f"Unsupported MIME type: {mime_type}"
            raise ValueError(msg)
        return mime_map[mime_type]

    @classmethod
    def from_extension(cls, extension: str) -> "ImageFormat":
        """Create an ImageFormat from a file extension."""
        if not extension.startswith("."):
            extension = f".{extension}"
        ext_map = {
            ".png": cls.PNG,
            ".jpg": cls.JPG,
            ".jpeg": cls.JPG,
            ".apng": cls.APNG,
        }
        if extension.lower() not in ext_map:
            msg = f"Unsupported file extension: {extension}"
            raise ValueError(msg)
        return ext_map[extension.lower()]


@dataclass
class CaptureFrame:
    """Represents a single captured viewport frame with metadata.

    Used in:
    - capture.py
    - tool.py
    """

    image_bytes: bytes
    scroll_position_y: int
    page_height: int
    viewport_height: int
    active_selector: str
    visible_html: str | None = None
    visible_text: str | None = None
    timestamp: datetime | None = None

    @property
    def scroll_percentage(self) -> int:
        """Calculate scroll position as percentage."""
        return min(int((self.scroll_position_y / self.page_height) * 10000), 9999)


@dataclass
class BrowserConfig:
    """Browser-specific configuration."""

    debug_port: int
    app_name: str
    platform_support: list[str]
    launch_args: list[str]
    executable_paths: list[str]


@dataclass
class CaptureConfig:
    """Screenshot capture configuration - unified parameter set.

    Used in:
    - __init__.py
    - api.py
    - capture.py
    - tool.py
    """

    url: str
    width: int = 0
    height: int = 0
    zoom: int = 100
    scroll_step: int = 100
    scale: int = 100
    format: ImageFormat = ImageFormat.PNG
    app: str = ""
    output_dir: str = ""
    subdirs: bool = False
    anim_spf: float = 0.5
    html: bool = False
    max_frames: int = 0
    from_selector: str = ""

    def validate(self) -> None:
        """Validate configuration parameters.

        Used in:
        - api.py
        """
        if not self.url.startswith(("http://", "https://")):
            msg = f"Invalid URL: {self.url}"
            raise ValueError(msg)
        if not 10 <= self.zoom <= 500:
            msg = f"Zoom must be between 10-500%: {self.zoom}"
            raise ValueError(msg)
        if not 10 <= self.scroll_step <= 200:
            msg = f"Scroll step must be between 10-200%: {self.scroll_step}"
            raise ValueError(msg)
        if not 10 <= self.scale <= 200:
            msg = f"Scale must be between 10-200%: {self.scale}"
            raise ValueError(msg)


@dataclass
class CaptureResult:
    """Unified result structure for all capture operations.

    Used in:
    - api.py
    """

    frames: dict[str, dict[str, Any]]  # path -> metadata
    format: ImageFormat
    total_frames: int
    capture_time: datetime


class MCPResource(BaseModel):
    """Model for MCP resource content."""

    uri: str = Field(..., description="Resource URI")
    mime_type: str = Field(..., description="MIME type of the resource")
    text: str | None = Field(
        None,
        description="Text content if available",
    )
    blob: str | None = Field(
        None,
        description="Base64-encoded binary data",
    )


class MCPTextContent(BaseModel):
    """Model for MCP text content items.

    Used in:
    - mcp.py
    """

    type: Literal["text"] = Field(default="text")
    text: str = Field(..., description="Text content")

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Override to ensure exclude_none is always True.

        Used in:
        - mcp.py
        """
        kwargs["exclude_none"] = True
        return super().model_dump(**kwargs)


class MCPImageContent(BaseModel):
    """Model for MCP image content items.

    Used in:
    - mcp.py
    """

    type: Literal["image"] = Field(default="image")
    data: str = Field(..., description="Base64-encoded image data")
    mime_type: str = Field(..., description="MIME type for image content", serialization_alias="mimeType")

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Override to ensure exclude_none is always True and use by_alias.

        Used in:
        - mcp.py
        """
        kwargs["exclude_none"] = True
        kwargs["by_alias"] = True
        return super().model_dump(**kwargs)


class MCPContentItem(BaseModel):
    """Model for MCP content items."""

    type: str = Field(
        ...,
        description="Content type (text, image, resource)",
    )
    text: str | None = Field(
        None,
        description="Text content if type is text",
    )
    data: str | None = Field(
        None,
        description="Base64-encoded data for binary content",
    )
    mime_type: str | None = Field(
        None,
        description="MIME type for binary content",
    )
    resource: MCPResource | None = Field(
        None,
        description="Resource content",
    )

    def to_camel_dict(self) -> dict[str, Any]:
        """Return a dict with camelCase keys for MCP output."""
        d = self.dict(exclude_none=True)
        if "mime_type" in d:
            d["mimeType"] = d.pop("mime_type")
        return d


class MCPScreenshotResult(BaseModel):
    """Model for MCP screenshot result metadata."""

    image: MCPImageContent = Field(..., description="Screenshot image data")
    selector: str = Field(
        "body",
        description="CSS selector for visible element",
    )
    text: str | None = Field(
        None,
        description="Extracted text content",
    )
    html: str | None = Field(
        None,
        description="Extracted HTML content",
    )

    def metadata_json(self, path: str) -> str:
        """Return JSON metadata for the text content item, keyed by file path."""
        import json

        meta = {
            path: {
                "selector": self.selector,
                "text": self.text,
            }
        }
        if self.html is not None:
            meta[path]["html"] = self.html
        return json.dumps(meta, ensure_ascii=False)


class MCPToolResult(BaseModel):
    """Model for MCP tool results.

    Used in:
    - mcp.py
    """

    content: list[MCPTextContent | MCPImageContent] = Field(
        ...,
        description="Content items in the result",
    )

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Override to ensure proper serialization of content items.

        Used in:
        - mcp.py
        """
        kwargs["exclude_none"] = True
        # First get the raw data without dumping the content items
        data = super().model_dump(**kwargs, mode="python")
        # Now manually serialize each content item with its own model_dump method
        if "content" in data and self.content:
            serialized_content = []
            for item in self.content:
                # Each item should use its own model_dump method
                serialized_content.append(item.model_dump())
            data["content"] = serialized_content
        return data
