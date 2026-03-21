# Task 4 -- Plan Visuals

Design one visual per day. All posts on the same day share the same image.

## Before Writing Prompts

Read `${CLAUDE_SKILL_DIR}/../../shared/references/brand-visuals.md` for prompt templates, palette, and typography rules.

## Visual Source Decision

| Source | When to use | What to include in plan |
|--------|-------------|------------------------|
| Gemini image generation | Default for most days | Full prompt using templates from brand-visuals.md |
| User-provided image URL | User gave image URLs as input | Assign URL to appropriate day |
| GHL Media Library | User references existing assets | Note "Use existing: [description]" |

## Gemini Prompt Rules

1. Single image day: use base prompt template. Fill in headline and body text from the day's post content.
2. Carousel day: use Hook Slide, Value Slide, and CTA Slide variants. One prompt per slide.
3. Add content pillar accent color if the day's theme aligns:
   - AI = gold #b8a06a
   - Leadership = sage #8fab8a
   - Health/Sustainability = blush #d4b0a8
   - Consciousness = lavender #c4b8cc
4. All visuals: ivory background (#f7f4ef), warm charcoal text (#3a352e), infographic illustrations, 4:5 portrait (1080 x 1350 px).

## Output

A visual plan per day with either:
- Full Gemini prompts ready for generation
- URLs to user-provided images
- References to existing GHL media

Proceed to Task 5 when all visual plans are written.
