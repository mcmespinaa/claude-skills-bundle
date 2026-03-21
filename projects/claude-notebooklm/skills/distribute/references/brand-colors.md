# BRAND COLORS — Ces (Maria Cecilia)

> Part of the [Brand Kit](brand-kit.md) | v2.0

---

## Backgrounds

| Token | Hex | Usage |
|-------|-----|-------|
| Ivory (primary) | `#f7f4ef` | Default background for all content |
| Warm Linen (secondary) | `#f0ece4` | Alternate background, section dividers |
| Card surface | `#faf8f4` | Elevated cards, modals |
| Pure white | `#ffffff` | Card surfaces only, use sparingly |

---

## Accent Colors (by Content Pillar)

| Pillar | Primary | Light | Usage |
|--------|---------|-------|-------|
| AI + Product | `#b8a06a` (Gold) | `#d4c48e` | Tags, emphasis text, step indicators |
| Leadership | `#8fab8a` (Sage) | — | Tags, background washes |
| Sustainability | `#d4b0a8` (Blush) | — | Tags, background washes |
| Consciousness | `#c4b8cc` (Lavender) | — | Tags, background washes, illustration strokes |

---

## 3D Gradient Palette

For project cards, hero backgrounds, decorative elements. Each gradient blends 2-3 colors.

| Name | Gradient | Tertiary |
|------|----------|----------|
| Lavender-blush | `#c4b8cc` → `#d4b0a8` | blue-gray `#b8c4d4` |
| Sage-gold | `#8fab8a` → `#d4c48e` | warm cream `#e8dfc8` |
| Blush-peach | `#d4b0a8` → `#e8cfc4` | soft teal `#a8c8c4` |
| Lavender-sage | `#c4b8cc` → `#8fab8a` | ivory `#f0ece4` |

### 3D Shape Color Combos (by Pillar)

| Pillar | Color flow |
|--------|-----------|
| AI + Product | Gold → cream → soft warm gray |
| Leadership | Sage → ivory → soft blue-gray |
| Sustainability | Blush → peach → soft teal |
| Consciousness | Lavender → blush → soft silver |

---

## Text Colors

| Token | Hex | Usage | Min size |
|-------|-----|-------|----------|
| Warm Charcoal (primary) | `#3a352e` | Headlines, body text | Any |
| Secondary | `#7a7268` | Body text, subheadings | 14px+ |
| Muted/caption | `#b0a898` | Captions, timestamps, handles | 16px+ |

---

## Glows and Overlays

| Pillar | Value | Usage |
|--------|-------|-------|
| Gold glow | `rgba(184,160,106,0.12)` | Tag backgrounds, hover states |
| Sage glow | `rgba(143,171,138,0.12)` | Tag backgrounds, hover states |
| Blush glow | `rgba(212,176,168,0.10)` | Tag backgrounds, hover states |
| Lavender glow | `rgba(196,184,204,0.08)` | Tag backgrounds, hover states |

---

## Accessibility Notes

### Contrast Ratios (WCAG 2.1)

| Combination | Ratio | WCAG AA | Notes |
|-------------|-------|---------|-------|
| Warm Charcoal `#3a352e` on Ivory `#f7f4ef` | 9.2:1 | PASS (AAA) | Primary text — fully accessible |
| Secondary `#7a7268` on Ivory `#f7f4ef` | 4.1:1 | PASS (AA normal) | Body text — meets AA at any size |
| Muted `#b0a898` on Ivory `#f7f4ef` | 2.4:1 | FAIL (AA normal) | Use at 16px+ bold or 18px+ regular only |
| Gold `#b8a06a` on Ivory `#f7f4ef` | 3.3:1 | PASS (AA large) | Emphasis words only, 18px+ or 14px bold |
| Sage `#8fab8a` on Ivory `#f7f4ef` | 2.8:1 | FAIL (AA normal) | Tags/badges only, not for running text |

**Guidance:**
- Muted text (`#b0a898`) should only be used for handles, timestamps, and decorative captions at 16px+ bold or 18px+ regular.
- Accent colors (gold, sage, blush, lavender) should never carry critical information as standalone text on ivory. Use them for tags with sufficient size or as decorative emphasis alongside charcoal text.
- For any UI elements, prefer Warm Charcoal for all interactive or informational text.

### Dark Mode Considerations

The brand does not use dark backgrounds. When platforms render in dark mode:
- Add a 1px `#f0ece4` (Warm Linen) border around carousel slides to prevent blending into dark feeds.
- Email templates: include a `background-color: #f7f4ef` on the outer wrapper so the ivory background is preserved.

---

## Utility Color (System Use Only)

| Token | Hex | Usage |
|-------|-----|-------|
| Error/alert | `#c47868` (Muted Terracotta) | Form validation, error states — not for brand content |
| Success | `#8fab8a` (Sage) | Reuse sage for success states in UI |

---

## Rules

1. Never use dark or black backgrounds.
2. Never use saturated, neon, or high-contrast colors.
3. Background should always be ivory or warm linen.
4. Accent colors appear as subtle washes, gradient blobs, tags, or fine linework — never as solid blocks.
5. When in doubt, default to Warm Charcoal text on Ivory background.
