"""Tests for brosh.image — in-memory image processing (no browser needed)."""

import io

from PIL import Image

from brosh.image import ImageProcessor


def _png_bytes(size: tuple[int, int] = (40, 30), mode: str = "RGB", color: tuple = (200, 100, 50)) -> bytes:
    """Build a small PNG in memory for testing."""
    img = Image.new(mode, size, color if mode != "RGBA" else (*color, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestOptimizePng:
    def test_optimize_returns_valid_png(self) -> None:
        """Optimized output is still a decodable PNG of the same size."""
        original = _png_bytes()
        result = ImageProcessor.optimize_png_bytes(original)
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"
        assert img.size == (40, 30)

    def test_optimize_bad_bytes_returns_input(self) -> None:
        """On failure the original bytes come back untouched, never an exception."""
        garbage = b"not a png"
        assert ImageProcessor.optimize_png_bytes(garbage) == garbage


class TestDownsamplePng:
    def test_downsample_halves_dimensions(self) -> None:
        result = ImageProcessor.downsample_png_bytes(_png_bytes((100, 80)), scale=50)
        img = Image.open(io.BytesIO(result))
        assert img.size == (50, 40)

    def test_downsample_bad_bytes_returns_input(self) -> None:
        garbage = b"broken"
        assert ImageProcessor.downsample_png_bytes(garbage, scale=50) == garbage


class TestConvertToJpg:
    def test_rgb_png_becomes_jpeg(self) -> None:
        result = ImageProcessor.convert_png_to_jpg_bytes(_png_bytes())
        assert Image.open(io.BytesIO(result)).format == "JPEG"

    def test_rgba_transparency_flattened_to_jpeg(self) -> None:
        """RGBA is composited onto white before JPEG encoding (JPEG has no alpha)."""
        result = ImageProcessor.convert_png_to_jpg_bytes(_png_bytes(mode="RGBA"))
        img = Image.open(io.BytesIO(result))
        assert img.format == "JPEG"
        assert img.mode == "RGB"

    def test_palette_png_becomes_jpeg(self) -> None:
        result = ImageProcessor.convert_png_to_jpg_bytes(_png_bytes(mode="P"))
        assert Image.open(io.BytesIO(result)).format == "JPEG"

    def test_bad_bytes_returns_input(self) -> None:
        garbage = b"nope"
        assert ImageProcessor.convert_png_to_jpg_bytes(garbage) == garbage


class TestCreateApng:
    def test_multiple_frames_produce_animated_png(self) -> None:
        frames = [_png_bytes(color=(255, 0, 0)), _png_bytes(color=(0, 255, 0))]
        result = ImageProcessor.create_apng_bytes(frames, delay_ms=200)
        img = Image.open(io.BytesIO(result))
        assert img.format == "PNG"
        assert getattr(img, "n_frames", 1) == 2

    def test_empty_frame_list_returns_empty_bytes(self) -> None:
        assert ImageProcessor.create_apng_bytes([]) == b""
