#!/usr/bin/env python3
# this_file: src/brosh/image.py

"""Image processing utilities for brosh."""

import io

from loguru import logger
from PIL import Image

try:
    import oxipng

    HAS_OXIPNG = True
except ImportError:
    HAS_OXIPNG = False


class ImageProcessor:
    """Handles all image manipulation operations in memory.

    Used in:
    - mcp.py
    - tool.py
    """

    @staticmethod
    def optimize_png_bytes(png_bytes: bytes, level: int = 6) -> bytes:
        """Optimize PNG data in memory using pyoxipng.

        Args:
            png_bytes: Raw PNG data
            level: Optimization level (0-6)

        Returns:
            Optimized PNG bytes
        """
        if not HAS_OXIPNG:
            return png_bytes  # Return original if oxipng not available

        try:
            return oxipng.optimize_from_memory(
                png_bytes,
                level=level,
                strip=oxipng.StripChunks.safe(),
                optimize_alpha=True,
            )
        except Exception as e:
            logger.error(f"Failed to optimize PNG: {e}")
            return png_bytes  # Return original on failure

    @staticmethod
    def downsample_png_bytes(png_bytes: bytes, scale: int) -> bytes:
        """Scale PNG data without writing to disk.

        Args:
            png_bytes: Raw PNG data
            scale: Scale percentage (e.g., 50 for 50%)

        Returns:
            Scaled PNG bytes
        """
        try:
            img = Image.open(io.BytesIO(png_bytes))
            new_width = int(img.width * scale / 100)
            new_height = int(img.height * scale / 100)
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            output = io.BytesIO()
            resized.save(output, format="PNG", optimize=True)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Failed to downsample PNG: {e}")
            return png_bytes  # Return original on failure

    @staticmethod
    def convert_png_to_jpg_bytes(png_bytes: bytes, quality: int = 85) -> bytes:
        """Convert PNG to JPG in memory.

        Args:
            png_bytes: Raw PNG data
            quality: JPEG quality (1-100)

        Returns:
            JPEG bytes
        """
        try:
            img = Image.open(io.BytesIO(png_bytes))

            # Handle transparency
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                if img.mode == "RGBA":
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background

            output = io.BytesIO()
            img.save(output, format="JPEG", quality=quality)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Failed to convert PNG to JPG: {e}")
            return png_bytes  # Return original on failure

    @staticmethod
    def create_apng_bytes(frame_bytes_list: list[bytes], delay_ms: int = 500) -> bytes:
        """Create APNG animation from frame bytes.

        Args:
            frame_bytes_list: List of PNG frame data
            delay_ms: Delay between frames in milliseconds

        Returns:
            APNG animation bytes
        """
        try:
            images = []
            for frame_bytes in frame_bytes_list:
                img = Image.open(io.BytesIO(frame_bytes))
                images.append(img)

            output = io.BytesIO()
            if images:
                images[0].save(output, format="PNG", save_all=True, append_images=images[1:], duration=delay_ms, loop=0)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Failed to create APNG: {e}")
            raise
