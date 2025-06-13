"""Pytest configuration and fixtures for brosh tests."""

import asyncio
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic.networks import AnyUrl

from brosh.models import CaptureConfig, CaptureFrame, ImageFormat


@pytest.fixture
def temp_output_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for test outputs.

    Used in:
    - tests/test_api.py
    - tests/test_cli.py
    - tests/test_models.py
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_url() -> AnyUrl:
    """Provide a sample URL for testing."""
    return AnyUrl("https://example.com")


@pytest.fixture
def sample_capture_config(temp_output_dir: Path, sample_url: AnyUrl) -> CaptureConfig:
    """Provide a sample CaptureConfig for testing."""
    return CaptureConfig(
        url=str(sample_url),
        width=1024,
        height=768,
        zoom=100,
        scroll_step=100,
        scale=100,
        format=ImageFormat.PNG,
        app="chrome",
        output_dir=str(temp_output_dir),
        subdirs=False,
        anim_spf=0.5,
        html=False,
        max_frames=0,
        from_selector="",
    )


@pytest.fixture
def sample_capture_frame() -> CaptureFrame:
    """Provide a sample CaptureFrame for testing."""
    return CaptureFrame(
        image_bytes=b"fake_image_data",
        scroll_position_y=0,
        page_height=2000,
        viewport_height=800,
        active_selector="body",
        visible_html="<html><body>Test content</body></html>",
        visible_text="Test content",
    )


@pytest.fixture
def mock_playwright_page() -> MagicMock:
    """Provide a mock Playwright page object."""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.set_viewport_size = AsyncMock()
    page.screenshot = AsyncMock(return_value=b"fake_screenshot_data")
    page.evaluate = AsyncMock(return_value={"height": 2000, "width": 1024})
    page.query_selector = AsyncMock()
    page.content = AsyncMock(return_value="<html><body>Test</body></html>")
    return page


@pytest.fixture
def mock_playwright_context() -> MagicMock:
    """Provide a mock Playwright context object."""
    context = AsyncMock()
    context.new_page = AsyncMock()
    context.close = AsyncMock()
    return context


@pytest.fixture
def mock_playwright_browser() -> MagicMock:
    """Provide a mock Playwright browser object."""
    browser = AsyncMock()
    browser.new_context = AsyncMock()
    browser.close = AsyncMock()
    return browser


@pytest.fixture
def mock_playwright() -> MagicMock:
    """Provide a mock Playwright instance."""
    p = MagicMock()
    p.chromium = AsyncMock()
    p.firefox = AsyncMock()
    p.webkit = AsyncMock()
    return p


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.close()
