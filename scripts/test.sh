#!/bin/bash
# this_file: scripts/test.sh
# Test script for brosh package

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Testing brosh package...${NC}"

# Install test dependencies
echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
pip install --break-system-packages -e ".[test]"

# Run linting
echo -e "${BLUE}🔍 Running linting checks...${NC}"
if command -v ruff &> /dev/null; then
    echo -e "${YELLOW}  Running Ruff linter...${NC}"
    ruff check src/brosh tests/ --output-format=github
    echo -e "${YELLOW}  Running Ruff formatter...${NC}"
    ruff format --check --respect-gitignore src/brosh tests/
else
    echo -e "${YELLOW}⚠️  Ruff not found, skipping linting${NC}"
fi

# Run type checking
echo -e "${BLUE}🔍 Running type checks...${NC}"
if command -v mypy &> /dev/null; then
    echo -e "${YELLOW}  Running MyPy...${NC}"
    mypy --install-types --non-interactive src/brosh tests/
else
    echo -e "${YELLOW}⚠️  MyPy not found, skipping type checking${NC}"
fi

# Run tests
echo -e "${BLUE}🧪 Running tests...${NC}"
python -m pytest tests/ \
    --verbose \
    --tb=short \
    --cov=src/brosh \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-report=xml \
    --cov-fail-under=70 \
    -x

# Check test results
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo -e "${BLUE}📊 Coverage report generated in htmlcov/index.html${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Testing completed successfully!${NC}"