---
name: render
description: Renders branded images from HTML templates using Playwright headless Chromium. Produces social cards, OG images, carousel slides, email previews, and YouTube thumbnails with pixel-perfect web fonts. Also rebrands third-party exports. Use when user says /render, render a social card, generate OG image, rebrand this image, screenshot this URL, or similar. Called by other skills (/post, /blog, /newsletter) for template-based visuals.
allowed-tools: "Bash(python3:*) Bash(bash:*) Read Write Edit Glob Grep"
---

# /render — Visual Rendering Engine

> **Do NOT use for:** Creative/illustrative images (use Gemini via the image-gen agent), or full post creation and scheduling (use /post). Requires Playwright installed.

Renders branded images from HTML templates using Playwright headless Chromium.

## Scripts

| Script | Purpose |
|--------|---------|
| `render.py` | Core engine: template + data -> PNG/JPG/PDF |
| `rebrand.py` | Remove third-party branding, inject brand assets |

Both scripts live in `${CLAUDE_SKILL_DIR}/../../shared/scripts/`.

## Templates

Templates live in `${CLAUDE_SKILL_DIR}/../../shared/scripts/templates/`.

| Template | Default Size | Used By |
|----------|-------------|---------|
| `social-card` | 1080x1080 | /post (text-heavy single images) |
| `og-image` | 1200x630 | /blog (featured images, Open Graph) |
| `carousel-slide` | 1080x1350 | /post (text-heavy carousel slides) |
| `email-preview` | 600x400 | /newsletter (preview cards) |
| `thumbnail` | 1280x720 | /yt-search, /post (YouTube thumbnails) |
| `base` | any | Shared layout shell (extended by other templates) |

## When to Use /render vs Gemini Image Gen

| Need | Use |
|------|-----|
| Text-heavy slide with exact typography | `/render` (Playwright) |
| Infographic with icons and illustrations | Gemini 3.1 Flash Image |
| Brand-consistent OG image or social card | `/render` (Playwright) |
| Creative visual, photo-realistic, abstract | Gemini 3.1 Flash Image |
| Rebrand a third-party export | `/render` (rebrand.py) |
| YouTube thumbnail with readable text | `/render` (Playwright) |

**Rule of thumb:** If text accuracy matters, use `/render`. If visual creativity matters, use Gemini.

## Usage

### Render a social card
```bash
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/render.py \
  --template social-card \
  --data '{"headline":"AI is transforming leadership","body":"Here is what changed","pillar":"ai_product","eyebrow":"AI + Product"}' \
  --size 1080x1080 \
  --output /tmp/social-card.png
```

### Render a blog OG image
```bash
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/render.py \
  --template og-image \
  --data '{"headline":"5 Lessons From Building an AI Startup","subtitle":"What nobody tells you about shipping AI products","category":"AI + Product","eyebrow":"Blog","pillar":"ai_product"}' \
  --size 1200x630 \
  --output /tmp/og-image.png
```

### Render carousel slides
```bash
# Hook slide
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/render.py \
  --template carousel-slide \
  --data '{"headline":"Stop doing this with AI","body":"Most founders waste 80% of their AI budget","slide_type":"hook","display_hook":"flex","display_value":"none","display_cta":"none","avatar_initial":"C","pillar":"ai_product"}' \
  --size 1080x1350 \
  --output /tmp/slide-01.png

# Value slide
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/render.py \
  --template carousel-slide \
  --data '{"headline":"Start with the problem","body":"Before choosing an AI model, map every manual step in your workflow.","slide_type":"value","display_hook":"none","display_value":"flex","display_cta":"none","step_number":"1","total":"5","pillar":"ai_product"}' \
  --size 1080x1350 \
  --output /tmp/slide-02.png

# CTA slide
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/render.py \
  --template carousel-slide \
  --data '{"headline":"Ready to build smarter?","body":"Follow for weekly AI product insights","slide_type":"cta","display_hook":"none","display_value":"none","display_cta":"flex","cta_text":"Follow","avatar_initial":"C","pillar":"ai_product"}' \
  --size 1080x1350 \
  --output /tmp/slide-06.png
```

### Render email preview
```bash
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/render.py \
  --template email-preview \
  --data '{"eyebrow":"Newsletter","headline":"3 AI tools we tested this week","body":"We tried 12 tools so you do not have to. Here are the 3 that actually worked.","cta_text":"Read More","sender_name":"Maria Cecilia Espina"}' \
  --size 600x400 \
  --output /tmp/email-preview.png
```

### Render YouTube thumbnail
```bash
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/render.py \
  --template thumbnail \
  --data '{"eyebrow":"AI Tools","title_line_1":"I Tested 12 AI Tools","title_line_2":"So You Don'\''t Have To","badge":"2026","pillar":"ai_product"}' \
  --size 1280x720 \
  --output /tmp/thumbnail.png
```

### Rebrand a third-party export
```bash
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/rebrand.py \
  --input /path/to/export.html \
  --remove ".logo, .watermark" \
  --inject-handle "@agentces" \
  --handle-position bottom-center \
  --size 1080x1350 \
  --output /tmp/rebranded.png
```

### Rebrand a raster image
```bash
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/rebrand.py \
  --input /path/to/infographic.png \
  --inject-handle "@agentces" \
  --handle-position bottom-center \
  --size 1080x1350 \
  --output /tmp/rebranded.png
```

### Screenshot a live URL
```bash
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/render.py \
  --url https://myblog.com/latest-post \
  --size 1200x630 \
  --output /tmp/screenshot.png
```

## Template Variables

All templates auto-resolve brand variables from `${CLAUDE_SKILL_DIR}/../../shared/references/brand-visuals.md`:

| Variable | Default | Example |
|----------|---------|---------|
| `$bg_color` | `#f7f4ef` | Ivory background |
| `$bg_secondary` | `#f0ece4` | Warm Linen |
| `$text_color` | `#3a352e` | Warm Charcoal |
| `$text_secondary` | `#7a7268` | Secondary text |
| `$text_muted` | `#b0a898` | Muted/caption text |
| `$accent_color` | `#b8a06a` | Resolved from `pillar` |
| `$font_headline` | Playfair Display | Serif headline |
| `$font_body` | DM Sans | Sans body |
| `$brand_handle` | `@agentces` | Brand handle |

Plus template-specific variables passed via `--data` JSON.

## Pillar -> Accent Color

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
pip install playwright && playwright install chromium
```

Also requires Pillow for `rebrand.py` image mode:
```bash
pip install Pillow
```

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| Playwright not installed | Missing dependency | Run `pip install playwright && playwright install chromium` |
| Template not found | Wrong template name | Check available templates in `shared/scripts/templates/` |
| Fonts not loading | Network issue | Templates load Google Fonts; requires internet access |
| Blurry output | Low scale factor | Use `--scale 2` (default) for retina quality |
| Input file not found | Wrong path | Check file exists before passing to `--input` |

## Integration with Other Skills

| Skill | How It Uses /render |
|-------|---------------------|
| `/post` | Carousel slides when text accuracy matters (alternative to Gemini) |
| `/blog` | OG image generation (1200x630 featured images) |
| `/newsletter` | Email preview card for social sharing |
| `/yt-search` | YouTube thumbnail generation (1280x720) |
| `/research` | Rebrand NotebookLM exports with brand handle |
