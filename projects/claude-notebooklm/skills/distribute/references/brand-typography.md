# BRAND TYPOGRAPHY — Ces (Maria Cecilia)

> Part of the [Brand Kit](brand-kit.md) | v2.0

---

## Font Stack

### Headlines and Hooks

| Property | Value |
|----------|-------|
| Font | Playfair Display |
| Fallback stack | `'Playfair Display', Georgia, 'Times New Roman', serif` |
| Weight | 500-600 |
| Style | Regular; Italic for emphasis |
| Letter-spacing | -0.02em |
| Line-height | 1.15-1.25 |

### Body Text

| Property | Value |
|----------|-------|
| Font | DM Sans |
| Fallback stack | `'DM Sans', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif` |
| Weight | 400 (regular), 500 (medium for emphasis) |
| Letter-spacing | 0 |
| Line-height | 1.5-1.6 |

### Labels and Eyebrows

| Property | Value |
|----------|-------|
| Font | DM Sans |
| Weight | 500 |
| Size | 11-12px |
| Letter-spacing | 2-3px |
| Transform | uppercase |

---

## Size Scale

### Carousel (1080 x 1350px)

| Element | Size | Color |
|---------|------|-------|
| Hook headline (Slide 1) | 42-52px | `#3a352e` or `#b8a06a` |
| Value headline (Slides 2-8) | 28-36px | `#3a352e` |
| Body text | 16-20px | `#7a7268` |
| Caption / handle | 12-14px | `#b0a898` |
| Eyebrow label | 11-12px | Pillar accent |
| Step indicator | 24-28px | `#b8a06a` |

### Web

| Element | Size | Color |
|---------|------|-------|
| Hero headline | 52-62px | `#3a352e` |
| Section headline | 36-42px | `#3a352e` |
| Body text | 16-18px | `#7a7268` or `#3a352e` |
| Caption | 13-14px | `#b0a898` |

### Mobile (responsive)

| Element | Size |
|---------|------|
| Hero headline | 32-40px |
| Section headline | 24-32px |
| Body text | 15-16px |
| Caption | 12-13px |

---

## Emphasis Patterns

| Technique | When to use | How |
|-----------|------------|-----|
| Gold keyword | Highlight 1-2 key words in a headline | Set those words to `#b8a06a` while rest stays `#3a352e` |
| Italic | Soften a phrase or add introspective tone | Playfair Display Italic, same weight |
| Medium weight | Emphasize a sentence in body text | DM Sans 500 instead of 400 |
| Uppercase eyebrow | Category labels, pillar names | DM Sans 500, 11-12px, 2-3px letter-spacing |

---

## Rules

1. Maximum 2 fonts per slide or graphic (Playfair Display + DM Sans).
2. Headlines always in Playfair Display. Body always in DM Sans.
3. No all-caps except for small labels/eyebrows (11-12px).
4. Never use font weights below 400 or above 600.
5. Gold-colored text (`#b8a06a`) should only be used at 18px+ or 14px bold (see [brand-colors.md](brand-colors.md) accessibility notes).
6. Always set fallback font stacks in CSS/web contexts.
