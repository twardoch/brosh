#!/usr/bin/env python3
# this_file: src/brosh/mcp.py

"""MCP server implementation for brosh."""

import sys

import platformdirs

try:
    from fastmcp import FastMCP, Image
except ImportError:
    sys.exit(1)

from loguru import logger

from .tool import BrowserScreenshotTool


def run_mcp_server():
    """Run the FastMCP server for browser screenshots."""

    mcp = FastMCP(
        name="Browser Screenshots",
        instructions=(
            "This _tool captures sequential screenshots of a webpage "
            "by scrolling through it in a real browser. "
            "You can specify URL, zoom, viewport size, scroll step, "
            "output scaling, format (png/jpg/apng), and animation "
            "speed. Screenshots are saved with descriptive filenames "
            "including domain, scroll position, and smart section "
            "identifiers. Choose browser or use OS default. If "
            "subdirs enabled, screenshots organized by domain. "
            "Ideal for long pages, documentation, QA. Works with "
            "remote debugging mode preserving authentication and "
            "cookies."
        ),
    )

    @mcp.tool
    async def capture_screenshot(
        url: str,
        zoom: int = 100,
        width: int = 0,
        height: int = 0,
        scroll_step: int = 100,
        scale: int = 100,
        app: str = "",
        output_dir: str = platformdirs.user_pictures_dir(),
        subdirs: bool = False,
        format: str = "png",
        anim_spf: float = 0.5,
        html: bool = False,
        max_frames: int = 0,
        from_selector: str = "",
    ) -> dict[str, dict[str, str | Image]]:
        """Capture screenshots of a webpage using Playwright.

        Args:
            url: The URL to navigate to (mandatory)
            zoom: Zoom level in % (default: 100)
            width: Width in pixels (default: main screen width)
            height: Height in pixels (default: main screen height). Use -1 to capture entire page
            scroll_step: Scroll step in % of height (default: 100)
            scale: Scale in % for resampling output image
                   (default: 100)
            app: Browser to use (default: OS default browser)
            output_dir: Output directory for screenshots
                       (default: Pictures)
            subdirs: Create subdirectories for domains
                    (default: False)
            format: Output format - png, jpg, or apng (default: png)
            anim_spf: Seconds per frame for APNG animation
                     (default: 0.5)
            html: Return dict with HTML/selectors instead of list
                 (default: False)
            max_frames: Maximum number of frames to capture, 0 for all
                       (default: 0)
            from_selector: CSS selector to scroll to before starting capture
                          (default: "")

        Returns:
            Dict with screenshot paths as keys and values containing:
            - "image": FastMCP Image object with the screenshot
            - "selector": CSS selector for the visible portion
            - "html": (optional, if html=True) HTML of visible elements
        """
        # Create a new instance to avoid recursion
        tool = BrowserScreenshotTool()

        # Capture with both selectors and optionally HTML
        result = await tool.capture(
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
            html=html,  # This will get both selector and HTML if True
            max_frames=max_frames,
            from_selector=from_selector,
        )

        # For MCP mode, we need to return a dict with image data
        if isinstance(result, dict):
            # Result is already a dict with paths as keys
            mcp_result = {}
            for path, value in result.items():
                # Read the image file
                try:
                    with open(path, "rb") as f:
                        img_bytes = f.read()

                    # Determine format from path
                    path_lower = path.lower()
                    if path_lower.endswith(".png"):
                        img_format = "png"
                    elif path_lower.endswith((".jpg", ".jpeg")):
                        img_format = "jpeg"
                    else:
                        img_format = "png"

                    # Build the response dict
                    response_dict = {
                        "image": Image(data=img_bytes, format=img_format),
                    }

                    # Handle both old format (string selector) and new format (dict with selector and html)
                    if isinstance(value, dict):
                        response_dict["selector"] = value.get("selector", "body")
                        if "html" in value:
                            response_dict["html"] = value["html"]
                    else:
                        # Old format - value is just the selector
                        response_dict["selector"] = value

                    mcp_result[path] = response_dict

                except Exception as e:
                    logger.error(f"Failed to read image {path}: {e}")
                    continue

            return mcp_result
        # Result is a list of paths (shouldn't happen with current logic)
        # Convert to dict format expected by MCP
        mcp_result = {}
        for path in result:
            try:
                with open(path, "rb") as f:
                    img_bytes = f.read()

                # Determine format from path
                path_lower = path.lower()
                if path_lower.endswith(".png"):
                    img_format = "png"
                elif path_lower.endswith((".jpg", ".jpeg")):
                    img_format = "jpeg"
                else:
                    img_format = "png"

                mcp_result[path] = {
                    "image": Image(data=img_bytes, format=img_format),
                    "selector": "body",  # Default selector
                }
            except Exception as e:
                logger.error(f"Failed to read image {path}: {e}")
                continue

        return mcp_result

    mcp.run()


def main():
    """Entry point for the brosh-mcp command."""
    run_mcp_server()


if __name__ == "__main__":
    main()
