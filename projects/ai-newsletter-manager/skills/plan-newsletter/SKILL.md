# /plan-newsletter — Batch Newsletter Planning

## Trigger
`/plan-newsletter`, "plan newsletters", "create a newsletter calendar", "batch newsletters"

## Overview
Plan and create multiple newsletter templates in batch. Build a content calendar, write all drafts, get user approval, then upload all templates to GoHighLevel. **This skill creates templates only** — campaign scheduling and sending must be done manually in GHL.

## Before You Start
Read these files every time:
1. `.claude/skills/newsletter/newsletter-voice.md` — Writing voice and structure
2. `.claude/skills/newsletter/email-design.md` — Design system and token reference
3. `CLAUDE.md` — Project config, quality standards, banned words

## Environment
Same as `/newsletter` skill. Credentials in `.claude/settings.local.json`.

## Workflow (7 Steps)

### Step 1: Understand Input
Gather what the user wants to send over the planning period.
- Accept: topics list, URLs, draft content, social posts, brand themes, or any mix
- Ask: How many newsletters? (default: 4 for monthly planning)
- Ask: What cadence? (weekly, biweekly, monthly)
- Ask: Any preference on types? (editorial, digest, hybrid, or mix)
- **Location selection:** Check `locations.json`. If only one location, use it automatically. If multiple, ask: "Which client location are you planning for?" and wait for selection.
- If user provides URLs, use WebFetch to read each one

### Step 2: Build Calendar
Create a content calendar mapping topics to dates and types.

**Calendar structure:**
| # | Target Date | Type | Topic / Theme | Key Angle |
|---|------------|------|---------------|-----------|

**Planning rules:**
- Alternate types for variety (don't send 4 editorials in a row)
- Match content depth to type:
  - Deep topics → Editorial
  - Social roundups → Digest
  - Mixed content → Hybrid
- Space topics logically (don't cluster similar themes)
- Consider seasonal relevance and timeliness

### Step 3: Write Drafts
For each newsletter in the calendar, write a complete draft.

**Draft each newsletter following `/newsletter` Step 3 rules:**
- Subject line (under 60 chars)
- Preview text (40-90 chars)
- Personal opening
- All section content (varies by type)
- CTA text and URL
- Sign-off
- Pillar colors (for digest cards)

**Cross-newsletter consistency:**
- Vary subject line formulas across the batch
- Don't reuse the same opening style back-to-back
- Each newsletter should feel fresh but recognizably "you"
- CTAs should point to different destinations when possible

### Step 4: Write newsletter-plan.md
Save the complete plan to `newsletter-plan.md` in the project root.

**Format:**
```markdown
# Newsletter Plan — [Month Year]

**Cadence:** [weekly/biweekly/monthly]
**Total:** [N] newsletters
**Created:** [date]

---

## Newsletter 1: [Subject Line]
**Target date:** [YYYY-MM-DD]
**Type:** [editorial/digest/hybrid]

**Subject:** [subject line]
**Preview:** [preview text]

**Personal Opening:**
[opening text]

**Section 1: [Header]**
[body text]

**Section 2: [Header]**
[body text]

[... all fields for this type ...]

**CTA:** [text] → [url]
**Sign-off:** [closing text]

---

## Newsletter 2: [Subject Line]
[... repeat ...]
```

### Step 5: User Review
Present the plan for approval before uploading anything.

**Show:**
- Calendar overview (table)
- Each newsletter's subject line and preview text
- Brief description of each newsletter's angle
- Ask: "Ready to upload all [N] templates to GHL?"

**User can:**
- Approve all → proceed to Step 6
- Request changes → edit specific newsletters, return to Step 4
- Approve some → upload only approved ones

### Step 6: Batch Upload
Upload all approved newsletters to GHL as templates.

**Process (error isolation per newsletter):**

1. **Build HTML** — For each newsletter:
   - Read the appropriate template from `templates/`
   - If the newsletter type is editorial or hybrid, generate a header image:
     ```bash
     HERO_URL=$(bash .claude/skills/newsletter/scripts/generate_header_image.sh \
       --prompt "[content-focused prompt for this newsletter]" \
       --output "newsletter-drafts/[N]-banner-[subject-slug].jpg" \
       --location "[LOCATION_KEY]")
     ```
   - If image generation fails, proceed without the hero image (remove the hero `<tr>` block)
   - If the newsletter type is digest, skip image generation
   - Replace all `{{TOKEN}}` placeholders (including `{{HERO_IMAGE_URL}}` if generated)
   - Save to `newsletter-drafts/[N]-[subject-slug].html`

2. **Upload templates** — For each newsletter (sequential to avoid rate limits):
   ```bash
   bash .claude/skills/newsletter/scripts/ghl_create_template.sh \
     --title "Newsletter [N]: [Subject Line]" \
     --html-file "newsletter-drafts/[N]-[subject-slug].html" \
     --location "[LOCATION_KEY]"
   ```
   - If one fails, log the error and continue with the rest
   - If the hook blocks a command, report which newsletter failed and why

3. **Update settings** — For each successfully created template:
   ```bash
   bash .claude/skills/newsletter/scripts/ghl_update_template.sh \
     --template-id "[TEMPLATE_ID]" \
     --subject "[Subject Line]" \
     --preview-text "[Preview Text]" \
     --from-name "[SENDER_NAME]" \
     --from-email "[SENDER_EMAIL]" \
     --location "[LOCATION_KEY]"
   ```
   (Use sender details from the selected location's config in `locations.json`)

### Step 7: Log & Confirm
Log all results and present a summary.

**Log each newsletter to `ghl_template_log.md`:**
```
| YYYY-MM-DD | LOCATION_KEY | Subject Line | template-id | type | created |
```

For any that failed, log:
```
| YYYY-MM-DD | LOCATION_KEY | Subject Line | — | type | failed: [reason] |
```

**Final summary:**
| # | Subject | Type | Status | Template ID |
|---|---------|------|--------|-------------|
| 1 | ... | editorial | created | abc123 |
| 2 | ... | digest | created | def456 |
| 3 | ... | hybrid | failed: banned word | — |

**Always remind:**
- "Templates are ready in GHL. To send them, create campaigns in GHL and select each template."
- "Recommend sending a test email from GHL before launching to your list."
- If any failed: "Fix the flagged issues and re-run `/newsletter` for the failed ones."

## Error Handling
- **Partial failure:** Log successes, report failures individually with reasons
- **All fail:** Check API key, show the first error in detail
- **Hook blocks:** Report which newsletter and which check failed
- **401 (token expired):** Stop batch, tell user to update key
- **429 (rate limit):** Wait 10s between uploads, retry failed ones once

## Important Notes
- **Templates only** — Campaigns must be created manually in GHL
- **Sequential uploads** — Don't parallelize API calls to avoid rate limits
- **newsletter-plan.md** is the staging document — always write it before uploading
- **Each newsletter is independent** — one failure doesn't affect others
