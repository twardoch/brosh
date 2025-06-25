#!/usr/bin/env bash

rm -rf dist/brosh*.*
uv build

# python -m uzpy run -e src # uzpy not available
# fd -e py -x autoflake -i {} # fd not available
# fd -e py -x pyupgrade --py311-plus {} # fd not available
# fd -e py -x ruff check --output-format=github --fix --unsafe-fixes {} # fd not available, ruff direct calls are better
# fd -e py -x ruff format --respect-gitignore --target-version py311 {} # fd not available, ruff direct calls are better

# Run ruff directly
echo "Running ruff format..."
ruff format src/brosh tests
echo "Running ruff check..."
ruff check --fix --unsafe-fixes src/brosh tests

echo "Running npx repomix..."
npx repomix -i varia,.specstory,AGENT.md,CLAUDE.md,PLAN.md,SPEC.md,llms.txt,.cursorrules,.github,.giga,.cursor,dist,htmlcov,node_modules,.pytest_cache,.ruff_cache,.tox,.venv,build,docs,examples,scripts,site,static,templates,test,tmp,ven,venv,www,__pycache__,node_modules,.tox,examples,jupyter_notebooks,notebooks,scripts,site,static,templates,test,tmp,ven,venv,www -o llms.txt .
echo "Running pytest..."
python -m pytest
