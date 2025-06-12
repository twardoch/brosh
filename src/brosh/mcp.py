#!/usr/bin/env python3
# this_file: src/brosh/mcp.py

"""MCP server implementation for brosh."""

import asyncio
import base64
import json
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from loguru import logger
from platformdirs import user_pictures_dir

from .api import capture_webpage
from .models import ImageFormat, MCPImageContent, MCPTextContent, MCPToolResult
from .texthtml import DOMProcessor

# MCP has different defaults than CLI
MCP_DEFAULTS = {
    "scale": 50,  # Default to 50% scaling for MCP to reduce size
}


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
        subdirs: bool = False,
        format: str = "png",
        anim_spf: float = 0.5,
        html: bool = False,
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
            html: Whether to include HTML content in results
            max_frames: Maximum frames to capture (0 for unlimited)
            from_selector: CSS selector to scroll to before starting capture

        Returns:
            MCPToolResult with screenshots and optional HTML content

        """
        try:
            # Convert string parameters to proper types for the API
            format_enum = ImageFormat(format.lower())
            output_path = Path(output_dir) if output_dir else Path(user_pictures_dir())

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
                "format": format_enum,
                "anim_spf": anim_spf,
                "html": html,
                "max_frames": max_frames,
                "from_selector": from_selector,
            }

            # Call the unified API
            result = capture_webpage(**api_kwargs)

            # Process results for MCP format
            return _convert_to_mcp_result(result, format_enum)

        except Exception as e:
            logger.error(f"MCP capture failed: {e}")
            return MCPToolResult(content=[MCPTextContent(text=f"Error: {e!s}")])

    # Register the tool with mcp
    mcp.tool(see_webpage)

    mcp.run()


def _convert_to_mcp_result(capture_result: dict[str, dict[str, Any]], format: ImageFormat) -> MCPToolResult:
    """Convert standard capture results to MCP format.

    Args:
        capture_result: Results from capture_webpage
        format: Image format used

    Returns:
        MCPToolResult with proper content items

    """
    content_items = []
    dom_processor = DOMProcessor()

    for filepath, metadata in capture_result.items():
        try:
            # Read the image file
            with open(filepath, "rb") as f:
                image_bytes = f.read()

            # Create image content
            image_content = MCPImageContent(
                data=base64.b64encode(image_bytes).decode(),
                mime_type=(format.mime_type if isinstance(format, ImageFormat) else "image/png"),
            )
            content_items.append(image_content)

            # Create metadata content
            meta_dict = {filepath: {"selector": metadata.get("selector", "body"), "text": metadata.get("text", "")}}

            # Add compressed HTML if present
            if "html" in metadata:
                compressed = dom_processor.compress_html(metadata["html"])
                meta_dict[filepath]["html"] = compressed

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
    MAX_SIZE = 1048576  # 1MB

    # Calculate initial size
    result_dict = result.model_dump()
    size = len(json.dumps(result_dict).encode("utf-8"))

    if size <= MAX_SIZE:
        return result

    logger.warning(f"Result size {size} exceeds limit, applying compression")

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

    if size <= MAX_SIZE:
        return result

    # Step 2: Downsample images
    from .image import ImageProcessor

    processor = ImageProcessor()

    new_content = []
    for item in result.content:
        if isinstance(item, MCPImageContent):
            try:
                img_data = base64.b64decode(item.data)
                downsampled = processor.downsample_png_bytes(img_data, 50)
                item = MCPImageContent(data=base64.b64encode(downsampled).decode(), mime_type=item.mime_type)
            except Exception as e:
                logger.error(f"Failed to downsample image: {e}")
        new_content.append(item)

    result = MCPToolResult(content=new_content)
    size = len(json.dumps(result.model_dump()).encode("utf-8"))

    if size <= MAX_SIZE:
        return result

    # Step 3: Remove screenshots from end
    while len(result.content) > 2 and size > MAX_SIZE:
        result.content = result.content[:-2]
        size = len(json.dumps(result.model_dump()).encode("utf-8"))

    return result


def main() -> None:
    """Run the MCP server."""
    run_mcp_server()


if __name__ == "__main__":
    main()

