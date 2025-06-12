#!/usr/bin/env python3
# this_file: src/brosh/api.py

"""Public API for brosh - single source of truth for all parameters."""

import asyncio
from pathlib import Path
from typing import Annotated, Any, Dict, Union

from platformdirs import user_pictures_dir
from pydantic import Field
from pydantic.networks import AnyUrl

from .models import CaptureConfig, CaptureResult, ImageFormat
from .tool import BrowserScreenshotTool


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
        Field(default_factory=lambda: Path(user_pictures_dir()), description="Output directory for screenshots"),
    ] = None,
    subdirs: Annotated[bool, Field(default=False, description="Create subdirectories per domain")] = False,
    format: Annotated[
        ImageFormat, Field(default=ImageFormat.PNG, description="Output format: png, jpg, or apng")
    ] = ImageFormat.PNG,
    anim_spf: Annotated[
        float, Field(default=0.5, ge=0.1, le=10.0, description="Seconds per frame for APNG animation")
    ] = 0.5,
    html: Annotated[bool, Field(default=False, description="Include visible HTML content for each screenshot")] = False,
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
        html: Whether to include HTML content in results
        max_frames: Maximum frames to capture (0 for unlimited)
        from_selector: CSS selector to start capture from

    Returns:
        Dictionary mapping file paths to metadata:
        {
            "/path/to/screenshot.png": {
                "selector": "main",
                "text": "visible text content",
                "html": "<div>...</div>"  # if html=True
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
        output_dir = Path(user_pictures_dir())

    # Create configuration object
    config = CaptureConfig(
        url=str(url),
        width=width,
        height=height,
        zoom=zoom,
        scroll_step=scroll_step,
        scale=scale,
        format=format,
        app=app,
        output_dir=str(output_dir),
        subdirs=subdirs,
        anim_spf=anim_spf,
        html=html,
        max_frames=max_frames,
        from_selector=from_selector,
    )

    # Validate configuration
    config.validate()

    # Create and run tool
    tool = BrowserScreenshotTool()

    # Handle async execution
    loop = None
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop
        pass

    if loop is not None:
        # Already in async context (e.g., from MCP)
        return asyncio.create_task(tool.capture(config))
    # Sync context (e.g., from CLI)
    return asyncio.run(tool.capture(config))


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
    kwargs["format"] = ImageFormat.APNG
    return capture_webpage(url, **kwargs)
