#!/bin/bash
# this_file: scripts/dev-setup.sh
# Development environment setup script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🛠️  Setting up brosh development environment...${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}❌ Python 3.10+ required, found $PYTHON_VERSION${NC}"
    exit 1
fi

# Install UV if not available
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}📦 Installing UV package manager...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc || true
fi

# Install development dependencies
echo -e "${YELLOW}📦 Installing development dependencies...${NC}"
pip install --break-system-packages -e ".[dev,test,all]"

# Install Playwright browsers
echo -e "${YELLOW}🌐 Installing Playwright browsers...${NC}"
playwright install

# Install pre-commit hooks
echo -e "${YELLOW}🔧 Setting up pre-commit hooks...${NC}"
if command -v pre-commit &> /dev/null; then
    pre-commit install
else
    echo -e "${YELLOW}⚠️  pre-commit not found, skipping hooks setup${NC}"
fi

# Make scripts executable
echo -e "${YELLOW}🔧 Making scripts executable...${NC}"
chmod +x scripts/*.sh

# Create necessary directories
mkdir -p htmlcov dist build

echo -e "${GREEN}🎉 Development environment setup completed!${NC}"
echo -e "${BLUE}   Available commands:${NC}"
echo -e "${BLUE}   • ./scripts/test.sh     - Run tests${NC}"
echo -e "${BLUE}   • ./scripts/build.sh    - Build package${NC}"
echo -e "${BLUE}   • ./scripts/release.sh  - Create release${NC}"
echo -e "${BLUE}   • brosh                 - Run CLI tool${NC}"
echo -e "${BLUE}   • brosh-mcp             - Run MCP server${NC}"