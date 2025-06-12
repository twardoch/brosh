✅ FIXED: MCP async error - capture_webpage returns Task instead of result

The issue was that `capture_webpage` was returning an asyncio Task object when called from the MCP server (async context) instead of the actual result. Fixed by:
1. Creating a separate `capture_webpage_async` function for async contexts
2. Updated MCP to use the async version
3. Kept the original `capture_webpage` for sync contexts (CLI)
