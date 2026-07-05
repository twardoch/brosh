---
title: Output
nav_order: 8
---

# Output

## File naming convention

Screenshots are saved with a descriptive filename pattern:

```
{domain}-{timestamp}-{scroll_percentage}-{section_id}.{format}
```

Example: `github_com-230715-103000-00500-readme_md.png`

- `github_com` — domain name, dots replaced with underscores.
- `230715-103000` — timestamp, `YYMMDD-HHMMSS` UTC.
- `00500` — scroll position as a percentage of total page height, times 100, padded to 5 digits (`00500` = 50.00%).
- `readme_md` — a semantic identifier for the visible section, usually derived from the most prominent header or element ID in view.
- `.png` — extension, based on the chosen `output_format`.

## Output formats

- **`png`** (default) — lossless, optimized with `pyoxipng`.
- **`jpg`** — lossy, smaller files. Good for photographic content or tight space budgets.
- **`apng`** — animated PNG assembled from every captured frame, showing the scroll sequence.

## JSON output details

With `--json` on the `shot` command (or via the Python API), brosh returns a dict keyed by absolute file path, valued by metadata:

```json
{
  "/path/to/output/domain-ts-scroll-section.png": {
    "selector": "css_selector_for_main_content_block",
    "text": "Extracted Markdown text from the visible part of the page...",
    "html": "<!DOCTYPE html><html>...</html>"
  }
}
```

`html` is present only when `--fetch_html` is set.

### Metadata fields

- `selector` (str) — CSS selector identifying the most relevant content block visible in that frame (e.g. `main`, `article#content`, `div.product-details`). Defaults to `body` if nothing more specific is found.
- `text` (str) — Markdown representation of the visible text, extracted via `html2text`. Included when `fetch_text` is true (default); trimmed to ~200 characters when `trim_text` is true (default).
- `html` (str, optional) — minified HTML of the fully visible elements, included only when `fetch_html` is true.

For `apng` output, the JSON contains a single entry for the animation file, with metadata like `{"selector": "animated", "text": "Animation with N frames", "frames": N}`.
