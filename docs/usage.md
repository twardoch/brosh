---
title: Usage
nav_order: 3
---

# Usage

## Command line

Brosh uses a `fire`-based CLI: global options come before the command, command-specific options come after.

```
brosh [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

```bash
brosh --width 1280 --height 720 shot "https://example.com" --scroll_step 80
```

See the [CLI Reference](cli-reference) for every option.

## Python API

```python
import asyncio
from brosh import (
    capture_webpage,
    capture_webpage_async,
    capture_full_page,
    capture_visible_area,
    capture_animation,
)
from brosh.models import ImageFormat

# Synchronous — simple scripts, manages its own event loop if needed.
def capture_sync_example():
    result = capture_webpage(
        url="https://example.com",
        width=1280,
        height=720,
        scroll_step=100,
        output_format=ImageFormat.JPG,
        scale=75,
        fetch_text=True,
    )
    for path, metadata in result.items():
        print(path, metadata.get("text", "")[:80])
    return result

# Asynchronous — for async apps, web servers, MCP.
async def capture_async_example():
    result = await capture_webpage_async(
        url="https://docs.python.org/3/",
        fetch_html=True,
        max_frames=3,
        from_selector="#getting-started",
        output_format=ImageFormat.PNG,
    )
    for path, metadata in result.items():
        print(path, metadata.get("selector"))
    return result

# Convenience wrappers (sync by default)
def convenience_examples():
    capture_full_page("https://www.python.org/psf/", output_format=ImageFormat.PNG, scale=50)
    capture_visible_area("https://www.djangoproject.com/", width=800, height=600)
    capture_animation("https://playwright.dev/", anim_spf=0.8, max_frames=5)

if __name__ == "__main__":
    capture_sync_example()
    asyncio.run(capture_async_example())
    convenience_examples()
```

See [Python API](python-api) for the full function signatures.

## MCP server mode

```bash
brosh-mcp
# or
brosh mcp
```

See [MCP Server](mcp-server) for client configuration.
