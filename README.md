# brosh - Browser Screenshot Tool

**Brosh** is an advanced browser screenshot tool designed for developers, QA testers, AI engineers, and content creators. It excels at capturing comprehensive, scrolling screenshots of webpages using Playwright's asynchronous API.

**What it does:** Brosh automates the process of taking full-page or partial screenshots, including those requiring scrolling. It can capture single images, a series of images, or even animated PNGs (APNGs) of the scrolling process. Beyond pixels, Brosh intelligently extracts visible text content (as Markdown) and optionally, the underlying HTML structure of captured sections.

**Who it's for:**
*   **Developers & QA Testers:** For visual regression testing, bug reporting, and documenting web application states.
*   **AI Engineers & Researchers:** To provide visual and textual context of webpages to AI models, especially via its Model Context Protocol (MCP) server.
*   **Content Creators & Archivists:** For capturing and preserving web content, creating documentation, or generating visual assets.
*   **Anyone needing high-quality webpage captures:** If you need more than a simple print-screen, Brosh offers fine-grained control and rich output.

**Why it's useful:**
*   **Comprehensive Captures:** Goes beyond the visible part of the page, capturing entire scrolling sections.
*   **Intelligent Extraction:** Provides not just images, but also the textual content and HTML structure, crucial for AI understanding and content analysis.
*   **Automation & Integration:** Offers a CLI for scripting, a Python API for programmatic use, and an MCP server for seamless integration with AI tools like Claude.
*   **Flexibility & Control:** Allows customization of browser type, viewport dimensions, zoom levels, output formats, and more.
*   **Unique Value:** Brosh's distinctive capability lies in its intelligent content detection (semantic section naming, text/HTML extraction) and its AI-ready capture features, setting it apart from basic screenshot utilities.

[![Python Version](https://img.shields.io/pypi/pyversions/brosh)](https://pypi.org/project/brosh/)
[![PyPI version](https://badge.fury.io/py/brosh.svg)](https://badge.fury.io/py/brosh)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://github.com/twardoch/brosh/actions/workflows/push.yml/badge.svg)](https://github.com/twardoch/brosh/actions/workflows/push.yml)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/redirect/twardoch/brosh)](https://coverage-badge.samuelcolvin.workers.dev/redirect/twardoch/brosh)

## 1. Table of Contents

- [Features](#features)
- [How It Works (Conceptual Overview)](#how-it-works-conceptual-overview)
- [Installation](#installation)
  - [Using uv/uvx (Recommended)](#using-uvuvx-recommended)
  - [Using pip](#using-pip)
  - [Using pipx](#using-pipx)
  - [From Source](#from-source)
  - [Install Playwright Browsers](#install-playwright-browsers)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Command Line Interface (CLI)](#command-line-interface-cli)
  - [Python API](#python-api)
  - [MCP Server Mode](#mcp-server-mode)
- [Command Reference](#command-reference)
  - [Global Options](#global-options)
  - [Commands](#commands)
- [Output](#output)
  - [File Naming Convention](#file-naming-convention)
  - [Output Formats](#output-formats)
  - [JSON Output Details](#json-output-details)
- [Technical Architecture Deep Dive](#technical-architecture-deep-dive)
  - [Core Modules and Flow](#core-modules-and-flow)
  - [Key Architectural Components (Business Domains)](#key-architectural-components-business-domains)
    - [Content Capture Engine (`capture.py`, `texthtml.py`)](#content-capture-engine-capturepy-texthtmlpy)
    - [Browser Integration Layer (`browser.py`)](#browser-integration-layer-browserpy)
    - [AI Integration Protocol (`mcp.py`)](#ai-integration-protocol-mcpy)
  - [Core Business Rules](#core-business-rules)
  - [Data Models (`models.py`)](#data-models-modelspy)
- [Coding and Contributing Guidelines](#coding-and-contributing-guidelines)
  - [Development Setup](#development-setup)
  - [Running Tests](#running-tests)
  - [Code Quality & Formatting](#code-quality--formatting)
  - [General Coding Principles (from AGENT.md)](#general-coding-principles-from-agentmd)
  - [Python Specific Guidelines (from AGENT.md)](#python-specific-guidelines-from-agentmd)
  - [Commit and Pull Request Process](#commit-and-pull-request-process)
  - [Further Reading for Contributors](#further-reading-for-contributors)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## 2. Features

- **🚀 Async Playwright Integration**: Fast and reliable browser automation using modern async capabilities.
- **🔍 Smart Section Detection**: Automatically identifies visible sections (based on headers/IDs) for descriptive filenames and metadata.
- **🖼️ Multiple Formats**: PNG, JPG, and animated PNG (APNG) output.
- **🌐 Browser Support**: Works with Chrome, Edge, and Safari (Safari on macOS only).
- **🔌 Remote Debugging**: Can connect to existing user browser sessions, preserving cookies, authentication, and extensions.
- **🤖 MCP Server**: Integrates with AI tools (like Claude) via the Model Context Protocol (MCP), providing screenshots, text, and HTML. Configurable output for AI needs.
- **📄 HTML Extraction**: Optionally captures the minified HTML content of visible elements for each screenshot.
- **📝 Text Extraction**: Automatically converts visible content to Markdown text, with optional trimming.
- **📐 Flexible Scrolling & Viewport**: Configurable scroll steps, starting CSS selectors, viewport size, and zoom level.
- **🎯 Precise Control**: Fine-tune output image scaling.
- **🔄 Robust Error Handling**: Includes retry logic and timeout management for more stable captures.
- **📦 Dual API**: Offers both synchronous and asynchronous Python APIs for versatile integration.
- **💻 Cross-Platform**: Works on macOS, Windows, and Linux.

## 3. How It Works (Conceptual Overview)

Brosh streamlines the process of capturing web content through several key steps:

1.  **Initialization (`__init__.py`, `cli.py`, `api.py`):**
    *   The user invokes Brosh via the CLI or its Python API.
    *   Parameters are parsed and a `CaptureConfig` object is created (defined in `models.py`).
2.  **Browser Management (`browser.py`, `tool.py`):**
    *   `BrowserManager` determines the target browser (Chrome, Edge, Safari) based on user input or auto-detection.
    *   It connects to an existing browser instance running in debug mode or launches a new one. Playwright is used for browser automation.
    *   A browser `page` object is configured with the specified viewport dimensions and zoom.
3.  **Navigation & Content Loading (`capture.py`, `tool.py`):**
    *   The Playwright `page` navigates to the target URL.
    *   Brosh waits for the DOM content to load and allows a brief period for dynamic content to render.
    *   If a `from_selector` is provided, the page scrolls to that element.
4.  **Screenshot Capture & Scrolling (`capture.py`):**
    *   `CaptureManager` calculates scroll positions based on viewport height and `scroll_step`.
    *   It iteratively scrolls the page. After each scroll:
        *   It waits for content to settle.
        *   A screenshot of the current viewport is taken.
        *   `DOMProcessor` (from `texthtml.py`) is invoked to extract:
            *   The most relevant CSS `active_selector` for the visible content.
            *   The `visible_text` (converted to Markdown).
            *   Optionally, the `visible_html` (minified).
        *   This data is stored as a `CaptureFrame` object.
5.  **Image Processing (`image.py`, `tool.py`):**
    *   `ImageProcessor` takes the captured raw image bytes (PNGs from Playwright).
    *   **Scaling:** If `scale` is specified, images are downsampled.
    *   **Format Conversion:**
        *   For `PNG` (default): Images are optimized using `pyoxipng`.
        *   For `JPG`: Images are converted from PNG to JPG, handling transparency.
        *   For `APNG`: All captured frames are compiled into an animated PNG.
6.  **Output Generation (`tool.py`):**
    *   `BrowserScreenshotTool` orchestrates the saving of processed images to disk.
    *   Filenames are generated using domain, timestamp, scroll percentage, and a semantic section ID (derived from `active_selector` or headers).
    *   A dictionary mapping file paths to their metadata (selector, text, HTML) is returned.
7.  **MCP Server (`mcp.py`):**
    *   If run in MCP mode (`brosh mcp` or `brosh-mcp`), a `FastMCP` server starts.
    *   It exposes a `see_webpage` tool that AI agents can call.
    *   This tool uses the asynchronous `capture_webpage_async` API function.
    *   Results are formatted according to `MCPToolResult` model, potentially including base64-encoded images and/or text/HTML, optimized for AI consumption (e.g., default smaller image scale, text trimming).

This modular design allows for flexibility and robust error handling at each stage.

## 4. Installation

### 4.1. Using uv/uvx (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager.

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run brosh directly with uvx (no installation needed)
uvx brosh shot "https://example.com"

# Or install globally as a command-line tool
uv tool install brosh

# Install with all optional dependencies (for development, testing, docs)
uv tool install "brosh[all]"
```

### 4.2. Using pip

```bash
# Basic installation
python -m pip install brosh

# With all optional dependencies
python -m pip install "brosh[all]"
```

### 4.3. Using pipx

[pipx](https://pipx.pypa.io/) installs Python applications in isolated environments.

```bash
# Install pipx (if not already installed)
python -m pip install --user pipx
python -m pipx ensurepath

# Install brosh
pipx install brosh
```

### 4.4. From Source

For development or to get the latest changes:

```bash
git clone https://github.com/twardoch/brosh.git
cd brosh
python -m pip install -e ".[all]" # Editable install with all extras
```

### 4.5. Install Playwright Browsers

After installing the `brosh` package, you need to install the browser drivers required by Playwright:

```bash
playwright install
# To install specific browsers, e.g., only Chromium:
# playwright install chromium
```
This command downloads the browser binaries (Chromium, Firefox, WebKit) that Playwright will use. Brosh primarily targets Chrome, Edge (Chromium-based), and Safari (WebKit-based).

## 5. Quick Start

```bash
# Capture a single webpage (e.g., example.com)
brosh shot "https://example.com"

# Capture a local HTML file
brosh shot "file:///path/to/your/local/file.html"

# For potentially better performance with multiple captures,
# start the browser in debug mode first (recommended for Chrome/Edge)
brosh --app chrome run
# Then, in the same or different terminal:
brosh --app chrome shot "https://example.com"
# When finished:
brosh --app chrome quit

# Create an animated PNG showing the scroll
brosh shot "https://example.com" --output_format apng

# Capture with a custom viewport size (e.g., common desktop)
brosh --width 1920 --height 1080 shot "https://example.com"

# Extract HTML content along with screenshots and output as JSON
brosh shot "https://example.com" --fetch_html --json > page_content.json
```

## 6. Usage

### 6.1. Command Line Interface (CLI)

Brosh uses a `fire`-based CLI. Global options are set before the command.

**Pattern:** `brosh [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]`

**Example:**
`brosh --width 1280 --height 720 shot "https://example.com" --scroll_step 80`

See [Command Reference](#command-reference) for all options.

### 6.2. Python API

Brosh offers both synchronous and asynchronous APIs.

```python
import asyncio
from brosh import (
    capture_webpage,
    capture_webpage_async,
    capture_full_page,
    capture_visible_area,
    capture_animation
)
from brosh.models import ImageFormat # For specifying image formats

# --- Synchronous API ---
# Best for simple scripts or CLI usage.
# It internally manages an asyncio event loop if needed.
def capture_sync_example():
    print("Running synchronous capture...")
    result = capture_webpage(
        url="https://example.com",
        width=1280,
        height=720,
        scroll_step=100,
        output_format=ImageFormat.JPG, # Use the enum
        scale=75, # Scale images to 75%
        fetch_text=True
    )

    print(f"Captured {len(result)} screenshots synchronously.")
    for path, metadata in result.items():
        print(f"  - Saved to: {path}")
        if metadata.get("text"):
            print(f"    Text preview: {metadata['text'][:80]}...")
    return result

# --- Asynchronous API ---
# Ideal for integration into async applications (e.g., web servers, MCP).
async def capture_async_example():
    print("\nRunning asynchronous capture...")
    result = await capture_webpage_async(
        url="https://docs.python.org/3/",
        fetch_html=True, # Get HTML content
        max_frames=3,    # Limit to 3 frames
        from_selector="#getting-started", # Start capturing from this element
        output_format=ImageFormat.PNG
    )

    print(f"Captured {len(result)} screenshots asynchronously.")
    for path, metadata in result.items():
        print(f"  - Saved to: {path}")
        print(f"    Selector: {metadata.get('selector', 'N/A')}")
        if metadata.get("html"):
            print(f"    HTML preview: {metadata['html'][:100]}...")
    return result

# --- Convenience Functions (use sync API by default) ---
def convenience_functions_example():
    print("\nRunning convenience functions...")
    # Capture entire page in one go (sets height=-1, max_frames=1)
    # Note: This may not work well for infinitely scrolling pages.
    full_page_result = capture_full_page(
        "https://www.python.org/psf/",
        output_format=ImageFormat.PNG,
        scale=50
    )
    print(f"Full page capture result: {list(full_page_result.keys())}")

    # Capture only the initial visible viewport (sets max_frames=1)
    visible_area_result = capture_visible_area(
        "https://www.djangoproject.com/",
        width=800, height=600
    )
    print(f"Visible area capture result: {list(visible_area_result.keys())}")

    # Create an animated PNG of the scrolling process
    animation_result = capture_animation(
        "https://playwright.dev/",
        anim_spf=0.8, # 0.8 seconds per frame
        max_frames=5  # Limit animation to 5 frames
    )
    print(f"Animation capture result: {list(animation_result.keys())}")

# --- Running the examples ---
if __name__ == "__main__":
    sync_results = capture_sync_example()

    # To run the async example:
    # asyncio.run(capture_async_example())
    # Note: If capture_sync_example() was called, it might have closed
    # the default event loop on some systems/Python versions if it created one.
    # For robust mixed sync/async, manage loops carefully or run separately.
    # For this example, we'll re-get/set a loop for the async part if needed.
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    async_results = loop.run_until_complete(capture_async_example())

    convenience_functions_example()

    print("\nAll examples complete.")
```

### 6.3. MCP Server Mode

Brosh can run as an MCP (Model Context Protocol) server, allowing AI tools like Claude to request web captures.

```bash
# Start the MCP server using the dedicated command:
brosh-mcp

# Or, using the main brosh command:
brosh mcp
```

This will start a server that listens for requests from MCP clients.

**Configuring with Claude Desktop:**

1.  Locate your Claude Desktop configuration file:
    *   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
    *   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
    *   **Linux:** `~/.config/Claude/claude_desktop_config.json`

2.  Add or modify the `mcpServers` section. Using `uvx` is recommended if `uv` is installed:

    ```json
    {
      "mcpServers": {
        "brosh": {
          "command": "uvx",
          "args": ["brosh-mcp"],
          "env": {
            "FASTMCP_LOG_LEVEL": "INFO" // Optional: control logging
          }
        }
      }
    }
    ```

3.  **Alternative if `uvx` is not used or preferred:**
    You can use the direct path to `brosh-mcp` or invoke it via `python -m brosh mcp`.
    To find the path to `brosh-mcp`:
    ```bash
    which brosh-mcp  # Unix-like systems
    # or
    python -c "import shutil; print(shutil.which('brosh-mcp'))"
    ```
    Then update `claude_desktop_config.json`:
    ```json
    {
      "mcpServers": {
        "brosh": {
          "command": "/full/path/to/your/python/bin/brosh-mcp", // Replace with actual path
          "args": []
        }
      }
    }
    ```
    Or using `python -m`:
    ```json
    {
      "mcpServers": {
        "brosh": {
          "command": "python", // or /path/to/specific/python
          "args": ["-m", "brosh", "mcp"]
        }
      }
    }
    ```

After configuration, (re)start Claude Desktop. You can then ask Claude to use Brosh, e.g., "Using the brosh tool, capture a screenshot of example.com and show me the text."

**MCP Tool Parameters:**
The `see_webpage` tool exposed via MCP accepts parameters similar to `capture_webpage_async`, including `url`, `zoom`, `width`, `height`, `scroll_step`, `scale` (defaults to 50 for MCP), `fetch_html`, `fetch_text`, `fetch_image`, `fetch_image_path`, etc.

## 7. Command Reference

### 7.1. Global Options

These options are specified *before* the command (e.g., `brosh --width 800 shot ...`).

| Option         | Type    | Default         | Description                                                                 |
| -------------- | ------- | --------------- | --------------------------------------------------------------------------- |
| `--app`        | str     | (auto-detect)   | Browser: `chrome`, `edge`, `safari`. Auto-detects installed browser if empty. |
| `--width`      | int     | (screen width)  | Viewport width in pixels. `0` for default screen width.                     |
| `--height`     | int     | (screen height) | Viewport height in pixels. `0` for default screen height, `-1` for full page. |
| `--zoom`       | int     | 100             | Browser zoom level in % (range: 10-500).                                    |
| `--output_dir` | str     | (user pictures) | Directory to save screenshots (defaults to `~/Pictures/brosh`).             |
| `--subdirs`    | bool    | `False`         | Create domain-based subdirectories within `output_dir`.                     |
| `--verbose`    | bool    | `False`         | Enable verbose debug logging.                                               |
| `--json`       | bool    | `False`         | Output results from `shot` command as JSON to stdout (CLI only).            |

### 7.2. Commands

#### 7.2.1. `run`

Starts the specified browser in remote debug mode. This can improve performance for multiple `shot` commands as the browser doesn't need to be re-initialized each time.

**Usage:** `brosh [GLOBAL_OPTIONS] run [--force_run]`

**Options:**

| Option       | Type | Default | Description                                       |
| ------------ | ---- | ------- | ------------------------------------------------- |
| `--force_run` | bool | `False` | Force restart browser even if one seems active. |

#### 7.2.2. `quit`

Quits the browser previously started with `run`.

**Usage:** `brosh [GLOBAL_OPTIONS] quit`

#### 7.2.3. `shot`

Captures screenshots of the given URL.

**Usage:** `brosh [GLOBAL_OPTIONS] shot URL [SHOT_OPTIONS]`

**Required Argument:**

*   `URL` (str): The URL of the webpage to capture. Can be `http://`, `https://`, or `file:///`.

**Shot Options:**

| Option             | Type    | Default     | Description                                                                      |
| ------------------ | ------- | ----------- | -------------------------------------------------------------------------------- |
| `--scroll_step`    | int     | 100         | Scroll step as % of viewport height (range: 10-200).                             |
| `--scale`          | int     | 100         | Scale output images by % (range: 10-200). `50` means 50% of original size.        |
| `--output_format`  | str     | `png`       | Output format: `png`, `jpg`, `apng`.                                             |
| `--anim_spf`       | float   | 0.5         | Seconds per frame for APNG animations (range: 0.1-10.0).                           |
| `--fetch_html`     | bool    | `False`     | Include minified HTML of visible elements in the output metadata.                |
| `--fetch_image`    | bool    | `False`     | (MCP context) Include base64 image data in MCP output.                           |
| `--fetch_image_path`| bool   | `True`      | (MCP context) Include image file path in MCP output.                             |
| `--fetch_text`     | bool    | `True`      | Include extracted Markdown text from visible elements in output metadata.        |
| `--trim_text`      | bool    | `True`      | Trim extracted text to ~200 characters in output metadata.                       |
| `--max_frames`     | int     | 0           | Maximum number of frames/screenshots to capture. `0` for unlimited (full scroll). |
| `--from_selector`  | str     | `""`        | CSS selector of an element to scroll to before starting capture.                 |

#### 7.2.4. `mcp`

Runs Brosh as an MCP (Model Context Protocol) server.

**Usage:** `brosh [GLOBAL_OPTIONS] mcp`

This command is also available as a dedicated script `brosh-mcp`.

## 8. Output

### 8.1. File Naming Convention

Screenshots are saved with a descriptive filename pattern:

`{domain}-{timestamp}-{scroll_percentage}-{section_id}.{format}`

**Example:** `github_com-230715-103000-00500-readme_md.png`

*   `github_com`: Domain name (underscores replace dots).
*   `230715-103000`: Timestamp (YYMMDD-HHMMSS, UTC).
*   `00500`: Scroll position as percentage of total page height, times 100 (e.g., 00500 means 50.00%). Padded to 5 digits.
*   `readme_md`: A semantic identifier for the currently visible section, often derived from the most prominent header or element ID in view.
*   `.png`: File extension based on the chosen `output_format`.

### 8.2. Output Formats

*   **`png` (default):** Lossless compression, excellent quality. Optimized with `pyoxipng`.
*   **`jpg`:** Lossy compression, smaller file sizes. Good for photographic content or when space is critical.
*   **`apng`:** Animated Portable Network Graphics. Creates an animation from all captured frames, showing the scrolling sequence.

### 8.3. JSON Output Details

When using the `--json` flag with the `shot` command (or when using the Python API), Brosh returns a dictionary. The keys are the absolute file paths of the saved screenshots, and the values are dictionaries containing metadata for each screenshot.

**Structure:**

```json
{
  "/path/to/output/domain-ts-scroll-section.png": {
    "selector": "css_selector_for_main_content_block",
    "text": "Extracted Markdown text from the visible part of the page...",
    "html": "<!DOCTYPE html><html>...</html>" // Only if --fetch_html is true
  },
  // ... more entries for other screenshots
}
```

**Metadata Fields:**

*   `selector` (str): A CSS selector identifying the most relevant content block visible in that frame (e.g., `main`, `article#content`, `div.product-details`). Defaults to `body` if no more specific selector is found.
*   `text` (str): Markdown representation of the text content visible in the frame. Extracted using `html2text`. Included if `fetch_text` is true (default). Can be trimmed if `trim_text` is true (default).
*   `html` (str, optional): Minified HTML of the elements fully visible in the frame. Included only if `fetch_html` is true.

For `apng` format, the JSON output will typically contain a single entry for the animation file, with metadata like `{"selector": "animated", "text": "Animation with N frames", "frames": N}`.

## 9. Technical Architecture Deep Dive

Brosh is built as a modular Python package. Understanding its architecture can help with advanced usage, customization, and contributions.

### 9.1. Core Modules and Flow

The primary logic flows through these key modules in `src/brosh/`:

1.  **`__main__.py` & `cli.py`**:
    *   `__main__.py` is the entry point for the `brosh` CLI command.
    *   `cli.py` defines `BrowserScreenshotCLI` using `python-fire`. It parses CLI arguments, initializes common settings, and maps commands (`run`, `quit`, `shot`, `mcp`) to their respective methods. These methods often delegate to `api.py`.

2.  **`api.py`**:
    *   This is the public interface for Brosh's functionality. It provides `capture_webpage` (synchronous wrapper) and `capture_webpage_async` (core asynchronous logic).
    *   It takes all capture parameters, validates them by creating a `CaptureConfig` object (from `models.py`), and then instantiates and uses `BrowserScreenshotTool`.
    *   Convenience functions like `capture_full_page` are also defined here.

3.  **`tool.py`**:
    *   Contains `BrowserScreenshotTool`, the main orchestrator.
    *   Its `capture` method (async) manages the entire screenshot process:
        *   Sets up output directories.
        *   Determines screen dimensions if not specified.
        *   Initializes Playwright.
        *   Uses `BrowserManager` to get a browser `page`.
        *   Uses `CaptureManager` to get `CaptureFrame` objects.
        *   Processes these frames (scaling, format conversion via `ImageProcessor`, saving files).
        *   Cleans up browser resources.

4.  **`browser.py`**:
    *   `BrowserManager` handles browser interactions:
        *   Detecting available browsers (Chrome, Edge, Safari) and their paths.
        *   Getting screen dimensions (OS-specific logic, Retina display handling on macOS).
        *   Launching browsers in debug mode or connecting to existing ones using Playwright's `connect_over_cdp` (for Chromium-based browsers) or `launch`.
        *   Managing debug ports (default: Chrome 9222, Edge 9223, Safari 9225).

5.  **`capture.py`**:
    *   `CaptureManager` is responsible for the actual screenshotting logic on a given Playwright `page`:
        *   Navigating to the URL.
        *   Handling `from_selector` to scroll to a starting point.
        *   Calculating scroll positions based on `scroll_step` and viewport height.
        *   Looping through scroll positions:
            *   Scrolling the page (`page.evaluate("window.scrollTo(...)")`).
            *   Waiting for dynamic content to settle.
            *   Taking a screenshot of the current viewport (`page.screenshot()`).
            *   Using `DOMProcessor` to get visible HTML, text, and active selector.
            *   Storing this as a `CaptureFrame` dataclass instance.

6.  **`texthtml.py`**:
    *   `DOMProcessor` extracts content from the browser's DOM:
        *   `extract_visible_content()`: Executes JavaScript in the page to get fully visible elements' HTML, then converts it to Markdown text using `html2text`. Also determines an `active_selector`.
        *   `get_section_id()`: Executes JavaScript to find a semantic ID for the current view (e.g., from a nearby header).
        *   `compress_html()`: Minifies HTML by removing comments, excessive whitespace, large data URIs, etc.

7.  **`image.py`**:
    *   `ImageProcessor` performs image manipulations in memory using Pillow and `pyoxipng`:
        *   `optimize_png_bytes()`: Optimizes PNGs.
        *   `downsample_png_bytes()`: Resizes images.
        *   `convert_png_to_jpg_bytes()`: Converts PNG to JPG, handling transparency.
        *   `create_apng_bytes()`: Assembles multiple PNG frames into an animated PNG.

8.  **`models.py`**:
    *   Defines Pydantic models and Enums:
        *   `ImageFormat` (Enum: PNG, JPG, APNG) with properties for MIME type and extension.
        *   `CaptureConfig` (Dataclass): Holds all settings for a capture job, including validation logic.
        *   `CaptureFrame` (Dataclass): Represents a single captured frame's data (image bytes, scroll position, text, HTML, etc.).
        *   `MCPTextContent`, `MCPImageContent`, `MCPToolResult` (Pydantic Models): Define the structure for data exchange in MCP mode.

9.  **`mcp.py`**:
    *   Implements the MCP server using `FastMCP`.
    *   Defines an async tool function `see_webpage` that mirrors `api.capture_webpage_async`'s signature.
    *   This function calls Brosh's core capture logic.
    *   It then formats the results into `MCPToolResult` (defined in `models.py`), handling `fetch_image`, `fetch_image_path`, `fetch_text`, `fetch_html` flags to tailor the output for AI agents.
    *   Includes logic to apply size limits to MCP responses.
    *   The `brosh-mcp` script entry point is also here.

### 9.2. Key Architectural Components (Business Domains)

As outlined in `CLAUDE.md`, Brosh's functionality can be grouped into three core domains:

#### 9.2.1. Content Capture Engine (`capture.py`, `texthtml.py`)

*   **Semantic Section Detection:**
    *   `DOMProcessor.get_section_id()` analyzes the DOM for prominent headers (`<h1>`-`<h6>`) or elements with IDs near the top of the viewport. This generates a human-readable identifier used in filenames (e.g., `introduction`, `installation-steps`).
    *   `DOMProcessor.extract_visible_content()` identifies the most encompassing, fully visible elements to determine the `active_selector` and extract their HTML and text. This helps in associating screenshots with specific content blocks.
*   **Viewport Management & Scrolling:**
    *   `CaptureManager` progressively scrolls the page. The `scroll_step` (percentage of viewport height) allows for overlapping captures if less than 100%, ensuring no content is missed.
    *   It dynamically determines total page height (`document.documentElement.scrollHeight`).
    *   Waits after scrolls (`SCROLL_AND_CONTENT_WAIT_SECONDS`) allow for dynamically loading or expanding content to render before capture.

#### 9.2.2. Browser Integration Layer (`browser.py`)

*   **Platform-Specific Browser Management:**
    *   `BrowserManager.get_browser_name()` uses a priority system (Chrome > Edge > Safari on macOS) for auto-detection.
    *   `BrowserManager.is_browser_available()` and `get_browser_paths()` check for browser installations in common locations across OSes.
    *   Firefox is explicitly unsupported. Safari is restricted to macOS.
*   **Resolution Detection & Debug Mode:**
    *   `BrowserManager.get_screen_dimensions()` attempts to get logical screen resolution, accounting for Retina displays on macOS (by checking physical resolution from `system_profiler`). Falls back to defaults if detection fails.
    *   Orchestrates launching browsers with remote debugging enabled (`--remote-debugging-port`) on specific ports (Chrome: 9222, Edge: 9223). This allows connection to the user's actual browser profile. WebKit (Safari) uses a different launch mechanism.

#### 9.2.3. AI Integration Protocol (`mcp.py`)

*   **MCP Tool Integration:**
    *   The `see_webpage` function acts as the tool interface for AI systems (like Claude) via `FastMCP`.
    *   It handles requests, invokes Brosh's core capture logic, and formats the output.
*   **Visual & Textual Context Extraction:**
    *   The MCP tool can return:
        *   Base64-encoded image data (`fetch_image=True`).
        *   File paths to saved images (`fetch_image_path=True`).
        *   Extracted Markdown text (`fetch_text=True`).
        *   Minified HTML (`fetch_html=True`).
    *   This provides rich, multi-modal context to language models. Default MCP scale is 50% to keep image sizes manageable. Text can be trimmed.
*   **HTML/Selector Mapping:**
    *   The `selector` field in metadata links screenshots and extracted text/HTML to a specific part of the DOM structure.

### 9.3. Core Business Rules

1.  **Screenshot Organization:**
    *   Files are stored in a structured way, optionally in domain-based subdirectories (`--subdirs`).
    *   Filenames include domain, timestamp, scroll percentage, and a semantic section ID, promoting findability.
    *   Overlap in captures is controlled by `scroll_step` (10-200% of viewport height).
2.  **Browser Constraints:**
    *   Safari usage is limited to macOS.
    *   Firefox is not supported.
    *   Specific debug ports are assigned per browser type.
3.  **Content Processing:**
    *   `scroll_step` calculation is based on viewport percentage.
    *   Section-aware naming for files.
    *   Waits are implemented to handle dynamic content loading.
    *   Text is automatically extracted as Markdown; HTML extraction is optional.

### 9.4. Data Models (`models.py`)

The use of Pydantic models and dataclasses ensures type safety, validation, and clear data structures throughout the application. `CaptureConfig` centralizes all job parameters, `CaptureFrame` standardizes per-frame data, and MCP models ensure compliant communication with AI tools.

## 10. Coding and Contributing Guidelines

We welcome contributions to Brosh! Please follow these guidelines to ensure a smooth process.

### 10.1. Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/twardoch/brosh.git
    cd brosh
    ```
2.  **Install in editable mode with all dependencies:**
    We recommend using `uv` for faster environment setup:
    ```bash
    uv venv  # Create a virtual environment
    source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
    uv pip install -e ".[all]"
    ```
    Alternatively, using `pip`:
    ```bash
    python -m venv .venv
    source .venv/bin/activate # Or .venv\Scripts\activate on Windows
    python -m pip install -e ".[all]"
    ```
3.  **Install pre-commit hooks:**
    This will automatically run linters and formatters before each commit.
    ```bash
    pre-commit install
    ```

### 10.2. Running Tests

Brosh uses `pytest` for testing.

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src/brosh --cov-report=term-missing

# Run tests in parallel (if you have pytest-xdist, included in [all])
pytest -n auto

# Run specific test file or test function
pytest tests/test_api.py
pytest tests/test_cli.py::TestBrowserScreenshotCLI::test_shot_basic
```
Ensure your changes pass all tests and maintain or increase test coverage. Test configuration is in `pyproject.toml` under `[tool.pytest.ini_options]`.

### 10.3. Code Quality & Formatting

This project uses `Ruff` for linting and formatting, and `mypy` for type checking. Pre-commit hooks should handle most of this automatically.

*   **Formatting:** `ruff format src tests`
*   **Linting & Auto-fixing:** `ruff check --fix --unsafe-fixes src tests`
*   **Type Checking:** `mypy src`

Configuration for these tools is in `pyproject.toml`.

### 10.4. General Coding Principles (from AGENT.md)

Adhere to these principles when developing:

*   **Iterate Gradually:** Make small, incremental changes.
*   **Preserve Existing Code:** Don't refactor unnecessarily unless it's part of the task.
*   **Constants over Magic Numbers:** Define and use named constants.
*   **Check for Existing Solutions:** Leverage existing code within Brosh before writing anew.
*   **Minimal Viable Increments:** Focus on shipping working, small improvements.
*   **Clear Documentation:** Write explanatory docstrings and comments (what, why, how it's used elsewhere).
*   **Graceful Failure Handling:** Implement retries, fallbacks, and clear user guidance for errors.
*   **Edge Cases & Validation:** Address edge cases and validate inputs/assumptions.
*   **Modularity:** Break down complex logic into concise, single-purpose functions.
*   **Flat Structures:** Prefer flat over deeply nested code.
*   **Holistic Overview:** Keep project documents (`README.md`, `CHANGELOG.md`, `TODO.md`) in mind.

### 10.5. Python Specific Guidelines (from AGENT.md)

*   **PEP 8:** Follow standard Python formatting and naming conventions (largely enforced by Ruff).
*   **PEP 20 (Zen of Python):** Keep code simple, explicit, and readable.
*   **Type Hints:** Use type hints for all functions and methods (e.g., `list`, `dict`, `|` for unions).
*   **PEP 257 (Docstrings):** Write clear, imperative docstrings for modules, classes, functions, and methods.
*   **F-strings:** Use f-strings for string formatting.
*   **Logging:** Utilize `loguru` for logging. Add `verbose` mode logging and `debug-log` where appropriate.
*   **CLI Scripts:** (Brosh uses `python-fire`) Standard shebangs and `this_file` comments are good practice.
*   **Post-Change Command Sequence (as per `AGENT.md`):**
    While `pre-commit` handles much of this, be aware of the typical full check sequence:
    ```bash
    # This is a conceptual guide; pre-commit and hatch scripts automate parts of this.
    # uzpy run . # (If used, uzpy seems to be a project-specific runner)
    fd -e py -x autoflake --remove-all-unused-imports -ir . # Remove unused imports
    fd -e py -x pyupgrade --py310-plus . # Upgrade syntax
    fd -e py -x ruff check --fix --unsafe-fixes . # Ruff lint and fix
    fd -e py -x ruff format . # Ruff format
    python -m pytest # Run tests
    ```
    (Note: `fd` is a command-line tool. If not installed, adapt Ruff/Autoflake commands to scan `src` and `tests`.)
    Hatch environments (`hatch run lint:all`, `hatch run test:test-cov`) simplify running these checks.

### 10.6. Commit and Pull Request Process

1.  **Branching:** Create a new branch for your feature or bugfix (e.g., `feature/new-output-option` or `fix/timeout-issue`).
2.  **Commits:** Make small, logical commits. Write clear commit messages (e.g., "Feat: Add WebP output format", "Fix: Correct handling of empty URLs").
3.  **Pre-commit Hooks:** Ensure pre-commit hooks pass before pushing.
4.  **Push:** Push your branch to your fork.
5.  **Pull Request:** Open a Pull Request against the `main` branch of `twardoch/brosh`.
    *   Provide a clear description of the changes.
    *   Reference any relevant issues.
    *   Ensure CI checks (GitHub Actions) pass.

### 10.7. Further Reading for Contributors

*   **`AGENT.md`:** Contains detailed working principles, Python guidelines, and tool usage instructions relevant to AI-assisted development for this project.
*   **`CLAUDE.md`:** Provides an overview of Brosh's architecture, commands, and development notes, particularly useful for understanding the system's design.
*   **`pyproject.toml`:** Defines dependencies, build system, and tool configurations (Ruff, Mypy, Pytest, Hatch).

## 11. Troubleshooting

*(This section is largely the same as the original README, as it was already comprehensive. Minor updates for consistency.)*

### 11.1. Common Issues

#### 11.1.1. Browser Not Found
**Error:** "Could not find chrome installation" or similar.
**Solution:**
*   Ensure Chrome, Edge, or Safari is installed in its default location.
*   Specify the browser explicitly: `brosh --app edge shot "https://example.com"`
*   Run `playwright install` to ensure Playwright's browser binaries are correctly installed.

#### 11.1.2. Connection Timeout / Browser Launch Issues
**Error:** "Failed to connect to browser", "TimeoutError", or browser doesn't launch as expected.
**Solution:**
*   Try starting the browser in debug mode first: `brosh --app chrome run`. Then, in another terminal, run your `shot` command.
*   Ensure no other instances of the same browser are using the required debug port (e.g., Chrome: 9222). The `--force_run` option with `run` can help.
*   Check for conflicting browser extensions or profiles if connecting to an existing browser.
*   On Linux, you might need to install additional dependencies: `sudo apt-get install -y libgbm-dev libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdbus-1-3 libdrm2 libexpat1 libgbm1 libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxtst6`.

#### 11.1.3. Screenshot Timeout
**Error:** "Screenshot timeout for position X" or page content doesn't load.
**Solution:**
*   The default page load and screenshot timeouts might be too short for complex pages. (Currently, these are not directly CLI-configurable, but this could be a future enhancement).
*   Try a simpler format if timeouts occur during processing: `brosh shot "..." --output_format jpg`.
*   Network issues or very slow-loading pages can cause timeouts.

#### 11.1.4. Permission Denied
**Error:** "Permission denied" when saving screenshots.
**Solution:**
*   Check permissions for the `output_dir`.
*   Specify a different output directory where you have write access: `brosh --output_dir /tmp/screenshots shot "..."`

### 11.2. Debug Mode

Enable verbose logging for detailed troubleshooting:
`brosh --verbose shot "https://example.com"`
This will print debug messages from `loguru` to stderr.

### 11.3. Platform-Specific Notes

#### 11.3.1. macOS
*   **Safari:** Requires enabling "Allow Remote Automation" in Safari's Develop menu (Develop > Allow Remote Automation).
*   **Retina Displays:** Brosh attempts to detect and handle logical pixel resolutions correctly.

#### 11.3.2. Windows
*   Ensure browsers are installed in their standard locations (e.g., Program Files).
*   If using `uvx` or `pipx` in environments like Git Bash or WSL, ensure paths are correctly resolved.

#### 11.3.3. Linux
*   Headless environments (servers without a display) might require Xvfb or similar virtual frame buffers, though Playwright often handles this.
*   Ensure all necessary browser dependencies are installed (see "Connection Timeout" above).

## 12. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

*   Created by [Adam Twardoch](https://github.com/twardoch)
*   Developed with assistance from AI tools by [Anthropic](https://www.anthropic.com/claude).
*   Uses [Playwright](https://playwright.dev/) for reliable browser automation.
*   Uses [python-fire](https://github.com/google/python-fire) for the CLI interface.
*   Implements [FastMCP](https://github.com/jlowin/fastmcp) for Model Context Protocol support.
*   Relies on many other excellent open-source Python packages - see `pyproject.toml`.
