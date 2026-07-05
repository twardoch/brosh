"""Tests for brosh.mcp result conversion and size limiting (no browser needed)."""

import json

from PIL import Image

from brosh.mcp import (
    MCP_MAX_SIZE_BYTES,
    _apply_size_limits,
    _convert_to_mcp_result,
)
from brosh.models import ImageFormat, MCPImageContent, MCPTextContent, MCPToolResult


def _write_png(path, color=(10, 20, 30)) -> str:
    img = Image.new("RGB", (20, 20), color)
    img.save(path, format="PNG")
    return str(path)


class TestConvertToMcpResult:
    def test_text_only_when_image_disabled(self, tmp_path) -> None:
        filepath = _write_png(tmp_path / "a.png")
        capture = {filepath: {"selector": "main", "text": "hello world", "html": "<p>x</p>"}}
        result = _convert_to_mcp_result(
            capture, ImageFormat.PNG, fetch_image=False, fetch_image_path=True, fetch_text=True, fetch_html=False
        )
        assert all(isinstance(item, MCPTextContent) for item in result.content)
        meta = json.loads(result.content[0].text)
        assert meta["image_path"] == filepath
        assert meta["selector"] == "main"
        assert meta["text"] == "hello world"

    def test_image_included_when_requested(self, tmp_path) -> None:
        filepath = _write_png(tmp_path / "b.png")
        capture = {filepath: {"selector": "body", "text": "t"}}
        result = _convert_to_mcp_result(
            capture, ImageFormat.PNG, fetch_image=True, fetch_image_path=False, fetch_text=True, fetch_html=False
        )
        assert any(isinstance(item, MCPImageContent) for item in result.content)

    def test_text_trimmed_to_limit(self, tmp_path) -> None:
        filepath = _write_png(tmp_path / "c.png")
        capture = {filepath: {"selector": "body", "text": "x" * 500}}
        result = _convert_to_mcp_result(
            capture, ImageFormat.PNG, fetch_image=False, fetch_image_path=False, fetch_text=True, trim_text=True
        )
        meta = json.loads(result.content[0].text)
        assert meta["text"].endswith("...")
        assert len(meta["text"]) < 250

    def test_missing_file_is_skipped_gracefully(self) -> None:
        """A path that cannot be read must not crash conversion."""
        capture = {"/does/not/exist.png": {"selector": "body", "text": "t"}}
        result = _convert_to_mcp_result(capture, ImageFormat.PNG, fetch_image=True, fetch_text=True)
        # The image read fails, but the text metadata block is still produced.
        assert isinstance(result, MCPToolResult)


class TestApplySizeLimits:
    def test_small_result_passes_through(self) -> None:
        result = MCPToolResult(content=[MCPTextContent(text="small")])
        assert _apply_size_limits(result) is result

    def test_oversized_text_is_trimmed_down(self) -> None:
        """A payload above the byte cap gets its trailing items dropped."""
        big = "y" * (MCP_MAX_SIZE_BYTES + 1000)
        items = [MCPTextContent(text=json.dumps({f"/p{i}.png": {"text": big}})) for i in range(4)]
        limited = _apply_size_limits(MCPToolResult(content=items))
        size = len(json.dumps(limited.model_dump()).encode("utf-8"))
        assert size <= MCP_MAX_SIZE_BYTES or len(limited.content) < len(items)


class TestMcpModelSerialization:
    def test_image_content_uses_camelcase_alias(self) -> None:
        dumped = MCPImageContent(data="abc", mime_type="image/png").model_dump()
        assert dumped["mimeType"] == "image/png"

    def test_tool_result_serializes_nested_items(self) -> None:
        result = MCPToolResult(content=[MCPTextContent(text="hi")])
        dumped = result.model_dump()
        assert dumped["content"][0]["text"] == "hi"
