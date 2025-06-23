# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial public release of brosh (Browser Screenshot Tool)
- Playwright-based async implementation for capturing scrolling screenshots
- Support for Chrome, Edge, and Safari browsers
- Smart section detection for descriptive filenames
- Multiple output formats: PNG, JPG, and animated PNG (APNG)
- Remote debugging mode to connect to existing browser sessions
- MCP (Model Context Protocol) server integration
- HTML extraction feature to capture visible element content
- Automatic text extraction: converts visible HTML to Markdown format
- Configurable scroll steps and starting positions
- Automatic browser detection and fallback logic
- Comprehensive error handling and retry mechanisms

### Changed
- Refactored monolithic script into modular Python package structure
- Migrated from script-based to package-based distribution
- Updated to use modern Python packaging with pyproject.toml

### Fixed
- Browser connection issues with improved retry logic
- MCP response format now properly excludes null fields and uses camelCase for field names (e.g., `mimeType` instead of `mime_type`)
- MCP server results now handle size limits properly with progressive compression
- Screenshot timeout handling
- Image scaling and format conversion edge cases
- MCP async execution error where Task object was returned instead of actual results

### Added
- PNG optimization using pyoxipng for all captured screenshots
- HTML content compression that removes SVG elements while preserving dimensions
- Progressive compression strategy for MCP results exceeding 1MB size limit
- Automatic downsampling and content reduction for oversized MCP responses
- Separate `capture_webpage_async` API function for async contexts
- New MCP configuration flags for granular output control:
  - `fetch_image`: Controls whether image data is included in MCP output (default: False)
  - `fetch_image_path`: Controls whether image paths are included (default: True)
  - `fetch_text`: Controls whether extracted text is included (default: True)
  - `trim_text`: Controls whether text is trimmed to 200 characters (default: True)

### Changed
- MCP output structure changed from nested dictionary to flat JSON format
  - Old: `{"/path/to/file.png": {"selector": "...", "text": "..."}}`
  - New: `{"image_path": "/path/to/file.png", "selector": "...", "text": "..."}`
- Renamed `html` parameter to `fetch_html` throughout the codebase for consistency
- Text extraction now automatically trims to 200 characters by default (configurable)
- Added support for `file://` URLs to capture local HTML files

### Code Quality
- **Imports**: Removed unused imports and organized existing ones using Ruff.
- **Security**: Hardened `subprocess` calls by using `shutil.which` to ensure absolute paths for system commands (`system_profiler`, `pkill`, `taskkill`), reducing potential S607 risks.
- **Style**:
    - Replaced `os.path.exists()` with `pathlib.Path().exists()` for consistency and modern practice.
    - Ensured all `datetime.now()` calls use `timezone.utc` for timezone-aware timestamps.
    - Made boolean parameters in function definitions keyword-only where appropriate to adhere to FBT001/FBT002 Ruff rules (e.g., in API functions, CLI class, MCP functions).
    - Replaced various magic numbers with named constants for improved readability and maintainability across several modules (e.g., default dimensions, timeouts, retry counts, sleep durations).
- **Testing**:
    - Refactored `pytest.raises()` blocks in model validation tests to ensure only the exception-raising statement is within the `with` block.
    - Added `match` parameter to several `pytest.raises()` calls for more specific exception message checking in API and browser tests.
    - Simplified nested `with patch(...)` statements in API tests by combining them into single `with` statements.
- **Async Practices**: Reviewed async functions for `time.sleep` and confirmed usage of `asyncio.sleep` where appropriate.

## [0.1.0] - 2025-06-12

### Added
- Initial implementation as a monolithic script
- Basic screenshot capture functionality
- Browser management commands (run, quit)
- Fire-based CLI interface

[Unreleased]: https://github.com/twardoch/brosh/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/twardoch/brosh/releases/tag/v0.1.0