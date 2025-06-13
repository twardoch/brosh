#!/usr/bin/env python3
# this_file: src/brosh/__init__.py

"""Browser screenshot tool using Playwright async API."""

from .api import (
    capture_animation,
    capture_full_page,
    capture_visible_area,
    capture_webpage,
)
from .cli import BrowserScreenshotCLI
from .models import CaptureConfig, ImageFormat
from .tool import BrowserScreenshotTool

try:
    from .__version__ import __version__
except ImportError:
    # Fallback version if __version__.py is not available
    __version__ = "0.0.0+unknown"
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
