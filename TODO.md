
# TODO

```
brosh|cat

NAME
    brosh - Fire CLI interface for browser screenshot operations.

SYNOPSIS
    brosh - GROUP | COMMAND | VALUE

DESCRIPTION
    Provides organized commands for browser management and screenshot capture.

GROUPS
    GROUP is one of the following:

     browser_manager
       Manages browser detection, launching, and connection.

     tool
       Tool for capturing scrolling screenshots using Playwright async API.

COMMANDS
    COMMAND is one of the following:

     mcp
       Run MCP server for browser screenshots.

     quit
       Quit the specified browser.

     run
       Run browser in remote debug mode.

     shot
       Take screenshots of a webpage.

VALUES
    VALUE is one of the following:

     app
       Browser to use - chrome, edge, safari (default: auto-detect)

     height
       Height in pixels (default: main screen height)

     output_dir
       Output directory for screenshots (default: Pictures)

     subdirs
       Create subdirectories for domains (default: False)

     verbose
       Enable debug logging (default: False)

     width
       Width in pixels (default: main screen width)

     zoom
       Zoom level in % (default: 100)
```

```
brosh-mcp
[06/12/25 18:57:14] INFO     Starting MCP server 'Browser Screenshots' with transport 'stdio'                  server.py:1159
```

## Completed Tasks (2025-06-12)

- [x] Run ./cleanup.sh and analyze the results. Use them to add new TODOs into this file. 
- [x] Run the code checks and fix identified issues
- [x] Start implementing the TODOs. 
- [x] Repeat the above steps until the TODO list is reasonably empty. 
- [x] Rewrite CHANGELOG.md to a sensible format (today is 2025 June 12). 
- [x] Update README.md. Research 'uvx' instalation of MCP servers, write a very very extensive documentation for our tool (both the CLI and MCP). Describe how the tool works, and why it's useful.

### Summary of Completed Work:
- Successfully refactored monolithic brosh.py into modular package structure
- Fixed all auto-fixable linting issues identified by ruff
- Created comprehensive CHANGELOG.md following Keep a Changelog format
- Created extensive 683-line README.md with:
  - Detailed uvx/uv installation instructions
  - Comprehensive usage examples
  - MCP integration guide with Claude Desktop configuration
  - Architecture overview
  - Troubleshooting section
  - Platform-specific notes

## Future Enhancements (Optional)

- [ ] Add unit tests for all modules
- [ ] Create GitHub Actions CI/CD pipeline
- [ ] Add support for additional browsers (Firefox)
- [ ] Implement parallel screenshot capture for performance
- [ ] Add screenshot annotation features
- [ ] Create documentation website with Sphinx
- [ ] Publish to PyPI for pip installation 