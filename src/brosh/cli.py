#!/usr/bin/env python3
# this_file: src/brosh/cli.py

"""CLI interface for brosh."""

import inspect
import json
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

import fire
from loguru import logger

from .api import capture_webpage
# Removed unused ImageFormat import: from .models import ImageFormat
from .browser import DEFAULT_FALLBACK_HEIGHT, DEFAULT_FALLBACK_WIDTH, BrowserManager
from .tool import dflt_output_folder

# Timeout for checking if browser is running via HTTP
BROWSER_CHECK_TIMEOUT_SECONDS = 2
# Seconds to wait after quitting browser before starting a new one
BROWSER_RESTART_WAIT_SECONDS = 2
# Max attempts to verify browser connection after launch
BROWSER_CONNECT_VERIFY_ATTEMPTS = 10
# Interval in seconds between browser connection verification attempts
BROWSER_CONNECT_VERIFY_INTERVAL_SECONDS = 1
# Timeout for pkill/taskkill subprocess calls
SUBPROCESS_PKILL_TIMEOUT_CLI = 5
# Max length for text preview in CLI output
CLI_TEXT_PREVIEW_LENGTH = 100


class BrowserScreenshotCLI:
    """Fire CLI interface for browser screenshot operations.

    Provides organized commands for browser management and screenshot capture.

    Used in:
    - __init__.py
    - __main__.py
    """

    def __init__(
        self,
        app: str = "",
        width: int = 0,
        height: int = 0,
        zoom: int = 100,
        output_dir: Path | None = None,  # B008: Changed default
        *,
        subdirs: bool = False,
        verbose: bool = False,
        json: bool = False,
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
            json: Output results as JSON

        """
        self.app = app
        self.width = width
        self.height = height
        self.zoom = zoom
        if output_dir is None:  # B008: Added handling
            output_dir = Path(dflt_output_folder())
        self.output_dir = output_dir
        self.subdirs = subdirs
        self.json = json
        self.verbose = verbose

        if not verbose:
            logger.remove()
            logger.add(sys.stderr, level="ERROR")

        self._browser_manager = BrowserManager()

    def run(self, *, force_run: bool = False) -> str:
        """Run browser in remote debug mode.

        Args:
            force_run: Always restart browser even if already running

        Returns:
            Status message

        Used in:
        - api.py
        - browser.py
        - mcp.py
        """
        browser_name = self._browser_manager.get_browser_name(self.app)
        debug_ports = self._browser_manager.debug_ports
        debug_port = debug_ports.get(browser_name, 9222)

        # Check if already running
        if not force_run:
            try:
                import urllib.request

                urllib.request.urlopen(f"http://localhost:{debug_port}/json", timeout=BROWSER_CHECK_TIMEOUT_SECONDS)
                return f"{browser_name} already running on port {debug_port}"
            except Exception:
                pass

        # Kill existing processes first if force_run
        if force_run:
            self.quit()
            time.sleep(BROWSER_RESTART_WAIT_SECONDS)

        # Launch browser directly with debug args
        browser_path_found = self._browser_manager.find_browser_path(browser_name)
        if not browser_path_found:
            return f"Could not find {browser_name} installation"

        # Ensure the found path is a valid executable using shutil.which
        browser_executable_path = shutil.which(browser_path_found)
        if not browser_executable_path:
            return f"Browser executable not found or not runnable at {browser_path_found}"

        try:
            width = self.width or DEFAULT_FALLBACK_WIDTH
            height = self.height or DEFAULT_FALLBACK_HEIGHT

            args = [browser_executable_path, *self._browser_manager.get_browser_args(browser_name, width, height, debug_port)]

            if not args[1:]:  # No args returned (not chromium/msedge)
                return f"Browser {browser_name} not supported for direct launch"

            logger.info(f"Starting {browser_name} with debug port {debug_port} using {browser_executable_path}")
            subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Wait and verify connection
            for _attempt in range(BROWSER_CONNECT_VERIFY_ATTEMPTS):
                time.sleep(BROWSER_CONNECT_VERIFY_INTERVAL_SECONDS)
                try:
                    import urllib.request

                    urllib.request.urlopen(f"http://localhost:{debug_port}/json", timeout=BROWSER_CHECK_TIMEOUT_SECONDS)
                    return f"Started {browser_name} in debug mode on port {debug_port}"
                except Exception as e:
                    logger.debug(f"Connection verification attempt failed for port {debug_port}: {e}")
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
                pkill_path = shutil.which("pkill")
                if pkill_path:
                    subprocess.run(
                        [pkill_path, "-f", f"remote-debugging-port={debug_port}"],
                        capture_output=True,
                        timeout=SUBPROCESS_PKILL_TIMEOUT_CLI,
                        check=False,
                    )
                    if "chrome" in browser_name.lower():
                        subprocess.run(
                            [pkill_path, "-f", "Google Chrome.*remote-debugging"],
                            capture_output=True,
                            timeout=SUBPROCESS_PKILL_TIMEOUT_CLI,
                            check=False,
                        )
                else:
                    logger.warning("pkill command not found.")
            else:  # Windows/Linux
                taskkill_path = shutil.which("taskkill")
                if taskkill_path:
                    subprocess.run(
                        [taskkill_path, "/F", "/IM", "chrome.exe"],
                        capture_output=True,
                        timeout=SUBPROCESS_PKILL_TIMEOUT_CLI,
                        check=False,
                    )
                else:
                    logger.warning("taskkill command not found.")

            return f"Quit {browser_name}"
        except Exception as e:
            return f"Failed to quit {browser_name}: {e}"

    def shot(self, url: str, **kwargs):
        """Take screenshots of a webpage.

        This method delegates to the api.capture_webpage function,
        automatically using the parameter definitions from there.

        Args:
            url: The URL to capture
            **kwargs: All parameters from api.capture_webpage

        Returns:
            Screenshot results (dict or JSON string based on --json flag)

        """
        # Ensure browser is running in debug mode
        self.run(force_run=False)

        # Merge global CLI options with command-specific options
        merged_kwargs = {
            "url": url,
            "app": self.app,
            "width": self.width,
            "height": self.height,
            "zoom": self.zoom,
            "output_dir": self.output_dir,
            "subdirs": self.subdirs,
        }

        # Override with any command-specific options
        merged_kwargs.update(kwargs)

        # Filter to only valid parameters for capture_webpage
        sig = inspect.signature(capture_webpage)
        valid_params = {k: v for k, v in merged_kwargs.items() if k in sig.parameters}
        if "app" in merged_kwargs:
            valid_params["app"] = merged_kwargs["app"]

        # Call the API
        try:
            result = capture_webpage(**valid_params)

            if self.json:
                return json.dumps(result, indent=2)
            # Pretty print results
            for _path, metadata in result.items():
                if metadata.get("text"):
                    text = metadata["text"]
                    metadata["text"] = (
                        f"{text[:CLI_TEXT_PREVIEW_LENGTH]}..."
                        if len(text) > CLI_TEXT_PREVIEW_LENGTH
                        else text
                    )

            return result

        except Exception as e:
            if self.json:
                return json.dumps({"error": str(e)})
            logger.error(f"Failed to capture screenshots: {e}")
            raise

    def mcp(self) -> None:
        """Run MCP server for browser screenshots.

        Automatically ensures browser is running in debug mode.

        """
        # Ensure browser is running in debug mode
        self.run(force_run=False)

        # Import and run MCP server
        from .mcp import run_mcp_server

        run_mcp_server()


def main():
    """Main CLI entry point."""
    fire.Fire(BrowserScreenshotCLI)


if __name__ == "__main__":
    main()
