---
title: Home
nav_order: 1
---

# brosh

Full-page browser screenshots, from the command line or from your own code, with the pixels, the text, and the HTML all handed back together.

Brosh drives a real browser (Chrome, Edge, or Safari) via Playwright, scrolls through a page, and captures each section as an image — plus the visible text as Markdown and, if you want it, the underlying HTML. Built for AI agents that need to *see* a page, not just fetch its source.

## Who it's for

- **Developers & QA testers** — visual regression testing, bug reports, documenting app state.
- **AI engineers** — feeding visual and textual page context to models, especially via the MCP server.
- **Content creators & archivists** — capturing and preserving web content, generating documentation assets.

## Features

- Async Playwright integration — fast, modern browser automation.
- Smart section detection — filenames and metadata derived from visible headers/IDs.
- Multiple output formats — PNG, JPG, animated PNG (APNG).
- Chrome, Edge, and Safari support (Safari on macOS only).
- Remote debugging — connect to an existing browser session, keeping cookies, logins, and extensions.
- MCP server for AI tools like Claude, returning images, text, and HTML.
- Optional HTML extraction (minified) alongside every screenshot.
- Automatic Markdown text extraction, with optional trimming.
- Configurable scroll steps, starting selector, viewport size, and zoom.
- Sync and async Python APIs.
- Cross-platform: macOS, Windows, Linux.

## Quick start

```bash
pip install brosh
playwright install
brosh shot "https://example.com"
```

The `playwright install` step downloads the browser binaries Playwright drives — skip it and every capture fails with a browser-not-found error.

From here:

- [Installation](installation) — all install methods, including binaries and pipx.
- [Usage](usage) — CLI patterns, Python API, MCP server mode.
- [CLI Reference](cli-reference) — every command and option.
- [Python API](python-api) — sync/async functions and convenience wrappers.
- [MCP Server](mcp-server) — wiring brosh into Claude and other AI tools.
- [Architecture](architecture) — how a capture flows through the codebase.
- [Output](output) — file naming, formats, and JSON structure.

## License

MIT. Created by [Adam Twardoch](https://github.com/twardoch), built on [Playwright](https://playwright.dev/), [python-fire](https://github.com/google/python-fire), and [FastMCP](https://github.com/jlowin/fastmcp).
