# /render Skill — Implementation Plan

## Purpose

A shared rendering engine that converts HTML templates + brand assets into production-ready images (PNG/JPG/PDF). One skill, many consumers. Every other skill that needs a visual artifact calls `/render` instead of rolling its own image pipeline.

**Why Playwright (not PIL/Pillow)?**
- PIL can resize and pad, but cannot render styled HTML, web fonts (Playfair Display, DM Sans), CSS gradients, or layered compositions
- The brand system is defined in CSS-friendly terms: hex colors, font families, border-radius, gradients
- HTML templates are the natural representation of branded slides, cards, and previews
- Playwright renders real browser output — pixel-perfect, font-accurate, retina-ready

**Why Python (not Node.js)?**
- Playwright Python module already installed (`from playwright.sync_api import sync_playwright`)
- All 9 existing scripts are Python; no `package.json` exists
- Shared `init.py` prelude provides brand/location resolution
- PIL/Pillow available for post-processing (crop, composite, format conversion)

---

## Architecture

```
content-engine/skills/render/
├── SKILL.md                    # Skill frontmatter + usage docs
├── scripts/
│   ├── render.py               # Core renderer (HTML -> screenshot -> export)
│   ├── rebrand.py              # Remove elements + inject brand assets
│   └── templates/
│       ├── base.html           # Shared layout shell (loads fonts, sets viewport)
│       ├── social-card.html    # LinkedIn/IG text+image posts
│       ├── og-image.html       # Blog Open Graph / featured image
│       ├── carousel-slide.html # Single carousel slide (hook/value/CTA variants)
│       ├── email-preview.html  # Newsletter preview card
│       ├── wireframe.html      # Web-design spec visualization
│       └── thumbnail.html      # YouTube thumbnail
└── references/
    └── dimensions.md           # Platform dimension reference
```

---

## Core Scripts

### 1. `render.py` — The Engine

**What it does:** Opens an HTML file (or injects content into a template), renders it in headless Chromium, screenshots at exact pixel dimensions, exports PNG/JPG/PDF.

**Interface:**
```bash
python3 render.py \
  --template social-card \       # Template name (looks in templates/)
  --data '{"headline":"...","body":"...","pillar":"ai_product"}' \  # JSON data for placeholders
  --brand ces \                  # Brand directory name (loads colors, fonts, logo)
  --size 1080x1080 \             # Output dimensions (WxH)
  --format png \                 # Output format: png, jpg, pdf
  --output /tmp/card.png         # Output path
  --location ces                 # For init.py context resolution
```

**Alternative: raw HTML input (no template):**
```bash
python3 render.py \
  --input /path/to/file.html \   # Render this HTML directly
  --size 1200x630 \
  --format png \
  --output /tmp/screenshot.png
```

**Alternative: URL input:**
```bash
python3 render.py \
  --url https://myblog.com/post-1 \  # Screenshot a live page
  --size 1200x630 \
  --clip "0,0,1200,630" \            # Optional: crop region (x,y,w,h)
  --output /tmp/screenshot.png
```

**Internal flow:**
1. Parse args (argparse)
2. If `--template`: load template HTML, read brand assets from `$BRAND_DIR`, inject data via `string.Template` (`$headline`, `$body`, `$accent_color`, etc.)
3. If `--input`: read HTML file as-is
4. If `--url`: navigate directly
5. Launch Playwright Chromium (headless)
6. Set viewport to `--size` dimensions
7. Load content (set_content or goto)
8. Wait for fonts to load (`document.fonts.ready`)
9. Screenshot (full_page=False, type=png/jpeg)
10. If `--format pdf`: use page.pdf() instead
11. Write to `--output`
12. Print JSON to stdout: `{"output": "/tmp/card.png", "width": 1080, "height": 1080}`

**Key design decisions:**
- **No Mustache/Jinja dependency.** Use Python `string.Template` (`$variable` syntax). Templates are plain HTML with `$headline`, `$body`, `$accent_color`, etc.
- **Brand injection:** Read `brand-colors.md` and `brand-typography.md` from `$BRAND_DIR`, parse hex codes and font names, inject as CSS custom properties into template.
- **Font loading:** Templates reference Google Fonts via `<link>` tags. Playwright loads them from the network. Fallback stacks (Georgia, Arial) ensure rendering even offline.
- **Retina output:** Use `device_scale_factor=2` for 2x resolution, then resize down to target dimensions. This gives crisp text on all platforms.
- **Stdout JSON:** Consistent with existing scripts (drive_upload.py, youtube_upload.py, pdf_to_slides.py).

### 2. `rebrand.py` — Logo Swap & Element Removal

**What it does:** Takes an existing HTML file or image, removes specified elements (NotebookLM watermarks, logos), and optionally injects brand assets.

**Interface:**
```bash
python3 rebrand.py \
  --input /path/to/notebooklm-export.html \
  --remove ".notebooklm-logo, .watermark, [data-brand='notebooklm']" \  # CSS selectors
  --inject-logo /path/to/logo.png \     # Optional: brand logo to add
  --logo-position bottom-right \         # top-left, top-right, bottom-left, bottom-right, center
  --logo-size 120 \                      # Max dimension in px
  --inject-handle "@agentces" \          # Optional: brand handle text
  --handle-position bottom-center \
  --brand ces \
  --size 1080x1350 \
  --output /tmp/rebranded.png
```

**Internal flow:**
1. Load HTML in Playwright
2. Execute JS to remove elements matching CSS selectors: `document.querySelectorAll(selector).forEach(el => el.remove())`
3. If `--inject-logo`: overlay logo image at specified position using CSS absolute positioning (inject a `<div>` with the logo)
4. If `--inject-handle`: add text element with brand typography
5. Screenshot at `--size` dimensions
6. Output to `--output`

**For image inputs (PNG/JPG, not HTML):**
- Fall back to PIL/Pillow for compositing
- Cannot remove CSS selectors from raster images (log warning)
- Can still overlay logo and handle text on raster images

### 3. Templates

Each template is a self-contained HTML file with CSS custom properties and `$variable` placeholders.

**Common variables injected into all templates:**
```
$bg_color          — Brand background (#f7f4ef for Ces)
$text_color        — Primary text (#3a352e)
$text_secondary    — Secondary text (#7a7268)
$accent_color      — Pillar accent (gold/sage/blush/lavender)
$font_headline     — Headline font family (Playfair Display)
$font_body         — Body font family (DM Sans)
$brand_handle      — @agentces
```

#### `social-card.html` — Social Media Image Posts

**Used by:** /linkedin (text+image posts), /distribute (image announcements)

**Dimensions:** 1080x1080 (square, LinkedIn/FB optimal) or 1080x1350 (portrait, IG/Threads)

**Layout:**
```
+----------------------------------+
|          [grain overlay]         |
|                                  |
|     $headline                    |
|     (Playfair Display, 48px)     |
|                                  |
|     $body                        |
|     (DM Sans, 20px, secondary)   |
|                                  |
|     [$accent_shape]              |
|     (3D gradient blob, optional) |
|                                  |
|          $brand_handle           |
+----------------------------------+
```

**Variables:** `$headline`, `$body`, `$pillar` (determines accent color), `$accent_shape` (optional SVG)

#### `og-image.html` — Blog Open Graph / Featured Image

**Used by:** /blog (featured image + OG meta), /distribute (blog announcement cards)

**Dimensions:** 1200x630 (Open Graph standard)

**Layout:**
```
+----------------------------------------------+
|  [accent gradient bar, 4px, top]             |
|                                              |
|  $headline                                   |
|  (Playfair Display, 42px, max 2 lines)       |
|                                              |
|  $subtitle                                   |
|  (DM Sans, 18px, secondary, optional)        |
|                                              |
|                           $brand_handle      |
+----------------------------------------------+
```

**Variables:** `$headline`, `$subtitle`, `$pillar`, `$category` (optional tag/badge)

#### `carousel-slide.html` — Carousel Slide

**Used by:** /linkedin (carousel generation), /distribute (infographic rebranding)

**Dimensions:** 1080x1350 (4:5 portrait, Instagram/LinkedIn standard)

**Variants (selected via `$slide_type`):**
- `hook`: Large headline (<10 words), gradient avatar ring, answers "Is this for me?"
- `value`: One idea, numbered step indicator, explanatory body text
- `cta`: Action text, centered avatar ring, warm gradient background

**Layout (value variant):**
```
+---------------------------+
|  $step_number / $total    |
|  (DM Sans, 14px, muted)  |
|                           |
|  $headline                |
|  (Playfair Display, 36px) |
|                           |
|  $body                    |
|  (DM Sans, 18px)          |
|                           |
|  [$illustration]          |
|  (optional SVG/gradient)  |
|                           |
|      $brand_handle        |
+---------------------------+
```

**Variables:** `$slide_type`, `$headline`, `$body`, `$step_number`, `$total`, `$pillar`

#### `email-preview.html` — Newsletter Preview Card

**Used by:** /newsletter (social sharing preview, "view in browser" thumbnail)

**Dimensions:** 600x400 (email-width preview)

**Layout:** Renders the email HTML at 600px width, captures the top 400px as a preview card.

**Variables:** `$email_html` (the full email HTML content to preview)

#### `wireframe.html` — Web Design Spec Visualization

**Used by:** /web-design (stakeholder preview of section specs)

**Dimensions:** 1440x900 (desktop viewport) or 375x812 (mobile)

**Layout:** Renders section-by-section wireframe blocks with placeholder shapes, brand colors, and section labels.

**Variables:** `$sections` (JSON array of `{name, layout, description}`)

#### `thumbnail.html` — YouTube Thumbnail

**Used by:** /distribute (YouTube uploads), /youtube-search (thumbnail generation)

**Dimensions:** 1280x720 (16:9, YouTube standard)

**Layout:**
```
+----------------------------------------------+
|                                              |
|  $title_line_1              [optional        |
|  $title_line_2               face cutout]    |
|  (Playfair Display, 56px,                    |
|   bold, with text shadow)                    |
|                                              |
|  [$badge]                    $brand_handle   |
+----------------------------------------------+
```

**Variables:** `$title_line_1`, `$title_line_2`, `$badge` (optional), `$background_image` (optional Unsplash URL)

---

## Brand Asset Resolution

**How `render.py` reads brand data:**

1. Resolve `$BRAND_DIR` via `init.py` (e.g., `/Users/UPCHANNEL/claude-notebooklm/brands/ces/`)
2. Parse `brand-colors.md`:
   - Extract hex codes by scanning for `#[0-9a-fA-F]{6}` patterns next to known labels
   - Map: `Ivory` -> `$bg_color`, `Warm Charcoal` -> `$text_color`, pillar names -> `$accent_color`
3. Parse `brand-typography.md`:
   - Extract font family names (Playfair Display, DM Sans)
   - Extract size scales for each template type
4. Parse `brand-kit.md`:
   - Extract `$brand_handle` (e.g., `@agentces`)
   - Extract content pillar -> accent color mapping
5. Inject all values as CSS custom properties + template variables

**Brand color parser (`_parse_brand_colors`):**
```python
def _parse_brand_colors(brand_dir: str) -> dict:
    """Parse brand-colors.md into a color map."""
    colors = {}
    text = Path(brand_dir, "brand-colors.md").read_text()
    # Pattern: "Name — #hexcode" or "Name: #hexcode" or "#hexcode (Name)"
    for match in re.finditer(r'(?:(\w[\w\s]+?)\s*[—:\-]\s*)?#([0-9a-fA-F]{6})', text):
        label = (match.group(1) or "").strip().lower()
        hex_val = f"#{match.group(2)}"
        # Map known labels to template variables
        if 'ivory' in label or 'background' in label:
            colors.setdefault('bg_color', hex_val)
        elif 'charcoal' in label or 'primary' in label:
            colors.setdefault('text_color', hex_val)
        # ... etc for secondary, accent colors
    return colors
```

**This is a best-effort parser.** Brand files are human-written markdown, not structured data. The parser uses heuristics (label keywords + proximity to hex codes). If a brand file changes format significantly, the parser may need updating.

---

## Integration Points — How Other Skills Call /render

### Integration 1: /distribute — Infographic Rebranding (Tier 1)

**Current state:** Distributes raw NotebookLM output with their branding. Only resizes to 4:5.

**With /render:**
```
Step 4 (Preprocess media) in SKILL.md gains a new sub-step:

4a. If input is NotebookLM HTML/PNG:
    python3 "${RENDER_SCRIPTS}/rebrand.py" \
      --input "$INPUT_FILE" \
      --remove ".notebooklm-logo, .watermark" \
      --inject-handle "@agentces" \
      --handle-position bottom-center \
      --brand "$LOCATION_KEY" \
      --size 1080x1350 \
      --output "/tmp/rebranded_$(basename $INPUT_FILE)"

    INPUT_FILE="/tmp/rebranded_$(basename $INPUT_FILE)"
```

**What changes in distribute/SKILL.md:**
- Add `RENDER_SCRIPTS="${CLAUDE_PLUGIN_ROOT}/skills/render/scripts"` to Step 0
- Add Step 4a (rebrand) before existing resize step
- Existing `resize_to_4x5.py` becomes unnecessary when rebrand.py already outputs at target size

**Platform-specific sizes:**
| Platform | Size | Notes |
|----------|------|-------|
| Instagram | 1080x1350 | 4:5 portrait (carousel + single) |
| Facebook | 1080x1080 | 1:1 square (single post) |
| LinkedIn | 1080x1350 | 4:5 portrait (carousel slides) |
| LinkedIn | 1200x627 | Landscape (link preview / article) |
| Threads | 1080x1350 | 4:5 portrait |
| YouTube | 1280x720 | 16:9 thumbnail |

When distributing to multiple platforms, render once at highest resolution (1080x1350) then crop/resize for each platform using PIL (fast, no re-render needed).

### Integration 2: /newsletter — Email Preview Image (Tier 1)

**Current state:** No visual preview. Emails are text-only in social sharing.

**With /render:**
```
After Step 5 (Send/save email), add:

6. Generate preview image:
   python3 "${RENDER_SCRIPTS}/render.py" \
     --template email-preview \
     --data "{\"email_html\": \"$(cat /tmp/email.html | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')\"}" \
     --size 600x400 \
     --output /tmp/email-preview.png

   # Upload preview to Drive for social sharing
   python3 "${DISTRIBUTE_SCRIPTS}/drive_upload.py" \
     --file /tmp/email-preview.png \
     --folder "Newsletter Previews"
```

**What changes in newsletter/SKILL.md:**
- Add optional Step 6 for preview generation
- Preview image can be attached when sharing newsletter link on social

### Integration 3: /linkedin — Auto-Generated Social Cards (Tier 1)

**Current state:** Text posts have no visual. Carousels require manual image creation.

**With /render — Text+Image Posts:**
```
Step 3 gains automatic image generation:

If post type is "text" and no image provided:
  python3 "${RENDER_SCRIPTS}/render.py" \
    --template social-card \
    --data '{"headline":"$HOOK_LINE","body":"$KEY_POINT","pillar":"$PILLAR"}' \
    --brand "$LOCATION_KEY" \
    --size 1080x1080 \
    --output /tmp/linkedin-card.png

  # Upload to GHL
  bash "${DISTRIBUTE_SCRIPTS}/ghl_upload_media.sh" \
    --file /tmp/linkedin-card.png \
    --name "linkedin-card-$(date +%Y%m%d)" \
    --location "$LOCATION_KEY" \
    --no-resize
```

**With /render — Carousel Generation:**
```
If post type is "carousel" and no slide images provided:
  for i in $(seq 1 $SLIDE_COUNT); do
    python3 "${RENDER_SCRIPTS}/render.py" \
      --template carousel-slide \
      --data "{\"slide_type\":\"$TYPE\",\"headline\":\"$HEADLINE\",\"body\":\"$BODY\",\"step_number\":$i,\"total\":$SLIDE_COUNT,\"pillar\":\"$PILLAR\"}" \
      --brand "$LOCATION_KEY" \
      --size 1080x1350 \
      --output "/tmp/carousel/slide-$(printf '%02d' $i).png"
  done

  # Assemble PDF for LinkedIn native carousel
  python3 -c "
  from PIL import Image
  import glob
  slides = sorted(glob.glob('/tmp/carousel/slide-*.png'))
  images = [Image.open(s).convert('RGB') for s in slides]
  images[0].save('/tmp/carousel.pdf', save_all=True, append_images=images[1:])
  "
```

**What changes in linkedin/SKILL.md:**
- Add render step in Step 3 (Create Content) for both text+image and carousel types
- Remove manual Gemini generation instructions (render.py handles visuals)
- Keep Unsplash as fallback option (user preference)

### Integration 4: /blog — OG Image / Featured Image (Tier 2)

**Current state:** Uses generic Unsplash photos. No branded, title-specific images.

**With /render:**
```
Step 5 (Featured image) gains a branded option:

Option A (branded OG image — NEW):
  python3 "${RENDER_SCRIPTS}/render.py" \
    --template og-image \
    --data '{"headline":"$BLOG_TITLE","subtitle":"$BLOG_DESCRIPTION","pillar":"$PILLAR"}' \
    --brand "$LOCATION_KEY" \
    --size 1200x630 \
    --output /tmp/og-image.png

Option B (Unsplash photo — EXISTING):
  python3 "${DISTRIBUTE_SCRIPTS}/unsplash_fetch.py" \
    --query "$TOPIC" --orientation landscape --output-dir /tmp

# Upload whichever was chosen
bash "${DISTRIBUTE_SCRIPTS}/ghl_upload_media.sh" \
  --file /tmp/og-image.png --name "blog-og-$(date +%Y%m%d)" \
  --location "$LOCATION_KEY" --no-resize
```

**What changes in blog/SKILL.md:**
- Add Option A to Step 5 (default to branded OG image)
- Keep Unsplash as Option B
- OG image dimensions: 1200x630 (Facebook/LinkedIn/Twitter standard)

### Integration 5: /web-design — Visual Mockup (Tier 2)

**Current state:** Outputs markdown spec only. No visual preview.

**With /render:**
```
After Step 8 (Final spec), add:

9. Generate visual preview:
   python3 "${RENDER_SCRIPTS}/render.py" \
     --template wireframe \
     --data '{"sections": $SECTIONS_JSON}' \
     --brand "$LOCATION_KEY" \
     --size 1440x900 \
     --output /tmp/wireframe-desktop.png

   python3 "${RENDER_SCRIPTS}/render.py" \
     --template wireframe \
     --data '{"sections": $SECTIONS_JSON}' \
     --brand "$LOCATION_KEY" \
     --size 375x812 \
     --output /tmp/wireframe-mobile.png
```

**What changes in web-design/SKILL.md:**
- Add optional Step 9 for visual preview generation
- Desktop (1440x900) + Mobile (375x812) previews

### Integration 6: /presentation — Slide Fallback (Tier 2)

**Current state:** Depends entirely on Canva API. No fallback.

**With /render:**
```
If Canva is unavailable or user prefers local generation:
  for i in $(seq 1 $SLIDE_COUNT); do
    python3 "${RENDER_SCRIPTS}/render.py" \
      --template carousel-slide \
      --data "{\"headline\":\"$TITLE\",\"body\":\"$BULLETS\",\"pillar\":\"$PILLAR\"}" \
      --brand "$LOCATION_KEY" \
      --size 1920x1080 \       # 16:9 for presentations
      --output "/tmp/slides/slide-$(printf '%02d' $i).png"
  done
```

**Note:** This is a degraded fallback. Canva produces richer designs. The render engine provides basic branded slides when Canva is unavailable.

### Integration 7: /blog — Post-Publish Screenshot (Tier 3)

**Current state:** Manual process.

**With /render:**
```
After successful publish, add:

python3 "${RENDER_SCRIPTS}/render.py" \
  --url "$PUBLISHED_URL" \
  --size 1200x630 \
  --output /tmp/blog-screenshot.png

# Feed to distribute as "New post!" announcement
```

### Integration 8: /distribute — YouTube Thumbnail (Tier 3)

**Current state:** No thumbnail generation. Relies on YouTube auto-generated thumbnails.

**With /render:**
```
If content type is video and --thumbnail not provided:
  python3 "${RENDER_SCRIPTS}/render.py" \
    --template thumbnail \
    --data '{"title_line_1":"$TITLE_1","title_line_2":"$TITLE_2","pillar":"$PILLAR"}' \
    --brand "$LOCATION_KEY" \
    --size 1280x720 \
    --output /tmp/youtube-thumb.png

  # Pass to youtube_upload.py --thumbnail /tmp/youtube-thumb.png
```

---

## Build Order

### Phase 1: Core Engine (build first)

| # | Task | Output | Depends On |
|---|------|--------|------------|
| 1 | Install Playwright browsers | `playwright install chromium` | Playwright Python (already installed) |
| 2 | Write `render.py` | Core renderer with --template, --input, --url modes | Browser binaries |
| 3 | Write `base.html` | Shared layout shell (Google Fonts, CSS custom properties, grain overlay) | — |
| 4 | Write brand color/font parser | `_parse_brand_colors()`, `_parse_brand_fonts()` functions in render.py | Brand files (exist) |
| 5 | Write `social-card.html` | First template — validates full pipeline | base.html, render.py |
| 6 | Manual test | Render a social card with Ces brand | All above |

### Phase 2: Templates + Rebrand (build second)

| # | Task | Output | Depends On |
|---|------|--------|------------|
| 7 | Write `og-image.html` | Blog featured image template | base.html |
| 8 | Write `carousel-slide.html` | Carousel slide template (3 variants) | base.html |
| 9 | Write `rebrand.py` | Element removal + logo/handle injection | render.py |
| 10 | Write `thumbnail.html` | YouTube thumbnail template | base.html |
| 11 | Write `email-preview.html` | Newsletter preview card | base.html |

### Phase 3: Skill Integrations (wire in)

| # | Task | Changes | Depends On |
|---|------|---------|------------|
| 12 | Wire into /distribute | Add Step 4a (rebrand) to SKILL.md | rebrand.py |
| 13 | Wire into /linkedin | Add render step to Step 3 | social-card.html, carousel-slide.html |
| 14 | Wire into /blog | Add Option A to Step 5 | og-image.html |
| 15 | Wire into /newsletter | Add Step 6 (preview) | email-preview.html |
| 16 | Wire into /distribute (YouTube) | Add thumbnail generation | thumbnail.html |

### Phase 4: Extended Templates (build later)

| # | Task | Output | Depends On |
|---|------|--------|------------|
| 17 | Write `wireframe.html` | Web-design spec visualization | base.html |
| 18 | Wire into /web-design | Add Step 9 (visual preview) | wireframe.html |
| 19 | Wire into /presentation | Add Canva fallback path | carousel-slide.html |

---

## SKILL.md Frontmatter

```yaml
---
name: render
description: >
  Shared rendering engine that converts HTML templates + brand assets into
  production-ready images (PNG, JPG, PDF). Renders social cards, OG images,
  carousel slides, email previews, wireframes, and YouTube thumbnails.
  Called by other skills (/distribute, /linkedin, /blog, /newsletter) —
  not typically invoked directly by users.
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
```

**Note:** `disable-model-invocation: true` because this is primarily a utility skill called by other skills. Users can invoke it directly with `/render` but it won't auto-trigger.

---

## Dimensions Reference

| Template | Default Size | Aspect Ratio | Used By |
|----------|-------------|--------------|---------|
| social-card | 1080x1080 | 1:1 | /linkedin, /distribute |
| social-card | 1080x1350 | 4:5 | /distribute (IG/Threads) |
| og-image | 1200x630 | ~1.9:1 | /blog, /distribute |
| carousel-slide | 1080x1350 | 4:5 | /linkedin, /distribute |
| email-preview | 600x400 | 3:2 | /newsletter |
| wireframe | 1440x900 | 16:10 | /web-design |
| wireframe | 375x812 | ~1:2.2 | /web-design (mobile) |
| thumbnail | 1280x720 | 16:9 | /distribute (YouTube) |
| presentation | 1920x1080 | 16:9 | /presentation |

---

## Dependencies & Setup

**Required (already installed):**
- Python 3.14+
- Playwright Python module (`from playwright.sync_api import sync_playwright`)
- PIL/Pillow (for post-processing, PDF assembly, raster compositing)

**One-time setup:**
```bash
playwright install chromium
# Downloads ~150MB headless Chromium to ~/.cache/ms-playwright/
```

**No new pip installs needed.** The skill uses only stdlib + playwright + PIL (both already available).

**Runtime requirements:**
- Internet connection (for Google Fonts loading on first render; cached after)
- ~200MB disk for Chromium binary
- ~100-300ms per render (headless screenshot is fast)

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Chromium not installed | Print error: "Run `playwright install chromium` first", exit 1 |
| Template not found | Print error: "Template '$name' not found in templates/", exit 1 |
| Brand dir not found | Fall back to `_example` templates, warn to stderr |
| Font load timeout | Proceed with fallback fonts (Georgia, Arial), warn to stderr |
| Invalid --size format | Print error: "Size must be WxH (e.g., 1080x1080)", exit 1 |
| Output dir doesn't exist | Create it with `os.makedirs(exist_ok=True)` |
| Playwright crash | Catch exception, print traceback to stderr, exit 1 |

---

## Testing Strategy

**Manual smoke tests (Phase 1):**
```bash
# 1. Verify Chromium works
python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(); b.close(); p.stop(); print('OK')"

# 2. Render a social card
python3 render.py --template social-card \
  --data '{"headline":"AI is transforming leadership","body":"Here is what changed in 2026","pillar":"ai_product"}' \
  --brand ces --size 1080x1080 --output /tmp/test-card.png

# 3. Verify output
open /tmp/test-card.png  # macOS: opens in Preview

# 4. Test rebrand
python3 rebrand.py --input /path/to/notebooklm-export.html \
  --remove ".logo" --inject-handle "@agentces" \
  --size 1080x1350 --output /tmp/rebranded.png
```

**Integration tests (Phase 3):**
- Run `/distribute` with a NotebookLM infographic — verify rebranding applied
- Run `/linkedin` text post — verify social card auto-generated
- Run `/blog` — verify OG image generated and uploaded as featured image

---

## What This Unlocks

| Before /render | After /render |
|----------------|---------------|
| NotebookLM infographics distributed with their branding | Rebranded with Ces colors, logo removed, handle added |
| LinkedIn text posts: text only (low engagement) | Auto-generated branded social card (2-3x engagement) |
| Blog featured images: generic Unsplash stock photos | Title-specific branded OG images |
| Newsletter sharing: no visual preview | Branded preview card for social sharing |
| YouTube thumbnails: auto-generated by YouTube | Custom branded thumbnails with title text |
| Web-design specs: markdown only | Visual wireframe preview for stakeholders |
| Carousel creation: manual image generation required | Auto-generated slides from text content |
| Presentation fallback: Canva-only | Basic branded slides when Canva unavailable |

---

## Nano Banana 2 Integration

### Overview

`nano_banana.py` provides AI image generation via Google's Nano Banana 2 model (Gemini 3.1 Flash Image).
It complements the template-based Playwright renderer — use Nano Banana for creative/generative imagery,
use render.py for pixel-perfect branded templates.

### When to Use Which

| Need | Tool | Why |
|------|------|-----|
| Social card with exact brand layout | `render.py --template social-card` | Pixel-perfect, repeatable |
| Hero image for a blog post | `nano_banana.py` | Creative, unique, topic-specific |
| Carousel slides with consistent format | `render.py --template carousel-slide` | Structured, numbered, branded |
| Product mockup or illustration | `nano_banana.py` | AI-generated, no stock photos |
| OG image with title text | `render.py --template og-image` | Exact typography control |
| Background texture or abstract art | `nano_banana.py` | Creative generation |
| Screenshot of a live URL | `render.py --url` | Browser-based capture |

### Script: `nano_banana.py`

```bash
# Text-to-image generation
python3 nano_banana.py --prompt "minimalist podcast cover, gold tones" \
  --brand ces --aspect-ratio 1:1 --size 1K --output /tmp/cover.png

# Image editing
python3 nano_banana.py --prompt "remove background, add soft gradient" \
  --input /tmp/photo.png --output /tmp/edited.png

# Multiple outputs
python3 nano_banana.py --prompt "hero image options" --count 3 --output /tmp/heroes/

# High-res for print/web
python3 nano_banana.py --prompt "landing page hero" --size 4K --aspect-ratio 16:9 \
  --output /tmp/hero-4k.png
```

### Models

| Key | Model ID | Use Case |
|-----|----------|----------|
| `flash` (default) | `gemini-3.1-flash-image-preview` | Fast generation, good quality |
| `pro` | `gemini-3-pro-image-preview` | Best quality, slower |
| `legacy` | `gemini-2.5-flash-image` | Fallback |

### Requirements

- `pip install google-genai`
- `GOOGLE_API_KEY` or `GEMINI_API_KEY` in `.env`
- Pricing: ~$0.045-0.15 per image depending on resolution

### Integration with /web-build

`/web-build` uses `nano_banana.py` for generating hero images, product visuals, and illustrations
that get embedded into Stitch-generated UI screens before deployment to Firebase or Cloud Run.
