# Presentation QA Checklist

Run this checklist at Step 7 (Quality Check) after Canva generates the deck. Review thumbnails of key slides and score each category.

---

## QA Process

1. After `create-design-from-candidate`, start an editing transaction to access thumbnails
2. Review thumbnails of: slide 1 (title), middle slide, and last slide at minimum
3. For decks 10+ slides, also check the hook slide, one data slide, and the CTA slide
4. Score each category below as PASS or FAIL
5. If any category is FAIL, use editing operations to fix before committing
6. Present QA summary to user before exporting

---

## Category 1: Narrative Flow

| Check | Criteria |
|-------|----------|
| Hook present | Slide 1 or 2 uses one of the 5 hook types (stat, bold claim, question, story, visual) |
| Arc coherence | Slides follow the selected framework structure (Pyramid, Sparkline, Raskin, etc.) |
| One idea per slide | Each slide communicates exactly one assertion |
| Transitions | Section dividers or breathing slides exist between major topic shifts |
| CTA present | Last content slide has a specific, actionable call to action |
| No dead slides | Every slide earns its place. Remove slides that repeat or add no new value |

---

## Category 2: Glance Test

| Check | Criteria |
|-------|----------|
| 3-second rule | Each slide's point is graspable within 3 seconds |
| Headline is an assertion | Headlines are sentences (claims), not topic labels |
| One dominant element | Each slide has one focal point, not competing visuals |
| Readable at distance | Text is large enough for the intended context (30pt+ default) |
| No walls of text | No slide exceeds 6 lines or 36 words of body text |

---

## Category 3: Visual Consistency

| Check | Criteria |
|-------|----------|
| Color discipline | Max 3-5 colors used across the deck (excluding black/white/gray) |
| Color meaning | Same color means the same thing on every slide |
| Font consistency | Max 2 font families. Headlines consistent, body consistent |
| Layout rhythm | Margins, alignment, and spacing feel consistent across slides |
| Whitespace | At least 25-30% of each slide is empty space |
| No chartjunk | Charts are clean: no 3D effects, gradient fills, unnecessary gridlines |
| Brand alignment | Colors and style match the resolved brand identity from BRAND_DOCS_DIR |

---

## Category 4: Content Density

| Check | Criteria |
|-------|----------|
| Font size | No text below 28pt (14pt acceptable for sources/footnotes only) |
| Bullet limit | No slide has more than 6 bullet points |
| Chart headlines | Every chart/data slide has an assertion headline explaining the insight |
| Quote length | Quotes are 3 sentences or fewer |
| Redundancy | No slide duplicates content from another slide |

---

## QA Summary Format

Present to user:

```
Presentation QA: [Title]
Framework: [Selected framework]
Slides: [count]
Brand: [resolved location/brand]

Narrative Flow:     [PASS/FAIL] - [note if FAIL]
Glance Test:        [PASS/FAIL] - [note if FAIL]
Visual Consistency: [PASS/FAIL] - [note if FAIL]
Content Density:    [PASS/FAIL] - [note if FAIL]

Issues found: [count]
[List specific issues if any]

Recommendation: [Ready to export / Needs editing]
```

---

## Fixing Failures

If QA reveals issues, use the editing transaction to fix:

| Issue | Fix via editing |
|-------|----------------|
| Too much text | `replace_text` to shorten, or `delete_element` to remove |
| Wrong headline type | `replace_text` to rewrite as assertion |
| Missing CTA | Cannot add new slides via editing. Note for user |
| Color inconsistency | `format_text` to adjust text colors |
| Low contrast | `format_text` to change text color for readability |
| Misaligned elements | `position_element` to reposition |

Limitations of Canva editing:
- Cannot add new slides (use `merge-designs` to insert pages from another design)
- Cannot change font family (only size, weight, style)
- Cannot change background colors directly
- If structural issues are found (wrong slide order, missing sections), recommend regenerating with an updated outline
