# Development Plan

## Future Enhancements

### Performance Optimization
- Implement concurrent screenshot capture for multi-frame operations
- Add caching mechanism for repeated captures of the same URL
- Optimize image processing pipeline for faster conversions

### Feature Additions
- Add support for custom user agents
- Implement proxy support for captures
- Add watermark/annotation capabilities
- Support for capturing specific regions/elements only
- Add PDF export format option

### Code Quality Improvements
- Add browser-mocked integration tests for `capture.py` and `tool.py` (see TODO.md)
- Improve error messages and user feedback
- Add performance benchmarks

> Done in the 2026 modernization pass: ruff + mypy clean; magic numbers and
> boolean-parameter warnings resolved or documented; the import-time crash in
> `get_screen_dimensions` fixed.

### Documentation
- Create video tutorials for common use cases

> Done in the 2026 modernization pass: Jekyll docs site under `docs/` covering
> installation, usage, CLI reference, Python API, MCP server, architecture, and
> output; README trimmed and refocused.

### Platform Support
- Add Firefox browser support
- Investigate headless mode optimizations
- Add Linux-specific installation instructions
- Test and document Docker deployment