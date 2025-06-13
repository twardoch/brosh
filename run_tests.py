#!/usr/bin/env python3
"""Simple test runner for brosh package."""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Run tests with appropriate options."""
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Basic test command
    cmd = [
        sys.executable,
        "-m", "pytest",
        str(project_root / "tests"),
        "--verbose",
        "--tb=short",
    ]
    
    # Add coverage if pytest-cov is available
    try:
        import pytest_cov
        del pytest_cov  # We just need to check if it's importable
        cmd.extend([
            "--cov=src/brosh",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
        ])
        print("Running tests with coverage...")
    except ImportError:
        print(
            "Running tests without coverage "
            "(install pytest-cov for coverage)..."
        )
    
    # Run the tests
    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        return 1
    except (OSError, subprocess.SubprocessError) as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
