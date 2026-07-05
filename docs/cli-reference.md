---
title: CLI Reference
nav_order: 4
---

# CLI Reference

## Global options

Specified *before* the command, e.g. `brosh --width 800 shot ...`.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `--app` | str | auto-detect | Browser: `chrome`, `edge`, `safari`. Auto-detects if empty. |
| `--width` | int | screen width | Viewport width in pixels. `0` for default screen width. |
| `--height` | int | screen height | Viewport height in pixels. `0` for default, `-1` for full page. |
| `--zoom` | int | 100 | Browser zoom level in % (10-500). |
| `--output_dir` | str | user pictures | Directory to save screenshots (`~/Pictures/brosh` by default). |
| `--subdirs` | bool | `False` | Create domain-based subdirectories inside `output_dir`. |
| `--verbose` | bool | `False` | Enable verbose debug logging. |
| `--json` | bool | `False` | Output `shot` results as JSON to stdout (CLI only). |

## Commands

### `run`

Starts the configured browser in remote debug mode, so repeated `shot` calls don't relaunch it each time.

```
brosh [GLOBAL_OPTIONS] run [--force_run]
```

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `--force_run` | bool | `False` | Restart the browser even if one seems active. |

### `quit`

Quits the browser previously started with `run`.

```
brosh [GLOBAL_OPTIONS] quit
```

### `shot`

Captures screenshots of a URL.

```
brosh [GLOBAL_OPTIONS] shot URL [SHOT_OPTIONS]
```

**Argument:** `URL` (str) — `http://`, `https://`, or `file:///`.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `--scroll_step` | int | 100 | Scroll step as % of viewport height (10-200). |
| `--scale` | int | 100 | Scale output images by % (10-200). |
| `--output_format` | str | `png` | `png`, `jpg`, or `apng`. |
| `--anim_spf` | float | 0.5 | Seconds per frame for APNG animations (0.1-10.0). |
| `--fetch_html` | bool | `False` | Include minified HTML of visible elements in metadata. |
| `--fetch_image` | bool | `False` | (MCP context) include base64 image data in output. |
| `--fetch_image_path` | bool | `True` | (MCP context) include image file path in output. |
| `--fetch_text` | bool | `True` | Include extracted Markdown text in metadata. |
| `--trim_text` | bool | `True` | Trim extracted text to ~200 characters. |
| `--max_frames` | int | 0 | Max frames to capture. `0` for unlimited (full scroll). |
| `--from_selector` | str | `""` | CSS selector to scroll to before capture starts. |

### `mcp`

Runs brosh as an MCP server. Also available as the dedicated `brosh-mcp` script.

```
brosh [GLOBAL_OPTIONS] mcp
```
