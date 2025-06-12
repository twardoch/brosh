#!/usr/bin/env python3
# this_file: src/brosh/__init__.py

"""Browser screenshot tool using Playwright async API."""

from .api import capture_animation, capture_full_page, capture_visible_area, capture_webpage
from .cli import BrowserScreenshotCLI
from .models import CaptureConfig, ImageFormat
from .tool import BrowserScreenshotTool

__version__ = "0.1.0"
__all__ = [
    "BrowserScreenshotCLI",
    "BrowserScreenshotTool",
    "CaptureConfig",
    "ImageFormat",
    "capture_animation",
    "capture_full_page",
    "capture_visible_area",
    "capture_webpage",
]
