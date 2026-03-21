# BRAND AI GENERATION PROMPTS — Ces (Maria Cecilia)

> Part of the [Brand Kit](brand-kit.md) | v2.0
> Templates for Gemini image generation and Veo 3.1 video generation

---

## How to Use These Templates

1. Choose the template matching your slide type (hook, value, CTA, single post).
2. Replace all `[BRACKETED]` placeholders with actual content.
3. Determine the content pillar to set `[PILLAR_COLORS]` and `[PILLAR_ACCENT]`.
4. Generate at the specified dimensions.
5. Validate output against the quality checklist in [brand-carousel.md](brand-carousel.md).

---

## Pillar Color Reference (for prompt insertion)

| Pillar | `[PILLAR_COLORS]` | `[PILLAR_ACCENT]` |
|--------|-------------------|-------------------|
| AI + Product | gold (#b8a06a) and cream (#d4c48e) | gold (#b8a06a) |
| Leadership | sage (#8fab8a) and ivory (#f0ece4) | sage (#8fab8a) |
| Sustainability | blush (#d4b0a8) and peach (#e8cfc4) | blush (#d4b0a8) |
| Consciousness | lavender (#c4b8cc) and blush (#d4b0a8) | lavender (#c4b8cc) |

---

## Image Templates

### Base Prompt (shared foundation)

```
Generate a carousel slide image for Instagram.

Background: soft ivory (#f7f4ef) gradient.

Optional elements: Minimalist infographic illustrations in [PILLAR_COLORS] with subtle
grain texture overlay. The infographic illustrations should match the content topic.

Large centered headline: "[HEADLINE_TEXT]" in an elegant warm charcoal serif font.

Below it: "[BODY_TEXT]" in a smaller clean sans-serif font, muted warm gray tone.

At the bottom center: "@agentces" in small muted text.

Style: Ethereal, minimal, warm, grounded. Modern gradients with grain. Generous white
space. Scandinavian editorial feel. Minimalist infographic illustrations matching the content.

Dimensions: 1080 x 1350px portrait.

IMPORTANT: Only render the quoted text as visible text on the slide. Do NOT render font
names, pixel sizes, hex codes, or weight numbers as visible text.

NEVER: dark backgrounds, neon colors, stock photography, heavy shadows, glossy effects,
cluttered layouts, more than 30 words of text.
```

### Negative Prompt (append to all image generations)

```
dark background, black background, neon colors, saturated colors, stock photography,
heavy shadows, glossy effects, cluttered layout, Flower of Life, photorealistic humans,
flat shapes, sharp edges, text rendering of hex codes or font names
```

---

### Hook Slide (Slide 1)

```
[BASE_PROMPT]

Additional requirements:
- Large headline text, maximum 10 words. Bold serif.
- Include gradient avatar ring element in upper portion using [PILLAR_COLORS].
- Small 3D gradient accent shape in background.
- Hook must answer: "Is this for me?" and "What do I get?"
- Headline color: warm charcoal (#3a352e). Optional: 1-2 key words in [PILLAR_ACCENT].
```

### Value Slide (Slides 2-8)

```
[BASE_PROMPT]

Additional requirements:
- One key idea. Clean layout.
- Optional: numbered step indicator in gold (#b8a06a).
- Small 3D gradient shape in [PILLAR_COLORS] as subtle accent.
- Text fills middle third of slide.
- Infographic illustration matching "[SLIDE_TOPIC]" topic.
```

### CTA Slide (Last Slide)

```
[BASE_PROMPT]

Additional requirements:
- Clear call-to-action text: "[CTA_TEXT]"
- Avatar ring centered using [PILLAR_COLORS] gradient.
- 3D gradient shape as soft background element.
- Warm, inviting feel.
- Include handle "@agentces" and name prominently.
```

### Single Post Image

```
[BASE_PROMPT]

Additional requirements:
- Single image, not part of a carousel.
- Headline is the primary visual element.
- Infographic illustration matching "[POST_TOPIC]" topic.
- If content aligns with a pillar, use [PILLAR_COLORS] for accent shapes.
- Dimensions: 1080 x 1350px (IG) or 1080 x 1080px (FB).
```

---

## Structured Config (for programmatic use)

When building prompts programmatically (e.g., `gen_multimodal_slides.py`), use this JSON structure:

```json
{
  "slide_type": "hook | value | cta | single",
  "pillar": "ai_product | leadership | sustainability | consciousness",
  "headline": "Your headline text here",
  "body": "Optional body text",
  "cta_text": "Save this for later",
  "slide_number": 1,
  "total_slides": 10,
  "topic": "Brief description of slide topic for illustration matching",
  "media_type": "image | video",
  "video_mode": "text-to-video | image-to-video",
  "dimensions": {
    "width": 1080,
    "height": 1350
  }
}
```

---

## Video Templates

See [brand-video.md](brand-video.md) for complete Veo 3.1 prompt templates. Key differences from image prompts:

- Add motion direction (camera push, gentle zoom, element drift)
- Specify duration (4s for hooks, 6s for re-engagement)
- Include the negative prompt specific to video
- Text must remain static — motion applies to visual elements only

---

## Prompt Construction Workflow

```
1. Identify content pillar → set PILLAR_COLORS and PILLAR_ACCENT
2. Determine slide type → select template (hook/value/CTA/single)
3. Write headline (< 10 words for hook, < 30 words for value)
4. Write body text if applicable
5. Describe the illustration topic for context matching
6. Assemble prompt from BASE_PROMPT + slide-specific additions
7. Append negative prompt
8. Generate at 1080 x 1350px
9. Validate against brand-carousel.md quality checklist
```
