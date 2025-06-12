With MCP: 

```
Traceback (most recent call last): File "/Library/Frameworks/Python.framework/Versions/3.12/bin/brosh-mcp", line 10, in <module>
sys.exit(main()) ^^^^^^ File "/Users/adam/Developer/vcs/github.twardoch/pub/brosh/src/brosh/mcp.py", line 202, in main
run_mcp_server()
File "/Users/adam/Developer/vcs/github.twardoch/pub/brosh/src/brosh/mcp.py", line 36, in run_mcp_server
@mcp.tool ^^^^^^^^ File "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/fastmcp/server/server.py", line 778, in tool
tool = Tool.from_function( ^^^^^^^^^^^^^^^^^^^ File "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/fastmcp/tools/tool.py", line 67, in from_function
return FunctionTool.from_function( ^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/fastmcp/tools/tool.py", line 129, in from_function
parsed_fn = ParsedFunction.from_function(fn, exclude_args=exclude_args)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/fastmcp/tools/tool.py", line 217, in from_function raise ValueError(
ValueError: Functions with **kwargs are not supported as tools
Traceback (most recent call last): File "/Library/Frameworks/Python.framework/Versions/3.12/bin/brosh-mcp", line 10, in <module>
sys.exit(main()) ^^^^^^ File "/Users/adam/Developer/vcs/github.twardoch/pub/brosh/src/brosh/mcp.py", line 202, in main
run_mcp_server()
File "/Users/adam/Developer/vcs/github.twardoch/pub/brosh/src/brosh/mcp.py", line 36, in run_mcp_server
@mcp.tool ^^^^^^^^
File "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/fastmcp/server/server.py", line 778, in tool
tool = Tool.from_function(
^^^^^^^^^^^^^^^^^^^ File "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/fastmcp/tools/tool.py", line 67, in from_function
return FunctionTool.from_function(
^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/fastmcp/tools/tool.py", line 129, in from_function
parsed_fn = ParsedFunction.from_function(fn, exclude_args=exclude_args)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/fastmcp/tools/tool.py", line 217, in from_function
raise ValueError( ValueError: Functions with **kwargs are not supported as tools
Traceback (most recent call last): File "/Library/Frameworks/Python.framework/Versions/3.12/bin/brosh-mcp", line 10, in <module>
sys.exit(main())
^^^^^^ File "/Users/adam/Developer/vcs/github.twardoch/pub/brosh/src/brosh/mcp.py", line 202, in main
run_mcp_server()
File "/Users/adam/Developer/vcs/github.twardoch/pub/brosh/src/brosh/mcp.py", line 36, in run_mcp_server
@mcp.tool ^^^^^^^^ File "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/fastmcp/server/server.py", line 778, in tool
tool = Tool.from_function( ^^^^^^^^^^^^^^^^^^^ File "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/fastmcp/tools/tool.py", line 67, in from_function
return FunctionTool.from_function(
^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/fastmcp/tools/tool.py", line 129, in from_function
parsed_fn = ParsedFunction.from_function(fn, exclude_args=exclude_args)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/fastmcp/tools/tool.py", line 217, in from_function
raise ValueError( ValueError: Functions with **kwargs are not supported as tools
```

Read https://gofastmcp.com/patterns/decorating-methods and modify our code. 