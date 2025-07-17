#!/bin/bash
# this_file: scripts/build.sh
# Build script for brosh package

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🏗️  Building brosh package...${NC}"

# Create scripts directory if it doesn't exist
mkdir -p dist

# Clean previous builds
echo -e "${YELLOW}📦 Cleaning previous builds...${NC}"
rm -rf dist/* build/ src/brosh.egg-info/

# Install build dependencies
echo -e "${YELLOW}🔧 Installing build dependencies...${NC}"
pip install --break-system-packages build hatchling hatch-vcs

# Build the package
echo -e "${YELLOW}🔨 Building package...${NC}"
python -m build --outdir dist

# Verify build
echo -e "${YELLOW}✅ Verifying build...${NC}"
if [ -n "$(find dist -name '*.whl')" ] && [ -n "$(find dist -name '*.tar.gz')" ]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
    echo "📦 Distribution files:"
    ls -la dist/
else
    echo -e "${RED}❌ Build failed - missing distribution files${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Build completed successfully!${NC}"