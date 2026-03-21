# content-plan.md Format

The plan file uses markdown headers and **bold key:** value pairs that are human-editable and machine-parseable. Draft text goes in fenced `draft` blocks. Visual prompts go in fenced `prompt` blocks.

## Parsing Contract

- Days are delimited by `## Day N` headers.
- Posts within days are delimited by `### Post N` headers.
- Key-value fields use the pattern `**key:** value`.
- Draft text lives between ` ```draft ` and ` ``` ` fences.
- Visual prompts live between ` ```prompt ` and ` ``` ` fences.
- The Summary table at the bottom is informational only. The source of truth is the individual day/post sections.
- Empty `**Post ID:**` means not yet published.
- After publishing, update `**Status:**` from `draft` to `scheduled` and fill in `**Post ID:**`.

## File Structure

```markdown
# Weekly Content Plan

**Generated:** YYYY-MM-DD
**Date range:** YYYY-MM-DD to YYYY-MM-DD
**Platforms:** Facebook, Instagram
**Total posts:** N
**Status:** draft

---

## Day 1 -- [Weekday], [Month Day]

**Theme:** [topic for this day]
**Content pillar:** [AI | Leadership | Health | Consciousness | General]
**Visual:** yes | no
**Visual source:** gemini | url | ghl_media
**Visual prompt:**
```

```prompt
[Full Gemini prompt using template from brand-visuals.md]
```

```markdown

### Post 1 -- [Platform]

**Platform:** [facebook | instagram | linkedin | twitter | tiktok | gmb]
**Account:** [shorthand from ghl_accounts_map.json: FB, IG, LI, X, etc.]
**Type:** [single image | carousel (N slides) | text-only]
**Schedule:** [ISO 8601 datetime]
**Status:** draft
**Post ID:**
```

```draft
[FULL post content here. Line breaks between ideas. Short sentences.
Brand voice. Proper emoji usage. The actual post as it would be published.
Not a summary. Not bullet points.]
```

```markdown

### Post 2 -- [Platform]

[Same structure, adapted for this platform's voice and limits]

---

## Day N -- [Weekday], [Month Day] (carousel)

**Theme:** [topic]
**Content pillar:** [pillar]
**Visual:** yes
**Visual source:** gemini

**Carousel slides:**

| Slide | Type | Text |
|-------|------|------|
| 1 | hook | [Under 10 words] |
| 2 | second hook | [Standalone scroll-stopper] |
| 3 | value | [One idea] |
| ... | ... | ... |
| N | cta | [Clear single CTA] |

**Slide prompts:**
```

```prompt
Slide 1 (Hook): [Carousel Hook template filled in]
Slide 2 (Second Hook): [Carousel Value template filled in]
Slides 3-7 (Value): [Carousel Value template filled in per slide]
Slide 8 (CTA): [Carousel CTA template filled in]
```

```markdown

### Post 1 -- Instagram (Carousel)

**Platform:** instagram
**Account:** IG
**Type:** carousel (8 slides)
**Schedule:** [ISO 8601]
**Status:** draft
**Post ID:**
```

```draft
[Full carousel caption. Mini blog post style. Keyword in first sentence.
First 125 chars hook for Instagram "more" cutoff.
Personal story or context that complements the slides.

#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5]
```

```markdown

---

## Summary

| Day | Date | Theme | Type | Platforms | Status |
|-----|------|-------|------|-----------|--------|
| 1 | [date] | [theme] | [type] | FB, IG | draft |
| 2 | [date] | [theme] | [type] | FB, IG | draft |
| ... | ... | ... | ... | ... | ... |
```
