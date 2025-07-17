#!/bin/bash
# this_file: scripts/release.sh
# Release script for brosh package

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if version is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}❌ Usage: $0 <version>${NC}"
    echo -e "${YELLOW}   Example: $0 1.0.0${NC}"
    exit 1
fi

VERSION=$1
TAG="v$VERSION"

echo -e "${GREEN}🚀 Releasing brosh version $VERSION...${NC}"

# Validate version format (basic semver check)
if [[ ! $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?$ ]]; then
    echo -e "${RED}❌ Invalid version format. Use semver format (e.g., 1.0.0)${NC}"
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}⚠️  You are not on the main branch (current: $CURRENT_BRANCH)${NC}"
    echo -e "${YELLOW}   Continue anyway? (y/N)${NC}"
    read -r response
    if [[ ! $response =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Release cancelled${NC}"
        exit 1
    fi
fi

# Check if tag already exists
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo -e "${RED}❌ Tag $TAG already exists${NC}"
    exit 1
fi

# Check working directory is clean
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}❌ Working directory is not clean. Please commit or stash changes.${NC}"
    exit 1
fi

# Run tests
echo -e "${BLUE}🧪 Running tests before release...${NC}"
./scripts/test.sh

# Build package
echo -e "${BLUE}🏗️  Building package...${NC}"
./scripts/build.sh

# Create and push tag
echo -e "${YELLOW}🏷️  Creating tag $TAG...${NC}"
git tag -a "$TAG" -m "Release version $VERSION"

echo -e "${YELLOW}📤 Pushing tag to remote...${NC}"
git push origin "$TAG"

echo -e "${GREEN}🎉 Release $VERSION completed successfully!${NC}"
echo -e "${BLUE}   • Tag $TAG created and pushed${NC}"
echo -e "${BLUE}   • GitHub Actions will automatically:${NC}"
echo -e "${BLUE}     - Build the package${NC}"
echo -e "${BLUE}     - Run tests${NC}"
echo -e "${BLUE}     - Create GitHub release${NC}"
echo -e "${BLUE}     - Publish to PyPI${NC}"
echo -e "${BLUE}     - Generate binary artifacts${NC}"

echo -e "${YELLOW}🔗 Monitor the release at: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions${NC}"