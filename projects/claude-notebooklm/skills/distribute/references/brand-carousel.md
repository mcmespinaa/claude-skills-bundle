# BRAND CAROUSEL SPECS — Ces (Maria Cecilia)

> Part of the [Brand Kit](brand-kit.md) | v2.0
> See also: [CAROUSEL_GUIDE.md](CAROUSEL_GUIDE.md) for deep research and examples

---

## Dimensions

| Property | Value |
|----------|-------|
| Aspect ratio | 4:5 portrait |
| Resolution | 1080 x 1350 px |
| File format | PNG (preferred) or JPG |
| Max file size | < 1 MB per slide (prevents platform compression artifacts) |
| Slide count | 8-10 (sweet spot), 12-20 for deep guides only |

---

## Safe Zone

All text and critical elements must stay within the safe zone:

```
┌──────────────────────────────┐
│         80px margin          │
│  ┌──────────────────────┐    │
│  │                      │    │
│  │                      │    │
│  │    SAFE ZONE         │    │
│  │    920 x 1190 px     │    │
│  │                      │    │
│  │                      │    │
│  │                      │    │
│  └──────────────────────┘    │
│         80px margin          │
│     ↑ handle area (40px) ↑   │
└──────────────────────────────┘
```

- **Minimum margins:** 80px from all edges
- **Handle placement:** Bottom center, within the bottom 40px of safe zone
- **Text vertical position:** Centered, biased slightly above center

---

## Slide Structure

### Slide 1 — Hook

| Property | Spec |
|----------|------|
| Purpose | Stop the scroll. Answer: "Is this for me?" and "What do I get?" |
| Word count | Under 10 words |
| Font | Playfair Display, 42-52px, weight 500-600 |
| Elements | Avatar ring (upper portion), 1 small 3D gradient shape |
| Handle | `@agentces` bottom center |

### Slide 2 — Second Hook

| Property | Spec |
|----------|------|
| Purpose | Stand alone as a scroll-stopper (Instagram re-shows carousels starting from slide 2) |
| Word count | Max 30 words |
| Must work | As if someone sees this slide first, without slide 1 context |

### Slides 3-8 — Value

| Property | Spec |
|----------|------|
| Purpose | Deliver one idea per slide |
| Word count | Max 30 words per slide |
| Layout | Text fills middle third of slide |
| Optional | Numbered step indicator in gold, small 3D gradient shape |
| Structure options | Step-by-step, myth vs. reality, before/after, numbered list, story arc |

### Mid-Carousel CTA (Slide 5 or 6)

| Property | Spec |
|----------|------|
| Purpose | Soft engagement prompt mid-scroll |
| Example | "Save this for later" or "Send to someone who needs this" |
| Style | Subtle, not a full CTA slide — integrated into a value slide |

### Last Slide — CTA

| Property | Spec |
|----------|------|
| Purpose | One clear action |
| Actions | Save, Send, Follow, or DM (pick one) |
| Elements | Avatar ring centered, 3D gradient shape as soft background |
| Handle | `@agentces` with name |

---

## Hook Formulas

Use these structures for Slide 1 headlines:

| # | Type | Template |
|---|------|----------|
| 1 | Contrarian | "Stop doing [common practice]. Do this instead." |
| 2 | Specific Result | "How I [outcome] in [timeframe]" |
| 3 | Identity Call-Out | "This is for every [role] who [frustration]" |
| 4 | List With Stakes | "[Number] things [costing/saving] you [outcome]" |
| 5 | Vulnerable Story | "I [personal struggle]. Here's what changed." |
| 6 | Myth Breaker | "Everyone says [belief]. The data says otherwise." |

---

## Slide Numbering

| Property | Spec |
|----------|------|
| Show indicators? | Optional. If used, place in upper-right corner |
| Format | `3/10` in DM Sans, 12px, `#b0a898` |
| When to use | Deep guides (12+ slides) to help readers track progress |
| When to skip | Standard 8-10 slide carousels |

---

## Mixed Media (Images + Video)

| Property | Spec |
|----------|------|
| Recommended placement | Slide 1 (hook video) + Slide 5 (re-engagement video) |
| Default split | 2 videos + 8 images for 10-slide carousel |
| Platform support | IG: YES, Threads: YES, FB: NO (image-only fallback) |
| Video duration | 4s (hook), 6s (re-engagement) |
| Video aspect ratio | 9:16 portrait |

See [brand-video.md](brand-video.md) for video generation specs.

---

## Quality Checklist

Run before uploading:

- [ ] All slides are 1080 x 1350 px, 4:5 ratio
- [ ] Background is ivory (`#f7f4ef`) or warm linen (`#f0ece4`)
- [ ] Text is warm charcoal (`#3a352e`), not black
- [ ] Max 30 words per slide
- [ ] One idea per slide
- [ ] Hook slide under 10 words
- [ ] Brand handle visible on each slide
- [ ] No text within 80px of edges
- [ ] Consistent visual style across all slides
- [ ] Accent colors match the content pillar
- [ ] No dark backgrounds, neon colors, or glossy effects
- [ ] Grain texture present on gradient shapes
