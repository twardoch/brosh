# === USER INSTRUCTIONS ===
**brosh** is a browser screenshot tool that captures scrolling screenshots of webpages using Playwright's async API. The tool has been refactored from a monolithic script into a modular Python package with the following structure:
```
src/brosh/
├── __init__.py      # Package exports
├── __main__.py      # CLI entry point
├── api.py           # Public API functions (sync and async)
├── cli.py           # Fire-based CLI interface
├── tool.py          # Main BrowserScreenshotTool class
├── browser.py       # Browser management utilities
├── capture.py       # Screenshot capture logic
├── image.py         # Image processing utilities
├── models.py        # Data models and enums
├── mcp.py           # MCP server functionality
└── texthtml.py      # HTML/text processing utilities
```
Legacy implementation:
- `brosh_sel.py`: Selenium-based synchronous implementation (deprecated)
## Commands
### Installation
```bash
# Install the package in development mode
pip install -e .
# Or install from PyPI (when published)
pip install brosh
# Install Playwright browsers
playwright install
```
### Running the Tools
The package provides two command-line tools:
- `brosh`: Main CLI for screenshot capture
- `brosh-mcp`: MCP server for AI tool integration
#### Primary Tool (brosh)
```bash
# Basic usage
brosh shot "https://example.com"
# Start browser in debug mode
brosh --app chrome run
# Take screenshots with options
brosh --app chrome --width 1920 --height 1080 shot "https://example.com" --scroll_step 80 --format png
# Run MCP server
brosh mcp
# Or use the dedicated command
brosh-mcp
```
#### Development Mode
```bash
# Run from source during development
python -m brosh shot "https://example.com"
# Or use the development script (if maintaining the monolithic version)
./brosh.py shot "https://example.com"
```
## Architecture
### Module Structure
The project has been refactored into a modular architecture:
- **api.py**: Public API with `capture_webpage` (sync) and `capture_webpage_async` (async) functions
- **browser.py**: `BrowserManager` class handles browser detection, launching, and connection
- **capture.py**: `CaptureManager` class handles screenshot capture and scrolling logic
- **image.py**: `ImageProcessor` class handles image scaling, conversion, and APNG creation
- **tool.py**: `BrowserScreenshotTool` orchestrates the other modules
- **cli.py**: `BrowserScreenshotCLI` provides the Fire-based command interface
- **mcp.py**: FastMCP server implementation for AI tool integration
- **models.py**: Data models including `ImageFormat` enum and MCP-specific types
- **texthtml.py**: `DOMProcessor` for HTML compression and text extraction
### Key Features
- **Async Architecture**: Uses Playwright's async API for better performance
- **Dual API**: Provides both synchronous and asynchronous APIs for different contexts
- **Command Structure**: Fire-based CLI with subcommands (run, shot, quit, mcp)
- **Browser Management**: Can connect to existing browsers or start new ones
- **MCP Integration**: Includes FastMCP server mode for model context protocol
- **Error Handling**: Comprehensive retry logic and timeout management
- **HTML Extraction**: Can extract minified HTML of fully visible elements
- **Text Extraction**: Automatically converts visible content to Markdown format
### Development Notes
- The refactored code maintains 100% backward compatibility with the original monolithic script
- Both `brosh` and `brosh-mcp` CLI tools are available after installation
- The package uses modern Python packaging with pyproject.toml
- Type hints are used throughout for better code clarity
- MCP server uses the async API to avoid asyncio context issues
# Working principles for software development
## When you write code (in any language)
- Iterate gradually, avoiding major changes
- Minimize confirmations and checks
- Preserve existing code/structure unless necessary
- Use constants over magic numbers
- Check for existing solutions in the codebase before starting
- Check often the coherence of the code you’re writing with the rest of the code.
- Focus on minimal viable increments and ship early
- Write explanatory docstrings/comments that explain what and WHY this does, explain where and how the code is used/referred to elsewhere in the code
- Analyze code line-by-line
- Handle failures gracefully with retries, fallbacks, user guidance
- Address edge cases, validate assumptions, catch errors early
- Let the computer do the work, minimize user decisions
- Reduce cognitive load, beautify code
- Modularize repeated logic into concise, single-purpose functions
- Favor flat over nested structures
- Consistently keep, document, update and consult the holistic overview mental image of the codebase:
  - README.md (purpose and functionality)
  - CHANGELOG.md (past changes)
  - TODO.md (future goals)
  - PROGRESS.md (detailed flat task list)
## Use MCP tools if you can
Before and during coding (if have access to tools), you should:
- consult the `context7` tool for most up-to-date software package documentation;
- ask intelligent questions to the `deepseek/deepseek-r1-0528:free` model via the `chat_completion` tool to get additional reasoning;
- also consult the `openai/o3` model via the `chat_completion` tool for additional reasoning and help with the task;
- use the `sequentialthinking` tool to think about the best way to solve the task;
- use the `perplexity_ask` and `duckduckgo_web_search` tools to gather up-to-date information or context;
## Keep track of paths
In each source file, maintain the up-to-date `this_file` record that shows the path of the current file relative to project root. Place the `this_file` record near the top of the file, as a comment after the shebangs, or in the YAML Markdown frontmatter.
## If you write Python
- PEP 8: Use consistent formatting and naming
- Write clear, descriptive names for functions and variables
- PEP 20: Keep code simple and explicit. Prioritize readability over cleverness
- Use type hints in their simplest form (list, dict, | for unions)
- PEP 257: Write clear, imperative docstrings
- Use f-strings. Use structural pattern matching where appropriate
- ALWAYS add "verbose" mode logugu-based logging, & debug-log
- For CLI Python scripts, use fire & rich, and start the script with
```
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["PKG1", "PKG2"]
# ///
# this_file: PATH_TO_CURRENT_FILE
```
After Python changes run:
```
uzpy run .; fd -e py -x autoflake {}; fd -e py -x pyupgrade --py312-plus {}; fd -e py -x ruff check --output-format=github --fix --unsafe-fixes {}; fd -e py -x ruff format --respect-gitignore --target-version py312 {}; python -m pytest;
```
## Additional guidelines
Ask before extending/refactoring existing code in a way that may add complexity or break things.
When you’re finished, print "Wait, but" to go back, think & reflect, revise & improvement what you’ve done (but don’t invent functionality freely). Repeat this. But stick to the goal of "minimal viable next version".
## Virtual team work
Be creative, diligent, critical, relentless & funny! Lead two experts: "Ideot" for creative, unorthodox ideas, and "Critin" to critique flawed thinking and moderate for balanced discussions. The three of you shall illuminate knowledge with concise, beautiful responses, process methodically for clear answers, collaborate step-by-step, sharing thoughts and adapting. If errors are found, step back and focus on accuracy and progress.
## API Usage Examples
### Synchronous API (for CLI and simple scripts)
```python
from brosh import capture_webpage
# Basic usage
result = capture_webpage("https://example.com", scale=50)
# Returns: {"path/to/screenshot.png": {"selector": "body", "text": "..."}}
```
### Asynchronous API (for MCP server and async applications)
```python
from brosh import capture_webpage_async
async def main():
    result = await capture_webpage_async("https://example.com", html=True)
    # Returns same format with optional "html" field
```
### Recent Updates
- Fixed MCP async execution error by separating sync/async API functions
- Added automatic text extraction to all captures (converts HTML to Markdown)
- Improved error handling in MCP server with proper async context management
# === END USER INSTRUCTIONS ===


# main-overview

## Development Guidelines

- Only modify code directly relevant to the specific request. Avoid changing unrelated functionality.
- Never replace code with placeholders like `# ... rest of the processing ...`. Always include complete code.
- Break problems into smaller steps. Think through each step separately before implementing.
- Always provide a complete PLAN with REASONING based on evidence from code and logs before making changes.
- Explain your OBSERVATIONS clearly, then provide REASONING to identify the exact issue. Add console logs when needed to gather more information.


The brosh system implements intelligent webpage screenshot capture through three core business domains:

## Content Capture Engine (Importance: 95)
Location: src/brosh/capture.py

- Semantic Section Detection
  - Analyzes DOM structure for meaningful content blocks
  - Generates contextual identifiers from visible elements
  - Maps viewport intersections to content hierarchy

- Viewport Management
  - Progressive scrolling with content overlap detection
  - Dynamic height adjustment for expanding content
  - Section boundary identification during scrolling

## Browser Integration Layer (Importance: 85)
Location: src/brosh/browser.py

- Platform-Specific Browser Management
  - Browser priority system (Chrome > Edge > Safari)
  - OS-specific resolution detection with Retina support
  - Debug mode orchestration with dedicated ports:
    - Chromium: 9222
    - Edge: 9223
    - WebKit: 9225

## AI Integration Protocol (Importance: 80)
Location: src/brosh/mcp.py

- MCP Tool Integration
  - Screenshot request handling for AI systems
  - Visual context extraction for language models
  - HTML/selector mapping for content analysis

## Core Business Rules

1. Screenshot Organization
- Domain-based hierarchical storage
- Semantic section identification
- Viewport overlap constraints (10-200%)

2. Browser Constraints
- Safari restricted to macOS
- Firefox explicitly unsupported
- Debug ports assigned per browser type

3. Content Processing
- Smart scroll step calculation
- Section-aware capture naming
- Dynamic content detection

The system's unique value proposition lies in intelligent content detection and AI-ready capture capabilities, distinguishing it from basic screenshot utilities through semantic understanding of webpage structure.

$END$
