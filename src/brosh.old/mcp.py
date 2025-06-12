#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fastmcp", "platformdirs", "pydantic", "loguru"]
# ///
# this_file: src/brosh/mcp.py

"""MCP server implementation for brosh.

This module provides FastMCP server functionality for capturing browser
screenshots using the brosh tool. It enables AI tools to request and receive
webpage captures with visual context and optional HTML/text content.
"""

import asyncio
import base64
import concurrent.futures
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated

from loguru import logger
from platformdirs import user_pictures_dir
from pydantic import Field
from pydantic.networks import AnyUrl

try:
    from playwright.async_api import Error as PlaywrightError
except ImportError:
    PlaywrightError = Exception

from fastmcp import FastMCP

from .models import (
    ImageFormat,
    MCPImageContent,
    MCPScreenshotResult,
    MCPTextContent,
    MCPToolResult,
)
from .optimize import (
    calculate_result_size,
    compress_html_content,
    downsample_png_data,
    optimize_png_file,
)
from .tool import BrowserScreenshotTool


def run_mcp_server() -> None:
    """Get a screenshot of a webpage in vertical slices together with text and/or HTML content."""
    mcp = FastMCP(
        name="Brosh Web Capture",
        instructions=("Get a screenshot of a webpage in vertical slices together with text and/or HTML content."),
    )

    @mcp.tool
    async def see_webpage(
        url: Annotated[AnyUrl, Field(description="The URL to capture")],
        zoom: Annotated[
            int,
            Field(
                default=100,
                description="Zoom level in %",
                ge=10,
                le=500,
            ),
        ],
        width: Annotated[
            int,
            Field(
                default=0,
                description="Width in pixels (0: screen width)",
            ),
        ],
        height: Annotated[
            int,
            Field(
                default=0,
                description="Height in pixels (0: screen height, -1: full page height)",
            ),
        ],
        from_selector: Annotated[
            str,
            Field(
                default="",
                description="CSS selector to start from (empty: page top)",
            ),
        ],
        scroll_step: Annotated[
            int,
            Field(
                default=100,
                description="Scroll step in % of height",
                ge=10,
                le=200,
            ),
        ],
        max_frames: Annotated[
            int,
            Field(
                default=0,
                description="Max vertical scroll shots (0: unlimited)",
            ),
        ],
        app: Annotated[
            str,
            Field(
                default="",
                description="Browser to use (default: chrome)",
            ),
        ],
        scale: Annotated[
            int,
            Field(
                default=50,
                description="Output image downsample %",
                ge=5,
                le=100,
            ),
        ],
        output_dir: Annotated[
            Path,
            Field(
                default=Path(user_pictures_dir()),
                description="Output folder for screenshots",
            ),
        ],
        subdirs: Annotated[
            bool,
            Field(
                default=False,
                description="Create per-domain subfolders",
            ),
        ],
        format: Annotated[
            str,
            Field(
                default="png",
                description="Output format: png (default), jpg, apng",
            ),
        ],
        anim_spf: Annotated[
            float,
            Field(
                default=0.5,
                description="APNG seconds per frame",
                ge=0.1,
                le=10.0,
            ),
        ],
        html: Annotated[
            bool,
            Field(
                default=False,
                description="Get visible HTML code for each screenshot",
            ),
        ],
    ) -> MCPToolResult:
        """Get screenshots and text or HTML from a webpage.

        Call this tool when you must *see* the page as a user would (e.g. verify design). Tweak zoom, viewport size, scroll_step, max_frames, format for optimal results. It scrolls from the given CSS selector (or top).

        Args:
            url: The webpage URL to capture
            zoom: Browser zoom level (10-500%)
            width: Viewport width (0: screen width)
            height: Viewport height (0: screen height, -1: full page)
            from_selector: Starting CSS selector (empty: page top)
            scroll_step: Vertical scroll increment (10-200% of height)
            max_frames: Maximum scroll captures (0: unlimited)
            app: Browser to use (default: chrome)
            scale: Output image scale (10-200%)
            output_dir: Screenshot save location
            subdirs: Create domain-based subdirectories
            format: Output image format (png/jpg/apng)
            anim_spf: APNG animation speed (0.1-10.0 seconds)
            html: Include visible HTML content

        Returns:
            {
                "<file_path>": {
                    "image": Image(...),      # screenshot or APNG frame
                    "selector": "<css>",      # DOM element in view
                    "text": "<markdown>",     # readable text found
                    "html": "<raw_html>"      # optional, if html=True
                },
                ...
            }

        Raises:
            Exception: If screenshot capture or processing fails
        """
        tool = BrowserScreenshotTool()
        logger.debug(f"MCP see_webpage called for url={url} html={html}")
        try:
            # Run capture in a separate event loop to avoid conflicts
            # This is similar to how the CLI works (asyncio.run)
            def run_capture():
                return asyncio.run(
                    tool.capture(
                        url=url,
                        zoom=zoom,
                        width=width,
                        height=height,
                        scroll_step=scroll_step,
                        scale=scale,
                        app=app,
                        output_dir=output_dir,
                        subdirs=subdirs,
                        mcp=False,  # Never recurse into MCP mode
                        format=format,
                        anim_spf=anim_spf,
                        html=html,  # Get both selector and HTML if True
                        max_frames=max_frames,
                        from_selector=from_selector,
                    )
                )

            # Execute in thread executor with timeout
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = loop.run_in_executor(executor, run_capture)
                result = await asyncio.wait_for(future, timeout=60.0)

            logger.debug("MCP see_webpage capture completed successfully")
        except TimeoutError:
            logger.error("MCP see_webpage: capture timed out")
            return MCPToolResult(content=[MCPTextContent(text="Error: Screenshot capture timed out.")])
        except asyncio.InvalidStateError as e:
            logger.error(f"MCP see_webpage: InvalidStateError: {e}")
            return MCPToolResult(content=[MCPTextContent(text=f"Error: InvalidStateError: {e}")])
        except PlaywrightError as e:
            logger.error(f"MCP see_webpage: Playwright error: {e}")
            return MCPToolResult(content=[MCPTextContent(text=f"Error: Playwright error: {e}")])
        except Exception as e:
            logger.error(f"MCP see_webpage: Unexpected error: {e}")
            return MCPToolResult(content=[MCPTextContent(text=f"Error: Unexpected error: {e}")])
        # Process capture results for MCP response
        if isinstance(result, dict):
            mcp_result = _process_dict_result(result, format)
        else:
            mcp_result = _process_list_result(result, format)

        # Post-process to ensure size limits
        return _post_process_result(mcp_result, has_html=html)

    mcp.run()


def _process_dict_result(
    result: Mapping[str, str | dict[str, str]],
    format: ImageFormat,
) -> MCPToolResult:
    """Process dictionary-format capture results.

    Args:
        result: Raw capture results with paths as keys
        format: Image format used for the captures

    Returns:
        Processed results with image data and metadata
    """
    content_items = []

    for path, value in result.items():
        try:
            screenshot = _create_screenshot_result(path, format)
            # Add metadata from the capture result
            if isinstance(value, dict):
                screenshot.selector = value.get("selector", "body")
                if "html" in value:
                    # Compress HTML to save space
                    screenshot.html = compress_html_content(value["html"])
                if "text" in value:
                    screenshot.text = value["text"]
            else:
                # Legacy format - value is just the selector
                screenshot.selector = str(value)
            # Add the image content item
            content_items.append(screenshot.image)
            # Add text metadata item
            content_items.append(MCPTextContent(text=screenshot.metadata_json(path)))
        except Exception as e:
            logger.error(f"Failed to process {path}: {e}")
            continue
    return MCPToolResult(content=content_items)


def _process_list_result(
    result: list[str],
    format: ImageFormat,
) -> MCPToolResult:
    """Process list-format capture results.

    Args:
        result: List of screenshot file paths
        format: Image format used for the captures

    Returns:
        Processed results with image data
    """
    content_items = []
    for path in result:
        try:
            screenshot = _create_screenshot_result(path, format)
            content_items.append(screenshot.image)
            content_items.append(MCPTextContent(text=screenshot.metadata_json(path)))
        except Exception as e:
            logger.error(f"Failed to process {path}: {e}")
            continue
    return MCPToolResult(content=content_items)


def _create_screenshot_result(
    path: str,
    format: ImageFormat,
    optimize: bool = True,
) -> MCPScreenshotResult:
    """Create a screenshot result from a file path.

    Args:
        path: Path to the image file
        format: Image format used for the capture
        optimize: Whether to optimize PNG files

    Returns:
        Screenshot result with image data and metadata

    Raises:
        Exception: If image file cannot be read
    """
    # Optimize PNG files if requested
    if optimize and format == ImageFormat.PNG:
        img_bytes = optimize_png_file(path, level=6, preserve_file=True)
    else:
        with open(path, "rb") as f:
            img_bytes = f.read()

    # Create image content item
    image = MCPImageContent(
        data=base64.b64encode(img_bytes).decode(),
        mime_type=format.mime_type,
    )

    return MCPScreenshotResult(
        image=image,
        selector="body",
        text=None,
        html=None,
    )


def _post_process_result(result: MCPToolResult, has_html: bool = False) -> MCPToolResult:
    """Post-process MCP result to ensure it fits within size limits.

    Args:
        result: The MCPToolResult to process
        has_html: Whether the result contains HTML content

    Returns:
        Processed MCPToolResult that fits within size limits
    """
    MAX_SIZE = 1048576  # 1MB limit

    # Check initial size
    result_dict = result.model_dump()
    size = calculate_result_size(result_dict)

    if size <= MAX_SIZE:
        return result

    logger.warning(f"Result size {size} exceeds limit {MAX_SIZE}, applying compression")

    # Step 1: If has HTML, remove all HTML except the first one
    if has_html and len(result.content) > 2:
        new_content = []
        html_found = False

        for _i, item in enumerate(result.content):
            if isinstance(item, MCPTextContent):
                # Parse the text to check if it contains HTML
                try:
                    import json

                    data = json.loads(item.text)
                    if isinstance(data, dict):
                        for path, metadata in data.items():
                            if "html" in metadata and html_found:
                                # Remove HTML from subsequent items
                                metadata.pop("html", None)
                                item = MCPTextContent(text=json.dumps({path: metadata}))
                            elif "html" in metadata:
                                html_found = True
                except:
                    pass
            new_content.append(item)

        result = MCPToolResult(content=new_content)
        size = calculate_result_size(result.model_dump())

        if size <= MAX_SIZE:
            return result

    # Step 2: Downsample images by 50%
    new_content = []
    for item in result.content:
        if isinstance(item, MCPImageContent):
            try:
                # Decode, downsample, re-encode
                img_data = base64.b64decode(item.data)
                downsampled = downsample_png_data(img_data, scale_factor=0.5)
                item = MCPImageContent(
                    data=base64.b64encode(downsampled).decode(),
                    mime_type=item.mime_type,
                )
            except Exception as e:
                logger.error(f"Failed to downsample image: {e}")
        new_content.append(item)

    result = MCPToolResult(content=new_content)
    size = calculate_result_size(result.model_dump())

    if size <= MAX_SIZE:
        return result

    # Step 3: Downsample again by 50%
    new_content = []
    for item in result.content:
        if isinstance(item, MCPImageContent):
            try:
                img_data = base64.b64decode(item.data)
                downsampled = downsample_png_data(img_data, scale_factor=0.5)
                item = MCPImageContent(
                    data=base64.b64encode(downsampled).decode(),
                    mime_type=item.mime_type,
                )
            except Exception as e:
                logger.error(f"Failed to downsample image again: {e}")
        new_content.append(item)

    result = MCPToolResult(content=new_content)
    size = calculate_result_size(result.model_dump())

    if size <= MAX_SIZE:
        return result

    # Step 4: Start removing screenshots from the end
    while len(result.content) > 2 and size > MAX_SIZE:
        # Remove last image and its metadata
        new_content = result.content[:-2]
        result = MCPToolResult(content=new_content)
        size = calculate_result_size(result.model_dump())

    return result


def main() -> None:
    """Run the MCP server."""
    run_mcp_server()


if __name__ == "__main__":
    main()
