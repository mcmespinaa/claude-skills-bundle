---
name: render
description: >
  Shared rendering engine that converts HTML templates + brand assets into
  production-ready images (PNG, JPG, PDF). Renders social cards, OG images,
  carousel slides, email previews, and YouTube thumbnails using Playwright
  headless Chromium. Called by other skills (/distribute, /linkedin, /blog,
  /newsletter) or invoked directly.
argument-hint: --template social-card --data '{"headline":"..."}' --brand ces --size 1080x1080
user-invocable: true
disable-model-invocation: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
model: claude-sonnet-4-6
---

# /render — Visual Rendering Engine

Renders branded images from HTML templates using Playwright headless Chromium.

## Scripts

| Script | Purpose |
|--------|---------|
| `render.py` | Core engine: template + brand -> PNG/JPG/PDF |
| `rebrand.py` | Remove third-party branding, inject brand assets |

## Templates

| Template | Default Size | Used By |
|----------|-------------|---------|
| `social-card` | 1080x1080 | /linkedin, /distribute |
| `og-image` | 1200x630 | /blog |
| `carousel-slide` | 1080x1350 | /linkedin, /distribute |
| `email-preview` | 600x400 | /newsletter |
| `thumbnail` | 1280x720 | /distribute (YouTube) |

## Usage

### Render a social card
```bash
python3 "$RENDER_SCRIPTS/render.py" \
  --template social-card \
  --data '{"headline":"AI is transforming leadership","body":"Here is what changed","pillar":"ai_product","eyebrow":"AI + Product"}' \
  --brand ces \
  --size 1080x1080 \
  --output /tmp/social-card.png
```

### Render a blog OG image
```bash
python3 "$RENDER_SCRIPTS/render.py" \
  --template og-image \
  --data '{"headline":"5 Lessons From Building an AI Startup","subtitle":"What nobody tells you about shipping AI products","category":"AI + Product","eyebrow":"Blog","pillar":"ai_product"}' \
  --brand ces \
  --size 1200x630 \
  --output /tmp/og-image.png
```

### Render carousel slides
```bash
# Hook slide
python3 "$RENDER_SCRIPTS/render.py" \
  --template carousel-slide \
  --data '{"headline":"Stop doing this with AI","body":"Most founders waste 80% of their AI budget","slide_type":"hook","display_hook":"flex","display_value":"none","display_cta":"none","avatar_initial":"C","pillar":"ai_product"}' \
  --brand ces \
  --size 1080x1350 \
  --output /tmp/slide-01.png

# Value slide
python3 "$RENDER_SCRIPTS/render.py" \
  --template carousel-slide \
  --data '{"headline":"Start with the problem","body":"Before choosing an AI model, map every manual step in your workflow. The bottleneck is never where you think it is.","slide_type":"value","display_hook":"none","display_value":"flex","display_cta":"none","step_number":"1","total":"5","pillar":"ai_product"}' \
  --brand ces \
  --size 1080x1350 \
  --output /tmp/slide-02.png

# CTA slide
python3 "$RENDER_SCRIPTS/render.py" \
  --template carousel-slide \
  --data '{"headline":"Ready to build smarter?","body":"Follow for weekly AI product insights","slide_type":"cta","display_hook":"none","display_value":"none","display_cta":"flex","cta_text":"Follow","avatar_initial":"C","pillar":"ai_product"}' \
  --brand ces \
  --size 1080x1350 \
  --output /tmp/slide-06.png
```

### Rebrand a NotebookLM export
```bash
python3 "$RENDER_SCRIPTS/rebrand.py" \
  --input /path/to/notebooklm-export.html \
  --remove ".notebooklm-logo, .watermark" \
  --inject-handle "@agentces" \
  --handle-position bottom-center \
  --brand ces \
  --size 1080x1350 \
  --output /tmp/rebranded.png
```

### Rebrand a raster image
```bash
python3 "$RENDER_SCRIPTS/rebrand.py" \
  --input /path/to/infographic.png \
  --inject-handle "@agentces" \
  --handle-position bottom-center \
  --size 1080x1350 \
  --output /tmp/rebranded.png
```

### Screenshot a live URL
```bash
python3 "$RENDER_SCRIPTS/render.py" \
  --url https://myblog.com/latest-post \
  --size 1200x630 \
  --output /tmp/screenshot.png
```

## Template Variables

All templates accept these brand variables (auto-resolved from brand dir):

| Variable | Source | Example |
|----------|--------|---------|
| `$bg_color` | brand-colors.md | `#f7f4ef` |
| `$bg_secondary` | brand-colors.md | `#f0ece4` |
| `$text_color` | brand-colors.md | `#3a352e` |
| `$text_secondary` | brand-colors.md | `#7a7268` |
| `$text_muted` | brand-colors.md | `#b0a898` |
| `$accent_color` | Resolved from `pillar` | `#b8a06a` |
| `$font_headline` | brand-typography.md | `'Playfair Display', Georgia, serif` |
| `$font_body` | brand-typography.md | `'DM Sans', sans-serif` |
| `$brand_handle` | brand-voice.md | `@agentces` |

Plus template-specific variables passed via `--data` JSON.

## Pillar -> Accent Color Mapping

| Pillar Key | Color | Hex |
|-----------|-------|-----|
| `ai_product` | Gold | `#b8a06a` |
| `leadership` | Sage | `#8fab8a` |
| `sustainability` | Blush | `#d4b0a8` |
| `consciousness` | Lavender | `#c4b8cc` |

## Output

Both scripts output JSON to stdout:
```json
{"output": "/tmp/card.png", "width": 1080, "height": 1080, "format": "png", "scale": 2}
```

## Setup

Requires Playwright Chromium (one-time):
```bash
playwright install chromium
```
