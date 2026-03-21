#!/usr/bin/env python3
"""render.py — Shared rendering engine for the content-engine.

Converts HTML templates + brand assets into production-ready images (PNG/JPG/PDF).
Uses Playwright headless Chromium for pixel-perfect rendering with web fonts.

Usage:
    # Render a template with brand data
    python3 render.py --template social-card \
      --data '{"headline":"AI is changing everything","pillar":"ai_product"}' \
      --brand ces --size 1080x1080 --output /tmp/card.png

    # Render raw HTML
    python3 render.py --input /path/to/file.html \
      --size 1200x630 --output /tmp/screenshot.png

    # Screenshot a live URL
    python3 render.py --url https://example.com \
      --size 1200x630 --output /tmp/screenshot.png

Output (stdout): JSON with output path, width, height.
Errors go to stderr.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from string import Template

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"

# Pillar name -> accent color mapping
PILLAR_COLORS = {
    "ai_product": "#b8a06a",
    "leadership": "#8fab8a",
    "sustainability": "#d4b0a8",
    "consciousness": "#c4b8cc",
}

# Default brand values (Ces) used when brand dir is unavailable
DEFAULT_BRAND = {
    "bg_color": "#f7f4ef",
    "bg_secondary": "#f0ece4",
    "text_color": "#3a352e",
    "text_secondary": "#7a7268",
    "text_muted": "#b0a898",
    "accent_color": "#b8a06a",
    "font_headline": "'Playfair Display', Georgia, 'Times New Roman', serif",
    "font_body": "'DM Sans', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif",
    "brand_handle": "@agentces",
}


def parse_brand_colors(brand_dir):
    """Parse brand-colors.md into a color map."""
    colors_file = Path(brand_dir) / "brand-colors.md"
    if not colors_file.is_file():
        return {}

    text = colors_file.read_text()
    colors = {}

    # Extract hex codes from markdown tables: | Label | `#hexcode` | ...
    for match in re.finditer(
        r"\|\s*([^|]+?)\s*\|\s*`?(#[0-9a-fA-F]{6})`?\s*\|", text
    ):
        label = match.group(1).strip().lower()
        hex_val = match.group(2)

        if "ivory" in label and "primary" in label:
            colors.setdefault("bg_color", hex_val)
        elif "warm linen" in label or "secondary" in label and "background" in label:
            colors.setdefault("bg_secondary", hex_val)
        elif "card" in label:
            colors.setdefault("bg_card", hex_val)
        elif "warm charcoal" in label or "primary" in label:
            colors.setdefault("text_color", hex_val)
        elif "secondary" in label and "7a" in hex_val:
            colors.setdefault("text_secondary", hex_val)
        elif "muted" in label or "caption" in label:
            colors.setdefault("text_muted", hex_val)
        elif "gold" in label:
            colors.setdefault("accent_gold", hex_val)
        elif "sage" in label:
            colors.setdefault("accent_sage", hex_val)
        elif "blush" in label:
            colors.setdefault("accent_blush", hex_val)
        elif "lavender" in label:
            colors.setdefault("accent_lavender", hex_val)

    return colors


def parse_brand_fonts(brand_dir):
    """Parse brand-typography.md for font families."""
    typo_file = Path(brand_dir) / "brand-typography.md"
    if not typo_file.is_file():
        return {}

    text = typo_file.read_text()
    fonts = {}

    # Look for fallback stack patterns: `'Font Name', fallback, ...`
    headline_match = re.search(
        r"Fallback stack\s*\|\s*`([^`]+)`", text
    )
    if headline_match:
        fonts["font_headline"] = headline_match.group(1)

    # Find body font (second fallback stack)
    body_section = text.split("### Body", 1)
    if len(body_section) > 1:
        body_match = re.search(
            r"Fallback stack\s*\|\s*`([^`]+)`", body_section[1]
        )
        if body_match:
            fonts["font_body"] = body_match.group(1)

    return fonts


def parse_brand_handle(brand_dir):
    """Extract brand handle from brand-kit.md or brand-voice.md."""
    for filename in ("brand-voice.md", "brand-kit.md"):
        filepath = Path(brand_dir) / filename
        if not filepath.is_file():
            continue
        text = filepath.read_text()
        match = re.search(r"@\w+", text)
        if match:
            return match.group(0)
    return None


def resolve_brand(brand_name):
    """Resolve brand directory and load brand variables."""
    brand_vars = dict(DEFAULT_BRAND)

    # Try to find brand dir
    brand_dir = None
    cwd_brand = Path.cwd() / "brands" / brand_name
    if cwd_brand.is_dir():
        brand_dir = str(cwd_brand)

    if brand_dir is None:
        plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
        if plugin_root:
            fallback = Path(plugin_root) / "skills" / "distribute" / "references"
            if fallback.is_dir():
                brand_dir = str(fallback)

    if brand_dir is None:
        print(
            f"Warning: Brand directory '{brand_name}' not found, using defaults",
            file=sys.stderr,
        )
        return brand_vars

    # Parse and merge
    colors = parse_brand_colors(brand_dir)
    fonts = parse_brand_fonts(brand_dir)
    handle = parse_brand_handle(brand_dir)

    brand_vars.update(colors)
    brand_vars.update(fonts)
    if handle:
        brand_vars["brand_handle"] = handle

    return brand_vars


def resolve_accent_color(brand_vars, pillar):
    """Set accent_color based on pillar name."""
    if pillar and pillar in PILLAR_COLORS:
        brand_vars["accent_color"] = PILLAR_COLORS[pillar]
    elif pillar:
        # Try accent_<pillar> from parsed brand colors
        key = f"accent_{pillar}"
        if key in brand_vars:
            brand_vars["accent_color"] = brand_vars[key]
    return brand_vars


def load_template(template_name, brand_vars, data):
    """Load an HTML template and substitute variables."""
    template_file = TEMPLATES_DIR / f"{template_name}.html"
    if not template_file.is_file():
        print(
            f"Error: Template '{template_name}' not found at {template_file}",
            file=sys.stderr,
        )
        sys.exit(1)

    html = template_file.read_text()

    # Merge brand vars and user data (user data takes precedence)
    all_vars = dict(brand_vars)
    all_vars.update(data)

    # Use safe_substitute so missing keys don't crash
    return Template(html).safe_substitute(all_vars)


def parse_size(size_str):
    """Parse 'WxH' into (width, height)."""
    match = re.match(r"(\d+)x(\d+)", size_str)
    if not match:
        print(
            f"Error: Size must be WxH (e.g., 1080x1080), got '{size_str}'",
            file=sys.stderr,
        )
        sys.exit(1)
    return int(match.group(1)), int(match.group(2))


def render(html_content=None, url=None, width=1080, height=1080,
           output_path="/tmp/render-output.png", fmt="png", scale=2):
    """Render HTML or URL to an image file using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Error: Playwright not installed. Run: pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    output_path = str(Path(output_path).resolve())
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=scale,
        )

        if url:
            page.goto(url, wait_until="networkidle")
        elif html_content:
            page.set_content(html_content, wait_until="networkidle")
        else:
            print("Error: No content to render", file=sys.stderr)
            browser.close()
            sys.exit(1)

        # Wait for web fonts to load
        page.evaluate("() => document.fonts.ready")

        if fmt == "pdf":
            page.pdf(
                path=output_path,
                width=f"{width}px",
                height=f"{height}px",
                print_background=True,
            )
        else:
            screenshot_type = "jpeg" if fmt in ("jpg", "jpeg") else "png"
            page.screenshot(
                path=output_path,
                full_page=False,
                type=screenshot_type,
                quality=90 if screenshot_type == "jpeg" else None,
            )

        browser.close()

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Render HTML templates to images using Playwright"
    )

    # Input source (mutually exclusive)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--template", help="Template name (e.g., social-card)")
    source.add_argument("--input", help="Path to HTML file to render")
    source.add_argument("--url", help="URL to screenshot")

    # Template data
    parser.add_argument(
        "--data", default="{}",
        help="JSON string with template variables"
    )
    parser.add_argument(
        "--brand", default="ces",
        help="Brand name for asset resolution (default: ces)"
    )

    # Output
    parser.add_argument(
        "--size", default="1080x1080",
        help="Output dimensions WxH (default: 1080x1080)"
    )
    parser.add_argument(
        "--format", default="png", choices=["png", "jpg", "jpeg", "pdf"],
        help="Output format (default: png)"
    )
    parser.add_argument(
        "--output", default="/tmp/render-output.png",
        help="Output file path"
    )
    parser.add_argument(
        "--scale", type=int, default=2,
        help="Device scale factor for retina output (default: 2)"
    )

    # Location (for init.py compatibility)
    parser.add_argument("--location", help="Location shorthand (ignored, for compatibility)")

    args = parser.parse_args()

    width, height = parse_size(args.size)

    # Parse user data
    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in --data: {e}", file=sys.stderr)
        sys.exit(1)

    # Resolve brand
    brand_vars = resolve_brand(args.brand)

    # Set accent color from pillar if provided
    pillar = data.get("pillar", "")
    brand_vars = resolve_accent_color(brand_vars, pillar)

    # Determine HTML content
    html_content = None
    url = None

    if args.template:
        html_content = load_template(args.template, brand_vars, data)
    elif args.input:
        input_path = Path(args.input)
        if not input_path.is_file():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        html_content = input_path.read_text()
    elif args.url:
        url = args.url

    # Render
    output_path = render(
        html_content=html_content,
        url=url,
        width=width,
        height=height,
        output_path=args.output,
        fmt=args.format,
        scale=args.scale,
    )

    # Output JSON result
    result = {
        "output": output_path,
        "width": width,
        "height": height,
        "format": args.format,
        "scale": args.scale,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
