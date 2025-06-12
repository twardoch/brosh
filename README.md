# brosh - Browser Screenshot Tool

A powerful browser screenshot tool that captures scrolling screenshots of webpages using Playwright's async API. Supports intelligent section identification, multiple output formats including animated PNG, and MCP (Model Context Protocol) integration.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
  - [Using uv/uvx (Recommended)](#using-uvuvx-recommended)
  - [Using pip](#using-pip)
  - [Using pipx](#using-pipx)
  - [From Source](#from-source)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [MCP Server Mode](#mcp-server-mode)
  - [Python API](#python-api)
- [Command Reference](#command-reference)
  - [Global Options](#global-options)
  - [Commands](#commands)
- [Output](#output)
- [Advanced Usage](#advanced-usage)
  - [Browser Management](#browser-management)
  - [Custom Viewports](#custom-viewports)
  - [HTML Extraction](#html-extraction)
  - [Animation Creation](#animation-creation)
- [MCP Integration](#mcp-integration)
  - [What is MCP?](#what-is-mcp)
  - [Setting Up MCP Server](#setting-up-mcp-server)
  - [Configuring Claude Desktop](#configuring-claude-desktop)
- [Architecture](#architecture)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **🚀 Async Playwright Integration**: Fast and reliable browser automation
- **🔍 Smart Section Detection**: Automatically identifies visible sections for descriptive filenames
- **🖼️ Multiple Formats**: PNG, JPG, and animated PNG (APNG) output
- **🌐 Browser Support**: Chrome, Edge, and Safari (macOS)
- **🔌 Remote Debugging**: Connects to existing browser sessions preserving cookies/auth
- **🤖 MCP Server**: Integrate with AI tools via Model Context Protocol
- **📄 HTML Extraction**: Optionally capture HTML content of visible elements
- **📐 Flexible Scrolling**: Configurable scroll steps and starting positions
- **🎯 Precise Control**: Set viewport size, zoom level, and output scaling
- **🔄 Automatic Retries**: Robust error handling with configurable retry logic

## How It Works

**brosh** works by:

1. **Browser Connection**: Connects to an existing browser in debug mode or launches a new instance
2. **Page Navigation**: Navigates to the specified URL and waits for content to load
3. **Smart Scrolling**: Scrolls through the page in configurable steps, capturing screenshots
4. **Section Detection**: Identifies visible headers and elements to create meaningful filenames
5. **Image Processing**: Applies scaling, format conversion, and creates animations if requested
6. **Output Organization**: Saves screenshots with descriptive names including domain, timestamp, and section

The tool is especially useful for:
- **Documentation**: Capturing long technical documentation or API references
- **QA Testing**: Visual regression testing and bug reporting
- **Content Archival**: Preserving web content with full page captures
- **Design Reviews**: Sharing complete page designs with stakeholders
- **AI Integration**: Providing visual context to language models via MCP

## Installation

### Using uv/uvx (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that replaces pip, pip-tools, pipx, poetry, pyenv, and virtualenv.

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run brosh directly with uvx (no installation needed)
uvx brosh shot "https://example.com"

# Or install globally
uv tool install brosh

# Install with all extras
uv tool install "brosh[all]"
```

### Using pip

```bash
# Basic installation
pip install brosh

# With all optional dependencies
pip install "brosh[all]"
```

### Using pipx

[pipx](https://pipx.pypa.io/) installs Python applications in isolated environments.

```bash
# Install pipx (if not already installed)
python -m pip install --user pipx
python -m pipx ensurepath

# Install brosh
pipx install brosh
```

### From Source

```bash
git clone https://github.com/twardoch/brosh.git
cd brosh
pip install -e ".[all]"
```

### Install Playwright Browsers

After installation, you need to install the browser drivers:

```bash
playwright install
```

## Quick Start

```bash
# Capture a single webpage
brosh shot "https://example.com"

# Start browser in debug mode for better performance
brosh run
brosh shot "https://example.com"

# Create an animated PNG showing the scroll
brosh shot "https://example.com" --format apng

# Capture with custom viewport
brosh --width 1920 --height 1080 shot "https://example.com"

# Extract HTML content
brosh shot "https://example.com" --html --json > content.json
```

## Usage

### Command Line Interface

brosh provides a Fire-based CLI with intuitive commands and options.

#### Basic Screenshot Capture

```bash
# Simple capture
brosh shot "https://example.com"

# Capture with custom settings
brosh --width 1920 --height 1080 --zoom 125 shot "https://example.com"

# Capture entire page height (no viewport limit)
brosh --height -1 shot "https://example.com"

# Save to specific directory
brosh --output_dir ~/Screenshots shot "https://example.com"

# Organize by domain
brosh --subdirs shot "https://example.com"
```

#### Advanced Capture Options

```bash
# Start from specific element
brosh shot "https://docs.python.org" --from_selector "#functions"

# Limit number of screenshots
brosh shot "https://example.com" --max_frames 5

# Adjust scroll step (percentage of viewport)
brosh shot "https://example.com" --scroll_step 50

# Scale output images
brosh shot "https://example.com" --scale 75

# Create animated PNG
brosh shot "https://example.com" --format apng --anim_spf 1.0

# Extract visible HTML
brosh shot "https://example.com" --html --json > page_content.json
```

### MCP Server Mode

Run as an MCP server for AI tool integration:

```bash
# Using the dedicated command
brosh-mcp

# Or via the main command
brosh mcp
```

### Python API

```python
import asyncio
from brosh import BrowserScreenshotTool

async def capture_screenshots():
    tool = BrowserScreenshotTool(verbose=True)
    
    # Basic capture
    screenshots = await tool.capture(
        url="https://example.com",
        width=1920,
        height=1080,
        scroll_step=100,
        format="png"
    )
    
    print(f"Captured {len(screenshots)} screenshots")
    for path in screenshots:
        print(f"  - {path}")
    
    # Capture with HTML extraction
    result = await tool.capture(
        url="https://example.com",
        html=True,
        max_frames=3,
        from_selector="#main-content"
    )
    
    # Result is a dict with paths as keys and HTML/selectors as values
    for path, data in result.items():
        print(f"\nScreenshot: {path}")
        print(f"Selector: {data['selector']}")
        print(f"HTML preview: {data['html'][:200]}...")

# Run the async function
asyncio.run(capture_screenshots())
```

## Command Reference

### Global Options

These options can be used with any command:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--app` | str | auto-detect | Browser to use: `chrome`, `edge`, `safari` |
| `--width` | int | screen width | Viewport width in pixels |
| `--height` | int | screen height | Viewport height in pixels (-1 for full page) |
| `--zoom` | int | 100 | Zoom level percentage (10-500) |
| `--output_dir` | str | ~/Pictures | Output directory for screenshots |
| `--subdirs` | bool | False | Create subdirectories for each domain |
| `--verbose` | bool | False | Enable debug logging |

### Commands

#### `run` - Start Browser in Debug Mode

```bash
brosh [--app BROWSER] run [--force_run]
```

Starts the browser in remote debugging mode for better performance with multiple captures.

**Options:**
- `--force_run`: Force restart even if already running

#### `quit` - Quit Browser

```bash
brosh [--app BROWSER] quit
```

Closes the browser started in debug mode.

#### `shot` - Capture Screenshots

```bash
brosh [OPTIONS] shot URL [SHOT_OPTIONS]
```

**Required:**
- `URL`: The webpage URL to capture

**Shot Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--scroll_step` | int | 100 | Scroll step as % of viewport height (10-200) |
| `--scale` | int | 100 | Scale output images by % (10-200) |
| `--format` | str | png | Output format: `png`, `jpg`, `apng` |
| `--anim_spf` | float | 0.5 | Seconds per frame for APNG |
| `--html` | bool | False | Extract HTML content of visible elements |
| `--json` | bool | False | Output results as JSON |
| `--max_frames` | int | 0 | Maximum screenshots (0 = all) |
| `--from_selector` | str | "" | CSS selector to start capture from |

#### `mcp` - Run MCP Server

```bash
brosh mcp
```

Starts the MCP server for AI tool integration.

## Output

### File Naming Convention

Screenshots are saved with descriptive filenames:

```
{domain}-{timestamp}-{scroll_position}-{section}.{format}
```

**Example:**
```
github_com-250612-185234-00500-readme.png
│         │              │     │
│         │              │     └── Section identifier
│         │              └──────── Scroll position (0-9999)
│         └─────────────────────── Timestamp (YYMMDD-HHMMSS)
└───────────────────────────────── Domain name
```

### Output Formats

- **PNG**: Lossless compression, best quality (default)
- **JPG**: Smaller file size, good for photos
- **APNG**: Animated PNG showing the scroll sequence

### JSON Output

When using `--html --json`, the output format is:

```json
{
  "/path/to/screenshot1.png": {
    "selector": "main.content",
    "html": "<main class='content'>...</main>"
  },
  "/path/to/screenshot2.png": {
    "selector": "#section-2",
    "html": "<section id='section-2'>...</section>"
  }
}
```

## Advanced Usage

### Browser Management

brosh can connect to your existing browser session, preserving cookies, authentication, and extensions:

```bash
# Start Chrome in debug mode
brosh --app chrome run

# Your regular browsing session remains active
# brosh connects to it for screenshots

# Take screenshots with your logged-in session
brosh shot "https://github.com/notifications"

# Quit when done
brosh --app chrome quit
```

### Custom Viewports

Simulate different devices by setting viewport dimensions:

```bash
# Desktop - 4K
brosh --width 3840 --height 2160 shot "https://example.com"

# Desktop - 1080p
brosh --width 1920 --height 1080 shot "https://example.com"

# Tablet
brosh --width 1024 --height 768 shot "https://example.com"

# Mobile
brosh --width 375 --height 812 shot "https://example.com"
```

### HTML Extraction

Extract the HTML content of visible elements for each screenshot:

```bash
# Get HTML with screenshots
brosh shot "https://example.com" --html --json > content.json

# Process the extracted content
cat content.json | jq 'to_entries | .[] | {
  screenshot: .key,
  wordCount: (.value.html | split(" ") | length)
}'
```

### Animation Creation

Create smooth animations showing page scroll:

```bash
# Standard animation (0.5 seconds per frame)
brosh shot "https://example.com" --format apng

# Faster animation
brosh shot "https://example.com" --format apng --anim_spf 0.2

# Slower, more detailed
brosh shot "https://example.com" --format apng --anim_spf 1.0 --scroll_step 50
```

## MCP Integration

### What is MCP?

The Model Context Protocol (MCP) is an open standard that enables seamless integration between AI applications and external data sources or tools. brosh implements an MCP server that allows AI assistants like Claude to capture and analyze web content.

### Setting Up MCP Server

#### 1. Using uvx (Recommended)

```bash
# Run directly without installation
uvx brosh-mcp

# Or install as a tool
uv tool install brosh
uvx brosh-mcp
```

#### 2. Configure Claude Desktop

Add brosh to your Claude Desktop configuration:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

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

#### 3. Alternative Configurations

**Using Python directly:**
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

**Using specific Python path:**
```json
{
  "mcpServers": {
    "brosh": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "brosh", "mcp"]
    }
  }
}
```

### Using with Claude

Once configured, you can ask Claude to:

- "Take a screenshot of python.org documentation"
- "Capture the entire React homepage with animations"
- "Get screenshots of the GitHub trending page and extract the visible HTML"
- "Show me what the Hacker News homepage looks like"

Claude will use brosh to capture the screenshots and can analyze the visual content or extracted HTML.

## Architecture

The project is organized into modular components:

```
src/brosh/
├── __init__.py      # Package exports
├── __main__.py      # CLI entry point
├── cli.py           # Command-line interface
├── tool.py          # Main screenshot tool
├── browser.py       # Browser management
├── capture.py       # Screenshot capture logic
├── image.py         # Image processing
├── models.py        # Data models
└── mcp.py           # MCP server implementation
```

### Key Components

- **BrowserManager**: Handles browser detection, launching, and connection
- **CaptureManager**: Manages scrolling and screenshot capture
- **ImageProcessor**: Handles image scaling, conversion, and animation
- **BrowserScreenshotTool**: Orchestrates the capture process
- **BrowserScreenshotCLI**: Provides the command-line interface

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/twardoch/brosh.git
cd brosh

# Install with development dependencies
pip install -e ".[dev,test,all]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/brosh --cov-report=term-missing

# Run specific test
pytest tests/test_capture.py -v
```

### Code Quality

```bash
# Format code
ruff format src/brosh tests

# Lint code
ruff check src/brosh tests

# Type checking
mypy src/brosh
```

### Building Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build documentation
sphinx-build -b html docs/source docs/build
```

## Troubleshooting

### Common Issues

#### Browser Not Found

**Error:** "Could not find chrome installation"

**Solution:** Ensure Chrome/Edge/Safari is installed in the default location, or specify the browser explicitly:
```bash
brosh --app edge shot "https://example.com"
```

#### Connection Timeout

**Error:** "Failed to connect to browser"

**Solution:** Start the browser in debug mode first:
```bash
brosh run
# Then in another terminal:
brosh shot "https://example.com"
```

#### Screenshot Timeout

**Error:** "Screenshot timeout for position X"

**Solution:** Increase the timeout or reduce the page complexity:
```bash
# Simpler format
brosh shot "https://example.com" --format jpg

# Fewer screenshots
brosh shot "https://example.com" --scroll_step 200
```

#### Permission Denied

**Error:** "Permission denied" when saving screenshots

**Solution:** Check the output directory permissions or use a different directory:
```bash
brosh --output_dir /tmp/screenshots shot "https://example.com"
```

### Debug Mode

Enable verbose logging to troubleshoot issues:

```bash
brosh --verbose shot "https://example.com"
```

### Platform-Specific Notes

#### macOS
- Safari requires enabling "Allow Remote Automation" in Develop menu
- Retina displays are automatically detected and handled

#### Windows
- Run as administrator if you encounter permission issues
- Chrome/Edge must be installed in default Program Files location

#### Linux
- Install additional dependencies: `sudo apt-get install libnss3 libxss1`
- Headless mode may be required on servers without display

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Process

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings to all public functions
- Keep functions focused and modular
- Write tests for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Created by [Adam Twardoch](https://github.com/twardoch)

## Acknowledgments

- Built with [Playwright](https://playwright.dev/) for reliable browser automation
- Uses [Fire](https://github.com/google/python-fire) for the CLI interface
- Implements [FastMCP](https://github.com/jlowin/fastmcp) for Model Context Protocol support
- Inspired by various web scraping and screenshot tools