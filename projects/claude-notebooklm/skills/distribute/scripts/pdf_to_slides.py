#!/usr/bin/env python3
"""pdf_to_slides.py — Convert a PDF to numbered PNG slides (4:5 portrait, 1080x1350).

Uses pypdfium2 (Google PDFium) to render each page, then resizes/pads to
1080x1350 with ivory background (#f7f4ef) matching resize_to_4x5.py logic.

Usage:
  python3 pdf_to_slides.py --input slides.pdf --output-dir ./slides_out
  python3 pdf_to_slides.py --input slides.pdf --output-dir ./slides_out --scale 3
  python3 pdf_to_slides.py --input slides.pdf --output-dir ./slides_out --max-slides 10

Output (stdout): JSON with output directory, file count, and list of absolute paths.
Errors go to stderr with exit code 1.
"""

import argparse
import json
import os
import sys

IVORY = (247, 244, 239)  # #f7f4ef — matches resize_to_4x5.py
TARGET_W, TARGET_H = 1080, 1350
DEFAULT_SCALE = 2  # 144 DPI (72 * 2)
DEFAULT_MAX_SLIDES = 10  # Instagram/Facebook cap via GHL


def resize_and_pad(pil_img):
    """Resize a PIL Image to fit 1080x1350 with ivory padding.

    Mirrors the logic in resize_to_4x5.py but operates on an in-memory
    PIL Image instead of a file path.
    """
    from PIL import Image

    orig_w, orig_h = pil_img.size

    if pil_img.mode not in ("RGB", "RGBA"):
        pil_img = pil_img.convert("RGB")

    scale_w = TARGET_W / orig_w
    scale_h = TARGET_H / orig_h
    scale = min(scale_w, scale_h)

    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    img_resized = pil_img.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGB", (TARGET_W, TARGET_H), IVORY)
    x_offset = (TARGET_W - new_w) // 2
    y_offset = (TARGET_H - new_h) // 2

    if img_resized.mode == "RGBA":
        canvas.paste(img_resized, (x_offset, y_offset), img_resized)
    else:
        canvas.paste(img_resized, (x_offset, y_offset))

    return canvas


def pdf_to_slides(pdf_path, output_dir, scale=DEFAULT_SCALE, max_slides=DEFAULT_MAX_SLIDES):
    """Render each page of a PDF to a padded 1080x1350 PNG."""
    try:
        import pypdfium2 as pdfium
    except ImportError:
        print("Error: pypdfium2 is not installed. Run: pip3 install pypdfium2", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(pdf_path):
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    doc = pdfium.PdfDocument(pdf_path)
    total_pages = len(doc)

    if total_pages == 0:
        print(f"Error: PDF has no pages: {pdf_path}", file=sys.stderr)
        doc.close()
        sys.exit(1)

    render_count = total_pages
    if total_pages > max_slides:
        print(
            f"Warning: PDF has {total_pages} pages, limiting to {max_slides} (--max-slides).",
            file=sys.stderr,
        )
        render_count = max_slides

    output_paths = []
    stem = os.path.splitext(os.path.basename(pdf_path))[0]

    for i, page in enumerate(doc):
        if i >= render_count:
            page.close()
            break

        bitmap = page.render(scale=scale, fill_color=(255, 255, 255, 255))
        pil_img = bitmap.to_pil()

        padded = resize_and_pad(pil_img)

        filename = f"{stem}-slide-{i + 1:02d}.png"
        out_path = os.path.join(output_dir, filename)
        padded.save(out_path, "PNG")

        output_paths.append(os.path.abspath(out_path))

        bitmap.close()
        page.close()

        print(f"  Rendered slide {i + 1}/{render_count}", file=sys.stderr)

    doc.close()
    return output_paths


def main():
    parser = argparse.ArgumentParser(
        description="Convert a PDF to 1080x1350 PNG slides for carousel posting."
    )
    parser.add_argument("--input", required=True, help="Path to the input PDF file")
    parser.add_argument("--output-dir", required=True, help="Directory to write PNG files into")
    parser.add_argument(
        "--scale",
        type=float,
        default=DEFAULT_SCALE,
        help=f"Render scale factor (default: {DEFAULT_SCALE} = 144 DPI). Use 3 for sharper output.",
    )
    parser.add_argument(
        "--max-slides",
        type=int,
        default=DEFAULT_MAX_SLIDES,
        help=f"Max slides to extract (default: {DEFAULT_MAX_SLIDES}). IG/FB carousel cap is 10.",
    )
    args = parser.parse_args()

    paths = pdf_to_slides(
        pdf_path=args.input,
        output_dir=args.output_dir,
        scale=args.scale,
        max_slides=args.max_slides,
    )

    output = {
        "input": os.path.abspath(args.input),
        "output_dir": os.path.abspath(args.output_dir),
        "slide_count": len(paths),
        "slides": paths,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
