---
title: MCP Server
nav_order: 6
---

# MCP Server Mode

Brosh can run as an MCP (Model Context Protocol) server, letting AI tools like Claude request web captures directly.

```bash
# dedicated command
brosh-mcp

# or via the main brosh command
brosh mcp
```

Either starts a server that listens for requests from MCP clients.

## Claude Code

```bash
claude mcp add brosh -- brosh-mcp
```

## Claude Desktop

Locate your config file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

Add or edit the `mcpServers` section. `uvx` is the easiest path if `uv` is installed:

```json
{
  "mcpServers": {
    "brosh": {
      "command": "uvx",
      "args": ["brosh-mcp"],
      "env": {
        "FASTMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Without `uvx`, point directly at the installed script:

```bash
which brosh-mcp
# or
python -c "import shutil; print(shutil.which('brosh-mcp'))"
```

```json
{
  "mcpServers": {
    "brosh": {
      "command": "/full/path/to/brosh-mcp",
      "args": []
    }
  }
}
```

Or invoke it via `python -m`:

```json
{
  "mcpServers": {
    "brosh": {
      "command": "python",
      "args": ["-m", "brosh", "mcp"]
    }
  }
}
```

Restart Claude Desktop after editing the config. Then ask it to, for example, "using the brosh tool, capture a screenshot of example.com and show me the text."

## Tool parameters

The exposed `see_webpage` tool takes parameters similar to `capture_webpage_async`: `url`, `zoom`, `width`, `height`, `scroll_step`, `scale` (defaults to 50 for MCP, to keep responses small), `fetch_html`, `fetch_text`, `fetch_image`, `fetch_image_path`, and more.

It can return, in any combination:

- Base64-encoded image data (`fetch_image=True`)
- File paths to saved images (`fetch_image_path=True`)
- Extracted Markdown text (`fetch_text=True`)
- Minified HTML (`fetch_html=True`)

Size limits are applied to MCP responses automatically to keep them manageable for the calling model.
