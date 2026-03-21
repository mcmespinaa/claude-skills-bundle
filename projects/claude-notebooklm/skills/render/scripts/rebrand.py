#!/usr/bin/env python3
"""rebrand.py — Remove third-party branding and inject brand assets.

Takes an HTML file or image, removes specified elements (NotebookLM watermarks,
logos) via CSS selectors, and optionally injects brand handle/logo.

For HTML inputs: uses Playwright to manipulate DOM and screenshot.
For image inputs: uses PIL for compositing (no CSS selector removal).

Usage:
    # Rebrand an HTML export
    python3 rebrand.py \
      --input /path/to/notebooklm-export.html \
      --remove ".notebooklm-logo, .watermark" \
      --inject-handle "@agentces" \
      --handle-position bottom-center \
      --brand ces \
      --size 1080x1350 \
      --output /tmp/rebranded.png

    # Rebrand a raster image (overlay handle only)
    python3 rebrand.py \
      --input /path/to/infographic.png \
      --inject-handle "@agentces" \
      --handle-position bottom-center \
      --size 1080x1350 \
      --output /tmp/rebranded.png

Output (stdout): JSON with output path, width, height.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Import brand resolution from render.py (same directory)
sys.path.insert(0, str(SCRIPT_DIR))
from render import resolve_brand, resolve_accent_color, parse_size


POSITION_CSS = {
    "top-left": "top: 40px; left: 40px;",
    "top-right": "top: 40px; right: 40px;",
    "top-center": "top: 40px; left: 50%; transform: translateX(-50%);",
    "bottom-left": "bottom: 40px; left: 40px;",
    "bottom-right": "bottom: 40px; right: 40px;",
    "bottom-center": "bottom: 40px; left: 50%; transform: translateX(-50%);",
    "center": "top: 50%; left: 50%; transform: translate(-50%, -50%);",
}


def is_image_file(filepath):
    """Check if file is a raster image (not HTML)."""
    ext = Path(filepath).suffix.lower()
    return ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")


def rebrand_html(input_path, remove_selectors, inject_handle, handle_position,
                 inject_logo, logo_position, logo_size, brand_vars,
                 width, height, output_path, scale=2):
    """Rebrand an HTML file using Playwright DOM manipulation."""
    from playwright.sync_api import sync_playwright

    html_content = Path(input_path).read_text()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=scale,
        )

        page.set_content(html_content, wait_until="networkidle")

        # Remove elements by CSS selector
        if remove_selectors:
            for selector in remove_selectors.split(","):
                selector = selector.strip()
                if selector:
                    page.evaluate(
                        f"document.querySelectorAll('{selector}').forEach(el => el.remove())"
                    )

        # Inject brand handle
        if inject_handle:
            pos_css = POSITION_CSS.get(handle_position, POSITION_CSS["bottom-center"])
            handle_color = brand_vars.get("text_muted", "#b0a898")
            font_body = brand_vars.get("font_body", "sans-serif")
            page.evaluate(f"""(() => {{
                const el = document.createElement('div');
                el.textContent = '{inject_handle}';
                el.style.cssText = 'position: absolute; {pos_css} font-family: {font_body}; font-size: 13px; color: {handle_color}; z-index: 999; letter-spacing: 0;';
                document.body.appendChild(el);
            }})()""")

        # Inject logo image
        if inject_logo and Path(inject_logo).is_file():
            logo_pos_css = POSITION_CSS.get(logo_position, POSITION_CSS["top-right"])
            # Read logo as base64
            import base64
            logo_data = base64.b64encode(Path(inject_logo).read_bytes()).decode()
            logo_ext = Path(inject_logo).suffix.lower().lstrip(".")
            if logo_ext == "jpg":
                logo_ext = "jpeg"
            page.evaluate(f"""(() => {{
                const img = document.createElement('img');
                img.src = 'data:image/{logo_ext};base64,{logo_data}';
                img.style.cssText = 'position: absolute; {logo_pos_css} max-width: {logo_size}px; max-height: {logo_size}px; z-index: 999;';
                document.body.appendChild(img);
            }})()""")

        # Wait for any injected fonts/images
        page.evaluate("() => document.fonts.ready")

        page.screenshot(path=output_path, full_page=False, type="png")
        browser.close()

    return output_path


def rebrand_image(input_path, inject_handle, handle_position,
                  inject_logo, logo_position, logo_size,
                  width, height, output_path):
    """Rebrand a raster image using PIL compositing."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Error: Pillow not installed. Run: pip install Pillow", file=sys.stderr)
        sys.exit(1)

    img = Image.open(input_path).convert("RGBA")

    # Resize to target dimensions with padding (same as resize_to_4x5.py logic)
    target_ratio = width / height
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        new_w = width
        new_h = int(width / img_ratio)
    else:
        new_h = height
        new_w = int(height * img_ratio)

    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Create padded canvas with ivory background
    canvas = Image.new("RGBA", (width, height), (247, 244, 239, 255))
    offset_x = (width - new_w) // 2
    offset_y = (height - new_h) // 2
    canvas.paste(img, (offset_x, offset_y), img if img.mode == "RGBA" else None)

    # Inject handle text
    if inject_handle:
        draw = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
        except (OSError, IOError):
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), inject_handle, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        pos_map = {
            "bottom-center": ((width - text_w) // 2, height - 80),
            "bottom-left": (80, height - 80),
            "bottom-right": (width - text_w - 80, height - 80),
            "top-center": ((width - text_w) // 2, 60),
            "top-left": (80, 60),
            "top-right": (width - text_w - 80, 60),
            "center": ((width - text_w) // 2, (height - text_h) // 2),
        }
        pos = pos_map.get(handle_position, pos_map["bottom-center"])
        draw.text(pos, inject_handle, fill=(176, 168, 152, 255), font=font)

    # Inject logo
    if inject_logo and Path(inject_logo).is_file():
        logo = Image.open(inject_logo).convert("RGBA")
        # Scale logo to fit within logo_size
        ratio = min(logo_size / logo.width, logo_size / logo.height)
        logo = logo.resize(
            (int(logo.width * ratio), int(logo.height * ratio)), Image.LANCZOS
        )

        logo_pos_map = {
            "top-left": (40, 40),
            "top-right": (width - logo.width - 40, 40),
            "top-center": ((width - logo.width) // 2, 40),
            "bottom-left": (40, height - logo.height - 40),
            "bottom-right": (width - logo.width - 40, height - logo.height - 40),
            "bottom-center": ((width - logo.width) // 2, height - logo.height - 40),
            "center": ((width - logo.width) // 2, (height - logo.height) // 2),
        }
        lpos = logo_pos_map.get(logo_position, logo_pos_map["top-right"])
        canvas.paste(logo, lpos, logo)

    # Save as RGB PNG
    canvas.convert("RGB").save(output_path, "PNG")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Remove third-party branding and inject brand assets"
    )
    parser.add_argument("--input", required=True, help="Path to HTML file or image")
    parser.add_argument("--remove", default="", help="CSS selectors to remove (comma-separated)")
    parser.add_argument("--inject-handle", default="", help="Brand handle text to inject")
    parser.add_argument("--handle-position", default="bottom-center",
                        choices=list(POSITION_CSS.keys()),
                        help="Position for handle text")
    parser.add_argument("--inject-logo", default="", help="Path to logo image to inject")
    parser.add_argument("--logo-position", default="top-right",
                        choices=list(POSITION_CSS.keys()),
                        help="Position for logo")
    parser.add_argument("--logo-size", type=int, default=120,
                        help="Max dimension for logo in px (default: 120)")
    parser.add_argument("--brand", default="ces", help="Brand name")
    parser.add_argument("--size", default="1080x1350", help="Output dimensions WxH")
    parser.add_argument("--output", default="/tmp/rebranded.png", help="Output file path")
    parser.add_argument("--scale", type=int, default=2, help="Device scale factor")
    parser.add_argument("--location", help="Location shorthand (for compatibility)")

    args = parser.parse_args()

    if not Path(args.input).is_file():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    width, height = parse_size(args.size)
    brand_vars = resolve_brand(args.brand)

    if is_image_file(args.input):
        if args.remove:
            print(
                "Warning: CSS selector removal not supported for image inputs",
                file=sys.stderr,
            )
        output_path = rebrand_image(
            input_path=args.input,
            inject_handle=args.inject_handle,
            handle_position=args.handle_position,
            inject_logo=args.inject_logo,
            logo_position=args.logo_position,
            logo_size=args.logo_size,
            width=width, height=height,
            output_path=args.output,
        )
    else:
        output_path = rebrand_html(
            input_path=args.input,
            remove_selectors=args.remove,
            inject_handle=args.inject_handle,
            handle_position=args.handle_position,
            inject_logo=args.inject_logo,
            logo_position=args.logo_position,
            logo_size=args.logo_size,
            brand_vars=brand_vars,
            width=width, height=height,
            output_path=args.output,
            scale=args.scale,
        )

    result = {"output": str(output_path), "width": width, "height": height}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
