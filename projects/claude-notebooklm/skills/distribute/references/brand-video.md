# BRAND VIDEO SPECS — Ces (Maria Cecilia)

> Part of the [Brand Kit](brand-kit.md) | v2.0

---

## Technical Specs

| Property | Value |
|----------|-------|
| Model | `veo-3.1-generate-preview` (Veo 3.1) |
| Resolution | 1080p |
| Aspect ratio | 9:16 portrait |
| Duration | 4-6 seconds (4s for hooks, 6s for re-engagement) |
| Frame rate | 24fps |
| Format | MP4 |
| Codec | H.264 |
| Color profile | sRGB / Rec. 709 |

---

## Motion Guidelines

- **Subtle, intentional motion.** No jarring cuts or fast transitions.
- Camera: gentle zoom-in, slow pan, or static with element animation.
- Animated elements: 2-3 max per clip.
- Concentric rings rotate, shapes drift, text fades in.
- Text stays static and readable throughout. Motion happens around/behind text.
- Match the ivory/warm aesthetic. No dark backgrounds, no neon.
- Grain texture overlay persists through video.
- Transitions: soft fade or cross-dissolve. Never hard cut.

---

## Video Types

### Hook Video (Slide 1) — Text-to-Video

**Purpose:** Stop the scroll. Motion catches the eye in feed autoplay.

**Prompt template:**
```
Smooth camera push into [PILLAR_ACCENT_COLOR] concentric rings on ivory (#f7f4ef) background.
Text "[HEADLINE]" in warm charcoal (#3a352e) elegant serif font fades in center,
weight 500-600. Subtle grain texture overlay. Minimalist Scandinavian editorial style.
Shapes drift gently. Warm, ethereal lighting. 9:16 portrait, 1080p, 4 seconds.
NEVER: dark backgrounds, neon colors, stock footage, jarring transitions, loud music.
```

### Re-engagement Video (Slide 5) — Image-to-Video

**Purpose:** Re-engage mid-carousel with motion. Uses existing image slide as initial frame.

**Prompt template:**
```
Gentle zoom into the infographic elements. [DESCRIBE_SHAPES] slowly rotate or drift.
Text stays static and readable. Warm ethereal lighting. Subtle grain texture.
Background remains ivory (#f7f4ef). Shapes animate with [PILLAR_ACCENT_COLOR] accents.
Smooth, meditative motion. 9:16 portrait, 1080p, 6 seconds.
NEVER: text animation, dark backgrounds, fast movement, dramatic transitions.
```

### CTA Video (Last Slide, Optional) — Image-to-Video

**Purpose:** Animate the CTA for emphasis (use sparingly).

**Prompt template:**
```
Soft pulse animation on CTA button or text area.
[PILLAR_ACCENT_COLOR] accent gently glows. Arrow or hand icon subtly animates.
Text "[CTA_TEXT]" in warm charcoal remains center, static and readable.
Background: ivory (#f7f4ef) with minimal shapes. 9:16 portrait, 1080p, 4 seconds.
NEVER: aggressive animations, dark backgrounds, stock footage, neon effects.
```

---

## Negative Prompt (use for all Veo generations)

```
cartoon, low quality, blurry, dark background, neon, stock footage, jarring transitions,
fast movement, loud colors, glossy effects, 3D render, photorealistic humans
```

---

## Audio Guidelines

| Context | Audio |
|---------|-------|
| Carousel videos | Silent (carousel videos autoplay on mute in feed) |
| Standalone Reels | Ambient, lo-fi, or trending audio — warm and minimal |
| YouTube Shorts | Optional subtle ambient music — no loud intros |
| Stories | Optional — match platform trends |

---

## DO / DON'T

### DO
- Match ivory background and warm palette from still slides
- Keep text legible and static — motion is for visual elements only
- Use pillar accent colors for animated shapes
- Maintain grain texture overlay
- Keep videos 4-6 seconds for carousel context

### DON'T
- No background music/sound for carousel videos
- No jarring cuts or fast transitions
- No dark backgrounds, neon colors, or glossy effects
- No stock footage or live-action
- No text animation (text must remain readable)
- No more than 2-3 animated elements per clip
