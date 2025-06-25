# this_file: src/brosh/constants.py

"""Centralized constants for the brosh package."""

# --- Browser Behavior ---
DEFAULT_FALLBACK_WIDTH: int = 1440
DEFAULT_FALLBACK_HEIGHT: int = 900
DEFAULT_VIEWPORT_HEIGHT_IF_FULLPAGE: int = 900  # Used when config.height is -1
DEFAULT_ZOOM_LEVEL: int = 100  # Percentage

# --- Browser Detection & Launch ---
RETINA_MIN_WIDTH: int = 2560  # Minimum physical width to consider a display Retina for scaling
BROWSER_LAUNCH_WAIT_SECONDS: int = 2  # Time to wait after killing browser before starting new one
BROWSER_CONNECT_RETRY_INTERVAL_SECONDS: int = 1  # Interval between connection attempts to new browser
BROWSER_CONNECT_MAX_ATTEMPTS: int = 10  # Max connection attempts to new browser
BROWSER_CONNECT_CDP_TIMEOUT_MS: int = 5000  # Timeout for Playwright's connect_over_cdp
BROWSER_CHECK_TIMEOUT_SECONDS: int = 2  # Timeout for checking if browser is running via HTTP for CLI

# --- Subprocess Timeouts ---
SUBPROCESS_GENERAL_TIMEOUT: int = 10  # General timeout for subprocess calls (e.g., system_profiler)
SUBPROCESS_PKILL_TIMEOUT: int = 5  # Timeout for pkill/taskkill subprocess calls

# --- Capture Process ---
PAGE_LOAD_DYNAMIC_CONTENT_WAIT_SECONDS: int = 3  # Wait after page.goto() for dynamic content
SCROLL_TO_SELECTOR_WAIT_SECONDS: int = 1  # Wait after scrolling to a specific selector
SCROLL_AND_CONTENT_WAIT_SECONDS: float = 0.8  # Wait after scrolling before taking screenshot

# --- MCP Specific ---
MCP_DEFAULT_SCALE: int = 50  # Default image scale percentage for MCP outputs
MCP_TRIM_TEXT_LENGTH: int = 200  # Max length for text in MCP output before trimming
MCP_MAX_SIZE_BYTES: int = 1024 * 1024  # 1MB, max size for MCP response
MCP_COMPRESSION_DOWNSAMPLE_PERCENTAGE: int = 50  # Downsample percentage for MCP image compression

# --- Image Processing & Naming ---
MILLISECONDS_PER_SECOND: int = 1000  # For APNG frame duration calculation
DEFAULT_OUTPUT_SUBFOLDER: str = "brosh"  # Default subfolder in user's pictures directory

# --- Default Debug Ports ---
# These are more like configurations than simple constants, kept in BrowserManager for now.
# DEBUG_PORT_CHROME: int = 9222
# DEBUG_PORT_EDGE: int = 9223
# DEBUG_PORT_SAFARI: int = 9225

# --- CLI Specific ---
# BROWSER_RESTART_WAIT_SECONDS is same as BROWSER_LAUNCH_WAIT_SECONDS
# BROWSER_CONNECT_VERIFY_ATTEMPTS is same as BROWSER_CONNECT_MAX_ATTEMPTS
# BROWSER_CONNECT_VERIFY_INTERVAL_SECONDS is same as BROWSER_CONNECT_RETRY_INTERVAL_SECONDS
# SUBPROCESS_PKILL_TIMEOUT_CLI is same as SUBPROCESS_PKILL_TIMEOUT
# These CLI-specific aliases can be removed from cli.py and constants used directly.
# If a distinct CLI value is ever needed, a new constant can be added here.
# Example: CLI_SUBPROCESS_PKILL_TIMEOUT if it needs to be different from general pkill.
# For now, assuming they can share the same value.
