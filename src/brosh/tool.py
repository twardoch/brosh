#!/usr/bin/env python3
# this_file: src/brosh/tool.py

"""Main screenshot tool orchestration for brosh."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from loguru import logger
from platformdirs import user_pictures_dir
from playwright.async_api import async_playwright

from .browser import BrowserManager
from .capture import CaptureManager
from .image import ImageProcessor
from .models import CaptureConfig, CaptureFrame, ImageFormat
from .texthtml import DOMProcessor

MILLISECONDS_PER_SECOND = 1000
DEFAULT_SCALE_PERCENTAGE = 100


def dflt_output_folder(subfolder: str | Path = "brosh") -> Path:
    """Get the 'brosh' folder within the user's pictures directory."""
    return Path(user_pictures_dir(), subfolder)


class BrowserScreenshotTool:
    """Main tool implementation orchestrating the capture process.

    Used in:
    - __init__.py
    - api.py
    """

    def __init__(self, *, verbose: bool = False): # verbose is already keyword-only
        """Initialize the screenshot tool.

        Args:
            verbose: Enable debug logging

        """
        self.verbose = verbose
        self.browser_manager = BrowserManager()
        self.capture_manager = CaptureManager()
        self.image_processor = ImageProcessor()
        self.dom_processor = DOMProcessor()

    async def capture(self, config: CaptureConfig) -> dict[str, dict[str, Any]]:
        """Main capture method orchestrating the entire process.

        Args:
            config: Validated capture configuration

        Returns:
            Dictionary mapping file paths to metadata

        Raises:
            RuntimeError: For browser or capture failures

        Used in:
        - api.py
        """
        # Parse URL for domain-based naming
        parsed_url = urlparse(config.url)
        domain = parsed_url.netloc.replace("www.", "").replace(".", "_")
        if not domain:
            msg = f"Invalid URL: {config.url}"
            raise ValueError(msg)

        # Setup output directory
        output_path = self._setup_output_directory(config, domain)

        # Get screen dimensions if not specified
        if config.width == 0 or config.height == 0:
            default_width, default_height = self.browser_manager.get_screen_dimensions()
            if config.width == 0:
                config.width = default_width
            if config.height == 0:
                config.height = default_height

        logger.info(f"Starting capture of {config.url}")

        results = {}
        async with async_playwright() as p:
            # Get browser instance
            browser, context, page = await self.browser_manager.get_browser_instance(
                p, self.browser_manager.get_browser_name(config.app), config.width, config.height, config.zoom
            )

            try:
                # Capture frames (in-memory)
                frames = await self.capture_manager.capture_frames(page, config)

                if not frames:
                    msg = "No frames captured"
                    raise RuntimeError(msg)

                # Process based on format
                if config.format == ImageFormat.APNG:
                    results = await self._process_apng_frames(frames, domain, output_path, config)
                else:
                    results = await self._process_regular_frames(frames, domain, output_path, config)

                logger.info(f"Successfully captured {len(results)} screenshots")

            finally:
                await self.browser_manager.cleanup_browser(page, context, browser)

        return results

    def _setup_output_directory(self, config: CaptureConfig, domain: str) -> Path:
        """Setup output directory structure.

        Args:
            config: Capture configuration
            domain: Domain name for subdirectory

        Returns:
            Path to output directory

        """
        output_path = Path(config.output_dir)
        if config.subdirs:
            output_path = output_path / domain
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path

    async def _process_regular_frames(
        self, frames: list[CaptureFrame], domain: str, output_path: Path, config: CaptureConfig
    ) -> dict[str, dict[str, Any]]:
        """Process frames for regular image formats (PNG/JPG).

        Args:
            frames: Captured frames
            domain: Domain name for filename
            output_path: Output directory
            config: Capture configuration

        Returns:
            Results dictionary

        """
        results = {}
        timestamp = datetime.now(timezone.utc).strftime("%y%m%d-%H%M%S") # Ensured timezone.utc is used

        for _i, frame in enumerate(frames):
            # Generate filename
            section_id = await self._get_section_id_from_frame(frame)
            filename = f"{domain}-{timestamp}-{frame.scroll_percentage:05d}-{section_id}.{config.format.value}"
            filepath = output_path / filename

            # Process image bytes
            image_bytes = frame.image_bytes

            # Scale if needed
            if config.scale != DEFAULT_SCALE_PERCENTAGE:
                image_bytes = self.image_processor.downsample_png_bytes(image_bytes, config.scale)

            # Convert format if needed
            if config.format == ImageFormat.JPG:
                image_bytes = self.image_processor.convert_png_to_jpg_bytes(image_bytes)
            elif config.format == ImageFormat.PNG:
                image_bytes = self.image_processor.optimize_png_bytes(image_bytes)

            # Save to disk
            filepath.write_bytes(image_bytes)

            # Store metadata
            metadata = {"selector": frame.active_selector, "text": frame.visible_text or ""}
            if config.fetch_html and frame.visible_html:
                metadata["html"] = self.dom_processor.compress_html(frame.visible_html)

            results[str(filepath)] = metadata

        return results

    async def _process_apng_frames(
        self, frames: list[CaptureFrame], domain: str, output_path: Path, config: CaptureConfig
    ) -> dict[str, dict[str, Any]]:
        """Process frames for APNG animation.

        Args:
            frames: Captured frames
            domain: Domain name for filename
            output_path: Output directory
            config: Capture configuration

        Returns:
            Results dictionary with APNG path

        """
        # Process all frame bytes
        frame_bytes_list = []
        for frame in frames:
            image_bytes = frame.image_bytes
            if config.scale != DEFAULT_SCALE_PERCENTAGE:
                image_bytes = self.image_processor.downsample_png_bytes(image_bytes, config.scale)
            frame_bytes_list.append(image_bytes)

        # Create APNG
        delay_ms = int(config.anim_spf * MILLISECONDS_PER_SECOND)
        apng_bytes = self.image_processor.create_apng_bytes(frame_bytes_list, delay_ms)

        # Save APNG
        apng_filename = f"{domain}-animated.png"
        apng_path = output_path / apng_filename
        apng_path.write_bytes(apng_bytes)

        # Return metadata for the animation
        return {
            str(apng_path): {
                "selector": "animated",
                "text": f"Animation with {len(frames)} frames",
                "frames": len(frames),
            }
        }

    async def _get_section_id_from_frame(self, _frame: CaptureFrame) -> str: # Prefixed unused frame with _
        """Extract section ID from frame metadata.

        Args:
            _frame: Capture frame (currently unused, placeholder for future logic)

        Returns:
            Section identifier string

        """
        # This would be populated during capture
        # For now, return a default
        return "section"
