#!/usr/bin/env python3
# this_file: src/brosh/api.py

"""Public API for brosh - single source of truth for all parameters."""

import asyncio
from pathlib import Path
from typing import Annotated, Any

from pydantic import Field
from pydantic.networks import AnyUrl

from .models import CaptureConfig, ImageFormat
from .tool import BrowserScreenshotTool, dflt_output_folder


def capture_webpage(
    url: Annotated[AnyUrl, Field(description="The webpage URL to capture")],
    zoom: Annotated[int, Field(default=100, ge=10, le=500, description="Browser zoom level in %")] = 100,
    width: Annotated[int, Field(default=0, ge=0, description="Viewport width in pixels (0: screen width)")] = 0,
    height: Annotated[
        int, Field(default=0, ge=-1, description="Viewport height in pixels (0: screen height, -1: full page)")
    ] = 0,
    scroll_step: Annotated[
        int, Field(default=100, ge=10, le=200, description="Scroll step in % of viewport height")
    ] = 100,
    scale: Annotated[int, Field(default=100, ge=10, le=200, description="Output image scale in %")] = 100,
    app: Annotated[
        str, Field(default="", description="Browser to use (chrome, edge, safari; empty: auto-detect)")
    ] = "",
    output_dir: Annotated[
        Path | None,
        Field(default_factory=lambda: Path(dflt_output_folder()), description="Output directory for screenshots"),
    ] = None,
    *,
    subdirs: Annotated[bool, Field(default=False, description="Create subdirectories per domain")] = False,
    output_format: Annotated[
        ImageFormat, Field(default=ImageFormat.PNG, description="Output format: png, jpg, or apng")
    ] = ImageFormat.PNG,
    anim_spf: Annotated[
        float, Field(default=0.5, ge=0.1, le=10.0, description="Seconds per frame for APNG animation")
    ] = 0.5,
    fetch_html: Annotated[
        bool, Field(default=False, description="Include visible HTML content for each screenshot")
    ] = False,
    fetch_image: Annotated[bool, Field(default=False, description="Include image data in MCP output")] = False,
    fetch_image_path: Annotated[bool, Field(default=True, description="Include image path in MCP output")] = True,
    fetch_text: Annotated[bool, Field(default=True, description="Include extracted text in MCP output")] = True,
    trim_text: Annotated[bool, Field(default=True, description="Trim text to 200 characters")] = True,
    max_frames: Annotated[
        int, Field(default=0, ge=0, description="Maximum number of frames to capture (0: unlimited)")
    ] = 0,
    from_selector: Annotated[
        str, Field(default="", description="CSS selector to scroll to before starting capture")
    ] = "",
) -> dict[str, dict[str, Any]]:
    """Capture webpage screenshots with comprehensive options.

    This is the main public API for the brosh screenshot tool. It captures
    scrolling screenshots of a webpage with various configuration options.

    Args:
        url: The webpage URL to capture
        zoom: Browser zoom level (10-500%)
        width: Viewport width in pixels (0 for screen width)
        height: Viewport height in pixels (0 for screen height, -1 for full page)
        scroll_step: Vertical scroll increment as percentage of viewport
        scale: Output image scaling factor
        app: Browser to use (chrome/edge/safari, empty for auto-detect)
        output_dir: Directory to save screenshots
        subdirs: Whether to create domain-based subdirectories
        format: Output image format
        anim_spf: Animation speed for APNG format
        fetch_html: Whether to include HTML content in results
        fetch_image: Whether to include image data in MCP output
        fetch_image_path: Whether to include image path in MCP output
        fetch_text: Whether to include extracted text in MCP output
        trim_text: Whether to trim text to 200 characters
        max_frames: Maximum frames to capture (0 for unlimited)
        from_selector: CSS selector to start capture from

    Returns:
        Dictionary mapping file paths to metadata:
        {
            "/path/to/screenshot.png": {
                "selector": "main",
                "text": "visible text content",
                "html": "<div>...</div>"  # if fetch_html=True
            },
            ...
        }

    Raises:
        ValueError: For invalid parameters
        RuntimeError: For browser or capture failures

    Used in:
    - __init__.py
    - cli.py
    - mcp.py
    """
    # Handle default for output_dir
    if output_dir is None:
        output_dir = Path(dflt_output_folder())

    # Create configuration object
    config = CaptureConfig(
        url=str(url),
        width=width,
        height=height,
        zoom=zoom,
        scroll_step=scroll_step,
        scale=scale,
        format=output_format,
        app=app,
        output_dir=str(output_dir),
        subdirs=subdirs,
        anim_spf=anim_spf,
        fetch_html=fetch_html,
        fetch_image=fetch_image,
        fetch_image_path=fetch_image_path,
        fetch_text=fetch_text,
        trim_text=trim_text,
        max_frames=max_frames,
        from_selector=from_selector,
    )

    # Validate configuration
    config.validate()

    # Create and run tool
    tool = BrowserScreenshotTool()

    # Handle async execution
    from contextlib import suppress # Added import

    loop = None
    with suppress(RuntimeError): # SIM105
        loop = asyncio.get_running_loop()

    if loop is not None:
        # Already in async context (e.g., from MCP)
        # Return the coroutine directly - caller will await it
        return tool.capture(config)
    # Sync context (e.g., from CLI)
    return asyncio.run(tool.capture(config))


# Async version for MCP and other async contexts
async def capture_webpage_async(
    url: Annotated[AnyUrl, Field(description="The webpage URL to capture")],
    zoom: Annotated[int, Field(default=100, ge=10, le=500, description="Browser zoom level in %")] = 100,
    width: Annotated[int, Field(default=0, ge=0, description="Viewport width in pixels (0: screen width)")] = 0,
    height: Annotated[
        int, Field(default=0, ge=-1, description="Viewport height in pixels (0: screen height, -1: full page)")
    ] = 0,
    scroll_step: Annotated[
        int, Field(default=100, ge=10, le=200, description="Scroll step in % of viewport height")
    ] = 100,
    scale: Annotated[int, Field(default=100, ge=10, le=200, description="Output image scale in %")] = 100,
    app: Annotated[
        str, Field(default="", description="Browser to use (chrome, edge, safari; empty: auto-detect)")
    ] = "",
    output_dir: Annotated[
        Path | None,
        Field(default_factory=lambda: Path(dflt_output_folder()), description="Output directory for screenshots"),
    ] = None,
    *,
    subdirs: Annotated[bool, Field(default=False, description="Create subdirectories per domain")] = False,
    output_format: Annotated[
        ImageFormat, Field(default=ImageFormat.PNG, description="Output format: png, jpg, or apng")
    ] = ImageFormat.PNG,
    anim_spf: Annotated[
        float, Field(default=0.5, ge=0.1, le=10.0, description="Seconds per frame for APNG animation")
    ] = 0.5,
    fetch_html: Annotated[
        bool, Field(default=False, description="Include visible HTML content for each screenshot")
    ] = False,
    fetch_image: Annotated[bool, Field(default=False, description="Include image data in MCP output")] = False,
    fetch_image_path: Annotated[bool, Field(default=True, description="Include image path in MCP output")] = True,
    fetch_text: Annotated[bool, Field(default=True, description="Include extracted text in MCP output")] = True,
    trim_text: Annotated[bool, Field(default=True, description="Trim text to 200 characters")] = True,
    max_frames: Annotated[
        int, Field(default=0, ge=0, description="Maximum number of frames to capture (0: unlimited)")
    ] = 0,
    from_selector: Annotated[
        str, Field(default="", description="CSS selector to scroll to before starting capture")
    ] = "",
) -> dict[str, dict[str, Any]]:
    """Async version of capture_webpage for use in async contexts like MCP.

    See capture_webpage for full documentation.
    """
    # Handle default for output_dir
    if output_dir is None:
        output_dir = Path(dflt_output_folder())

    # Create configuration object
    config = CaptureConfig(
        url=str(url),
        width=width,
        height=height,
        zoom=zoom,
        scroll_step=scroll_step,
        scale=scale,
        format=output_format,
        app=app,
        output_dir=str(output_dir),
        subdirs=subdirs,
        anim_spf=anim_spf,
        fetch_html=fetch_html,
        fetch_image=fetch_image,
        fetch_image_path=fetch_image_path,
        fetch_text=fetch_text,
        trim_text=trim_text,
        max_frames=max_frames,
        from_selector=from_selector,
    )

    # Validate configuration
    config.validate()

    # Create and run tool
    tool = BrowserScreenshotTool()
    return await tool.capture(config)


# Convenience functions for common use cases
def capture_full_page(url: str, **kwargs) -> dict[str, dict[str, Any]]:
    """Capture entire webpage in a single screenshot.

    Used in:
    - __init__.py
    """
    kwargs["height"] = -1
    kwargs["scroll_step"] = 100
    kwargs["max_frames"] = 1
    return capture_webpage(url, **kwargs)


def capture_visible_area(url: str, **kwargs) -> dict[str, dict[str, Any]]:
    """Capture only the visible viewport area.

    Used in:
    - __init__.py
    """
    kwargs["max_frames"] = 1
    return capture_webpage(url, **kwargs)


def capture_animation(url: str, **kwargs) -> dict[str, dict[str, Any]]:
    """Capture scrolling animation as APNG.

    Used in:
    - __init__.py
    """
    kwargs["output_format"] = ImageFormat.APNG
    return capture_webpage(url, **kwargs)
