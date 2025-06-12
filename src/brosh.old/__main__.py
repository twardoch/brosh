#!/usr/bin/env python3
# this_file: src/brosh/__main__.py

"""CLI entry point for brosh."""

import fire

from .cli import BrowserScreenshotCLI


def main():
    """Main entry point for the brosh CLI."""
    fire.Fire(BrowserScreenshotCLI)


if __name__ == "__main__":
    main()
