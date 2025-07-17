# this_file: Makefile
# Makefile for brosh project

.PHONY: help install test lint build clean dev-setup release binary package docs all

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default target
help:
	@echo "$(GREEN)🔧 Brosh Project Build System$(NC)"
	@echo ""
	@echo "Available targets:"
	@echo "  $(YELLOW)help$(NC)          Show this help message"
	@echo "  $(YELLOW)dev-setup$(NC)     Set up development environment"
	@echo "  $(YELLOW)install$(NC)       Install package in development mode"
	@echo "  $(YELLOW)test$(NC)          Run tests with coverage"
	@echo "  $(YELLOW)lint$(NC)          Run linting and formatting checks"
	@echo "  $(YELLOW)build$(NC)         Build Python package"
	@echo "  $(YELLOW)binary$(NC)        Build binary executable"
	@echo "  $(YELLOW)package$(NC)       Build both Python package and binary"
	@echo "  $(YELLOW)docs$(NC)          Build documentation"
	@echo "  $(YELLOW)clean$(NC)         Clean build artifacts"
	@echo "  $(YELLOW)release$(NC)       Create a new release (requires VERSION)"
	@echo "  $(YELLOW)all$(NC)           Run lint, test, and build"
	@echo ""
	@echo "Usage examples:"
	@echo "  make dev-setup     # Set up development environment"
	@echo "  make test          # Run tests"
	@echo "  make release VERSION=1.0.0  # Create release"

# Development setup
dev-setup:
	@echo "$(GREEN)🛠️  Setting up development environment...$(NC)"
	@chmod +x scripts/*.sh
	@./scripts/dev-setup.sh

# Install package in development mode
install:
	@echo "$(GREEN)📦 Installing package in development mode...$(NC)"
	@pip install --break-system-packages -e ".[dev,test,all]"

# Run tests
test:
	@echo "$(GREEN)🧪 Running tests...$(NC)"
	@./scripts/test.sh

# Run linting
lint:
	@echo "$(GREEN)🔍 Running linting checks...$(NC)"
	@if command -v ruff &> /dev/null; then \
		echo "$(YELLOW)  Running Ruff linter...$(NC)"; \
		ruff check src/brosh tests/ --output-format=github; \
		echo "$(YELLOW)  Running Ruff formatter...$(NC)"; \
		ruff format --check --respect-gitignore src/brosh tests/; \
	else \
		echo "$(YELLOW)⚠️  Ruff not found, skipping linting$(NC)"; \
	fi
	@if command -v mypy &> /dev/null; then \
		echo "$(YELLOW)  Running MyPy...$(NC)"; \
		mypy --install-types --non-interactive src/brosh tests/; \
	else \
		echo "$(YELLOW)⚠️  MyPy not found, skipping type checking$(NC)"; \
	fi

# Build Python package
build:
	@echo "$(GREEN)🏗️  Building Python package...$(NC)"
	@./scripts/build.sh

# Build binary executable
binary:
	@echo "$(GREEN)🔨 Building binary executable...$(NC)"
	@pip install --break-system-packages pyinstaller
	@pip install --break-system-packages -e ".[all]"
	@pyinstaller brosh.spec --clean --distpath dist/binary
	@echo "$(GREEN)✅ Binary built: dist/binary/brosh$(NC)"

# Build both package and binary
package: build binary
	@echo "$(GREEN)📦 All packages built successfully!$(NC)"

# Build documentation
docs:
	@echo "$(GREEN)📚 Building documentation...$(NC)"
	@pip install --break-system-packages -e ".[docs]"
	@if [ -d docs ]; then \
		sphinx-build -b html docs docs/_build/html; \
		echo "$(GREEN)✅ Documentation built: docs/_build/html/index.html$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  No docs directory found, skipping$(NC)"; \
	fi

# Clean build artifacts
clean:
	@echo "$(GREEN)🧹 Cleaning build artifacts...$(NC)"
	@rm -rf dist/ build/ src/brosh.egg-info/ htmlcov/ .coverage coverage.xml
	@rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Clean completed$(NC)"

# Create release
release:
	@if [ -z "$(VERSION)" ]; then \
		echo "$(RED)❌ VERSION is required. Usage: make release VERSION=1.0.0$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)🚀 Creating release $(VERSION)...$(NC)"
	@chmod +x scripts/release.sh
	@./scripts/release.sh $(VERSION)

# Run all checks and builds
all: lint test build
	@echo "$(GREEN)🎉 All tasks completed successfully!$(NC)"

# Quick development commands
.PHONY: fmt fix serve
fmt:
	@echo "$(GREEN)✨ Formatting code...$(NC)"
	@ruff format src/brosh tests/
	@ruff check --fix src/brosh tests/

fix:
	@echo "$(GREEN)🔧 Fixing code issues...$(NC)"
	@ruff check --fix --unsafe-fixes src/brosh tests/
	@ruff format src/brosh tests/

serve:
	@echo "$(GREEN)🚀 Starting MCP server...$(NC)"
	@python -m brosh mcp