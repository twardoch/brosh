#!/usr/bin/env python3
# this_file: src/brosh/browser.py

"""Browser management utilities for brosh."""

import asyncio
import platform
import shutil
import subprocess
from pathlib import Path

from loguru import logger

# Default screen dimensions if detection fails
DEFAULT_FALLBACK_WIDTH = 1440
DEFAULT_FALLBACK_HEIGHT = 900
# Minimum physical width to consider a display Retina for scaling
RETINA_MIN_WIDTH = 2560
# Timeout for subprocess calls like system_profiler
SUBPROCESS_TIMEOUT = 10
# Timeout for pkill/taskkill subprocess calls
SUBPROCESS_PKILL_TIMEOUT = 5
# Default viewport height to use when capturing "full page" (height = -1)
DEFAULT_VIEWPORT_HEIGHT_IF_FULLPAGE = 900
# Seconds to wait after killing browser processes before starting a new one
BROWSER_LAUNCH_WAIT_SECONDS = 2
# Seconds between attempts to connect to a newly launched browser
BROWSER_CONNECT_RETRY_INTERVAL_SECONDS = 1
# Maximum number of attempts to connect to a newly launched browser
BROWSER_CONNECT_MAX_ATTEMPTS = 10
# Timeout in milliseconds for playwright.chromium.connect_over_cdp
BROWSER_CONNECT_CDP_TIMEOUT_MS = 5000
# Default zoom level percentage
DEFAULT_ZOOM_LEVEL = 100


class BrowserManager:
    """Manages browser detection, launching, and connection.

    Used in:
    - cli.py
    - tool.py
    """

    def __init__(self, connection_timeout: int = 30):
        """Initialize browser manager.

        Args:
            connection_timeout: Timeout for browser connections in seconds

        """
        self.connection_timeout = connection_timeout
        self.debug_ports = {
            "chrome": 9222,
            "edge": 9223,
            "safari": 9225,
        }

    def get_screen_dimensions(self) -> tuple[int, int]:
        """Get main screen dimensions in logical pixels for browser sizing.

        Returns:
            Tuple of (width, height) in logical pixels (CSS pixels)

        Used in:
        - tool.py
        """
        if platform.system() == "Darwin":  # macOS
            try:
                # Get physical resolution
                system_profiler_path = shutil.which("system_profiler")
                if not system_profiler_path:
                    logger.warning("system_profiler not found, using fallback dimensions.")
                    return DEFAULT_FALLBACK_WIDTH, DEFAULT_FALLBACK_HEIGHT
                try:
                    # This is a blocking call, but get_screen_dimensions is a sync utility function.
                    result = subprocess.run(
                        [system_profiler_path, "SPDisplaysDataType"],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=SUBPROCESS_TIMEOUT,
                    )
                    for line in result.stdout.split("\n"):
                    if "Resolution:" in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if "x" in part and i > 0:
                                physical_width = int(parts[i - 1])
                                physical_height = int(parts[i + 1])

                                # Check if it's a Retina display
                                if "Retina" in line or physical_width >= RETINA_MIN_WIDTH:
                                    # Retina: logical = physical / 2
                                    return (
                                        physical_width // 2,
                                        physical_height // 2,
                                    )
                                # Non-Retina: logical = physical
                                return physical_width, physical_height
                        break

            except subprocess.CalledProcessError as e:
                logger.warning(f"system_profiler call failed: {e}, using fallback dimensions.")
            except subprocess.TimeoutExpired:
                logger.warning("system_profiler call timed out, using fallback dimensions.")
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse system_profiler output: {e}, using fallback dimensions.")
            except Exception as e: # Catch any other unexpected error
                logger.warning(f"Unexpected error getting macOS screen dimensions: {e}, using fallback dimensions.")


        elif platform.system() == "Windows":
            try:
                import tkinter as tk

                root = tk.Tk()
                # Get logical size (accounts for DPI scaling automatically)
                width = root.winfo_screenwidth()
                height = root.winfo_screenheight()
                root.destroy()
                return width, height
            except ImportError:
                logger.warning("tkinter not available on Windows")

        # Default fallback for unknown systems or errors
        return DEFAULT_FALLBACK_WIDTH, DEFAULT_FALLBACK_HEIGHT  # Common laptop logical resolution

    def get_browser_name(self, app: str = "") -> str:
        """Determine browser name from app parameter or OS default.

        Priority order: Chrome > Edge > Safari (macOS only)
        Firefox support removed per user request.

        Args:
            app: User-specified browser preference

        Returns:
            Browser name compatible with Playwright

        Used in:
        - cli.py
        - tool.py
        """
        if bool(app):
            app_lower = app.lower()
            if "chrome" in app_lower:
                return "chrome"
            if "edge" in app_lower:
                return "edge"
            if "safari" in app_lower and platform.system() == "Darwin":
                return "safari"

        # Auto-detect available browser in priority order
        if platform.system() == "Darwin":  # macOS
            # Priority: Chrome > Edge > Safari
            for browser in ["chrome", "edge", "safari"]:
                if self.is_browser_available(browser):
                    return browser
        else:  # Windows/Linux
            # Priority: Chrome > Edge
            for browser in ["chrome", "edge"]:
                if self.is_browser_available(browser):
                    return browser

        # Fallback
        return "chrome"

    def is_browser_available(self, browser_name: str) -> bool:
        """Check if browser is installed and available.

        Args:
            browser_name: Browser name to check

        Returns:
            True if browser is available

        """
        paths = self.get_browser_paths(browser_name)

        # Check if any path exists
        return any(Path(path).exists() for path in paths)

    def get_browser_paths(self, browser_name: str) -> list:
        """Get possible paths for a browser.

        Args:
            browser_name: Browser name

        Returns:
            List of possible paths

        """
        if browser_name == "chrome":
            return [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/opt/google/chrome/chrome",
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            ]
        if browser_name == "edge":
            return [
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
            ]
        if browser_name == "safari":
            return ["/Applications/Safari.app/Contents/MacOS/Safari"]
        return []

    def find_browser_path(self, browser_name: str) -> str | None:
        """Find the path to the specified browser executable.

        Args:
            browser_name: Name of the browser to find

        Returns:
            Path to browser executable or None if not found

        Used in:
        - cli.py
        """
        paths = self.get_browser_paths(browser_name)

        return next((path_str for path_str in paths if Path(path_str).exists()), None)

    async def get_browser_instance(self, playwright, browser_name: str, width: int, height: int, zoom: int) -> tuple:
        """Get browser instance, connecting to user's actual browser.

        This method tries to connect to the user's existing browser in
        debug mode. If that fails, it will attempt to restart the browser
        in debug mode.

        Args:
            playwright: Playwright instance
            browser_name: Name of browser to use
            width: Viewport width
            height: Viewport height
            zoom: Zoom level percentage

        Returns:
            Tuple of (browser, context, page)

        Raises:
            RuntimeError: If browser connection fails

        Used in:
        - tool.py
        """
        debug_port = self.debug_ports.get(browser_name, 9222)

        # Try to connect to existing browser instance first
        browser = None
        try:
            if browser_name in ["chrome", "edge"]:
                browser = await playwright.chromium.connect_over_cdp(
                    f"http://localhost:{debug_port}",
                    timeout=self.connection_timeout * 1000,
                )

            if browser:
                # Don't set device_scale_factor - let browser use natural scaling
                # Use default height if height is -1 (capture entire page)
                viewport_height = height if height != -1 else DEFAULT_VIEWPORT_HEIGHT_IF_FULLPAGE
                context = await browser.new_context(viewport={"width": width, "height": viewport_height})
                page = await context.new_page()

                # Apply zoom via CSS instead of device scale factor
                if zoom != DEFAULT_ZOOM_LEVEL:  # PLR2004
                    await page.add_init_script(f"""
                        document.addEventListener('DOMContentLoaded', () => {{
                            document.body.style.zoom = '{zoom}%';
                        }});
                    """)

                return browser, context, page
        except Exception as e:
            logger.info(f"Could not connect to existing browser: {e}")
            logger.info("Attempting to start browser in debug mode...")

        # If we can't connect, try to launch the user's actual browser
        # in debug mode (not Playwright's browser)
        browser = None

        if browser_name == "chrome":
            # Try to launch user's Chrome in debug mode
            chrome_paths = self.get_browser_paths("chrome")

            for chrome_path in chrome_paths:
                if await self.launch_browser_and_connect(
                    chrome_path,
                    debug_port,
                    width,
                    height,
                    playwright.chromium,
                    "chrome",
                ):
                    browser = await playwright.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
                    break

        elif browser_name == "edge":
            # Try to launch user's Edge in debug mode
            edge_paths = self.get_browser_paths("edge")

            for edge_path in edge_paths:
                if await self.launch_browser_and_connect(
                    edge_path,
                    debug_port,
                    width,
                    height,
                    playwright.chromium,
                    "edge",
                ):
                    browser = await playwright.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
                    break

        elif browser_name == "safari":
            # For Safari, we need to enable "Develop" menu first
            logger.info("For Safari: Enable Develop menu in Preferences > Advanced")
            logger.info("Then enable 'Allow Remote Automation' in Develop menu")
            # Safari doesn't support remote debugging like Chrome/Firefox
            # Fall back to launching safari
            browser = await playwright.webkit.launch(headless=False)

        if not browser:
            msg = (
                f"Could not connect to or launch {browser_name} browser. "
                "Please ensure the browser is installed and try again."
            )
            raise RuntimeError(msg)

        # Create context without device scale factor to avoid scaling issues
        # Use default height if height is -1 (capture entire page)
        viewport_height = height if height != -1 else DEFAULT_VIEWPORT_HEIGHT_IF_FULLPAGE
        context = await browser.new_context(viewport={"width": width, "height": viewport_height})
        page = await context.new_page()

        # Apply zoom via CSS instead of device scale factor
        if zoom != DEFAULT_ZOOM_LEVEL:  # PLR2004
            await page.add_init_script(f"""
                document.addEventListener('DOMContentLoaded', () => {{
                    document.body.style.zoom = '{zoom}%';
                }});
            """)

        return browser, context, page

    async def launch_browser_and_connect(
        self,
        browser_path: str,
        debug_port: int,
        width: int,
        height: int,
        playwright_browser,
        browser_type: str,
    ) -> bool:
        """Launch browser with debug mode and test connection.

        Args:
            browser_path: Path to browser executable
            debug_port: Debug port to use
            width: Window width
            height: Window height
            playwright_browser: Playwright browser module
            browser_type: Type of browser (chrome, edge)

        Returns:
            True if successfully launched and connected

        """
        if not Path(browser_path).exists():
            logger.debug(f"Browser path does not exist: {browser_path}")
            return False

        try:
            # Kill existing processes with same debug port - more aggressive cleanup
            try:
                if platform.system() == "Darwin":  # macOS
                    pkill_path = shutil.which("pkill")
                    if pkill_path:
                        # Kill by process name and port
                        # These are fire-and-forget, so not strictly blocking the async flow.
                        subprocess.Popen(
                            [pkill_path, "-f", f"remote-debugging-port={debug_port}"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                        # Also try killing by process name
                        if "chrome" in browser_path.lower():
                            subprocess.Popen(
                                [pkill_path, "-f", "Google Chrome.*remote-debugging"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                            )
                    else:
                        logger.warning("pkill command not found for process cleanup.")
                else:  # Windows/Linux
                    taskkill_path = shutil.which("taskkill")
                    if taskkill_path:
                        subprocess.Popen(
                            [taskkill_path, "/F", "/IM", "chrome.exe"], # General cleanup for Chrome
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                        # Add similar for Edge if browser_type is edge
                        if "edge" in browser_path.lower():
                             subprocess.Popen(
                                [taskkill_path, "/F", "/IM", "msedge.exe"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                            )
                    else:
                        logger.warning("taskkill command not found for process cleanup.")
            except Exception as e:
                logger.warning(f"Process cleanup issue: {e}") # Changed to warning

            await asyncio.sleep(BROWSER_LAUNCH_WAIT_SECONDS)

            # Launch browser with remote debugging
            if browser_type in ["chrome", "edge"]:
                args = [
                    browser_path,
                    f"--remote-debugging-port={debug_port}",
                    "--no-startup-window",
                    "--noerrdialogs",
                    "--no-user-gesture-required",
                    "--no-network-profile-warning",
                    "--no-first-run",
                    "--no-experiments",
                    "--no-default-browser-check",
                    "--remote-debug-mode",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-infobars",
                    "--disable-extensions",
                    "--disable-sync",
                    "--disable-translate",
                    "--disable-background-networking",
                    f"--window-size={width},{height}",
                    "--user-data-dir=/tmp/chrome-debug-brosh",
                ]
            else:
                return False

            logger.info(f"Launching {browser_type} with debug port {debug_port}")
            process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Wait for browser to start and test connection more robustly
            for attempt in range(BROWSER_CONNECT_MAX_ATTEMPTS):  # More attempts
                await asyncio.sleep(BROWSER_CONNECT_RETRY_INTERVAL_SECONDS)  # Shorter intervals
                try:
                    if browser_type in ["chrome", "edge"]:
                        test_browser = await playwright_browser.connect_over_cdp(
                            f"http://localhost:{debug_port}", timeout=BROWSER_CONNECT_CDP_TIMEOUT_MS
                        )
                    else:
                        return False

                    # Test that we can actually create a page
                    test_context = await test_browser.new_context()
                    test_page = await test_context.new_page()
                    await test_page.close()
                    await test_context.close()
                    await test_browser.close()

                    logger.info(f"Successfully launched {browser_type} at {browser_path}")
                    return True

                except Exception as e:
                    logger.debug(f"Connection attempt {attempt + 1}/{BROWSER_CONNECT_MAX_ATTEMPTS} failed: {e}")
                    if attempt == BROWSER_CONNECT_MAX_ATTEMPTS - 1:  # Last attempt
                        # Kill the process we started if it's still running
                        try:
                            process.terminate()
                            await asyncio.sleep(BROWSER_CONNECT_RETRY_INTERVAL_SECONDS)
                            if process.poll() is None:
                                process.kill()
                        except Exception:
                            pass
                        return False
                    continue

        except Exception as e:
            logger.error(f"Failed to launch {browser_type} at {browser_path}: {e}")
            return False

        return False  # Explicit return for all paths

    async def cleanup_browser(self, page, context, browser) -> None:
        """Clean up browser resources safely.

        Args:
            page: Playwright page instance
            context: Playwright context instance
            browser: Playwright browser instance

        Used in:
        - tool.py
        """
        try:
            if page:
                await page.close()
        except Exception as e:
            logger.warning(f"Failed to close page: {e}")

        try:
            if context:
                await context.close()
        except Exception as e:
            logger.warning(f"Failed to close context: {e}")

        try:
            if hasattr(browser, "_browser") and browser._browser:
                await browser.close()
        except Exception as e:
            logger.warning(f"Failed to close browser: {e}")

    def get_browser_args(self, browser_type: str, width: int, height: int, debug_port: int) -> list:
        """Get browser launch arguments.

        Args:
            browser_type: Type of browser
            width: Window width
            height: Window height
            debug_port: Debug port

        Returns:
            List of command line arguments

        Used in:
        - cli.py
        """
        if browser_type in ["chrome", "edge"]:
            return [
                f"--remote-debugging-port={debug_port}",
                "--no-startup-window",
                "--noerrdialogs",
                "--no-user-gesture-required",
                "--no-network-profile-warning",
                "--no-first-run",
                "--no-experiments",
                "--no-default-browser-check",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-infobars",
                "--disable-extensions",
                "--disable-sync",
                "--disable-translate",
                "--disable-background-networking",
                f"--window-size={width},{height}",
                "--user-data-dir=/tmp/chrome-debug-brosh",
            ]
        return []
