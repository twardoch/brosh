#!/usr/bin/env python3
# this_file: src/brosh/cli.py

"""CLI interface for brosh."""

import asyncio
import platform
import subprocess
import time

import platformdirs
from loguru import logger

from .browser import BrowserManager
from .tool import BrowserScreenshotTool


class BrowserScreenshotCLI:
    """Fire CLI interface for browser screenshot operations.

    Provides organized commands for browser management and screenshot capture.

    """

    def __init__(
        self,
        app: str = "",
        width: int = 0,
        height: int = 0,
        zoom: int = 100,
        output_dir: str = platformdirs.user_pictures_dir(),
        subdirs: bool = False,
        verbose: bool = False,
    ) -> None:
        """Initialize CLI with common parameters.

        Args:
            app: Browser to use - chrome, edge, safari (default: auto-detect)
            width: Width in pixels (default: screen width)
            height: Height in pixels (-1: no limit, default: screen height)
            zoom: Zoom level in % (default: 100)
            output_dir: Output folder for screenshots (default: user's pictures)
            subdirs: Create subfolders per domain
            verbose: Enable debug logging

        """
        self.app = app
        self.width = width
        self.height = height
        self.zoom = zoom
        self.output_dir = output_dir
        self.subdirs = subdirs
        self.verbose = verbose
        self._tool = BrowserScreenshotTool(verbose=verbose)
        self._browser_manager = BrowserManager()

    def run(self, force_run: bool = False) -> str:
        """Run browser in remote debug mode.

        Args:
            force_run: Always restart browser even if already running

        Returns:
            Status message

        """
        browser_name = self._browser_manager.get_browser_name(self.app)
        debug_ports = self._browser_manager.debug_ports
        debug_port = debug_ports.get(browser_name, 9222)

        # Check if already running
        if not force_run:
            try:
                import urllib.request

                urllib.request.urlopen(f"http://localhost:{debug_port}/json", timeout=2)
                return f"{browser_name} already running on port {debug_port}"
            except Exception:
                pass

        # Kill existing processes first if force_run
        if force_run:
            self.quit()
            time.sleep(2)

        # Launch browser directly with debug args
        browser_path = self._browser_manager.find_browser_path(browser_name)
        if not browser_path:
            return f"Could not find {browser_name} installation"

        try:
            width = self.width or 1440
            height = self.height or 900

            args = [browser_path, *self._browser_manager.get_browser_args(browser_name, width, height, debug_port)]

            if not args[1:]:  # No args returned (not chromium/msedge)
                return f"Browser {browser_name} not supported for direct launch"

            logger.info(f"Starting {browser_name} with debug port {debug_port}")
            subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Wait and verify connection
            for _attempt in range(10):
                time.sleep(1)
                try:
                    import urllib.request

                    urllib.request.urlopen(f"http://localhost:{debug_port}/json", timeout=2)
                    return f"Started {browser_name} in debug mode on port {debug_port}"
                except Exception:
                    continue

            return f"Started {browser_name} but could not verify debug connection"

        except Exception as e:
            return f"Failed to start {browser_name}: {e}"

    def quit(self) -> str:
        """Quit the specified browser.

        Returns:
            Status message

        """
        browser_name = self._browser_manager.get_browser_name(self.app)
        debug_ports = self._browser_manager.debug_ports
        debug_port = debug_ports.get(browser_name, 9222)

        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run(
                    ["pkill", "-f", f"remote-debugging-port={debug_port}"],
                    capture_output=True,
                    timeout=5,
                    check=False,
                )
                if "chrome" in browser_name.lower():
                    subprocess.run(
                        ["pkill", "-f", "Google Chrome.*remote-debugging"],
                        capture_output=True,
                        timeout=5,
                        check=False,
                    )
            else:  # Windows/Linux
                subprocess.run(
                    ["taskkill", "/F", "/IM", "chrome.exe"],
                    capture_output=True,
                    timeout=5,
                    check=False,
                )

            return f"Quit {browser_name}"
        except Exception as e:
            return f"Failed to quit {browser_name}: {e}"

    def shot(
        self,
        url: str,
        scroll_step: int = 100,
        scale: int = 100,
        format: str = "png",
        anim_spf: float = 0.5,
        html: bool = False,
        max_frames: int = 0,
        json: bool = False,
        from_selector: str = "",
    ) -> list[str] | dict[str, str] | str:
        """Take screenshots of a webpage.

        Automatically ensures browser is running in debug mode.

        Args:
            url: The URL to navigate to (mandatory)
            scroll_step: Scroll step in % of height (default: 100)
            scale: Scale in % for resampling output image (default: 100)
            format: Output format - png, jpg, or apng (default: png)
            anim_spf: Seconds per frame for APNG animation (default: 0.5)
            html: Return dict with HTML/selectors instead of list (default: False)
            max_frames: Maximum number of frames to capture, 0 for all (default: 0)
            json: Return JSON string output (default: False)
            from_selector: CSS selector to scroll to before starting capture (default: "")

        Returns:
            If json=True: JSON string of the results
            If html=True: Dict with screenshot paths as keys and HTML/selectors as values
            If html=False: List of paths to saved screenshot files

        """
        # Ensure browser is running in debug mode
        self.run(force_run=False)

        result = asyncio.run(
            self._tool.capture(
                url=url,
                zoom=self.zoom,
                width=self.width,
                height=self.height,
                scroll_step=scroll_step,
                scale=scale,
                app=self.app,
                output_dir=self.output_dir,
                subdirs=self.subdirs,
                mcp=False,
                format=format,
                anim_spf=anim_spf,
                html=html,
                max_frames=max_frames,
                from_selector=from_selector,
            )
        )

        if json:
            import json as json_module

            return json_module.dumps(result, indent=2)
        return result

    def mcp(self) -> None:
        """Run MCP server for browser screenshots.

        Automatically ensures browser is running in debug mode.

        """
        # Ensure browser is running in debug mode
        self.run(force_run=False)

        # Import and run MCP server
        from .mcp import run_mcp_server

        run_mcp_server()
