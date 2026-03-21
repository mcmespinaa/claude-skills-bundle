---
name: newsletter
description: Send styled HTML email newsletters via GHL. Converts markdown content to branded email, searches contacts by tag, and sends through GHL Conversations API or saves as GHL Email Builder template. Use when user says /newsletter, send newsletter, email this to subscribers, send this as an email, or similar.
allowed-tools: "Bash(python3:*) Bash(bash:*) Bash(curl:*) WebFetch WebSearch Read Write Edit Glob Grep"
---

# /newsletter — Email Newsletter Skill

> **Trigger:** User says `/newsletter`, "send newsletter", "email this to subscribers", "send this as an email", or similar.
> **Do NOT use for:** Social media posts (use /post), SMS marketing, or transactional emails (use GHL workflows directly).

## Role

You send content as styled HTML email newsletters through GoHighLevel's Conversations API. You search for recipients by tag, convert markdown to branded HTML, and send personalized emails. You can also save emails as GHL templates for campaign use (with open/click tracking).

**You inherit brand voice and writing rules from the `/post` skill.** Before writing any content, read:
- `${CLAUDE_SKILL_DIR}/../post/SKILL.md` — Writing style, banned words, tone
- `${CLAUDE_SKILL_DIR}/../../shared/references/voice-samples.md` — Brand voice samples

---

## Content Types

| Input Type | How to Process |
|------------|----------------|
| Markdown file | Convert to branded HTML via `md_to_html.py` |
| Blog post URL | WebFetch, extract content, convert to newsletter format |
| Research brief | From `/research` skill, format as email body |
| Social post content | Expand a social post into newsletter-length content |
| Raw text/topic | Draft newsletter content from scratch, then convert |

---

## Workflow

### Step 0 — Resolve Location

1. Read `locations.json`. If multiple locations, ask: "Which client/location?"
2. Get `senderEmail` and `senderName` from the location config.
3. If `senderEmail` is empty, stop and ask the user to add it to `locations.json`.

### Step 1 — Identify Content

Three invocation patterns:

1. **File path given:** `/newsletter ./report.md --tag "newsletter"` — use the file directly.
2. **Topic given:** "Send a newsletter about AI adoption" — draft the content first.
3. **After /blog or /research:** Use that output as the newsletter body.

### Step 2 — Draft or Polish Content

If drafting from scratch or polishing existing content:

1. Read brand voice from `/post` SKILL.md (banned words, no em dashes, active voice).
2. Write newsletter body in markdown:
   - **Length:** 300-800 words (shorter than blog, longer than social post)
   - **Structure:** Hook paragraph, 2-3 value sections, CTA
   - **Tone:** Conversational, direct, personal (like writing to a friend who asked a question)
3. Present draft to user: **"Here's the newsletter draft. Approve, edit, or regenerate?"**

### Step 3 — Convert to HTML

```bash
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/md_to_html.py \
  "<content_file>" > /tmp/newsletter_email.html
```

The output includes:
- Branded inline-CSS styling (ivory background, charcoal text, gold accents)
- Responsive table layout (600px max-width, email-safe)
- Footer with unsubscribe note

**Hero image (optional):** To add a topic-relevant hero image, use a hosted image URL in the markdown: `![Hero](https://...)`. Email clients need hosted URLs, not local files.

### Step 4 — Write Subject Line

Rules:
- 6-10 words, curiosity-driven, no clickbait
- No em dashes, no banned words, no ALL CAPS words
- Match brand voice (warm, direct, grounded)

Present to user: **"Subject: '[proposed subject]'. Approve, edit, or regenerate?"**

Do NOT proceed until the user approves the subject line.

### Step 5 — Resolve Recipients

```bash
bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_search_contacts.sh \
  --tag "<tag_name>" \
  --location <shorthand>
```

Show the user: **"Found [N] contacts with tag '[tag]' ([M] with email addresses). Proceed?"**

If `--test` flag is set, send only to the first contact (or a specified test email).

### Step 6 — Deliver

Present two options:

**"How would you like to deliver this newsletter?"**
1. **Save as GHL template** — for sending via GHL UI with open/click tracking
2. **Send now** — sends immediately via Conversations API

#### Option A: Save as GHL Template

```bash
bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_create_template.sh \
  --name "<approved_subject>" \
  --html-file "/tmp/newsletter_email.html" \
  --location <shorthand>
```

Tell the user: **"Template '[name]' saved to GHL Email Builder. Use it in Marketing > Emails or Workflows for full open/click tracking."**

Skip to Step 7.

#### Option B: Send Now

First, send a draft to the sender for inbox preview:

1. Search for the sender's contact:
```bash
bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_search_contacts.sh \
  --query "<senderEmail>" --location <shorthand>
```

2. Send draft:
```bash
bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_send_email.sh \
  --contact-id "<sender_contact_id>" \
  --subject "[DRAFT] <approved_subject>" \
  --html-file "/tmp/newsletter_email.html" \
  --from "<senderEmail>" \
  --location <shorthand>
```

**"Draft sent to <senderEmail>. Check your inbox. Approve to send to all [N] contacts?"**

Do NOT proceed until the user confirms the draft looks good.

Then send to all contacts (1 second between sends to avoid rate limiting):

```bash
bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_send_email.sh \
  --contact-id "<contact_id>" \
  --subject "<approved_subject>" \
  --html-file "/tmp/newsletter_email.html" \
  --from "<senderEmail>" \
  --location <shorthand>
```

If a send fails for a specific contact, log the error and continue. Report failures at the end.

### Step 7 — Log & Confirm

Append to `newsletter_send_log.md` at project root:

```
| <Location> | <subject> | <recipient_count> | <datetime> | sent |
```

If some sends failed:
```
| <Location> | <subject> | <success_count>/<total_count> | <datetime> | partial (N failed) |
```

Confirm: **"Newsletter sent to [N] contacts. Subject: '[subject]'."**

---

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| 401 Unauthorized | GHL token expired | Notify user to refresh GHL_API_KEY |
| 400/422 Bad Request | Invalid payload | Show raw response, check contactId and emailFrom |
| 429 Rate Limited | Too many API calls | Wait 10s, retry the failed send |
| Empty senderEmail | Not configured in locations.json | Stop and ask user to update locations.json |
| No contacts found | Tag doesn't exist | Suggest available tags or broader search |
| HTML conversion fails | Malformed markdown | Show error, offer to send as plain text |

---

## Autonomy Rules

**Run automatically (no confirmation):**
- Reading locations.json
- Searching contacts
- Converting markdown to HTML
- Reading brand voice files

**Ask before running:**
- Saving as GHL template
- Sending draft email to sender (wait for inbox preview approval)
- Sending emails to all recipients (only after draft approval)
- Writing to newsletter_send_log.md

---

## Examples

### Example 1: File to Newsletter

```
User: /newsletter ./weekly-insights.md --tag "newsletter" --location ces

Actions:
1. Read locations.json, get senderEmail for ces
2. Convert weekly-insights.md to branded HTML
3. Write subject line, get approval
4. Search contacts with tag "newsletter"
5. Ask: save as template or send now?
6. Send draft to sender, get preview approval
7. Send to all contacts
8. Log and confirm
```

### Example 2: Topic to Newsletter

```
User: Send a newsletter about our latest AI tools roundup

Actions:
1. Draft 500-word newsletter body in brand voice
2. Get user approval on draft
3. Convert to HTML
4. Write subject: "3 AI tools we tested this week"
5. Ask for recipient tag
6. Search contacts, send draft, get approval, send all
```

### Example 3: Template Only

```
User: /newsletter ./report.md --tag "vip" --location ces

User chooses: "Save as template"

Actions:
1. Convert to HTML
2. Write subject line
3. Save to GHL Email Builder
4. Report: "Template saved. Use in Marketing > Emails."
```

---

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| `/blog` | Send blog excerpt as newsletter with link to full post |
| `/research` | Send research brief as newsletter |
| `/post` | Inherits brand voice and writing rules |
| `/plan-week` | Could include newsletter as a weekly distribution channel |
