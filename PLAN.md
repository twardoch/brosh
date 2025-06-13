# Code Cleaning Plan for brosh

## Analysis Summary

After analyzing all Python files in `src/brosh/`, the following unused constructs have been identified for removal:

## 1. Entire Files to Remove

### `src/brosh/brosh.py`
- **Reason**: Completely unrelated to browser screenshot functionality
- **Issues**:
  - Contains unrelated `Config` dataclass and `process_data()` function
  - Has a missing import (`logging` not imported but used)
  - Contains TODO comment indicating incomplete implementation
  - Not imported or referenced by any other module
- **Action**: DELETE entire file

## 2. Unused Functions/Methods to Remove

### In `src/brosh/image.py`
Legacy file-based methods that are no longer used (replaced by in-memory versions):
- `scale_image()` (lines 136-152) - Not used anywhere
- `convert_to_jpg()` (lines 154-181) - Not used anywhere
- `optimize_png()` (lines 184-202) - Not used anywhere
- `create_apng()` (lines 205-236) - Not used anywhere

These were kept "for backward compatibility" but analysis shows they are not actually used anywhere in the codebase.

## 3. Unused Classes to Remove

### In `src/brosh/models.py`
The following classes are defined but never imported or used:
- `BrowserConfig` (lines 84-89) - Not used anywhere
- `MCPResource` (lines 119-127) - Not used anywhere
- `MCPContentItem` (lines 129-133) - Not used anywhere
- `MCPScreenshotResult` (lines 135-138) - Not used anywhere

## 4. Code Quality Observations

### Active and Necessary Files:
-  `__init__.py` - Package exports
-  `__main__.py` - CLI entry point
-  `__version__.py` - Auto-generated version info
-  `api.py` - Public API functions
-  `browser.py` - Browser management
-  `capture.py` - Screenshot capture logic
-  `cli.py` - CLI interface
-  `image.py` - Image processing (after cleanup)
-  `mcp.py` - MCP server
-  `models.py` - Data models (after cleanup)
-  `texthtml.py` - HTML/text processing
-  `tool.py` - Main orchestration

### Import Analysis:
- No unused imports detected in active modules
- No circular dependencies
- Clean modular architecture

## Execution Plan

1. **Delete `src/brosh/brosh.py`** - Entire file is unused
2. **Clean `src/brosh/image.py`** - Remove 4 legacy methods
3. **Clean `src/brosh/models.py`** - Remove 4 unused model classes
4. **Run tests** to ensure nothing breaks
5. **Update any documentation** if needed

## Expected Benefits

- Reduced code complexity
- Clearer codebase without misleading legacy code
- Smaller package size
- Easier maintenance

## Risk Assessment

- **Low Risk**: All identified code is genuinely unused based on thorough analysis
- **Mitigation**: Changes can be easily reverted via git if needed