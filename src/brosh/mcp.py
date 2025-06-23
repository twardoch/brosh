#!/usr/bin/env python3
# this_file: src/brosh/mcp.py

"""MCP server implementation for brosh."""

import base64
import json
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from loguru import logger

from .api import capture_webpage_async
from .models import ImageFormat, MCPImageContent, MCPTextContent, MCPToolResult
from .texthtml import DOMProcessor
from .tool import dflt_output_folder

# MCP has different defaults than CLI
MCP_DEFAULTS = {
    "scale": 50,  # Default to 50% scaling for MCP to reduce size
}

TRIM_TEXT_LENGTH = 200
MCP_MAX_SIZE_BYTES = 1024 * 1024  # 1MB
MCP_COMPRESSION_DOWNSAMPLE_PERCENTAGE = 50


def run_mcp_server() -> None:
    """Run FastMCP server for browser screenshots.

    Used in:
    - cli.py
    """

    mcp = FastMCP(
        name="Brosh Web Capture",
        instructions="Get a screenshot of a webpage in vertical slices together with text and/or HTML content.",
    )

    # Define the MCP tool function with explicit parameters matching api.capture_webpage
    # This avoids **kwargs which FastMCP doesn't support
    async def see_webpage(
        url: str,
        zoom: int = 100,
        width: int = 0,
        height: int = 0,
        scroll_step: int = 100,
        scale: int = 50,  # MCP default: lower scale for smaller images
        app: str = "",
        output_dir: str = "",
        *,
        subdirs: bool = False,
        output_format: str = "png",
        anim_spf: float = 0.5,
        fetch_html: bool = False,
        fetch_image: bool = False,
        fetch_image_path: bool = True,
        fetch_text: bool = True,
        trim_text: bool = True,
        max_frames: int = 0,
        from_selector: str = "",
    ) -> MCPToolResult:
        """Get screenshots and text or HTML from a webpage.

        Captures scrolling screenshots of a webpage with various configuration options.
        Optimized for AI tools with smaller default image scale.

        Args:
            url: The webpage URL to capture
            zoom: Browser zoom level (10-500%)
            width: Viewport width in pixels (0 for screen width)
            height: Viewport height in pixels (0 for screen height, -1 for full page)
            scroll_step: Vertical scroll increment as percentage of viewport
            scale: Output image scaling factor (default 50% for MCP)
            app: Browser to use (chrome/edge/safari, empty for auto-detect)
            output_dir: Directory to save screenshots (empty for default)
            subdirs: Whether to create domain-based subdirectories
            format: Output image format (png, jpg, apng)
            anim_spf: Animation speed for APNG format
            fetch_html: Whether to include HTML content in results
            fetch_image: Whether to include image data in results (default False)
            fetch_image_path: Whether to include image path in results (default True)
            fetch_text: Whether to include extracted text in results (default True)
            trim_text: Whether to trim text to 200 characters (default True)
            max_frames: Maximum frames to capture (0 for unlimited)
            from_selector: CSS selector to scroll to before starting capture

        Returns:
            MCPToolResult with screenshots and optional HTML content

        """
        try:
            # Convert string parameters to proper types for the API
            format_enum = ImageFormat(output_format.lower()) # Use output_format
            output_path = Path(output_dir) if output_dir else Path(dflt_output_folder())

            # Build kwargs for the API call
            api_kwargs = {
                "url": url,
                "zoom": zoom,
                "width": width,
                "height": height,
                "scroll_step": scroll_step,
                "scale": scale,
                "app": app,
                "output_dir": output_path,
                "subdirs": subdirs,
                "output_format": format_enum, # Use output_format
                "anim_spf": anim_spf,
                "fetch_html": fetch_html,
                "fetch_image": False,  # FIXME: fetch_image,
                "fetch_image_path": fetch_image_path,
                "fetch_text": fetch_text,
                "trim_text": trim_text,
                "max_frames": max_frames,
                "from_selector": from_selector,
            }

            # Call the unified API
            result = await capture_webpage_async(**api_kwargs)

            # Process results for MCP format
            return _convert_to_mcp_result(
                result,
                format_enum,
                fetch_image=fetch_image,
                fetch_image_path=fetch_image_path,
                fetch_text=fetch_text,
                fetch_html=fetch_html,
                trim_text=trim_text,
            )

        except Exception as e:
            logger.error(f"MCP capture failed: {e}")
            return MCPToolResult(content=[MCPTextContent(text=f"Error: {e!s}")])

    # Register the tool with mcp
    mcp.tool(see_webpage)

    mcp.run()


def _convert_to_mcp_result(
    capture_result: dict[str, dict[str, Any]],
    output_format: ImageFormat, # Renamed from format
    *,
    fetch_image: bool = False,
    fetch_image_path: bool = True,
    fetch_text: bool = True,
    fetch_html: bool = False,
    trim_text: bool = True,
) -> MCPToolResult:
    """Convert standard capture results to MCP format with configurable output.

    Args:
        capture_result: Results from capture_webpage
        format: Image format used
        fetch_image: Whether to include image data
        fetch_image_path: Whether to include image path
        fetch_text: Whether to include extracted text
        fetch_html: Whether to include HTML content
        trim_text: Whether to trim text to 200 characters

    Returns:
        MCPToolResult with configured content items

    """
    content_items = []
    dom_processor = DOMProcessor()

    for filepath, metadata in capture_result.items():
        try:
            # Only process image if fetch_image is True
            if fetch_image:
                with open(filepath, "rb") as f:
                    image_bytes = f.read()

                image_content = MCPImageContent(
                    data=base64.b64encode(image_bytes).decode(),
                    mime_type=(output_format.mime_type if isinstance(output_format, ImageFormat) else "image/png"), # Use output_format
                )
                content_items.append(image_content)

            # Build metadata based on flags
            meta_dict = {}

            if fetch_image_path:
                meta_dict["image_path"] = filepath

            meta_dict["selector"] = metadata.get("selector", "body")

            if fetch_text:
                text = metadata.get("text", "")
                if trim_text and len(text) > TRIM_TEXT_LENGTH:
                    text = f"{text[:TRIM_TEXT_LENGTH]}..."
                meta_dict["text"] = text

            if fetch_html and "html" in metadata:
                compressed = dom_processor.compress_html(metadata["html"])
                meta_dict["html"] = compressed

            # Only add text content if there's something to add
            if meta_dict:
                content_items.append(MCPTextContent(text=json.dumps(meta_dict)))

        except Exception as e:
            logger.error(f"Failed to process {filepath}: {e}")

    # Apply size limits
    return _apply_size_limits(MCPToolResult(content=content_items))


def _apply_size_limits(result: MCPToolResult) -> MCPToolResult:
    """Apply MCP size limits to results.

    Progressive strategy:
    1. Remove all but first HTML
    2. Downsample images by 50%
    3. Downsample again by 50%
    4. Remove screenshots from end

    Args:
        result: MCPToolResult to process

    Returns:
        Size-limited MCPToolResult

    """
    # Calculate initial size
    result_dict = result.model_dump()
    size = len(json.dumps(result_dict).encode("utf-8"))

    if size <= MCP_MAX_SIZE_BYTES:
        return result

    logger.warning(f"Result size {size} exceeds limit {MCP_MAX_SIZE_BYTES}, applying compression")

    # Step 1: Remove all but first HTML
    new_content = []
    html_found = False

    for item in result.content:
        if isinstance(item, MCPTextContent):
            try:
                data = json.loads(item.text)
                if isinstance(data, dict):
                    for path, metadata in data.items():
                        if "html" in metadata and html_found:
                            metadata.pop("html", None)
                            item = MCPTextContent(text=json.dumps({path: metadata}))
                        elif "html" in metadata:
                            html_found = True
            except Exception:
                pass
        new_content.append(item)

    result = MCPToolResult(content=new_content)
    size = len(json.dumps(result.model_dump()).encode("utf-8"))

    if size <= MCP_MAX_SIZE_BYTES:
        return result

    # Step 2: Downsample images
    from .image import ImageProcessor

    processor = ImageProcessor()

    new_content = []
    for item in result.content:
        if isinstance(item, MCPImageContent):
            try:
                img_data = base64.b64decode(item.data)
                downsampled = processor.downsample_png_bytes(img_data, MCP_COMPRESSION_DOWNSAMPLE_PERCENTAGE)
                item = MCPImageContent(data=base64.b64encode(downsampled).decode(), mime_type=item.mime_type)
            except Exception as e:
                logger.error(f"Failed to downsample image: {e}")
        new_content.append(item)

    result = MCPToolResult(content=new_content)
    size = len(json.dumps(result.model_dump()).encode("utf-8"))

    if size <= MCP_MAX_SIZE_BYTES:
        return result

    # Step 3: Remove screenshots from end
    # Keep at least one image and one text block if possible (hence > 2)
    while len(result.content) > 2 and size > MCP_MAX_SIZE_BYTES:
        result.content = result.content[:-2]  # Remove an image and its corresponding text metadata
        size = len(json.dumps(result.model_dump()).encode("utf-8"))

    return result


def main() -> None:
    """Run the MCP server."""
    run_mcp_server()


if __name__ == "__main__":
    main()
