✅ COMPLETED: Codebase Cleaning

## Summary of Changes:

1. **Deleted `src/brosh/brosh.py`** - Entire file was unrelated to browser screenshot functionality
   - Contained unused `Config` dataclass and `process_data()` function
   - Had missing imports and TODO comments
   - Not referenced anywhere in the codebase

2. **Cleaned `src/brosh/image.py`** - Removed 4 legacy file-based methods:
   - `scale_image()` - replaced by `downsample_png_bytes()`
   - `convert_to_jpg()` - replaced by `convert_png_to_jpg_bytes()`
   - `optimize_png()` - replaced by `optimize_png_bytes()`
   - `create_apng()` - replaced by `create_apng_bytes()`

3. **Cleaned `src/brosh/models.py`** - Removed 4 unused model classes:
   - `BrowserConfig` - not used anywhere
   - `MCPResource` - not used anywhere
   - `MCPContentItem` - not used anywhere
   - `MCPScreenshotResult` - not used anywhere

## Results:
- ✅ Package still imports successfully
- ✅ CLI functionality tested and working
- ✅ No broken imports or dependencies
- ✅ Codebase is now cleaner and more maintainable

See `PLAN.md` for the detailed analysis and execution plan.