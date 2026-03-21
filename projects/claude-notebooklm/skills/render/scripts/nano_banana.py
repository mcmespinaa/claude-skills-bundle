#!/usr/bin/env python3
"""nano_banana.py — AI image generation using Google Nano Banana 2 (Gemini 3.1 Flash Image).

Generates and edits images from text prompts via the Gemini API.
Used by /render, /linkedin, /blog, /distribute, /newsletter for
branded visual content generation.

Usage:
    # Generate an image from a text prompt
    python3 nano_banana.py --prompt "minimalist social card, ivory background, gold accent" \
      --aspect-ratio 1:1 --size 1K --output /tmp/social-card.png

    # Generate with brand context
    python3 nano_banana.py --prompt "hero image for AI leadership blog post" \
      --brand ces --aspect-ratio 16:9 --output /tmp/hero.png

    # Edit an existing image
    python3 nano_banana.py --prompt "remove the background and add a soft gradient" \
      --input /tmp/photo.png --output /tmp/edited.png

    # Generate multiple images (pick the best)
    python3 nano_banana.py --prompt "podcast cover art" --count 3 --output /tmp/covers/

Output (stdout): JSON with output path(s), dimensions, model used.
Errors go to stderr.

Requires:
    pip install google-genai
    GOOGLE_API_KEY in .env (or GEMINI_API_KEY)
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Models in preference order
MODELS = {
    "flash": "gemini-3.1-flash-image-preview",
    "pro": "gemini-3-pro-image-preview",
    "legacy": "gemini-2.5-flash-image",
}

VALID_ASPECT_RATIOS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4",
    "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
]

VALID_SIZES = ["512", "1K", "2K", "4K"]

# Brand style prompts — appended to user prompt for consistency
BRAND_STYLE = {
    "ces": (
        "Nordic minimalist aesthetic. Warm ivory (#f7f4ef) background. "
        "Warm charcoal (#3a352e) text. Gold (#b8a06a) accent. "
        "Clean composition with generous white space. "
        "Elegant, premium feel. No clutter."
    ),
}


def _resolve_api_key():
    """Find the Gemini API key from environment."""
    # Load .env if available
    env_file = Path.cwd() / ".env"
    if env_file.is_file():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(
                    key.strip(), val.strip().strip('"').strip("'")
                )

    for var in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
        val = os.environ.get(var, "")
        if val:
            return val

    print(
        "Error: No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY in .env",
        file=sys.stderr,
    )
    sys.exit(1)


def _build_prompt(user_prompt, brand=None, edit_mode=False):
    """Build the full prompt with optional brand context."""
    parts = []

    if brand and brand in BRAND_STYLE:
        parts.append(f"Style context: {BRAND_STYLE[brand]}")

    parts.append(user_prompt)

    if not edit_mode:
        parts.append(
            "Generate a high-quality, professional image. "
            "No watermarks, no text artifacts unless explicitly requested."
        )

    return " ".join(parts)


def generate_image(
    prompt,
    model_key="flash",
    aspect_ratio="1:1",
    image_size="1K",
    input_image_path=None,
    output_path="/tmp/nano-banana-output.png",
    brand=None,
):
    """Generate or edit an image using the Gemini API."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print(
            "Error: google-genai not installed. Run: pip install google-genai",
            file=sys.stderr,
        )
        sys.exit(1)

    api_key = _resolve_api_key()
    client = genai.Client(api_key=api_key)

    model = MODELS.get(model_key, MODELS["flash"])
    edit_mode = input_image_path is not None

    full_prompt = _build_prompt(prompt, brand=brand, edit_mode=edit_mode)

    # Build contents
    contents = []
    if edit_mode:
        input_path = Path(input_image_path)
        if not input_path.is_file():
            print(f"Error: Input image not found: {input_image_path}", file=sys.stderr)
            sys.exit(1)

        img_bytes = input_path.read_bytes()
        mime = "image/png" if input_path.suffix.lower() == ".png" else "image/jpeg"
        contents.append(
            types.Part.from_bytes(data=img_bytes, mime_type=mime)
        )

    contents.append(full_prompt)

    # Configure response
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=image_size,
        ),
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    if not response.candidates:
        print("Error: No image generated. The prompt may have been blocked.", file=sys.stderr)
        sys.exit(1)

    # Extract and save images
    output_path = Path(output_path).resolve()
    os.makedirs(output_path.parent, exist_ok=True)

    saved = []
    for i, part in enumerate(response.candidates[0].content.parts):
        if hasattr(part, "inline_data") and part.inline_data:
            if i == 0:
                save_path = output_path
            else:
                save_path = output_path.parent / f"{output_path.stem}_{i}{output_path.suffix}"

            save_path.write_bytes(part.inline_data.data)
            saved.append(str(save_path))

    if not saved:
        print("Error: Response contained no image data.", file=sys.stderr)
        sys.exit(1)

    return saved


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Google Nano Banana 2 (Gemini Image)"
    )

    parser.add_argument(
        "--prompt", required=True,
        help="Text prompt describing the image to generate",
    )
    parser.add_argument(
        "--input",
        help="Path to input image for editing (omit for text-to-image)",
    )
    parser.add_argument(
        "--brand", default=None,
        help="Brand name for style context (e.g., ces)",
    )
    parser.add_argument(
        "--model", default="flash", choices=list(MODELS.keys()),
        help="Model to use: flash (fast), pro (quality), legacy (default: flash)",
    )
    parser.add_argument(
        "--aspect-ratio", default="1:1", choices=VALID_ASPECT_RATIOS,
        help="Output aspect ratio (default: 1:1)",
    )
    parser.add_argument(
        "--size", default="1K", choices=VALID_SIZES,
        help="Output resolution (default: 1K)",
    )
    parser.add_argument(
        "--output", default="/tmp/nano-banana-output.png",
        help="Output file path (default: /tmp/nano-banana-output.png)",
    )
    parser.add_argument(
        "--count", type=int, default=1,
        help="Number of images to generate (default: 1)",
    )

    # Location (for init.py compatibility)
    parser.add_argument("--location", help="Location shorthand (for compatibility)")

    args = parser.parse_args()

    if args.aspect_ratio not in VALID_ASPECT_RATIOS:
        print(f"Error: Invalid aspect ratio. Choose from: {', '.join(VALID_ASPECT_RATIOS)}", file=sys.stderr)
        sys.exit(1)

    all_outputs = []
    for i in range(args.count):
        if args.count > 1:
            stem = Path(args.output).stem
            suffix = Path(args.output).suffix or ".png"
            out = str(Path(args.output).parent / f"{stem}_{i + 1}{suffix}")
        else:
            out = args.output

        saved = generate_image(
            prompt=args.prompt,
            model_key=args.model,
            aspect_ratio=args.aspect_ratio,
            image_size=args.size,
            input_image_path=args.input,
            output_path=out,
            brand=args.brand,
        )
        all_outputs.extend(saved)

    result = {
        "outputs": all_outputs,
        "count": len(all_outputs),
        "model": MODELS.get(args.model, MODELS["flash"]),
        "aspect_ratio": args.aspect_ratio,
        "size": args.size,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
