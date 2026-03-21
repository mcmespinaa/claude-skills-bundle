#!/usr/bin/env python3
"""md_to_blog_html.py — Convert markdown to clean semantic HTML for GHL blog posts.

Usage:
    python3 md_to_blog_html.py input.md > output.html
    python3 md_to_blog_html.py --stdin < content.md > output.html
    echo "# Hello" | python3 md_to_blog_html.py --stdin

Unlike the email converter (md_to_html.py), this produces semantic HTML without
inline styles — the GHL blog theme handles styling. Output uses standard HTML5
tags: <h2>, <h3>, <p>, <ul>, <ol>, <blockquote>, <a>, <img>, <code>, <pre>.

External links get rel="noopener noreferrer" and target="_blank".
Images get loading="lazy" for performance.
"""

import re
import sys
import html as html_lib


def md_to_blog_html(md: str) -> str:
    """Convert markdown text to semantic blog HTML."""
    lines = md.strip().split("\n")
    html_lines: list[str] = []
    in_code_block = False
    code_lang = ""
    code_lines: list[str] = []
    in_list = ""  # "ul" or "ol" or ""
    list_lines: list[str] = []

    def flush_list():
        nonlocal in_list, list_lines
        if in_list and list_lines:
            tag = in_list
            items = "\n".join(f"  <li>{item}</li>" for item in list_lines)
            html_lines.append(f"<{tag}>\n{items}\n</{tag}>")
            list_lines = []
            in_list = ""

    def flush_code():
        nonlocal in_code_block, code_lines, code_lang
        if in_code_block and code_lines:
            content = html_lib.escape("\n".join(code_lines))
            lang_attr = f' class="language-{code_lang}"' if code_lang else ""
            html_lines.append(f"<pre><code{lang_attr}>{content}</code></pre>")
            code_lines = []
            in_code_block = False
            code_lang = ""

    def process_inline(text: str) -> str:
        """Process inline markdown: bold, italic, code, links, images."""
        # Images: ![alt](url)
        text = re.sub(
            r"!\[([^\]]*)\]\(([^)]+)\)",
            r'<img src="\2" alt="\1" loading="lazy">',
            text,
        )
        # Links: [text](url)
        def replace_link(m):
            link_text = m.group(1)
            url = m.group(2)
            if url.startswith(("http://", "https://")):
                return f'<a href="{url}" rel="noopener noreferrer" target="_blank">{link_text}</a>'
            return f'<a href="{url}">{link_text}</a>'

        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, text)
        # Inline code: `code`
        text = re.sub(
            r"`([^`]+)`",
            lambda m: f"<code>{html_lib.escape(m.group(1))}</code>",
            text,
        )
        # Bold: **text** or __text__
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
        # Italic: *text* or _text_
        text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
        text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<em>\1</em>", text)
        return text

    for line in lines:
        # Code blocks
        if line.startswith("```"):
            if in_code_block:
                flush_code()
            else:
                flush_list()
                in_code_block = True
                code_lang = line[3:].strip()
                code_lines = []
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        stripped = line.strip()

        # Empty line
        if not stripped:
            flush_list()
            continue

        # Headings
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading_match:
            flush_list()
            level = len(heading_match.group(1))
            text = process_inline(html_lib.escape(heading_match.group(2)))
            # Generate an id for deep linking
            slug = re.sub(r"[^a-z0-9]+", "-", heading_match.group(2).lower()).strip("-")
            html_lines.append(f'<h{level} id="{slug}">{text}</h{level}>')
            continue

        # Horizontal rule
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            flush_list()
            html_lines.append("<hr>")
            continue

        # Blockquote
        if stripped.startswith("> "):
            flush_list()
            quote_text = process_inline(html_lib.escape(stripped[2:]))
            html_lines.append(f"<blockquote><p>{quote_text}</p></blockquote>")
            continue

        # Unordered list
        ul_match = re.match(r"^[-*+]\s+(.+)$", stripped)
        if ul_match:
            if in_list and in_list != "ul":
                flush_list()
            in_list = "ul"
            list_lines.append(process_inline(html_lib.escape(ul_match.group(1))))
            continue

        # Ordered list
        ol_match = re.match(r"^\d+\.\s+(.+)$", stripped)
        if ol_match:
            if in_list and in_list != "ol":
                flush_list()
            in_list = "ol"
            list_lines.append(process_inline(html_lib.escape(ol_match.group(1))))
            continue

        # Regular paragraph
        flush_list()
        text = process_inline(html_lib.escape(stripped))
        html_lines.append(f"<p>{text}</p>")

    # Flush remaining
    flush_list()
    flush_code()

    return "\n".join(html_lines)


def main():
    if "--stdin" in sys.argv:
        md = sys.stdin.read()
    elif len(sys.argv) > 1 and sys.argv[1] != "--stdin":
        filepath = sys.argv[1]
        try:
            with open(filepath) as f:
                md = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: md_to_blog_html.py <input.md> | --stdin", file=sys.stderr)
        sys.exit(1)

    html_output = md_to_blog_html(md)
    print(html_output)


if __name__ == "__main__":
    main()
