---
title: Python API
nav_order: 5
---

# Python API

Brosh offers both synchronous and asynchronous APIs.

## Synchronous

Best for simple scripts or CLI-style usage. Manages its own asyncio event loop if needed.

```python
from brosh import capture_webpage
from brosh.models import ImageFormat

result = capture_webpage(
    url="https://example.com",
    width=1280,
    height=720,
    scroll_step=100,
    output_format=ImageFormat.JPG,
    scale=75,
    fetch_text=True,
)

print(f"Captured {len(result)} screenshots synchronously.")
for path, metadata in result.items():
    print(f"  - Saved to: {path}")
    if metadata.get("text"):
        print(f"    Text preview: {metadata['text'][:80]}...")
```

## Asynchronous

Ideal for integration into async applications (web servers, MCP).

```python
from brosh import capture_webpage_async
from brosh.models import ImageFormat

async def capture_async_example():
    result = await capture_webpage_async(
        url="https://docs.python.org/3/",
        fetch_html=True,
        max_frames=3,
        from_selector="#getting-started",
        output_format=ImageFormat.PNG,
    )
    for path, metadata in result.items():
        print(f"  - Saved to: {path}")
        print(f"    Selector: {metadata.get('selector', 'N/A')}")
        if metadata.get("html"):
            print(f"    HTML preview: {metadata['html'][:100]}...")
    return result
```

## Convenience functions

Use the synchronous API by default.

```python
from brosh import capture_full_page, capture_visible_area, capture_animation
from brosh.models import ImageFormat

# Entire page in one go (sets height=-1, max_frames=1).
# May not work well for infinitely scrolling pages.
capture_full_page("https://www.python.org/psf/", output_format=ImageFormat.PNG, scale=50)

# Only the initial visible viewport (sets max_frames=1).
capture_visible_area("https://www.djangoproject.com/", width=800, height=600)

# Animated PNG of the scrolling process.
capture_animation("https://playwright.dev/", anim_spf=0.8, max_frames=5)
```

## Return value

Both `capture_webpage` and `capture_webpage_async` return a dict keyed by the absolute file path of each saved screenshot. See [Output](output) for the metadata structure.
