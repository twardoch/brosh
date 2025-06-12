#!/usr/bin/env python3
# this_file: src/brosh/tool.py

"""Main screenshot tool implementation for brosh."""

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlparse

import platformdirs
from loguru import logger
from playwright.async_api import async_playwright

from .browser import BrowserManager
from .capture import CaptureManager
from .image import ImageProcessor
from .models import ImageFormat


class BrowserScreenshotTool:
    """Tool for capturing scrolling screenshots using Playwright async API.

    Optimized for reliability with comprehensive error handling,
    intelligent browser detection, and performance optimizations.

    """

    def __init__(self, verbose: bool = False):
        """Initialize the screenshot _tool with default settings.

        Args:
            verbose: Enable debug logging

        """
        self.max_retries = 3
        self.connection_timeout = 30
        self.page_timeout = 60
        self.screenshot_timeout = 10
        self.verbose = verbose

        # Configure logging based on verbose flag
        if not verbose:
            logger.remove()
            logger.add(sys.stderr, level="ERROR")

        # Initialize managers
        self.browser_manager = BrowserManager(self.connection_timeout)
        self.capture_manager = CaptureManager(self.page_timeout, self.screenshot_timeout)
        self.image_processor = ImageProcessor()

    async def capture(
        self,
        url: str,
        zoom: int = 100,
        width: int = 0,
        height: int = 0,
        scroll_step: int = 100,
        scale: int = 100,
        app: str = "",
        output_dir: str = platformdirs.user_pictures_dir(),
        subdirs: bool = False,
        mcp: bool = False,
        format: str = "png",
        anim_spf: float = 0.5,
        html: bool = False,
        max_frames: int = 0,
        from_selector: str = "",
    ) -> list[str] | dict[str, str]:
        """Capture screenshots of a webpage using Playwright.

        This method navigates to a URL and captures sequential screenshots
        while scrolling through the page. Each screenshot is named with
        domain, scroll position, and section identifier.

        Args:
            url: The URL to navigate to (mandatory)
            zoom: Zoom level in % (default: 100)
            width: Width in pixels (default: main screen width)
            height: Height in pixels (default: main screen height). Use -1 to capture entire page
            scroll_step: Scroll step in % of height (default: 100)
            scale: Scale in % for resampling output image (default: 100)
            app: Browser to use - chrome, edge, safari (default: auto-detect)
            output_dir: Output directory for screenshots (default: Pictures)
            subdirs: Create subdirectories for domains (default: False)
            mcp: Run in FastMCP mode (default: False)
            format: Output format - png, jpg, or apng (default: png)
            anim_spf: Seconds per frame for APNG animation (default: 0.5)
            html: Return dict with HTML/selectors instead of list
                 (default: False)
            max_frames: Maximum number of frames to capture, 0 for all
                       (default: 0)
            from_selector: CSS selector to scroll to before starting capture
                          (default: "")

        Returns:
            If html=True: Dict with screenshot paths as keys and HTML/selectors
                         as values
            If html=False: List of paths to saved screenshot files

        Raises:
            ValueError: For invalid parameters
            RuntimeError: For browser connection or navigation failures

        """
        if mcp:
            # This should be handled in mcp.py now
            msg = "MCP mode should be handled by mcp module"
            raise RuntimeError(msg)

        # Validate inputs
        self.capture_manager.validate_inputs(url, zoom, scroll_step, scale, format)
        img_format = format.lower()

        # Parse URL and get domain for filename generation
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "").replace(".", "_")
        if not domain:
            msg = f"Invalid URL: {url}"
            raise ValueError(msg)

        # Create output directory structure
        output_path = Path(output_dir)
        if subdirs:
            output_path = output_path / domain
        output_path.mkdir(parents=True, exist_ok=True)

        # Get screen dimensions if not specified
        if width == 0 or (height == 0 or height == -1):
            default_width, default_height = self.browser_manager.get_screen_dimensions()
            width = width or default_width
            if height == 0:
                height = default_height
            # If height is -1, we'll handle it as "capture entire page"

        if height == -1:
            logger.info(f"Starting capture of {url} at {width}x(entire page)")
        else:
            logger.info(f"Starting capture of {url} at {width}x{height}")

        # Determine browser to use (no Firefox support)
        browser_name = self.browser_manager.get_browser_name(app)
        logger.info(f"Using browser: {browser_name}")

        saved_paths = []
        html_data = {}  # For HTML/selector data when html=True
        temp_png_paths: list[Path] = []  # For APNG conversion

        # Retry mechanism for browser connection
        for attempt in range(self.max_retries):
            try:
                async with async_playwright() as p:
                    # Connect to existing browser or launch new one
                    browser, context, page = await self.browser_manager.get_browser_instance(
                        p, browser_name, width, height, zoom
                    )

                    try:
                        saved_paths, html_data = await self.capture_manager.capture_screenshots(
                            page,
                            url,
                            domain,
                            output_path,
                            width,
                            height,
                            scroll_step,
                            scale,
                            img_format,
                            anim_spf,
                            temp_png_paths,
                            html,
                            max_frames,
                            from_selector,
                        )
                        logger.info(f"Successfully captured {len(saved_paths)} screenshots")
                        break  # Success, exit retry loop

                    finally:
                        # Clean up browser resources
                        await self.browser_manager.cleanup_browser(page, context, browser)

            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt == self.max_retries - 1:
                    msg = f"Failed to capture screenshots after {self.max_retries} attempts: {e}"
                    raise RuntimeError(msg)
                await asyncio.sleep(2)  # Wait before retry

        # Always return html_data when populated (either HTML content or selectors)
        if html_data:
            return html_data
        return saved_paths
