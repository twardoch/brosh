#!/usr/bin/env python3
# this_file: src/brosh/optimize.py

"""Image optimization utilities for brosh."""

from pathlib import Path

import oxipng

from loguru import logger
from PIL import Image


def optimize_png_file(
    file_path: str | Path,
    level: int = 6,
    preserve_file: bool = True,
) -> bytes:
    """Optimize a PNG file using pyoxipng.

    Args:
        file_path: Path to the PNG file to optimize
        level: Optimization level (0-6, default 6)
        preserve_file: If True, keeps the original file; if False, overwrites it

    Returns:
        Optimized PNG data as bytes
    """

    try:
        # Read the original file
        with open(file_path, "rb") as f:
            original_data = f.read()

        # Optimize the PNG data
        optimized_data = oxipng.optimize_from_memory(
            original_data,
            level=level,
            strip=oxipng.StripChunks.safe(),
            interlace=None,  # Keep existing interlacing
            optimize_alpha=True,
            fast_evaluation=False,
        )

        original_size = len(original_data)
        optimized_size = len(optimized_data)
        reduction_pct = 100 * (1 - optimized_size / original_size)

        logger.debug(f"PNG optimization: {original_size} -> {optimized_size} bytes ({reduction_pct:.1f}% reduction)")

        # Write back if not preserving original
        if not preserve_file:
            with open(file_path, "wb") as f:
                f.write(optimized_data)

        return optimized_data

    except Exception as e:
        logger.error(f"Failed to optimize PNG: {e}")
        with open(file_path, "rb") as f:
            return f.read()


def downsample_png_data(
    png_data: bytes,
    scale_factor: float = 0.5,
) -> bytes:
    """Downsample PNG data by a given scale factor.

    Args:
        png_data: Raw PNG data
        scale_factor: Scale factor (0.5 = 50% size)

    Returns:
        Downsampled PNG data as bytes
    """
    import io

    try:
        # Load image from bytes
        img = Image.open(io.BytesIO(png_data))

        # Calculate new dimensions
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)

        # Resize with high-quality resampling
        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save to bytes
        output = io.BytesIO()
        resized.save(output, format="PNG", optimize=True)
        output.seek(0)

        return output.read()

    except Exception as e:
        logger.error(f"Failed to downsample PNG: {e}")
        return png_data


def compress_html_content(html: str) -> str:
    """Compress HTML content by removing SVG elements and other optimizations.

    Args:
        html: Raw HTML content

    Returns:
        Compressed HTML content
    """
    import re

    # Remove SVG content but keep placeholder
    def replace_svg(match):
        svg_tag = match.group(0)
        # Extract width and height if present
        width_match = re.search(r'width=["\']([\d.]+)["\']', svg_tag)
        height_match = re.search(r'height=["\']([\d.]+)["\']', svg_tag)

        attrs = []
        if width_match:
            attrs.append(f'width="{width_match.group(1)}"')
        if height_match:
            attrs.append(f'height="{height_match.group(1)}"')

        attr_str = " " + " ".join(attrs) if attrs else ""
        return f"<svg{attr_str}></svg>"

    # Replace SVG elements
    html = re.sub(r"<svg[^>]*>.*?</svg>", replace_svg, html, flags=re.DOTALL | re.IGNORECASE)

    # Remove comments
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)

    # Remove excessive whitespace
    html = re.sub(r"\s+", " ", html)
    html = re.sub(r">\s+<", "><", html)

    # Remove inline styles if they're too long
    html = re.sub(r'style="[^"]{500,}"', 'style=""', html)

    # Remove data URIs
    html = re.sub(r'src="data:[^"]{100,}"', 'src=""', html)
    html = re.sub(r'href="data:[^"]{100,}"', 'href=""', html)

    return html.strip()


def calculate_result_size(result: dict) -> int:
    """Calculate the serialized size of a result dictionary.

    Args:
        result: Dictionary to calculate size for

    Returns:
        Size in bytes
    """
    import json

    try:
        # Serialize to JSON to get actual size
        json_str = json.dumps(result, ensure_ascii=False)
        return len(json_str.encode("utf-8"))
    except Exception as e:
        logger.error(f"Failed to calculate result size: {e}")
        return 0
