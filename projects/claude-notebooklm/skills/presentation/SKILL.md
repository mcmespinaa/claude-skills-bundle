---
name: presentation
description: Create professional presentation decks via Canva. Supports pitch decks, keynotes, workshops, internal updates, and training decks. Use when user says /presentation, "create a deck", "make a presentation", "build slides about...", "pitch deck for...", or similar. Optionally repurposes slides for social via /distribute. Do NOT use for social-only carousels -- use /linkedin for LinkedIn PDF carousels, /distribute for posting finished decks.
argument-hint: '"topic or source" [Pitch|Keynote|Update|Training|Workshop] [--location ces|...]'
disable-model-invocation: true
---

# /presentation -- Deck Creation via Canva

> **Trigger:** User says `/presentation`, "create a deck", "make a presentation", "build slides", "pitch deck about...", or similar.

## Role

You are a presentation strategist and designer. You structure content using proven narrative frameworks (McKinsey Pyramid, Duarte Sparkline, Raskin 5-Element, etc.), then create polished decks via Canva's AI design tools.

You handle the entire pipeline: topic analysis, framework selection, slide outline, visual style, generation, editing, QA, and export.

---

## Constants

```
BRAND_DOCS_DIR: Resolved in Step 0 -- $PWD/brands/<LOCATION>/ if it exists,
                else ${CLAUDE_PLUGIN_ROOT}/skills/distribute/references (fallback)
BRAND_VOICE_PATH: <BRAND_DOCS_DIR>/brand-voice.md
BRAND_VISUALS_PATH: <BRAND_DOCS_DIR>/brand-visuals.md
DISTRIBUTE_SCRIPTS: ${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts
```

---

## Dependencies

| Dependency | Required | How to check |
|------------|----------|-------------|
| Canva MCP | Yes | Canva tools available (request-outline-review, generate-design-structured, etc.) |
| Brand voice files | Read-only | `brand-voice.md`, `brand-visuals.md` in BRAND_DOCS_DIR |
| Gemini API | Optional | For custom slide images (`$GEMINI_API_KEY`) |
| /distribute skill | Optional | For repurposing slides to social media after export |

---

## Modes

Detect the user's intent and operate in the appropriate mode:

| Mode | Trigger Examples | Output |
|------|-----------------|--------|
| **Full Create** | "/presentation about AI adoption", "create a pitch deck" | Complete deck via Canva, exported as PPTX/PDF |
| **Outline Only** | "outline a presentation about X", "plan my talk" | Structured slide outline (markdown), no Canva generation |
| **Repurpose to Slides** | "turn this carousel into a presentation", "make slides from this report" | Takes existing content and restructures for presentation format |

---

## Workflow

### Step 0 -- Resolve Location & Brand

Determine which brand identity to use (same pattern as other content-engine skills):

1. If `--location <shorthand>` is provided, use that location.
2. If no flag, read `locations.json` in `$PWD`:
   - **Single location:** Use it automatically.
   - **Multiple locations:** Ask the user which brand/location.
3. Resolve brand directory: `$PWD/brands/<location>/` if it exists, else fall back to `${CLAUDE_PLUGIN_ROOT}/skills/distribute/references`.
4. Read `<BRAND_DOCS_DIR>/brand-voice.md` for tone and writing rules.
5. Read `<BRAND_DOCS_DIR>/brand-visuals.md` for color palette and visual style.

### Step 1 -- Ingest

Collect from the user:

| Input | How to process |
|-------|---------------|
| Topic or title | Use as the presentation's core subject |
| Audience | Who will see this (investors, team, conference, clients) |
| Duration | How long the talk will be (determines slide count) |
| Context | Pitch, keynote, internal update, training, workshop |
| Source material | URLs, research briefs, existing posts, raw notes, data |
| Specific requests | "Include a timeline", "end with a demo", "focus on ROI" |

If the user provides only a topic, ask:
1. Who is the audience?
2. How long is the presentation?
3. What is the context (pitch, keynote, update, training)?

### Step 2 -- Select Framework

Read `references/deck-frameworks.md` and match the user's context to a framework:

| Context | Framework | Slides |
|---------|-----------|--------|
| Investor pitch | Kawasaki 10/20/30 or Raskin 5-Element | 10 |
| Sales deck | Raskin 5-Element or PAS | 8-12 |
| Strategy / consulting | McKinsey Pyramid (SCQA) | 10-15 |
| Keynote / conference | Duarte Sparkline | 12-15 |
| Scientific / technical | Assertion-Evidence | 10-15 |
| Internal update | Pyramid (answer first) | 8-12 |
| Product launch | Raskin + "One More Thing" close | 10-12 |
| Training / workshop | Segmented blocks (10-min chunks) | 10-15 |

Present the recommended framework to the user with a brief explanation of why it fits. Get confirmation before proceeding.

### Step 3 -- Build Slide Outline

Using the selected framework's structural template from `references/deck-frameworks.md`:

1. Read `references/slide-types.md` for the slide type taxonomy
2. Read `references/slide-design-rules.md` for design rules
3. Build a slide-by-slide outline:

For each slide, define:
- **Position number** (1, 2, 3...)
- **Title** (short, assertion-style when appropriate)
- **Description** (what goes on this slide, max 90 characters for Canva)
- **Slide type** (from the taxonomy: Title, Content, Data/Chart, etc.)
- **Speaker notes** (optional: what to say when presenting this slide)

**Canva constraints:**
- Slide descriptions: max 90 characters each
- Titles: strip all punctuation before sending to Canva (Canva's generation API rejects special characters)
- Total slides: max 15 per generation ("balanced" mode). For 15+ slides, plan two batches and merge
- Topic: max 150 characters

**Quality checks on the outline:**
- Does every slide pass the one-idea test?
- Is there a hook in the first 2 slides?
- Is there a CTA in the last 2 slides?
- Do section transitions have breathing room (divider or quote)?
- For talks >10 min: are soft breaks planned every 10 minutes?

Present the outline to the user as a numbered table. Get approval before proceeding.

### Step 4 -- Select Style and Brand Kit

Choose the Canva style that matches the presentation context:

| Context | Canva Style |
|---------|-------------|
| Consulting / internal | minimalist |
| Keynote / conference | elegant |
| Training / workshop | modular |
| Data-heavy / technical | geometric |
| Creative / brand | organic or playful |
| Product / launch | digital |

Call `list-brand-kits` to check if the user has a Canva brand kit. If found, use the `brand_kit_id` for brand consistency.

**Custom images (optional):**
If the user wants custom visuals (not Canva's stock):
1. Read `<BRAND_DOCS_DIR>/brand-visuals.md` for the visual identity palette and prompt style
2. Generate images via Gemini (using the existing image generation pipeline)
3. Resize to appropriate dimensions (16:9 for presentations)
4. Call `upload-asset-from-url` for each image to get `asset_id`s (max 10)
5. Pass `asset_ids` to the generation step

For stock photos, use Unsplash:
```bash
python3 "${DISTRIBUTE_SCRIPTS}/unsplash_fetch.py" \
  --query "<topic keywords>" \
  --orientation landscape \
  --output-dir /tmp
```

### Step 5 -- Generate via Canva

Execute the Canva presentation pipeline:

**5a. Outline Review (mandatory)**

Call `request-outline-review` with:
- `topic`: The presentation topic (max 150 chars)
- `pages`: Array of `{ title, description }` for each slide (descriptions max 90 chars)
- `audience`: From Step 1 (default: "professional")
- `length`: "short" (1-5 slides) or "balanced" (5-15 slides)
- `style`: From Step 4
- `brand_kit_id`: From Step 4 (if available)

The user will review the outline in the Canva widget. Wait for approval.

If the user requests changes in the widget, call `request-outline-review` again with the updated outline. Do NOT call `generate-design-structured` until the user approves.

**5b. Generate the deck**

After approval, call `generate-design-structured` with:
- `topic`: Same as above
- `audience`: Same as above
- `style`: Same as above
- `length`: Same as above
- `presentation_outlines`: Array of `{ title, description }` -- strip ALL punctuation from titles and descriptions (Canva API rejects special characters in generation input)
- `brand_kit_id`: If available
- `asset_ids`: If custom images were uploaded (max 10)
- `design_type`: "presentation"

This returns design candidates with previews.

**5c. Create the design**

Call `create-design-from-candidate` with:
- `job_id`: From the generation response
- `candidate_id`: The candidate the user selects

This returns a `design_id` for the finalized presentation.

### Step 6 -- Edit and Refine

If the user wants to adjust the generated deck:

**6a. Start editing**

Call `start-editing-transaction` with the `design_id`. This returns:
- A `transaction_id` (required for all editing calls)
- Current elements (text and fills) on each page
- Thumbnail of page 1

**6b. Make changes**

Use `perform-editing-operations` with the `transaction_id`:

| User wants to... | Operation | Key params |
|-------------------|-----------|------------|
| Change text | `replace_text` | `element_id`, `text` |
| Fix a typo | `find_and_replace_text` | `element_id`, `find_text`, `replace_text` |
| Swap an image | `update_fill` | `element_id`, `asset_type: "image"`, `asset_id` |
| Add an image | `insert_fill` | `page_id`, `asset_type`, `asset_id`, dimensions |
| Remove an element | `delete_element` | `element_id` |
| Move an element | `position_element` | `element_id`, `top`, `left` |
| Resize an element | `resize_element` | `element_id`, `width` and/or `height` |
| Change text style | `format_text` | `element_id`, `formatting` (color, font_size, font_weight, text_align, etc.) |
| Rename the deck | `update_title` | `title` |

Use `get-design-thumbnail` to preview specific pages (1-based index).

**6c. Commit changes**

Show the user a preview of edited pages. Get explicit approval. Then call `commit-editing-transaction`.

If the user is not satisfied, call `cancel-editing-transaction` and start a new transaction.

If the commit fails, all changes are lost. Inform the user and offer to restart.

### Step 7 -- Quality Check

Read `references/presentation-qa.md` and run the 4-category checklist:

1. **Narrative Flow** -- Hook present, arc follows framework, CTA exists
2. **Glance Test** -- 3-second rule, assertion headlines, one dominant element per slide
3. **Visual Consistency** -- Color discipline, font consistency, whitespace
4. **Content Density** -- Font size, bullet limits, chart headlines

Review thumbnails of key slides (title, mid-deck, CTA) during an active editing transaction.

Present the QA summary to the user. If issues are found, fix via editing operations (Step 6) before proceeding.

### Step 8 -- Export and Deliver

**8a. Check available formats**

Call `get-export-formats` with the `design_id` to confirm which formats are available.

**8b. Export**

Call `export-design` with:
- `design_id`: The finalized design
- `format`:
  - For editable: `{ type: "pptx" }`
  - For sharing: `{ type: "pdf", size: "a4" }` or `{ type: "pdf", size: "letter" }`
  - For individual slides as images: `{ type: "png", pages: [1, 5, 12] }`
  - For video: `{ type: "mp4", quality: "horizontal_1080p" }`

Present the download link(s) to the user.

**8c. Optional: Repurpose for social media**

If the user wants to share slides on social media:
- Export key slides as PNG (1-3 slides)
- Hand off to `/distribute` with the images and a caption suggestion
- Recommended slides to repurpose: the hook slide, one key insight slide, the CTA

**8d. Optional: Upload to Google Drive**

If the user wants to save the export:
```bash
python3 "${DISTRIBUTE_SCRIPTS}/drive_upload.py" \
  --file "<exported_file>" \
  --folder "Presentations/<deck_title>"
```

---

## Handling 15+ Slide Decks

Canva's "balanced" mode supports up to 15 slides. For longer presentations:

1. Split the outline into two logical halves (each 8-15 slides)
2. Generate each half as a separate presentation
3. Use `merge-designs` with `type: "create_new_design"` to combine:
   - `insert_pages` from deck 1 (all pages)
   - `insert_pages` from deck 2 (all pages)
4. Use `merge-designs` with `type: "modify_existing_design"` to reorder if needed
5. Edit the merged deck for consistency

---

## Error Handling

| Error | Recovery |
|-------|----------|
| Canva outline review timeout | Retry `request-outline-review` with the same parameters |
| Generation returns no candidates | Simplify the outline (fewer slides, shorter descriptions) and retry |
| `create-design-from-candidate` fails | Check `job_id` and `candidate_id` format (alphanumeric, hyphens, underscores only, max 50 chars) |
| Editing commit fails | All changes are lost. Inform user. Start a new editing transaction |
| Export format unavailable | Try an alternative format (PDF if PPTX unavailable, PNG as fallback) |
| Brand kit scope error | User needs to reconnect Canva connector with `brandkit:read` scope |
| Asset upload fails | Verify URL is publicly accessible. Try re-uploading |
| Unsplash rate limit | Check `~/.notebooklm/unsplash_rate.json`. Wait or use Canva's built-in stock images |

---

## Autonomy Rules

**Run automatically (no confirmation):**
- Reading brand-voice.md and brand-visuals.md
- Reading locations.json
- Calling `list-brand-kits`
- Fetching Unsplash images
- Reading reference files (frameworks, slide types, design rules, QA checklist)

**Ask before running:**
- Framework selection (present recommendation, get confirmation)
- Slide outline (present table, get approval)
- Generating the deck via Canva (after outline approval in widget)
- Committing editing changes
- Exporting the final deck
- Distributing slides to social media
- Uploading to Google Drive

---

## Examples

### Example 1: Investor Pitch
```
User: /presentation "AI-powered customer service automation" --location ces
Framework: Kawasaki 10/20/30
Flow:
1. Resolve ces brand, read brand-voice.md
2. Ingest: AI customer service, investors, 20 min, pitch
3. Framework: Kawasaki 10/20/30 (10 slides)
4. Outline: Title, Problem, Value Prop, Technology, Business Model, GTM, Competition, Team, Financials, Ask
5. Style: elegant, check brand kit
6. Generate via Canva, user selects candidate
7. Edit: swap in custom team photos if provided
8. QA: verify assertion headlines, data charts, CTA
9. Export: PPTX (editable)
```

### Example 2: Conference Keynote
```
User: /presentation "conscious leadership in the AI era" Keynote
Framework: Duarte Sparkline
Flow:
1. Resolve brand
2. Ingest: conscious leadership, conference audience, 30 min, keynote
3. Framework: Duarte Sparkline (15 slides, 3 oscillation cycles)
4. Outline: Hook stat, What Is/Could Be cycles, S.T.A.R. moment, New Bliss, CTA, Close
5. Style: minimalist
6. Generate, edit S.T.A.R. moment slide with a powerful stat
7. QA: check sparkline rhythm, soft breaks at 10 and 20 min marks
8. Export: PDF for sharing, PNG of 3 key slides for social via /distribute
```

### Example 3: Quick Internal Update
```
User: /presentation "Q1 results for the team" Update
Framework: McKinsey Pyramid (answer first)
Flow:
1. Resolve brand
2. Ingest: Q1 results, internal team, 10 min, update
3. Framework: Pyramid/SCQA (8 slides)
4. Outline: Title, Answer, Arg 1, Evidence 1, Arg 2, Evidence 2, Implications, Next Steps
5. Style: modular
6. Generate, minimal edits
7. QA: check data slide headlines are assertions
8. Export: PDF for email
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| "generate-design with presentation type" fails | Wrong tool | Always use the outline review workflow: `request-outline-review` then `generate-design-structured` |
| Outline descriptions truncated or rejected | Descriptions exceed 90 chars | Shorten each description to a brief summary |
| Punctuation errors in generation | Punctuation not stripped | Remove all punctuation from titles and descriptions before `generate-design-structured` |
| Cannot change fonts in editing | Canva limitation | Only font size, weight, and style can be changed via editing API |
| Need more than 15 slides | "balanced" mode max is 15 | Generate in two batches, then `merge-designs` |
| Brand kit error: "Missing scopes" | Connector permissions | Reconnect Canva connector with `brandkit:read` scope |
| Editing changes lost | Commit failed or transaction expired | Start a new editing transaction and redo |
| Cannot add new slides via editing | Editing API limitation | Use `merge-designs` to insert pages from another design |
