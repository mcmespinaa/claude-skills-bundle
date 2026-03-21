# Email Design System — Ces Newsletter

Read this file before building any HTML email template. Every newsletter must follow these specs for consistent branding and reliable rendering across email clients.

---

## LAYOUT FUNDAMENTALS

### Container
- **Max width:** 600px (industry standard for email)
- **Background:** Ivory #f7f4ef (outer body), White #ffffff (inner content cards)
- **Padding:** 40px top/bottom, 20px left/right on the outer container
- **Border-radius:** 0px on outer container (some clients strip it), 8px on inner cards

### Structure (single column, top to bottom)
1. **Header bar** — Logo/name area (optional hero image)
2. **Personal opening** — 2-3 sentence intro
3. **Main content** — Editorial body or digest cards
4. **CTA block** — Single call-to-action button
5. **Sign-off** — Warm closing
6. **Footer** — Unsubscribe, social links, legal

### Spacing
- Between sections: 32px
- Between paragraphs: 16px
- Between digest cards: 24px
- Header to first content: 40px
- Last content to footer: 48px

---

## COLOR PALETTE (Email-Safe)

### Backgrounds
| Use | Color | Hex |
|-----|-------|-----|
| Email body (outer) | Ivory | #f7f4ef |
| Content area (inner) | White | #ffffff |
| Card backgrounds | Warm Linen | #f0ece4 |
| Divider lines | Light muted | #e8e4dc |

### Text
| Use | Color | Hex |
|-----|-------|-----|
| Headlines | Warm Charcoal | #3a352e |
| Body text | Warm Charcoal | #3a352e |
| Secondary text | Medium gray | #7a7268 |
| Muted/caption | Light gray | #b0a898 |
| Links | Soft Gold | #b8a06a |

### Accents & Buttons
| Use | Color | Hex |
|-----|-------|-----|
| CTA button background | Soft Gold | #b8a06a |
| CTA button text | White | #ffffff |
| CTA button hover | Dark Gold | #a08a5a |
| Section divider accent | Soft Gold | #b8a06a |

### Content Pillar Accents (for section borders or subtle backgrounds)
| Pillar | Color | Hex |
|--------|-------|-----|
| AI / Product | Gold | #b8a06a |
| Leadership | Sage | #8fab8a |
| Sustainability | Blush | #d4b0a8 |
| Consciousness | Lavender | #c4b8cc |

### RULES
- Never use dark or black backgrounds (#000, #111, etc.)
- Never use saturated or neon accent colors
- CTA buttons always use Soft Gold background with white text
- Links always use Soft Gold (#b8a06a), never default blue

---

## TYPOGRAPHY

Email clients have limited font support. Use web-safe fallback stacks.

### Headlines
```css
font-family: Georgia, 'Times New Roman', Times, serif;
font-weight: bold;
font-size: 24px;
line-height: 1.3;
color: #3a352e;
```
Georgia is the web-safe fallback for Playfair Display.

### Body Text
```css
font-family: Arial, Helvetica, 'Segoe UI', sans-serif;
font-weight: normal;
font-size: 16px;
line-height: 1.6;
color: #3a352e;
```
Arial is the web-safe fallback for DM Sans.

### Captions / Muted Text
```css
font-family: Arial, Helvetica, sans-serif;
font-size: 13px;
line-height: 1.5;
color: #b0a898;
```

### Section Headers
```css
font-family: Georgia, serif;
font-size: 20px;
font-weight: bold;
color: #3a352e;
border-bottom: 2px solid #b8a06a;
padding-bottom: 8px;
margin-bottom: 16px;
```

### RULES
- Maximum 2 font families per email (serif for headlines, sans-serif for body)
- No custom web fonts via @import (unreliable in email clients)
- Minimum body font size: 14px (16px preferred)
- Minimum line-height: 1.5 for body text

---

## COMPONENT SPECS

### Hero Image / Banner
- Width: 600px (fills container)
- Height: 200-300px
- Alt text: always required (describe the image content)
- Format: JPEG or PNG, hosted URL
- Fallback: background color #f0ece4 if image fails to load
- Optional: skip the hero image entirely for a cleaner, text-first look

### Digest Card (for social post roundups)
```
+-------------------------------------+
|  [Platform Icon]  Platform Name     |
|                                     |
|  Post excerpt text goes here...     |
|  First 2-3 sentences of the post.  |
|                                     |
|  Date                               |
+-------------------------------------+
```
- Background: #f0ece4 (Warm Linen)
- Border-radius: 8px
- Padding: 20px
- Border-left: 4px solid [pillar accent color]
- Platform icon: small inline image or emoji
- Post excerpt: first 2-3 sentences, truncated with "..."
- Date: muted text below

### CTA Button
```css
display: inline-block;
background-color: #b8a06a;
color: #ffffff;
font-family: Arial, Helvetica, sans-serif;
font-size: 16px;
font-weight: bold;
text-decoration: none;
padding: 14px 32px;
border-radius: 6px;
text-align: center;
```
- Always centered in its container
- One button per newsletter (the primary CTA)
- VML fallback for Outlook (buttons render as rectangles without it)

### Pull Quote (for editorial newsletters)
```css
border-left: 4px solid #b8a06a;
padding-left: 20px;
margin: 24px 0;
font-family: Georgia, serif;
font-size: 18px;
font-style: italic;
color: #7a7268;
```

### Divider Line
```css
border: none;
border-top: 1px solid #e8e4dc;
margin: 32px 0;
```

### Footer
- Font size: 12px
- Color: #b0a898 (muted)
- Contains: unsubscribe link, mailing address (CAN-SPAM compliance), optional social icons
- Unsubscribe link: always present, always visible, never hidden

---

## RESPONSIVE DESIGN

### Media Query (for mobile < 480px)
```css
@media only screen and (max-width: 480px) {
  .email-container { width: 100% !important; }
  .content-padding { padding: 20px 16px !important; }
  .headline { font-size: 22px !important; }
  .body-text { font-size: 15px !important; }
  .cta-button { padding: 12px 24px !important; width: 100% !important; display: block !important; }
  .digest-card { padding: 16px !important; }
  .hero-image { height: auto !important; }
}
```

### Mobile Rules
- All widths become 100%
- Padding reduces (40px -> 16px sides)
- Headlines shrink (24px -> 22px)
- CTA button becomes full-width block
- Images scale to container width
- Stack any side-by-side elements vertically

---

## DARK MODE

Some email clients (Apple Mail, Outlook.com, Gmail app) auto-invert colors in dark mode. Add these meta overrides:

```html
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
```

```css
@media (prefers-color-scheme: dark) {
  /* Backgrounds */
  .email-body { background-color: #1a1a1a !important; }
  .email-container { background-color: #2a2a2a !important; }
  .digest-card { background-color: #333333 !important; }

  /* Text */
  .headline, .body-text { color: #e8e4dc !important; }
  .muted-text { color: #8a8478 !important; }
  .section-header { color: #e8e4dc !important; border-bottom-color: #d4c48e !important; }
  .pull-quote { color: #b0a898 !important; }
  .card-label { color: #8a8478 !important; }
  .footer-text { color: #8a8478 !important; }

  /* Interactive */
  .cta-button { background-color: #d4c48e !important; color: #1a1a1a !important; }

  /* Borders */
  .divider-light { border-top-color: #444 !important; }
}
```

### Dark Mode Class Reference

These CSS classes exist only for dark mode targeting. They have no light mode rules, so adding them to elements does not affect light mode rendering.

| Class | Purpose | Dark Override |
|-------|---------|--------------|
| `.section-header` | `<h2>` section headings | Text #e8e4dc, border #d4c48e |
| `.pull-quote` | Pull quote `<p>` | Text #b0a898 |
| `.card-label` | Digest card platform label `<p>` | Text #8a8478 |
| `.divider-light` | Footer `<hr>` divider | Border #444 |
| `.footer-text` | Unsubscribe `<p>` | Text #8a8478 |

**Note:** Dark mode support is best-effort. Not all clients respect these overrides. Design primarily for light mode.

---

## HTML EMAIL RULES

### Inline CSS Only
- All styles must be inline (`style="..."` on each element)
- No `<style>` blocks in `<head>` for primary styles (only for responsive/dark mode overrides)
- No external CSS files
- No `<link>` tags for stylesheets

### Table-Based Layout
- Use `<table>` elements for layout structure (not `<div>` for critical layout)
- `<div>` is fine for text blocks and non-structural elements
- Set `cellpadding="0" cellspacing="0" border="0"` on all layout tables
- Use `width` attributes on `<table>` and `<td>` elements (not just CSS)

### Image Rules
- All images: hosted URLs (never base64 inline, never local file paths)
- Always include `alt` text
- Always include `width` and `height` attributes
- Add `style="display: block;"` to prevent gaps below images
- Use `border="0"` to prevent blue borders in some clients

### Compatibility
- Avoid: CSS grid, flexbox, position: absolute/fixed, float (unreliable in email)
- Avoid: JavaScript (blocked by all email clients)
- Avoid: SVG (inconsistent support)
- Avoid: CSS animations / transitions
- Prefer: HTML attributes over CSS where both exist (width, height, align, bgcolor)

---

## TEMPLATE TOKENS

Base templates use these placeholder tokens, replaced at build time:

| Token | Description |
|-------|-------------|
| `{{SUBJECT}}` | Email subject line |
| `{{PREVIEW_TEXT}}` | Preview text (hidden preheader) |
| `{{HERO_IMAGE_URL}}` | Hero banner image URL |
| `{{HERO_ALT}}` | Hero image alt text |
| `{{PERSONAL_OPENING}}` | Opening paragraph (2-3 sentences) |
| `{{SECTION_HEADER_N}}` | Section header text (N = 1, 2, 3...) |
| `{{SECTION_BODY_N}}` | Section body text |
| `{{DIGEST_CARD_N}}` | Complete digest card HTML (N = 1, 2, 3...) |
| `{{PULL_QUOTE}}` | Pull quote text |
| `{{CTA_TEXT}}` | Button label |
| `{{CTA_URL}}` | Button link URL |
| `{{SIGNOFF}}` | Closing message |
| `{{SENDER_NAME}}` | From name |
| `{{UNSUBSCRIBE_URL}}` | Unsubscribe link |
| `{{PILLAR_COLOR}}` | Content pillar accent hex |
| `{{CURRENT_YEAR}}` | Year for copyright footer |

---

## DO / DON'T

### DO
- Use ivory/white backgrounds with warm charcoal text
- Keep to single-column layout (600px max)
- Inline all CSS
- Use table-based layout for structure
- Include alt text on every image
- Test: does this look good with images disabled? (Many clients block images by default)
- Include unsubscribe link in footer
- Keep total email size under 100KB (excluding images)

### DON'T
- Use dark or black backgrounds
- Use custom web fonts (they won't load in most clients)
- Use JavaScript or CSS animations
- Use more than one CTA button
- Use em dashes (commas, periods, or ellipsis instead)
- Use background images for critical content (unreliable)
- Hide the unsubscribe link or make it tiny
- Send without testing in at least 2 email clients
