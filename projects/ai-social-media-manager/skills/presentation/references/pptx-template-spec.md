# python-pptx Backend Reference

The python-pptx backend generates branded `.pptx` files locally without Canva. Use it for offline generation, data-driven decks, or when maximum control over layout is needed.

Read this file at Step 4B/5B when the user selects the python-pptx backend.

---

## When to Use python-pptx vs Canva

| Scenario | Backend |
|----------|---------|
| AI-designed creative slides | Canva |
| Data report or dashboard deck | python-pptx |
| Offline / no Canva account | python-pptx |
| Brand kit integration | Canva |
| Custom image placement control | python-pptx |
| Interactive outline review | Canva |
| Recurring templated reports | python-pptx |
| Export to video (MP4) | Canva |

---

## Script Usage

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_pptx.py \
  --input slides.json \
  --output presentation.pptx \
  --context conference \
  --accent gold
```

### Arguments

| Arg | Required | Values | Default |
|-----|----------|--------|---------|
| `--input` | Yes | Path to JSON manifest or `-` for stdin | - |
| `--output` | Yes | Output .pptx file path | - |
| `--context` | No | `large_venue`, `conference`, `meeting`, `screen_share`, `pdf` | `conference` |
| `--accent` | No | `gold`, `sage`, `blush`, `lavender` | `gold` |

Context controls font sizes. Accent selects the pillar color used for decorative elements.

---

## JSON Manifest Format

```json
{
  "title": "Presentation Title",
  "context": "conference",
  "accent": "gold",
  "slides": [
    { "type": "slide-type", "title": "...", ...fields... }
  ]
}
```

`context` and `accent` in the manifest override CLI arguments.

---

## Supported Slide Types

### `title`
```json
{ "type": "title", "title": "Main Title", "subtitle": "Speaker | Date", "notes": "..." }
```

### `agenda`
```json
{ "type": "agenda", "title": "Agenda", "items": ["Topic 1", "Topic 2", "Topic 3"], "notes": "..." }
```

### `section-divider`
```json
{ "type": "section-divider", "title": "Section Name", "notes": "..." }
```

### `content`
```json
{ "type": "content", "title": "Assertion headline", "body": "Supporting text", "image": "/path/to/img.png", "notes": "..." }
```
If `image` is provided and exists, layout splits into text left + image right. Otherwise full-width text.

### `data`
```json
{ "type": "data", "title": "Assertion about the data", "image": "/path/to/chart.png", "caption": "Source: ...", "notes": "..." }
```
If no image, shows a placeholder rectangle with "[Insert chart or data visualization]".

### `comparison`
```json
{
  "type": "comparison",
  "title": "Option A vs Option B",
  "columns": [
    { "title": "Option A", "body": "Pros and details..." },
    { "title": "Option B", "body": "Pros and details..." }
  ],
  "notes": "..."
}
```
Supports 2-3 columns.

### `quote`
```json
{ "type": "quote", "quote": "The quote text here.", "attribution": "Speaker Name, Title", "notes": "..." }
```

### `big-number`
```json
{ "type": "big-number", "number": "47%", "context": "of companies will not exist in 10 years", "notes": "..." }
```

### `process`
```json
{ "type": "process", "title": "How it works", "steps": ["Step 1 text", "Step 2 text", "Step 3 text"], "notes": "..." }
```
Supports 3-5 steps in horizontal flow with numbered circles and arrows.

### `summary`
```json
{ "type": "summary", "title": "Key Takeaways", "points": ["Point 1", "Point 2", "Point 3"], "notes": "..." }
```

### `cta`
```json
{ "type": "cta", "title": "Next Steps", "action": "Book a 15-minute call", "contact": "email@example.com | yoursite.com", "notes": "..." }
```

---

## Brand Encoding

All brand values are hardcoded in the script. No external template file needed.

**Colors:**
- Background: Ivory `#f7f4ef` (all slides)
- Section dividers and quotes: Warm Linen `#f0ece4`
- Primary text: Warm Charcoal `#3a352e`
- Secondary text: `#7a7268`
- Muted text: `#b0a898`

**Accent colors (one per deck, matching content pillar):**
- Gold `#b8a06a` (AI topics)
- Sage `#8fab8a` (Leadership)
- Blush `#d4b0a8` (Sustainability)
- Lavender `#c4b8cc` (Consciousness)

**Fonts:**
- Headlines: Playfair Display (fallback: Georgia)
- Body: DM Sans (fallback: Calibri)

**Font sizes by context:**

| Context | Title | Body | Caption | Big Number |
|---------|-------|------|---------|------------|
| Large venue | 44pt | 32pt | 18pt | 96pt |
| Conference | 40pt | 28pt | 16pt | 88pt |
| Meeting | 36pt | 24pt | 14pt | 80pt |
| Screen share | 32pt | 24pt | 16pt | 72pt |
| PDF | 28pt | 20pt | 14pt | 64pt |

**Layout:**
- Slide: 16:9 (13.333 x 7.5 inches)
- Margins: 0.75 inches all sides
- Title area: top 0.75-1.95 inches
- Content area: 2.2 inches from top to 0.75 inches from bottom

---

## Limitations vs Canva

| Feature | Canva | python-pptx |
|---------|-------|-------------|
| AI-designed layouts | Yes | No (fixed templates) |
| Animations / transitions | No (via API) | No |
| Font family changes | No (via API) | Yes (any installed font) |
| Video embedding | Yes (via editing) | No |
| Brand kit integration | Yes | Manual (hardcoded) |
| Export to PDF | Yes | No (open in PowerPoint/Slides) |
| Export to PNG | Yes | No |
| Export to MP4 | Yes | No |
| Offline generation | No | Yes |
| Charts from data | No | Placeholder only |
| Custom image placement | Limited | Full control (position, size) |
| Speaker notes | No (via API) | Yes |

---

## Font Availability

python-pptx writes the font name into the .pptx file. The viewing application (PowerPoint, Google Slides, Keynote) renders the font if installed on that machine. If not installed:
- PowerPoint substitutes the closest available font
- Google Slides uses a default sans-serif
- Keynote uses Helvetica

To ensure Playfair Display and DM Sans render correctly:
- Install them on the presenting machine from Google Fonts
- Or accept the automatic substitution (Georgia for Playfair, Calibri for DM Sans)
