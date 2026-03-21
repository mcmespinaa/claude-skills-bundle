# BRAND VISUAL IDENTITY — Ces (Maria Cecilia)

> **Note:** This is the legacy combined reference. It remains valid but has been split into modular files for easier maintenance. For the latest specs, start from **[brand-kit.md](brand-kit.md)** which links to:
> - [brand-colors.md](brand-colors.md) — palette + accessibility
> - [brand-typography.md](brand-typography.md) — fonts + spacing
> - [brand-illustrations.md](brand-illustrations.md) — visual elements + spacing system
> - [brand-carousel.md](brand-carousel.md) — slide specs + safe zones
> - [brand-video.md](brand-video.md) — Veo 3.1 specs
> - [brand-prompts.md](brand-prompts.md) — AI generation templates

Read this file before generating any visual content. Every image, carousel slide, social graphic, and branded asset must follow these specs.

---

## FEEL

Ethereal, warm, grounded, intentional. A space where product strategy and consciousness coexist without contradiction. Think: soft morning light in a Scandinavian studio. Minimalist Aesthetics, infographic illustrations that matches given contexts and copy. Generous white space. Nothing loud. Everything deliberate.

---

## COLOR PALETTE

### Backgrounds
- Primary: #f7f4ef (Ivory)
- Secondary: #f0ece4 (Warm Linen)
- Card/elevated: #faf8f4
- Pure white: #ffffff (sparingly, card surfaces only)

### Accent Colors (one per pillar)
- Gold (AI + Product pillar): #b8a06a primary, #d4c48e light
- Sage (Leadership pillar): #8fab8a
- Blush (Sustainability pillar): #d4b0a8
- Lavender (Consciousness pillar): #c4b8cc

### 3D Gradient Palette (for project cards, hero backgrounds, decorative elements)
- Lavender-blush: #c4b8cc → #d4b0a8 (with subtle blue-gray: #b8c4d4)
- Sage-gold: #8fab8a → #d4c48e (with warm cream: #e8dfc8)
- Blush-peach: #d4b0a8 → #e8cfc4 (with soft teal: #a8c8c4)
- Lavender-sage: #c4b8cc → #8fab8a (with ivory: #f0ece4)

### Text
- Primary: #3a352e (Warm Charcoal)
- Secondary: #7a7268
- Muted/caption: #b0a898

### Glows and Overlays
- Gold glow: rgba(184,160,106,0.12)
- Sage glow: rgba(143,171,138,0.12)
- Blush glow: rgba(212,176,168,0.10)
- Lavender glow: rgba(196,184,204,0.08)

### RULES
- Never use dark or black backgrounds.
- Never use saturated, neon, or high-contrast colors.
- Background should always be ivory or warm linen.
- Accent colors appear as subtle washes, gradient blobs, tags, or fine linework. Never as solid blocks.

---

## TYPOGRAPHY

### Headlines and Hooks
- Font: Playfair Display
- Weight: 500-600
- Style: Regular or Italic for emphasis
- Size range: 28-52px (carousel), 42-62px (web)
- Color: #3a352e (Warm Charcoal) or #b8a06a (Gold, for emphasis words)

### Body Text
- Font: DM Sans
- Weight: 400-500
- Size range: 12-20px
- Color: #7a7268 (secondary) or #3a352e (primary)

### RULES
- Maximum 2 fonts per slide or graphic.
- Headlines always in Playfair Display. Body always in DM Sans.
- No all-caps except for small labels/eyebrows (11-12px, letter-spacing 2-3px).

---

## CAROUSEL SLIDE SPECS

### Dimensions
- Aspect ratio: 4:5 portrait
- Resolution: 1080 x 1350px
- Slide count: 8-10 (sweet spot), 12-20 for deep guides only

### Content Limits
- Hook slide (Slide 1): Under 10 words. Specific. Use numbers.
- Value slides (Slides 2-8): One idea per slide. Max 30 words.
- CTA slide (last): One clear action (Save, Send, Follow, or DM).

### Layout
- Text centered vertically, biased slightly above center.
- Generous margins (minimum 80px from edges).
- One idea per slide. White space is essential.
- Minimalist Aesthetics, infographic illustrations that matches given contexts and copy.
---

## VISUAL ELEMENTS

### Illustrations
- Minimalist Aesthetics, infographic illustrations that matches given contexts and copy.
- Stroke style: Fine lines (0.5-1px), in lavender (#c4b8cc) and gold (#d4c48e).

**Style:**
- Soft infographic illustration
- Multi-color gradients blending 2-3 brand accent colors.
- Subtle grain/noise texture overlay (2-5% opacity) for modern feel.
- Soft shadows and reflections for depth.
- Background: muted gradient (lavender-gray, blush-cream, or sage-ivory).

**Color Combinations for 3D Shapes:**
- AI + Product: Gold → cream → soft warm gray
- Leadership: Sage → ivory → soft blue-gray
- Sustainability: Blush → peach → soft teal
- Consciousness: Lavender → blush → soft silver

### Tags and Badges
- Pill-shaped (border-radius: 100px)
- Background: pillar glow color (12% opacity)
- Text: pillar accent color
- Font: DM Sans, 12px, 500 weight

---

## CAROUSEL HOOK FORMULAS

Use these structures for Slide 1 headlines:

1. Contrarian: "Stop doing [common practice]. Do this instead."
2. Specific Result: "How I [outcome] in [timeframe]"
3. Identity Call-Out: "This is for every [role] who [frustration]"
4. List With Stakes: "[Number] things [costing/saving] you [outcome]"
5. Vulnerable Story: "I [personal struggle]. Here's what changed."
6. Myth Breaker: "Everyone says [belief]. The data says otherwise."

---

## IMAGE GENERATION PROMPT TEMPLATE

When generating images through Gemini or any AI image tool, use this base prompt and customize the bracketed sections:

```
Generate a carousel slide image for Instagram.

Background: soft ivory (#f7f4ef) soft gradient.

Optional elements: Minimalist Aesthetics, infographic illustrations that matches given contexts and copy in [PILLAR COLORS] with subtle grain texture overlay. The infographic  illustrations should match the context, dimensional, and modern.

Text area: [HEADLINE TEXT] in elegant serif font (Playfair Display style), warm charcoal (#3a352e) color, centered. Weight 500-600.

Subtext: [BODY TEXT] in clean sans-serif font (DM Sans style), muted tone (#7a7268), below headline.

Style: Ethereal, minimal, warm, grounded. Modern gradients with grain. Generous white space. Scandinavian editorial feel. Minimalist Aesthetics, infographic illustrations that matches given contexts and copy.

Dimensions: 1080 x 1350px portrait.

NEVER: dark backgrounds, neon colors, stock photography, heavy shadows, glossy effects, cluttered layouts, more than 30 words of text.
```

### Slide-Specific Variants

**Hook Slide (Slide 1):**
```
[Base prompt] +
Large headline text, maximum 10 words. Bold serif. Include avatar ring element in upper portion. Small 3D gradient accent shape in background. Hook must answer: "Is this for me?" and "What do I get?"
```

**Value Slide (Slides 2-8):**
```
[Base prompt] +
One key idea. Clean layout. Optional: numbered step indicator in gold. Small 3D gradient shape or Seed of Life accent. Text fills middle third of slide.
```

**CTA Slide (Last Slide):**
```
[Base prompt] +
Clear call-to-action: "Save this" or "Send to a friend who needs this." Avatar ring centered. 3D gradient shape as soft background. Warm, inviting feel. Include handle/name.
```

---

## DO / DON'T

### DO
- Use ivory/cream gradient backgrounds with warm charcoal text.
- Add subtle grain/noise texture to gradient shapes for modern feel.
- Keep slide text under 30 words.
- Use Playfair Display for headlines, DM Sans for body.
- Include gradient avatar ring on hook slides.
- Use soft washes of gold/sage/blush/lavender as background accents.
- Keep emojis to 1-2 per slide (if any).
- Use specific numbers in hooks.
- Mix in 1-2 short video clips per carousel to spike dwell time.
- Put CTA twice: one soft mid-carousel, one clear on last slide.

### DON'T
- Use Flower of Life
- Use dark or black backgrounds.
- Use em dashes (commas, periods, or ellipsis instead).
- Use more than 2 fonts per slide.
- Use stock photos or generic illustrations.
- Use saturated or neon colors.
- Use any forbidden words (see brand-voice.md for full list).
- Overcrowd slides with text or elements.
- Use heavy drop shadows or glossy effects.
- Use hashtags on slides (captions only).
- Use flat or sharp-edged shapes (always soft, organic, dimensional).

---

## SKILL INTEGRATION

### Where This File Lives
```
/skills/post/brand-visuals.md
```

### How the Agent Uses It
1. Before generating any visual content, read `brand-visuals.md`.
2. Extract the relevant color palette, typography, and layout specs.
3. Build the Gemini prompt using the template above, customizing brackets.
4. Generate images at 1080x1350px (carousel) or specified dimensions.
5. Validate: Does the output match the "feel" section? Ethereal, warm, grounded, intentional? Are illustrations, looks minimalist Aesthetics, infographic illustrations that matches given contexts and copy

### SKILL.md Step Addition
Add after content generation, before publishing:

```
Step: Generate carousel visuals
Input: Read brand-visuals.md for style specs + slide content from previous step
Action: For each slide, construct a Gemini image prompt using the template.
  - Slide 1: Use Hook Slide variant
  - Slides 2-N: Use Value Slide variant
  - Last slide: Use CTA Slide variant
  - Apply pillar-specific accent color and 3D gradient combo based on post topic
Output: PNG files at 1080x1350px, one per slide, saved to /output/carousel/
Validation: Check ivory background, serif headline, max 30 words, 3D gradient shapes present, no dark elements
```
