#!/usr/bin/env python3
# this_file: src/brosh/models.py

"""Data models and enums for the brosh package."""

from enum import Enum


class ImageFormat(str, Enum):
    """Supported image output formats."""

    PNG = "png"
    JPG = "jpg"
    APNG = "apng"
