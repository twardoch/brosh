#!/usr/bin/env python3
# this_file: src/brosh/texthtml.py

"""HTML and text processing utilities for brosh."""

import re
from typing import Optional, Tuple

import html2text
from loguru import logger

# JavaScript constants extracted from capture.py
GET_VISIBLE_HTML_JS = """() => {
    const {innerHeight: H, innerWidth: W} = window;
    const nodes = [...document.querySelectorAll('*')];
    const fullyVisibleElements = [];

    const excludeTags = ['HTML', 'HEAD', 'BODY', 'SCRIPT', 'STYLE', 'META', 'LINK', 'TITLE'];

    nodes.forEach(node => {
        if (excludeTags.includes(node.tagName) || node.nodeType !== 1) {
            return;
        }

        const r = node.getBoundingClientRect();
        if (r.top >= 0 && r.bottom <= H && r.left >= 0 && r.right <= W && r.width > 0 && r.height > 0) {
            let isContained = false;
            for (const existing of fullyVisibleElements) {
                if (existing.contains(node)) {
                    isContained = true;
                    break;
                }
            }
            if (!isContained) {
                const filtered = fullyVisibleElements.filter(el => !node.contains(el));
                fullyVisibleElements.length = 0;
                fullyVisibleElements.push(...filtered, node);
            }
        }
    });

    const htmlParts = fullyVisibleElements.map(el => el.outerHTML);
    return htmlParts.join('').replace(/\\s+/g, ' ').trim();
}"""

GET_SECTION_ID_JS = """() => {
    const viewportHeight = window.innerHeight;
    const headers = Array.from(
        document.querySelectorAll('h1, h2, h3, h4, h5, h6, [id]')
    );

    for (const header of headers) {
        const rect = header.getBoundingClientRect();
        if (rect.top >= 0 && rect.top < viewportHeight / 2) {
            return (header.id || header.textContent || '').trim()
                .toLowerCase()
                .replace(/[^a-z0-9]+/g, '-')
                .replace(/^-+|-+$/g, '')
                .substring(0, 20);
        }
    }
    return 'section';
}"""

GET_ACTIVE_SELECTOR_JS = """() => {
    const {innerHeight: H} = window;

    const candidates = [
        'main', 'article', '[role="main"]', '.content', '#content',
        'section:first-of-type', 'div.container'
    ];

    for (const sel of candidates) {
        const el = document.querySelector(sel);
        if (el) {
            const r = el.getBoundingClientRect();
            if (r.top < H && r.bottom > 0) {
                return sel;
            }
        }
    }

    const sections = [...document.querySelectorAll('section, div')];
    for (const section of sections) {
        const r = section.getBoundingClientRect();
        if (r.top >= 0 && r.top < H/2) {
            if (section.id) return '#' + section.id;
            if (section.className) {
                const classes = section.className.split(' ').filter(c => c);
                if (classes.length) return '.' + classes.join('.');
            }
        }
    }

    return 'body';
}"""


class DOMProcessor:
    """Handles DOM querying and content extraction.

    Used in:
    - capture.py
    - mcp.py
    - tool.py
    """

    def __init__(self):
        """Initialize DOM processor with html2text converter."""
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.body_width = 0  # Don't wrap lines

    async def extract_visible_content(self, page) -> tuple[str, str, str]:
        """Extract visible HTML, text and active selector.

        Args:
            page: Playwright page instance

        Returns:
            Tuple of (visible_html, visible_text, active_selector)

        Used in:
        - capture.py
        """
        try:
            visible_html = await page.evaluate(GET_VISIBLE_HTML_JS)
            visible_text = self.html_to_markdown(visible_html)
            active_selector = await page.evaluate(GET_ACTIVE_SELECTOR_JS)
            return visible_html, visible_text, active_selector
        except Exception as e:
            logger.error(f"Failed to extract content: {e}")
            return "", "", "body"

    async def get_section_id(self, page) -> str:
        """Get semantic section identifier for current viewport.

        Args:
            page: Playwright page instance

        Returns:
            Section identifier string

        Used in:
        - capture.py
        """
        try:
            return await page.evaluate(GET_SECTION_ID_JS)
        except Exception:
            return "section"

    def html_to_markdown(self, html: str) -> str:
        """Convert HTML to markdown text.

        Args:
            html: Raw HTML string

        Returns:
            Markdown formatted text

        """
        return self.html_converter.handle(html).strip()

    @staticmethod
    def compress_html(html: str) -> str:
        """Compress HTML by removing non-essential content.

        Args:
            html: Raw HTML content

        Returns:
            Compressed HTML
        """

        # Remove SVG content but keep dimensions
        def replace_svg(match):
            svg_tag = match.group(0)
            width_match = re.search(r'width=["\']([\d.]+)["\']', svg_tag)
            height_match = re.search(r'height=["\']([\d.]+)["\']', svg_tag)

            attrs = []
            if width_match:
                attrs.append(f'width="{width_match.group(1)}"')
            if height_match:
                attrs.append(f'height="{height_match.group(1)}"')

            attr_str = " " + " ".join(attrs) if attrs else ""
            return f"<svg{attr_str}></svg>"

        html = re.sub(r"<svg[^>]*>.*?</svg>", replace_svg, html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
        html = re.sub(r"\s+", " ", html)
        html = re.sub(r">\s+<", "><", html)
        html = re.sub(r'style="[^"]{500,}"', 'style=""', html)
        html = re.sub(r'src="data:[^"]{100,}"', 'src=""', html)
        html = re.sub(r'href="data:[^"]{100,}"', 'href=""', html)

        return html.strip()
