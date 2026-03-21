# /newsletter — Single Newsletter Creation

## Trigger
`/newsletter`, "write a newsletter", "create an email", "draft a newsletter"

## Overview
Create a single newsletter email: draft content, build HTML from template, and upload to GoHighLevel as a reusable email template. **This skill creates templates only** — campaign scheduling and sending must be done manually in GHL.

## Before You Start
Read these files every time:
1. `newsletter-voice.md` — Writing voice, tone, subject line formulas, structure
2. `email-design.md` — Design system, color palette, component specs, token reference
3. The chosen HTML template from `templates/` — Token list and structure
4. `locations.json` — Available client locations (if managing multiple subaccounts)

## Environment
Credentials are in `.claude/settings.local.json`:
- `$GHL_API_KEY` — Bearer token for GHL API
- `$GHL_VERSION` — API version (2021-07-28)

Location config in `locations.json`:
- Maps location keys to GHL location IDs and sender info
- Default location used if only one exists
- Multiple locations require explicit `--location` selection

## Multi-Location Support

If managing multiple GHL sub-accounts:

1. **Check locations.json** — Read the file to see available locations
2. **Single location** — If only one location exists, use it automatically
3. **Multiple locations** — If multiple exist, ask user: "Which location are you creating this for?" and wait for their choice
4. **Pass location to scripts** — Add `--location "<key>"` to all helper scripts in Step 5
5. **Use location sender info** — Instead of `$GHL_SENDER_EMAIL` and `$GHL_SENDER_NAME`, use the sender details from the selected location's config

## Workflow (7 Steps)

### Step 1: Ingest
Understand what the user wants to write about.
- Accept: topic, URL, draft text, social posts, article, notes, or any mix
- If a URL is provided, use WebFetch to read it
- Ask: What type of newsletter? (editorial, digest, or hybrid)
- If user doesn't specify, recommend based on content:
  - **Editorial** — Deep-dive on one topic, thought leadership, 3 sections
  - **Digest** — Curated social post roundup, 3 cards with brief context
  - **Hybrid** — Editorial opening (2 sections) + digest cards (3 cards)

### Step 2: Research (if needed)
If the user provides a topic but not full content:
- Use WebSearch to find 2-3 recent angles or data points
- Look for quotes, statistics, or examples to strengthen the piece
- Keep research focused — this informs the draft, not the final content

### Step 3: Draft Content
Write the newsletter content following `newsletter-voice.md` rules.

**For all types, draft these fields:**
- **Subject line** — Under 60 chars, use a formula from the voice guide
- **Preview text** — 40-90 chars, complements but doesn't repeat subject
- **Personal opening** — 2-3 sentences, warm and direct, "you" focused
- **CTA text** — Action verb + benefit (e.g., "Read the Full Guide")
- **CTA URL** — Link destination (ask user if not obvious)
- **Sign-off** — Brief, warm closing with name

**Editorial-specific fields:**
- Section Header 1, Section Body 1
- Section Header 2, Section Body 2
- Pull Quote (key insight, italicized)
- Section Header 3, Section Body 3

**Digest-specific fields:**
- Card 1: Platform, Excerpt (2-3 sentences), Context (engagement note)
- Card 2: Platform, Excerpt, Context
- Card 3: Platform, Excerpt, Context
- Pillar colors: Match content to brand pillars
  - AI/Tech = `#b8a06a` (gold)
  - Leadership = `#8fab8a` (sage)
  - Sustainability = `#d4b0a8` (blush)
  - Consciousness = `#c4b8cc` (lavender)

**Hybrid-specific fields:**
- All editorial fields (2 sections instead of 3) + all digest fields

**Writing rules (enforced by hook):**
- No em dashes (— or –). Use commas or "..."
- No banned words (see CLAUDE.md for full list)
- No spam trigger phrases
- Subject line: warn at 60+ chars, block at 80+
- Active voice, short sentences, clear language
- Emoji: 0-1 in subject line, 0-2 in body (sparingly)

### Step 3.5: Generate Header Image (Optional)

After drafting content, generate a branded header image for the newsletter. This step is optional and degrades gracefully if it fails.

**When to generate:**
- Editorial and Hybrid newsletters: generate by default (these templates include a hero image block)
- Skip for Digest newsletters (no hero image block in the digest template)

**When to skip:**
- User provides their own hero image URL
- User requests no hero image
- Digest newsletter type
- `$GEMINI_API_KEY` is not set

**Image prompt formula:**

Compose a prompt describing the newsletter's visual theme. The script automatically wraps it with brand style constraints (ivory background, warm charcoal + gold palette, minimalist editorial illustration, no text, 600x300 aspect ratio). You only need to describe the subject matter:

> "[Visual metaphor for the newsletter topic]. Include subtle [content pillar] accents. Geometric, flat illustration style with clean lines."

**Examples:**
- Topic "AI replacing coworkers" -> "A human figure and an AI robot connected by flowing circuit lines, collaborating at a shared workspace"
- Topic "Leadership in uncertainty" -> "A figure standing at a crossroads with multiple paths, one lit by a warm golden glow"
- Topic "Sustainable business" -> "Abstract plants growing from geometric shapes, intertwined with subtle tech elements"

**Reference style:** See `newsletter-drafts/banner-ai-employee-pro.jpg` for the target aesthetic.

**Run the script:**
```bash
HERO_URL=$(bash .claude/skills/newsletter/scripts/generate_header_image.sh \
  --prompt "[your content-focused prompt]" \
  --output "newsletter-drafts/banner-[subject-slug].jpg" \
  --location "[LOCATION_KEY]")
```

**On success:** Store `$HERO_URL` for use in Step 4 as `{{HERO_IMAGE_URL}}`. Draft an alt text description (under 125 chars, describes the illustration content) for `{{HERO_ALT}}`.

**On failure:** Log the error to stderr, proceed without a hero image. In Step 4, remove the hero image `<tr>` block from the HTML template. The newsletter works fine without it.

**Pillar-specific accent guidance for prompts:**
- AI/Tech topics: emphasize gold (#b8a06a) accents, circuit patterns, digital elements
- Leadership topics: emphasize sage (#8fab8a) accents, human figures, paths
- Sustainability topics: emphasize blush (#d4b0a8) accents, organic + geometric fusion
- Consciousness topics: emphasize lavender (#c4b8cc) accents, abstract/meditative forms

### Step 4: Build HTML
Replace template tokens with drafted content.

1. Read the chosen template from `templates/`:
   - `digest.html` for digest type
   - `editorial.html` for editorial type
   - `hybrid.html` for hybrid type

2. Replace all `{{TOKEN}}` placeholders with content:
   - `{{SUBJECT}}` — Subject line
   - `{{PREVIEW_TEXT}}` — Preview text
   - `{{PERSONAL_OPENING}}` — Opening paragraph
   - `{{SECTION_HEADER_N}}` / `{{SECTION_BODY_N}}` — Sections
   - `{{PULL_QUOTE}}` — Featured quote
   - `{{CARD_N_PLATFORM}}` — Platform name (uppercase)
   - `{{CARD_N_EXCERPT}}` — Card content
   - `{{CARD_N_CONTEXT}}` — Engagement context
   - `{{PILLAR_COLOR_N}}` — Hex color code
   - `{{CTA_TEXT}}` / `{{CTA_URL}}` — Button text and link
   - `{{SIGNOFF}}` — Closing text
   - `{{SENDER_NAME}}` — From `$GHL_SENDER_NAME`
   - `{{UNSUBSCRIBE_URL}}` — Use `{{contact.unsubscribe_url}}` (GHL merge field)
   - `{{CURRENT_YEAR}}` — Current year (e.g., 2026)
   - `{{HERO_IMAGE_URL}}` / `{{HERO_ALT}}` — Hero image (if provided)

3. If Step 3.5 returned a hero image URL, set `{{HERO_IMAGE_URL}}` to that URL and `{{HERO_ALT}}` to the drafted alt text. If Step 3.5 was skipped or failed, remove the entire hero image `<tr>` block from the HTML.

4. Save the built HTML to `newsletter-drafts/[subject-slug].html`

### Step 5: Upload to GHL
Use the helper scripts to create or update the template.

**New template:**
```bash
bash .claude/skills/newsletter/scripts/ghl_create_template.sh \
  --title "Newsletter: [Subject Line]" \
  --html-file "newsletter-drafts/[subject-slug].html" \
  --location "[LOCATION_KEY]"
```

**Update existing template:**
```bash
bash .claude/skills/newsletter/scripts/ghl_update_template.sh \
  --template-id "[TEMPLATE_ID]" \
  --html-file "newsletter-drafts/[subject-slug].html" \
  --subject "[Subject Line]" \
  --preview-text "[Preview Text]" \
  --from-name "[SENDER_NAME]" \
  --from-email "[SENDER_EMAIL]" \
  --location "[LOCATION_KEY]"
```

Note: If only one location is configured, `--location` is optional. For multiple locations, always include the flag. Use sender details from the selected location's config in `locations.json`.

The validation hook (`validate_ghl_email.py`) runs automatically before these commands. If it blocks, fix the flagged issues and retry.

### Step 6: Confirm
Show the user a summary:
- Subject line
- Preview text
- Template type (editorial/digest/hybrid)
- Template ID (from GHL response)
- Hero image: [Generated / Skipped / Failed] (if generated, show the GHL-hosted URL)
- Reminder: "Template created. To send it, create a campaign in GHL and select this template."

### Step 7: Log
Append a row to `ghl_template_log.md`:
```
| YYYY-MM-DD | LOCATION_KEY | Subject Line | template-id | editorial/digest/hybrid | created |
```

## Error Handling
- **401 (token expired):** Tell user to update `GHL_API_KEY` in `.claude/settings.local.json`
- **400/422 (bad request):** Show error body, check for HTML issues or missing fields
- **429 (rate limit):** Wait 10s, retry once
- **Hook blocks command:** Fix flagged issues (em dashes, banned words, spam triggers, subject length), then retry

## Important Notes
- **Templates only** — GHL API does not support creating/scheduling/sending campaigns programmatically. Always remind the user to create a campaign in GHL manually.
- **No attachments** — Email templates don't support file attachments via API.
- **Unsubscribe** — Always use `{{contact.unsubscribe_url}}` GHL merge field, never hardcode.
- **Testing** — Recommend user send a test email from GHL before launching to their list.
