#!/usr/bin/env python3
# this_file: src/brosh/image.py

"""Image processing utilities for brosh."""

from pathlib import Path

from loguru import logger
from PIL import Image

from .optimize import optimize_png_file


class ImageProcessor:
    """Handles image processing operations."""

    @staticmethod
    def scale_image(filepath: Path, scale: int) -> None:
        """Scale the image by the given percentage.

        Args:
            filepath: Path to the image file
            scale: Scale percentage (100 = no scaling)

        """
        try:
            img = Image.open(filepath)
            new_width = int(img.width * scale / 100)
            new_height = int(img.height * scale / 100)
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            resized.save(filepath)
        except Exception as e:
            logger.error(f"Failed to scale image {filepath}: {e}")

    @staticmethod
    def convert_to_jpg(png_path: Path) -> Path:
        """Convert PNG to JPG format.

        Args:
            png_path: Path to PNG file

        Returns:
            Path to JPG file

        """
        try:
            jpg_path = png_path.with_suffix(".jpg")
            img = Image.open(png_path)

            # Convert RGBA to RGB for JPG
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background

            img.save(jpg_path, "JPEG", quality=90)
            png_path.unlink()  # Remove original PNG
            return jpg_path
        except Exception as e:
            logger.error(f"Failed to convert {png_path} to JPG: {e}")
            return png_path  # Return original if conversion fails

    @staticmethod
    def optimize_png(png_path: Path) -> None:
        """Optimize a PNG file in-place.

        Args:
            png_path: Path to PNG file to optimize
        """
        try:
            # Optimize the PNG file, overwriting the original
            optimize_png_file(png_path, level=6, preserve_file=False)
            logger.debug(f"Optimized PNG: {png_path}")
        except Exception as e:
            logger.error(f"Failed to optimize PNG {png_path}: {e}")

    @staticmethod
    def create_apng(
        png_paths: list[Path],
        domain: str,
        output_path: Path,
        anim_spf: float,
    ) -> Path:
        """Create an animated PNG from a list of PNG files.

        Args:
            png_paths: List of PNG file paths to combine
            domain: Domain name for output filename
            output_path: Output directory
            anim_spf: Seconds per frame

        Returns:
            Path to created APNG file

        """
        apng_path = output_path / f"{domain}-animated.png"

        try:
            # Load all images
            images = []
            for png_path in png_paths:
                img = Image.open(png_path)
                images.append(img)

            # Convert seconds per frame to milliseconds
            duration_ms = int(anim_spf * 1000)

            # Save as animated PNG
            if images:
                images[0].save(
                    apng_path,
                    format="PNG",
                    save_all=True,
                    append_images=images[1:],
                    duration=duration_ms,
                    loop=0,  # Infinite loop
                )
        except Exception as e:
            logger.error(f"Failed to create APNG: {e}")
            raise

        return apng_path
