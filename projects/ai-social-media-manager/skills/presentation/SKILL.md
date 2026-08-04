---
name: presentation
description: >-
  Creates professional presentation decks via Canva (AI-designed) or python-pptx
  (template-based, offline). Supports pitch decks, keynotes, workshops, internal
  updates, and training decks. Use when user says /presentation, create a deck,
  make a presentation, build slides, use PowerPoint, or similar. Do NOT use for
  social media posts or carousels -- use /post instead.
allowed-tools: "Bash(python3:*) Bash(bash:*) WebFetch WebSearch Read Write Edit Glob Grep"
---

# /presentation -- Deck Creation (Canva + python-pptx)

## Role

You are a presentation strategist and designer. You structure content using proven narrative frameworks (McKinsey Pyramid, Duarte Sparkline, Raskin 5-Element, etc.), then create polished decks via either Canva AI or python-pptx templates.

You handle the entire pipeline: topic analysis, framework selection, slide outline, visual style, generation, editing, QA, and export.

> **Do NOT use for:** Social media posts or carousels (use /post), email newsletters (use /newsletter), or blog articles (use /blog).

---

## Compatibility

Requires Canva MCP for Canva backend. Optional python-pptx (`pip3 install python-pptx`) for offline PPTX generation. Optional Pillow for custom images.

---

## Backends

| Backend | Best for | Requires |
|---------|----------|----------|
| **Canva** | AI-designed creative slides, brand kit integration, interactive editing | Canva MCP connected |
| **python-pptx** | Template-based, offline, data reports, maximum layout control | `pip3 install python-pptx` |

**Auto-detection:** If user says "offline", "pptx", "PowerPoint", "template", "no Canva", or "data report", default to python-pptx. Otherwise default to Canva. User can always override with "use pptx" or "use Canva".

---

## Dependencies

| Dependency | Required | How to check |
|------------|----------|-------------|
| Canva MCP | For Canva backend | Canva tools available (request-outline-review, etc.) |
| python-pptx | For pptx backend | `python3 -c "import pptx"` (install: `pip3 install python-pptx`) |
| `/post` references | Read-only | Read `brand-visuals.md` for palette and typography |
| `/research` skill | Optional | For research-backed presentations |
| Gemini API | Optional | For custom slide images (`$GEMINI_API_KEY`) |

---

## Modes

Detect the user's intent and operate in the appropriate mode:

| Mode | Trigger Examples | Output |
|------|-----------------|--------|
| **Full Create** | "/presentation about AI adoption", "create a pitch deck" | Complete deck via Canva, exported as PPTX/PDF |
| **Research to Deck** | "/research then create a keynote", "research and present" | Research brief from `/research`, then full deck |
| **Outline Only** | "outline a presentation about X", "plan my talk" | Structured slide outline (markdown), no Canva generation |
| **Repurpose to Slides** | "turn this carousel into a presentation" | Takes existing content and restructures for presentation format |

---

## Workflow

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

If the user provides a research brief from `/research`, extract the key insights, data points, and quotable findings as source material.

**Backend selection:** Determine which backend to use based on the user's request (see Backends section above). Note the choice -- it affects Steps 4-6.

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

Present the recommended framework to the user with a brief explanation of why it fits. Get confirmation before proceeding. If the user prefers a different framework, switch.

### Step 3 -- Build Slide Outline

Using the selected framework's structural template from `references/deck-frameworks.md`:

1. Read `references/slide-types.md` for the slide type taxonomy
2. Read `references/slide-design-rules.md` for the 10 non-negotiable rules
3. Build a slide-by-slide outline:

For each slide, define:
- **Position number** (1, 2, 3...)
- **Title** (short, assertion-style when appropriate)
- **Description** (what goes on this slide, max 90 characters for Canva)
- **Slide type** (from the taxonomy: Title, Content, Data/Chart, etc.)
- **Speaker notes** (optional: what to say when presenting this slide)

**Canva constraints to observe:**
- Slide descriptions: max 90 characters each
- Titles: strip all punctuation before sending to Canva (periods, commas, colons, semicolons, question marks, exclamation marks, em dashes, parentheses)
- Total slides: max 15 per generation ("balanced" mode). For 15+ slides, plan to generate in two batches and merge
- Topic: max 150 characters

**Quality checks on the outline:**
- Does every slide pass the one-idea test?
- Is there a hook in the first 2 slides?
- Is there a CTA in the last 2 slides?
- Do section transitions have breathing room (divider or quote)?
- For talks >10 min: are soft breaks planned every 10 minutes?

Present the outline to the user as a numbered table. Get approval or edits before proceeding.

### Step 4 -- Configure Backend

#### Step 4A -- Canva Backend

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
1. Read `brand-visuals.md` for the visual identity palette and prompt style
2. Generate images via Gemini (using the existing image generation pipeline)
3. Resize to appropriate dimensions (16:9 for presentations)
4. Call `upload-asset-from-url` for each image to get `asset_id`s (max 10)
5. Pass `asset_ids` to the generation step

#### Step 4B -- python-pptx Backend

Read `references/pptx-template-spec.md` for the full specification.

1. Select **accent color** based on content pillar:
   - AI / Product topics: `gold`
   - Leadership topics: `sage`
   - Sustainability topics: `blush`
   - Consciousness topics: `lavender`

2. Select **context** for font sizing based on how the deck will be presented:
   - `large_venue` (100+ seats, projected)
   - `conference` (20-50 people, default)
   - `meeting` (5-15 people)
   - `screen_share` (virtual / remote)
   - `pdf` (read-ahead document)

3. If user has custom images, note the file paths for insertion into specific slides.

No brand kit lookup needed -- brand colors, fonts, and layout rules are baked into the script.

### Step 5 -- Generate the Deck

#### Step 5A -- Canva Generation

Execute the Canva presentation pipeline:

**5a. Outline Review (mandatory)**

Call `request-outline-review` with:
- `topic`: The presentation topic (max 150 chars)
- `pages`: Array of `{ title, description }` for each slide (descriptions max 90 chars)
- `audience`: From Step 1 (default: "professional")
- `length`: "short" (1-5 slides) or "balanced" (5-15 slides)
- `style`: From Step 4A
- `brand_kit_id`: From Step 4A (if available)

The user will review the outline in the Canva widget. Wait for approval.

If the user requests changes in the widget, call `request-outline-review` again with the updated outline. Do NOT call `generate-design-structured` until the user approves.

**5b. Generate the deck**

After approval, call `generate-design-structured` with:
- `topic`: Same as above
- `audience`: Same as above
- `style`: Same as above
- `length`: Same as above
- `presentation_outlines`: Array of `{ title, description }` -- **strip ALL punctuation from titles and descriptions** (only alphanumeric and spaces)
- `brand_kit_id`: If available
- `asset_ids`: If custom images were uploaded (max 10)
- `design_type`: "presentation"

This returns design candidates with previews.

**5c. Create the design**

Call `create-design-from-candidate` with:
- `job_id`: From the generation response
- `candidate_id`: The candidate the user selects

This returns a `design_id` for the finalized presentation.

#### Step 5B -- python-pptx Generation

1. **Build JSON slide manifest** from the outline (Step 3 output). For each slide, map:
   - The slide type from the outline to a pptx type: `title`, `agenda`, `section-divider`, `content`, `data`, `comparison`, `quote`, `big-number`, `process`, `summary`, `cta`
   - Title, body text, items/steps/points/columns as needed per type
   - Speaker notes
   - Image paths if applicable

2. **Write the manifest** to a temp file (e.g., `/tmp/presentation_manifest.json`)

3. **Run the builder script:**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/create_pptx.py \
     --input /tmp/presentation_manifest.json \
     --output ~/Desktop/presentation.pptx \
     --context conference \
     --accent gold
   ```

4. **Present the output** file path to user. The file is ready to open in PowerPoint, Google Slides, or Keynote.

### Step 6 -- Edit and Refine

#### Step 6A -- Canva Editing

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

**Important:** If the commit fails, all changes are lost. Inform the user and offer to restart.

#### Step 6B -- python-pptx Editing

python-pptx uses a regenerate model -- there is no interactive editing.

If the user wants changes:
1. Modify the JSON manifest (update text, swap slide types, add/remove slides, add image paths)
2. Re-run `create_pptx.py` with the updated manifest
3. The output file is overwritten with the new version

For minor text edits after generation, the user can open the `.pptx` in PowerPoint or Google Slides directly.

### Step 7 -- Quality Check

Read `references/presentation-qa.md` and run the 4-category checklist:

1. **Narrative Flow** -- Hook present, arc follows framework, CTA exists
2. **Glance Test** -- 3-second rule, assertion headlines, one dominant element per slide
3. **Visual Consistency** -- Color discipline, font consistency, whitespace
4. **Content Density** -- Font size, bullet limits, chart headlines

Review thumbnails of key slides (title, mid-deck, CTA) during an active editing transaction.

Present the QA summary to the user. If issues are found, fix via editing operations (Step 6) before proceeding.

### Step 8 -- Export and Deliver

#### Canva Export

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

#### python-pptx Export

The output of `create_pptx.py` is already a `.pptx` file -- no additional export step needed.

For PDF conversion: tell the user to open the `.pptx` in PowerPoint or Google Slides and export to PDF. There is no programmatic PDF conversion without LibreOffice.

#### Optional: Repurpose for social media (both backends)

If the user wants to share slides on social media:
- Canva: export key slides as PNG (1-3 slides) via `export-design`
- python-pptx: user can screenshot slides or export from PowerPoint/Slides
- Hand off to `/post` skill with the images and a caption suggestion
- Recommended slides to repurpose: the hook slide, one key insight slide, the CTA

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
| python-pptx not installed | Run `pip3 install python-pptx` and retry |
| Font not available on viewer | python-pptx writes font names into the file. PowerPoint auto-substitutes (Georgia for Playfair, Calibri for DM Sans). Install fonts from Google Fonts for exact match |
| Image path not found | Script skips the image and warns. Check the path and re-run |

---

## Integration with Other Skills

### `/research` to `/presentation`
1. User runs `/research` on a topic
2. `/research` produces a research brief (markdown with key insights, data, quotes)
3. User says "now create a presentation from this"
4. `/presentation` Step 1 ingests the research brief as source material
5. Framework selection and outline building use the brief's data points and structure

### `/presentation` to `/post`
1. After exporting, user says "post slide 3 on LinkedIn"
2. Export that slide as PNG: `export-design` with `{ type: "png", pages: [3] }`
3. Hand off PNG URL + caption to `/post`

---

## Examples

**Investor pitch (Canva):** "Create a pitch deck about AI customer service" -> Kawasaki 10/20/30, 10 slides -> elegant style, brand kit -> Canva generation -> edit team photos -> QA assertion headlines -> export PPTX.

**Keynote from research:** "/research conscious leadership then create a keynote" -> research brief first -> Duarte Sparkline, 15 slides, 3 oscillation cycles -> minimalist style -> generate, edit S.T.A.R. moment slide -> QA sparkline rhythm -> export PDF + 3 key PNGs for social.

**Quick internal update (Canva):** "Q1 results for the team" -> McKinsey Pyramid, 8 slides -> modular style -> generate -> update numbers via text replacement -> QA data headlines -> export PDF.

**Data report (python-pptx):** "Q1 metrics report, use PowerPoint" -> Pyramid/SCQA, 10 slides -> accent=gold, context=screen_share -> build JSON manifest -> `create_pptx.py` -> output .pptx ready to present.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| "generate-design with presentation type" fails | Wrong tool. `generate-design` blocks "presentation" type | Always use the outline review workflow: `request-outline-review` then `generate-design-structured` |
| Outline descriptions truncated or rejected | Descriptions exceed 90 chars | Shorten each description to a brief summary, max 90 characters |
| Punctuation errors in generation | Punctuation not stripped | Remove all periods, commas, colons, semicolons, question marks, exclamation marks, dashes, parentheses from titles and descriptions before calling `generate-design-structured` |
| Cannot change fonts in editing | Canva limitation | Font family changes are not supported via editing API. Only font size, weight, and style can be changed |
| Need more than 15 slides | "balanced" mode max is 15 | Generate in two batches, then use `merge-designs` to combine |
| Brand kit error: "Missing scopes" | Connector permissions | User must disconnect and reconnect their Canva connector with `brandkit:read` scope |
| Editing changes lost | Commit failed or transaction expired | Changes are not recoverable. Start a new editing transaction and redo |
| Cannot add new slides via editing | Editing API limitation | Use `merge-designs` to insert pages from another design |
| python-pptx: fonts look different | Playfair Display or DM Sans not installed on viewer machine | Install from Google Fonts, or accept auto-substitution |
| python-pptx: need PDF output | No programmatic PDF conversion | Open .pptx in PowerPoint or Google Slides and export to PDF |
| python-pptx: want to add animations | python-pptx does not support animations | Switch to Canva backend, or add animations manually in PowerPoint |
