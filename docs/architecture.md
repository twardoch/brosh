---
title: Architecture
nav_order: 7
---

# Architecture

Brosh is a modular Python package under `src/brosh/`. Understanding its shape helps with advanced usage, customization, and contributions.

## How a capture flows

1. **`__main__.py` / `cli.py`** — `__main__.py` is the CLI entry point. `cli.py` defines `BrowserScreenshotCLI` (built with `python-fire`), which parses arguments and maps commands (`run`, `quit`, `shot`, `mcp`) to methods, mostly delegating to `api.py`.
2. **`api.py`** — the public interface. `capture_webpage` (sync wrapper) and `capture_webpage_async` (core async logic) validate parameters into a `CaptureConfig` (from `models.py`) and drive `BrowserScreenshotTool`. Convenience functions like `capture_full_page` live here too.
3. **`tool.py`** — `BrowserScreenshotTool` orchestrates the whole job: sets up output directories, determines screen dimensions, initializes Playwright, gets a page via `BrowserManager`, gets frames via `CaptureManager`, processes them (scaling, format conversion, saving), and cleans up.
4. **`browser.py`** — `BrowserManager` detects available browsers (Chrome, Edge, Safari) and their paths, gets screen dimensions (with Retina handling on macOS), and launches or connects to a browser in debug mode via Playwright's `connect_over_cdp` (Chromium) or `launch` (WebKit). Debug ports default to Chrome 9222, Edge 9223, Safari 9225.
5. **`capture.py`** — `CaptureManager` navigates to the URL, handles `from_selector`, calculates scroll positions from `scroll_step` and viewport height, and loops: scroll, wait for content to settle, screenshot, invoke `DOMProcessor` for HTML/text/selector, and store as a `CaptureFrame`.
6. **`texthtml.py`** — `DOMProcessor` extracts DOM content: `extract_visible_content()` gets fully visible elements' HTML and converts to Markdown via `html2text`, determining an `active_selector`; `get_section_id()` finds a semantic ID (e.g. from a nearby header); `compress_html()` minifies HTML.
7. **`image.py`** — `ImageProcessor` handles image work in memory with Pillow and `pyoxipng`: PNG optimization, downsampling, PNG-to-JPG conversion (with transparency handling), and APNG assembly from multiple frames.
8. **`models.py`** — Pydantic models and enums: `ImageFormat` (PNG/JPG/APNG with MIME/extension helpers), `CaptureConfig` (job settings plus validation), `CaptureFrame` (one captured frame's data), and `MCPTextContent`/`MCPImageContent`/`MCPToolResult` for MCP data exchange.
9. **`mcp.py`** — the MCP server, built with `FastMCP`. Defines the async `see_webpage` tool, mirroring `capture_webpage_async`'s signature, and formats results into `MCPToolResult`, tailoring output via the `fetch_*` flags. Also hosts the `brosh-mcp` script entry point.

## Key components

### Content capture engine (`capture.py`, `texthtml.py`)

- **Semantic section detection** — `DOMProcessor.get_section_id()` looks for prominent headers or elements with IDs near the top of the viewport, producing human-readable identifiers for filenames (e.g. `introduction`, `installation-steps`). `extract_visible_content()` finds the most encompassing, fully visible elements to set `active_selector` and pull HTML/text.
- **Viewport management & scrolling** — `CaptureManager` scrolls progressively; `scroll_step` (percent of viewport height) can overlap captures when below 100% to avoid missing content. Total page height is read dynamically (`document.documentElement.scrollHeight`). Waits after each scroll let dynamic content settle before the screenshot.

### Browser integration layer (`browser.py`)

- **Platform-specific management** — browser priority is Chrome > Edge > Safari (macOS) for auto-detection; installations are checked in common per-OS locations. Firefox is explicitly unsupported; Safari is macOS-only.
- **Resolution detection & debug mode** — logical screen resolution is read with Retina handling on macOS (via `system_profiler`), falling back to defaults on failure. Browsers launch with remote debugging enabled on fixed ports so brosh can connect to the user's real profile; WebKit uses a different launch path.

### AI integration protocol (`mcp.py`)

- **MCP tool integration** — `see_webpage` is the tool interface for AI systems via `FastMCP`: it invokes brosh's core capture logic and formats the output.
- **Visual & textual context** — returns any combination of base64 image data, image file paths, Markdown text, and minified HTML, giving rich multi-modal context to the calling model. Default MCP scale is 50% to keep payloads small; text can be trimmed.
- **Selector mapping** — the `selector` field links a screenshot and its extracted text/HTML to a specific DOM location.

## Core business rules

1. **Screenshot organization** — files can go into domain-based subdirectories (`--subdirs`); filenames encode domain, timestamp, scroll percentage, and section ID for findability. `scroll_step` (10-200% of viewport height) controls capture overlap.
2. **Browser constraints** — Safari is macOS-only; Firefox isn't supported; each browser type gets a fixed debug port.
3. **Content processing** — scroll step is percentage-of-viewport based; filenames are section-aware; waits handle dynamic content; text is extracted as Markdown automatically, HTML extraction is opt-in.

## Data models (`models.py`)

Pydantic models and dataclasses give type safety and validation throughout. `CaptureConfig` centralizes job parameters, `CaptureFrame` standardizes per-frame data, and the MCP models ensure compliant communication with AI tools.
