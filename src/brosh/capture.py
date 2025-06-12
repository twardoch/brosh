#!/usr/bin/env python3
# this_file: src/brosh/capture.py

"""Screenshot capture logic for brosh."""

import asyncio
from datetime import datetime
from pathlib import Path

from loguru import logger
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from .image import ImageProcessor


class CaptureManager:
    """Manages screenshot capture operations."""

    def __init__(self, page_timeout: int = 60, screenshot_timeout: int = 10):
        """Initialize capture manager.

        Args:
            page_timeout: Page load timeout in seconds
            screenshot_timeout: Screenshot capture timeout in seconds
        """
        self.page_timeout = page_timeout
        self.screenshot_timeout = screenshot_timeout
        self.image_processor = ImageProcessor()

    def validate_inputs(self, url: str, zoom: int, scroll_step: int, scale: int, format: str) -> None:
        """Validate input parameters.

        Args:
            url: URL to validate
            zoom: Zoom level to validate
            scroll_step: Scroll step to validate
            scale: Scale to validate
            format: Format to validate

        Raises:
            ValueError: For invalid parameters

        """
        if not url or not url.startswith(("http://", "https://")):
            msg = f"Invalid URL: {url}"
            raise ValueError(msg)

        if not (10 <= zoom <= 500):
            msg = f"Zoom must be between 10-500%: {zoom}"
            raise ValueError(msg)

        if not (10 <= scroll_step <= 200):
            msg = f"Scroll step must be between 10-200%: {scroll_step}"
            raise ValueError(msg)

        if not (10 <= scale <= 200):
            msg = f"Scale must be between 10-200%: {scale}"
            raise ValueError(msg)

        if format.lower() not in ["png", "jpg", "apng"]:
            msg = f"Unsupported format: {format}. Use: png, jpg, apng"
            raise ValueError(msg)

    async def capture_screenshots(
        self,
        page,
        url: str,
        domain: str,
        output_path: Path,
        width: int,
        height: int,
        scroll_step: int,
        scale: int,
        img_format: str,
        anim_spf: float,
        temp_png_paths: list[Path],
        html: bool = False,
        max_frames: int = 0,
        from_selector: str = "",
    ) -> tuple[list[str], dict[str, str]]:
        """Capture all screenshots for the page.

        Args:
            page: Playwright page instance
            url: URL being captured
            domain: Domain name for filenames
            output_path: Output directory
            width: Viewport width
            height: Viewport height
            scroll_step: Scroll step percentage
            scale: Image scale percentage
            img_format: Output format
            anim_spf: Animation seconds per frame
            temp_png_paths: List to store temp PNG paths
            html: Whether to capture HTML/selectors
            max_frames: Maximum number of frames to capture
            from_selector: CSS selector to scroll to before starting

        Returns:
            Tuple of (saved file paths, html data dict)

        """
        saved_paths = []
        html_data = {}

        # Navigate to URL with timeout and retries
        try:
            logger.info(f"Navigating to {url}")
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.page_timeout * 1000,
            )
            await asyncio.sleep(3)  # Additional wait for dynamic content
        except PlaywrightTimeoutError:
            logger.warning("Page load timeout, proceeding anyway")
        except Exception as e:
            msg = f"Failed to navigate to {url}: {e}"
            raise RuntimeError(msg)

        # Handle from_selector - scroll to element before starting
        start_position = 0
        if from_selector:
            try:
                logger.info(f"Scrolling to element: {from_selector}")
                # Scroll element into view and get its position
                start_position = await page.evaluate(f"""
                    (() => {{
                        const element = document.querySelector('{from_selector}');
                        if (element) {{
                            element.scrollIntoView({{behavior: 'instant', block: 'start'}});
                            return element.getBoundingClientRect().top + window.pageYOffset;
                        }}
                        return 0;
                    }})()
                """)
                await asyncio.sleep(1)  # Wait for scroll to complete
                logger.info(f"Starting capture from position: {start_position}px")
            except Exception as e:
                logger.warning(f"Failed to find selector '{from_selector}': {e}, starting from top")
                start_position = 0

        # Get total page height for scroll calculation
        try:
            total_height = await page.evaluate("document.documentElement.scrollHeight")
            # Handle height == -1 to capture entire page
            if height == -1:
                viewport_height = await page.evaluate("window.innerHeight")
                logger.info(f"Capturing entire page - height: {total_height}px, viewport: {viewport_height}px")
            else:
                viewport_height = height
                logger.info(f"Page height: {total_height}px, viewport: {viewport_height}px")
        except Exception as e:
            msg = f"Failed to get page dimensions: {e}"
            raise RuntimeError(msg)

        # Calculate all scroll positions based on step size
        scroll_positions = []
        current_pos = start_position
        while current_pos < total_height:
            scroll_positions.append(int(current_pos))
            current_pos += int(viewport_height * scroll_step / 100)

        # Limit frames if max_frames is specified
        if max_frames > 0:
            scroll_positions = scroll_positions[:max_frames]

        logger.info(f"Will capture {len(scroll_positions)} screenshots")

        # Generate timestamp for filename
        now = datetime.now()
        timestamp = now.strftime("%y%m%d-%H%M%S")

        # Capture screenshots at each scroll position
        for _i, scroll_pos in enumerate(scroll_positions):
            try:
                # Scroll to the calculated position
                await page.evaluate(f"window.scrollTo(0, {scroll_pos})")
                await asyncio.sleep(0.8)  # Wait for scroll animation and content load

                # Calculate scroll percentage for filename
                scroll_percentage = min(int((scroll_pos / total_height) * 10000), 9999)

                # Get semantic section ID based on visible content
                section_id = await self.get_section_id(page)

                # Generate descriptive filename
                if img_format == "apng":
                    # For APNG, save as PNG first, convert later
                    filename = f"{domain}-{timestamp}-{scroll_percentage:05d}-{section_id}.png"
                    filepath = output_path / filename
                    temp_png_paths.append(filepath)
                else:
                    filename = f"{domain}-{timestamp}-{scroll_percentage:05d}-{section_id}.{img_format}"
                    filepath = output_path / filename

                # Capture the visible area screenshot with timeout
                try:
                    await page.screenshot(
                        path=str(filepath),
                        full_page=False,
                        timeout=self.screenshot_timeout * 1000,
                    )
                except PlaywrightTimeoutError:
                    logger.warning(f"Screenshot timeout for position {scroll_pos}, skipping")
                    continue

                # Apply scaling if requested
                if scale != 100:
                    self.image_processor.scale_image(filepath, scale)

                # Convert to JPG if needed
                if img_format == "jpg":
                    filepath = self.image_processor.convert_to_jpg(filepath)

                if img_format != "apng":
                    saved_paths.append(str(filepath))
                    logger.debug(f"Captured: {filepath}")

                # Capture HTML or selector if requested
                # Always get selector
                selector = await self.get_visible_selector(page)

                if html:
                    visible_html = await self.get_visible_html(page)
                    # Store both selector and HTML when in html mode
                    html_data[str(filepath)] = {"selector": selector, "html": visible_html}
                else:
                    html_data[str(filepath)] = selector

            except Exception as e:
                logger.error(f"Failed to capture screenshot at position {scroll_pos}: {e}")
                continue  # Continue with next screenshot

        # Create APNG if requested
        if img_format == "apng" and temp_png_paths:
            try:
                apng_path = self.image_processor.create_apng(temp_png_paths, domain, output_path, anim_spf)
                saved_paths.append(str(apng_path))
                logger.info(f"Created APNG: {apng_path}")

                # Clean up temporary PNG files
                for temp_path in temp_png_paths:
                    try:
                        temp_path.unlink()
                    except Exception as e:
                        logger.warning(f"Failed to delete temp file {temp_path}: {e}")
            except Exception as e:
                logger.error(f"Failed to create APNG: {e}")

        return saved_paths, html_data

    async def get_section_id(self, page) -> str:
        """Get a smart ID based on current visible content.

        This method attempts to identify the current section by looking
        for visible headers or elements with IDs in the viewport.

        Args:
            page: Playwright page instance

        Returns:
            Section identifier string

        """
        try:
            # Execute JavaScript to find visible headers in viewport
            headers = await page.evaluate("""() => {
                const viewportHeight = window.innerHeight;
                const headers = Array.from(
                    document.querySelectorAll('h1, h2, h3, h4, h5, h6, [id]')
                );

                for (const header of headers) {
                    const rect = header.getBoundingClientRect();
                    if (rect.top >= 0 && rect.top < viewportHeight / 2) {
                        return (header.id || header.textContent || '').trim()
                            .toLowerCase()
                            .replace(/[^a-z0-9]+/g, '-')
                            .replace(/^-+|-+$/g, '')
                            .substring(0, 20);
                    }
                }
                return 'section';
            }""")

            return headers or "section"
        except Exception:
            return "section"

    async def get_visible_html(self, page) -> str:
        """Get minified HTML of visible portion of the page.

        Args:
            page: Playwright page instance

        Returns:
            Minified HTML string of visible elements

        """
        try:
            return await page.evaluate("""() => {
                const {innerHeight: H, innerWidth: W} = window;
                const nodes = [...document.querySelectorAll('*')];
                const fullyVisibleElements = [];

                // Tags to exclude from capture
                const excludeTags = ['HTML', 'HEAD', 'BODY', 'SCRIPT', 'STYLE', 'META', 'LINK', 'TITLE'];

                // Find elements that are FULLY visible in the viewport
                nodes.forEach(node => {
                    // Skip excluded tags and non-element nodes
                    if (excludeTags.includes(node.tagName) || node.nodeType !== 1) {
                        return;
                    }

                    const r = node.getBoundingClientRect();
                    // Check if element is fully visible
                    if (r.top >= 0 && r.bottom <= H && r.left >= 0 && r.right <= W && r.width > 0 && r.height > 0) {
                        // Check if this element is already contained in a parent we've added
                        let isContained = false;
                        for (const existing of fullyVisibleElements) {
                            if (existing.contains(node)) {
                                isContained = true;
                                break;
                            }
                        }
                        if (!isContained) {
                            // Remove any previously added children of this element
                            const filtered = fullyVisibleElements.filter(el => !node.contains(el));
                            fullyVisibleElements.length = 0;
                            fullyVisibleElements.push(...filtered, node);
                        }
                    }
                });

                // Convert to HTML strings and concatenate
                const htmlParts = fullyVisibleElements.map(el => el.outerHTML);

                // Return minified HTML
                return htmlParts.join('').replace(/\\s+/g, ' ').trim();
            }""")
        except Exception as e:
            logger.error(f"Failed to get visible HTML: {e}")
            return ""

    async def get_visible_selector(self, page) -> str:
        """Get a good selector for the visible portion of the page.

        Args:
            page: Playwright page instance

        Returns:
            CSS selector string for visible portion

        """
        try:
            return await page.evaluate("""() => {
                const {innerHeight: H} = window;

                // Try to find the most specific container for visible content
                const candidates = [
                    'main', 'article', '[role="main"]', '.content', '#content',
                    'section:first-of-type', 'div.container'
                ];

                for (const sel of candidates) {
                    const el = document.querySelector(sel);
                    if (el) {
                        const r = el.getBoundingClientRect();
                        if (r.top < H && r.bottom > 0) {
                            return sel;
                        }
                    }
                }

                // Find first visible section or div
                const sections = [...document.querySelectorAll('section, div')];
                for (const section of sections) {
                    const r = section.getBoundingClientRect();
                    if (r.top >= 0 && r.top < H/2) {
                        if (section.id) return '#' + section.id;
                        if (section.className) {
                            const classes = section.className.split(' ').filter(c => c);
                            if (classes.length) return '.' + classes.join('.');
                        }
                    }
                }

                // Fallback to body viewport
                return 'body';
            }""")
        except Exception as e:
            logger.error(f"Failed to get visible selector: {e}")
            return "body"
