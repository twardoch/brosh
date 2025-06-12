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
- Configurable scroll steps and starting positions
- Automatic browser detection and fallback logic
- Comprehensive error handling and retry mechanisms

### Changed
- Refactored monolithic script into modular Python package structure
- Migrated from script-based to package-based distribution
- Updated to use modern Python packaging with pyproject.toml

### Fixed
- Browser connection issues with improved retry logic
- Screenshot timeout handling
- Image scaling and format conversion edge cases

## [0.1.0] - 2025-06-12

### Added
- Initial implementation as a monolithic script
- Basic screenshot capture functionality
- Browser management commands (run, quit)
- Fire-based CLI interface

[Unreleased]: https://github.com/twardoch/brosh/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/twardoch/brosh/releases/tag/v0.1.0