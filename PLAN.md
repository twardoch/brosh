1.  **Analyze and Refine Parameter Naming and Defaults:** ✅
    *   **`api.py` and `mcp.py`**: Rename the `format` parameter in `api.capture_webpage` and `api.capture_webpage_async` to `output_format` for consistency with its usage in `CaptureConfig` and how it's called from `mcp.py`. Update calls within `cli.py` accordingly. (Completed: Confirmed `output_format` was already largely in use, updated docstrings).
    *   **`cli.py`**: Modify `BrowserScreenshotCLI.__init__` to set `output_dir` to `None` by default and resolve it to `dflt_output_folder()` if `None` within the constructor, similar to `api.py`, to avoid mutable default arguments (B008). (Completed: Verified this was already correctly implemented).

2.  **Consolidate API Logic:** ✅
    *   **`api.py`**: Refactor `capture_webpage` and `capture_webpage_async` to reduce code duplication. Create a private helper function, e.g., `_create_capture_config_and_validate(**kwargs)`, that both public functions can use to instantiate and validate `CaptureConfig`. (Completed).

3.  **Centralize Constants:** ✅
    *   Create `src/brosh/constants.py`. (Completed).
    *   Move default values like `DEFAULT_ZOOM_LEVEL`, `DEFAULT_FALLBACK_WIDTH`, `DEFAULT_FALLBACK_HEIGHT`, timeouts, retry counts, etc., from `browser.py`, `cli.py`, `capture.py`, and `mcp.py` to this new `constants.py` file. (Completed).
    *   Update all modules to import these constants. (Completed).

4.  **Clarify/Simplify Section ID Logic:** ✅
    *   **`capture.py`**: In `_capture_single_frame`, the call to `self.dom_processor.get_section_id(page)` seems unused. Determine if this is intended. (Completed: Now used).
    *   **`tool.py`**: The `_get_section_id_from_frame` method currently returns a placeholder `"section"`. (Completed: Now uses data from CaptureFrame).
    *   **Decision for MVP**:
        *   If actual dynamic section ID generation via `GET_SECTION_ID_JS` (from `texthtml.py`) is functional and simple enough for MVP, ensure it's correctly plumbed through `CaptureFrame` and used in `tool.py` for filename generation. (Completed: Plumbed through).
        *   If it's complex or not fully working, simplify filenames for MVP to not rely on dynamic section IDs (e.g., use a frame index or a simpler placeholder) and remove the unused JS call. For this plan, assume we will attempt to use the dynamic section ID if the JS is already present.

5.  **Review and Refine `BrowserManager`:** ✅
    *   **`browser.py`**: Briefly review the extensive list of browser arguments in `get_browser_args` and `launch_browser_and_connect`. For MVP, ensure the core arguments for stable screenshotting are present. Avoid deep changes without thorough testing, but remove any obviously obsolete or redundant arguments if identifiable. *Conservative approach: primarily document this as a potential future refinement unless clear low-risk changes are found.* (Completed: Consolidated arg list and removed one redundant flag).
    *   **`browser.py`**: In `get_browser_instance`, the `zoom != constants.DEFAULT_ZOOM_LEVEL` check uses a literal `100` for comparison on the first instance, then the constant. Standardize to use the constant. (Completed: Verified it was already using the constant).

6.  **Streamline `cli.py`:** ✅
    *   **`cli.py`**: Ensure `shot` command correctly passes the (potentially renamed) `output_format` parameter to `capture_webpage`. (Completed: Verified dynamic handling is correct).

7.  **Update Documentation and Supporting Files:** (Current step)
    *   **`README.md`**: Update with any changes to CLI arguments or API parameters. Ensure it accurately reflects the MVP's capabilities. Remove obsolete information.
    *   **`CHANGELOG.md`**: Document all significant changes made during this streamlining process. (Completed).
    *   **`PLAN.md`**: This file will be replaced by the current plan. Mark items as complete as they are done. (Being done now).
    *   **`TODO.md`**: Create a new `TODO.md` with a simplified checklist based on this plan.

8.  **Testing and Validation:**
    *   Run `./cleanup.sh` which includes linters, formatters, and tests.
    *   Manually test core CLI functionality for taking screenshots with different browsers and options to ensure MVP works as expected.

9.  **Submit Changes:**
    *   Commit all changes with a descriptive message.