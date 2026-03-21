#!/usr/bin/env python3
"""Resize an image to 4:5 portrait (1080x1350) with ivory padding.
Usage: python3 resize_to_4x5.py input.png [output.png]
If output is omitted, overwrites the input file.
"""
import sys
from PIL import Image

IVORY = (247, 244, 239)  # #f7f4ef
TARGET_W, TARGET_H = 1080, 1350

def resize_to_4x5(input_path, output_path=None):
    if output_path is None:
        output_path = input_path

    img = Image.open(input_path)
    orig_w, orig_h = img.size

    # Already correct size
    if orig_w == TARGET_W and orig_h == TARGET_H:
        print(f"Already {TARGET_W}x{TARGET_H}, skipping: {input_path}")
        return

    # Scale to fit within target, maintaining aspect ratio
    scale_w = TARGET_W / orig_w
    scale_h = TARGET_H / orig_h
    scale = min(scale_w, scale_h)

    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    img_resized = img.resize((new_w, new_h), Image.LANCZOS)

    # Create ivory canvas and center the image
    canvas = Image.new("RGB", (TARGET_W, TARGET_H), IVORY)
    x_offset = (TARGET_W - new_w) // 2
    y_offset = (TARGET_H - new_h) // 2

    if img_resized.mode == "RGBA":
        canvas.paste(img_resized, (x_offset, y_offset), img_resized)
    else:
        canvas.paste(img_resized, (x_offset, y_offset))

    canvas.save(output_path, "PNG")
    print(f"Resized: {orig_w}x{orig_h} -> {TARGET_W}x{TARGET_H} ({output_path})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 resize_to_4x5.py input.png [output.png]", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    resize_to_4x5(input_file, output_file)
