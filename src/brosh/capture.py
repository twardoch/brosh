#!/usr/bin/env python3
# this_file: src/brosh/capture.py

"""Screenshot capture logic for brosh - pure browser interaction."""

import asyncio
from datetime import datetime
from typing import List, Optional

from loguru import logger
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from .models import CaptureConfig, CaptureFrame
from .texthtml import DOMProcessor


class CaptureManager:
    """Manages viewport scrolling and screenshot capture.

    Used in:
    - tool.py
    """

    def __init__(self, page_timeout: int = 60, screenshot_timeout: int = 10):
        """Initialize capture manager.

        Args:
            page_timeout: Page load timeout in seconds
            screenshot_timeout: Screenshot capture timeout in seconds

        """
        self.page_timeout = page_timeout
        self.screenshot_timeout = screenshot_timeout
        self.dom_processor = DOMProcessor()

    async def capture_frames(self, page: Page, config: CaptureConfig) -> list[CaptureFrame]:
        """Capture all viewport frames.

        Args:
            page: Playwright page instance
            config: Capture configuration

        Returns:
            List of captured frames with metadata

        Used in:
        - tool.py
        """
        # Navigate to URL
        try:
            logger.info(f"Navigating to {config.url}")
            await page.goto(
                str(config.url),
                wait_until="domcontentloaded",
                timeout=self.page_timeout * 1000,
            )
            await asyncio.sleep(3)  # Wait for dynamic content
        except PlaywrightTimeoutError:
            logger.warning("Page load timeout, proceeding anyway")

        # Handle from_selector if specified
        start_position = await self._handle_from_selector(page, config.from_selector)

        # Get page dimensions
        total_height = await page.evaluate("document.documentElement.scrollHeight")
        viewport_height = config.height if config.height != -1 else await page.evaluate("window.innerHeight")

        # Calculate scroll positions
        scroll_positions = self._calculate_scroll_positions(
            start_pos=start_position,
            page_height=total_height,
            viewport_height=viewport_height,
            scroll_step=config.scroll_step,
            max_frames=config.max_frames,
        )

        logger.info(f"Will capture {len(scroll_positions)} frames")

        # Capture frames
        frames = []
        for pos in scroll_positions:
            frame = await self._capture_single_frame(page, pos, total_height, viewport_height, config.html)
            if frame:
                frames.append(frame)

        return frames

    async def _handle_from_selector(self, page: Page, from_selector: str) -> int:
        """Handle from_selector to determine starting position.

        Args:
            page: Playwright page instance
            from_selector: CSS selector to scroll to

        Returns:
            Starting Y position in pixels

        """
        if not from_selector:
            return 0

        try:
            logger.info(f"Scrolling to element: {from_selector}")
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
            await asyncio.sleep(1)
            return start_position
        except Exception as e:
            logger.warning(f"Failed to find selector '{from_selector}': {e}")
            return 0

    def _calculate_scroll_positions(
        self, start_pos: int, page_height: int, viewport_height: int, scroll_step: int, max_frames: int
    ) -> list[int]:
        """Calculate scroll positions for capture.

        Args:
            start_pos: Starting Y position
            page_height: Total page height
            viewport_height: Viewport height
            scroll_step: Scroll step percentage
            max_frames: Maximum frames to capture

        Returns:
            List of Y positions to capture

        """
        positions = []
        current_pos = start_pos

        while current_pos < page_height:
            positions.append(int(current_pos))
            current_pos += int(viewport_height * scroll_step / 100)

        if max_frames > 0:
            positions = positions[:max_frames]

        return positions

    async def _capture_single_frame(
        self, page: Page, scroll_pos: int, page_height: int, viewport_height: int, capture_html: bool
    ) -> CaptureFrame | None:
        """Capture a single viewport frame.

        Args:
            page: Playwright page instance
            scroll_pos: Y position to scroll to
            page_height: Total page height
            viewport_height: Viewport height
            capture_html: Whether to capture HTML content

        Returns:
            CaptureFrame or None if capture failed

        """
        try:
            # Scroll to position
            await page.evaluate(f"window.scrollTo(0, {scroll_pos})")
            await asyncio.sleep(0.8)  # Wait for scroll and content

            # Capture screenshot as bytes
            screenshot_bytes = await page.screenshot(
                full_page=False,
                timeout=self.screenshot_timeout * 1000,
            )

            # Get section identifier
            await self.dom_processor.get_section_id(page)

            # Extract content if needed
            visible_html = None
            visible_text = None
            active_selector = "body"

            if capture_html:
                visible_html, visible_text, active_selector = await self.dom_processor.extract_visible_content(page)
            else:
                # Always get text and selector for metadata
                _, visible_text, active_selector = await self.dom_processor.extract_visible_content(page)

            return CaptureFrame(
                image_bytes=screenshot_bytes,
                scroll_position_y=scroll_pos,
                page_height=page_height,
                viewport_height=viewport_height,
                active_selector=active_selector,
                visible_html=visible_html,
                visible_text=visible_text,
                timestamp=datetime.now(),
            )

        except PlaywrightTimeoutError:
            logger.warning(f"Screenshot timeout for position {scroll_pos}")
            return None
        except Exception as e:
            logger.error(f"Failed to capture frame at position {scroll_pos}: {e}")
            return None
