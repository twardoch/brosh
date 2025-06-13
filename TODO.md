# TODO

Analyze the entire codebase (read `llms.txt`)

Carefully analyze every single .py file: 

src/brosh/__init__.py
src/brosh/__main__.py
src/brosh/__version__.py
src/brosh/api.py
src/brosh/brosh.py
src/brosh/browser.py
src/brosh/capture.py
src/brosh/cli.py
src/brosh/image.py
src/brosh/mcp.py
src/brosh/models.py
src/brosh/texthtml.py
src/brosh/tool.py

Identify the purpose of each construct (function, class etc.) in the file. Think very hard whether that construct is actually needed. 

Into `PLAN.md` write down which constructs are not needed and should be removed. Our goal is to clean the baggage and to just keep functioning code. 

Once you’ve finished making the `PLAN.md`, perform the actual cleaning.