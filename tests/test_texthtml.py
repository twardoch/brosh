"""Tests for brosh.texthtml — pure HTML/text processing (no browser needed)."""

from brosh.texthtml import DOMProcessor


class TestHtmlToMarkdown:
    def test_headings_and_paragraphs(self) -> None:
        md = DOMProcessor().html_to_markdown("<h1>Title</h1><p>Body text</p>")
        assert "Title" in md
        assert "Body text" in md

    def test_links_are_kept(self) -> None:
        md = DOMProcessor().html_to_markdown('<a href="https://example.com">site</a>')
        assert "example.com" in md


class TestCompressHtml:
    def test_comments_removed(self) -> None:
        assert "secret" not in DOMProcessor.compress_html("<div><!-- secret --></div>")

    def test_whitespace_collapsed(self) -> None:
        out = DOMProcessor.compress_html("<p>a</p>   \n\n   <p>b</p>")
        assert "><" in out
        assert "  " not in out

    def test_svg_body_stripped_but_dimensions_kept(self) -> None:
        html = '<svg width="24" height="24"><path d="M0 0h24v24"/></svg>'
        out = DOMProcessor.compress_html(html)
        assert "path" not in out
        assert 'width="24"' in out
        assert 'height="24"' in out

    def test_long_data_uri_src_emptied(self) -> None:
        html = f'<img src="data:image/png;base64,{"A" * 200}">'
        out = DOMProcessor.compress_html(html)
        assert 'src=""' in out

    def test_plain_html_survives(self) -> None:
        out = DOMProcessor.compress_html("<main><h2>Hi</h2></main>")
        assert "<main>" in out
        assert "Hi" in out
