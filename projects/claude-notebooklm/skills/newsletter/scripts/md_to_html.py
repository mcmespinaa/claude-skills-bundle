#!/usr/bin/env python3
"""md_to_html.py — Convert markdown to branded inline-CSS HTML email.

Usage:
    python3 md_to_html.py input.md > output.html
    python3 md_to_html.py --stdin < content.md > output.html
    echo "# Hello" | python3 md_to_html.py --stdin

Email clients strip <style> blocks, so all CSS is applied as inline
style="" attributes using <table> layout for maximum compatibility.

Brand colors:
    Background: #f7f4ef (ivory)
    Text:       #3a352e (warm charcoal)
    Accent:     #b8a06a (gold)
    Link:       #b8a06a (gold)
"""

import re
import sys
import html as html_lib

# ---------------------------------------------------------------------------
# Brand styles (inline CSS)
# ---------------------------------------------------------------------------

STYLES = {
    "body_bg": "background-color: #f7f4ef;",
    "container": (
        "max-width: 600px; margin: 0 auto; padding: 32px 24px; "
        "background-color: #ffffff; border-radius: 8px;"
    ),
    "h1": (
        "font-family: Georgia, 'Times New Roman', serif; "
        "font-size: 28px; line-height: 1.3; color: #3a352e; "
        "margin: 0 0 16px 0; padding: 0;"
    ),
    "h2": (
        "font-family: Georgia, 'Times New Roman', serif; "
        "font-size: 22px; line-height: 1.3; color: #3a352e; "
        "margin: 24px 0 12px 0; padding: 0; "
        "border-bottom: 2px solid #b8a06a; padding-bottom: 6px;"
    ),
    "h3": (
        "font-family: Georgia, 'Times New Roman', serif; "
        "font-size: 18px; line-height: 1.3; color: #3a352e; "
        "margin: 20px 0 8px 0; padding: 0;"
    ),
    "p": (
        "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
        "'Helvetica Neue', Arial, sans-serif; "
        "font-size: 16px; line-height: 1.6; color: #3a352e; "
        "margin: 0 0 16px 0; padding: 0;"
    ),
    "a": "color: #b8a06a; text-decoration: underline;",
    "strong": "font-weight: 700; color: #3a352e;",
    "em": "font-style: italic;",
    "ul": (
        "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
        "'Helvetica Neue', Arial, sans-serif; "
        "font-size: 16px; line-height: 1.6; color: #3a352e; "
        "margin: 0 0 16px 0; padding: 0 0 0 24px;"
    ),
    "ol": (
        "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
        "'Helvetica Neue', Arial, sans-serif; "
        "font-size: 16px; line-height: 1.6; color: #3a352e; "
        "margin: 0 0 16px 0; padding: 0 0 0 24px;"
    ),
    "li": "margin: 0 0 6px 0;",
    "blockquote": (
        "border-left: 4px solid #b8a06a; margin: 0 0 16px 0; "
        "padding: 12px 16px; background-color: #f7f4ef; "
        "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
        "'Helvetica Neue', Arial, sans-serif; "
        "font-size: 16px; line-height: 1.6; color: #3a352e; "
        "font-style: italic;"
    ),
    "hr": (
        "border: none; border-top: 2px solid #b8a06a; "
        "margin: 24px 0; padding: 0;"
    ),
    "img": "max-width: 100%; height: auto; border-radius: 4px; margin: 0 0 16px 0;",
    "footer": (
        "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
        "'Helvetica Neue', Arial, sans-serif; "
        "font-size: 12px; line-height: 1.5; color: #999999; "
        "text-align: center; margin: 24px 0 0 0; padding: 16px 0 0 0; "
        "border-top: 1px solid #eeeeee;"
    ),
}

# ---------------------------------------------------------------------------
# Markdown → HTML conversion (no external dependencies)
# ---------------------------------------------------------------------------

def escape(text: str) -> str:
    """HTML-escape text."""
    return html_lib.escape(text, quote=True)


def convert_inline(text: str) -> str:
    """Convert inline markdown: bold, italic, links, images, code."""
    # Images: ![alt](url)
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: f'<img src="{escape(m.group(2))}" alt="{escape(m.group(1))}" style="{STYLES["img"]}" />',
        text,
    )
    # Links: [text](url)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{escape(m.group(2))}" style="{STYLES["a"]}">{m.group(1)}</a>',
        text,
    )
    # Bold: **text** or __text__
    text = re.sub(
        r"\*\*(.+?)\*\*|__(.+?)__",
        lambda m: f'<strong style="{STYLES["strong"]}">{m.group(1) or m.group(2)}</strong>',
        text,
    )
    # Italic: *text* or _text_
    text = re.sub(
        r"\*(.+?)\*|(?<!\w)_(.+?)_(?!\w)",
        lambda m: f'<em style="{STYLES["em"]}">{m.group(1) or m.group(2)}</em>',
        text,
    )
    # Inline code: `code`
    text = re.sub(
        r"`([^`]+)`",
        lambda m: f'<code style="background-color: #f0ede8; padding: 2px 6px; border-radius: 3px; font-size: 14px;">{escape(m.group(1))}</code>',
        text,
    )
    return text


def md_to_html(markdown: str) -> str:
    """Convert markdown string to inline-CSS HTML email body."""
    lines = markdown.split("\n")
    html_parts = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            html_parts.append(f'<hr style="{STYLES["hr"]}" />')
            i += 1
            continue

        # Headings
        heading_match = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading_match:
            level = len(heading_match.group(1))
            text = convert_inline(heading_match.group(2))
            tag = f"h{level}"
            html_parts.append(f'<{tag} style="{STYLES[tag]}">{text}</{tag}>')
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip().lstrip("> ").strip())
                i += 1
            text = convert_inline("<br>".join(quote_lines))
            html_parts.append(f'<blockquote style="{STYLES["blockquote"]}">{text}</blockquote>')
            continue

        # Unordered list
        if re.match(r"^[-*+]\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*+]\s+", lines[i]):
                item_text = re.sub(r"^\s*[-*+]\s+", "", lines[i]).strip()
                items.append(f'<li style="{STYLES["li"]}">{convert_inline(item_text)}</li>')
                i += 1
            html_parts.append(f'<ul style="{STYLES["ul"]}">{"".join(items)}</ul>')
            continue

        # Ordered list
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                item_text = re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip()
                items.append(f'<li style="{STYLES["li"]}">{convert_inline(item_text)}</li>')
                i += 1
            html_parts.append(f'<ol style="{STYLES["ol"]}">{"".join(items)}</ol>')
            continue

        # Paragraph (collect consecutive non-empty, non-special lines)
        para_lines = []
        while i < len(lines):
            current = lines[i].strip()
            if not current:
                i += 1
                break
            if re.match(r"^(#{1,3}\s|[-*+]\s|\d+\.\s|>|(-{3,}|\*{3,}|_{3,})$)", current):
                break
            para_lines.append(current)
            i += 1
        text = convert_inline(" ".join(para_lines))
        html_parts.append(f'<p style="{STYLES["p"]}">{text}</p>')

    return "\n".join(html_parts)


def wrap_email(body_html: str) -> str:
    """Wrap HTML body in a complete email document with table layout."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Newsletter</title>
</head>
<body style="margin: 0; padding: 0; {STYLES['body_bg']}">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin: 0; padding: 0; {STYLES['body_bg']}">
  <tr>
    <td align="center" style="padding: 24px 16px;">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="{STYLES['container']}">
        <tr>
          <td>
{body_html}
          </td>
        </tr>
      </table>
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td style="{STYLES['footer']}">
            You received this email because you subscribed to our newsletter.<br />
            If you no longer wish to receive these emails, please reply with "unsubscribe".
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</body>
</html>"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--stdin":
        markdown = sys.stdin.read()
    elif len(sys.argv) > 1 and sys.argv[1] != "--help":
        filepath = sys.argv[1]
        try:
            with open(filepath) as f:
                markdown = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: python3 md_to_html.py <input.md>", file=sys.stderr)
        print("       python3 md_to_html.py --stdin", file=sys.stderr)
        sys.exit(1)

    body = md_to_html(markdown)
    print(wrap_email(body))


if __name__ == "__main__":
    main()
