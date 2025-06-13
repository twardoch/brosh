# Development Plan

## Completed Features ✅
- MCP data model restructuring (flat JSON)
- Parameter renaming (html → fetch_html)
- New configuration flags (fetch_image, fetch_image_path, fetch_text, trim_text)
- Test updates for all new functionality

## Immediate Issues to Fix

### Code Quality Issues (from cleanup.sh analysis)
1. **Import Issues**
   - Remove unused import `async_playwright` in browser.py
   - Fix import organization

2. **Security Warnings**
   - Address subprocess security warnings (S603, S607)
   - Use safer subprocess execution methods

3. **Code Style Issues**
   - Replace magic numbers with constants (2560, 100, 200, etc.)
   - Fix boolean parameter warnings (FBT001, FBT002)
   - Use Path.exists() instead of os.path.exists()
   - Add timezone to datetime.now() calls

4. **Test Improvements**
   - Fix pytest.raises() blocks to contain single statements
   - Add match parameters to pytest.raises for specificity
   - Simplify nested with statements

5. **Async Best Practices**
   - Fix ASYNC221 warning about blocking methods in async functions

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
- Address remaining linter warnings (boolean parameters, magic numbers)
- Add more comprehensive integration tests
- Improve error messages and user feedback
- Add performance benchmarks

### Documentation
- Create detailed API documentation
- Add more usage examples
- Create video tutorials for common use cases
- Document MCP integration best practices

### Platform Support
- Add Firefox browser support
- Investigate headless mode optimizations
- Add Linux-specific installation instructions
- Test and document Docker deployment