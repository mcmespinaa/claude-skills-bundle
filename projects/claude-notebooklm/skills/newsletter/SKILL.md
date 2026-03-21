---
name: newsletter
description: Send NotebookLM-generated content as styled HTML email newsletters via GHL. Use when user says "send newsletter", "email this to subscribers", "send this as an email", "email the report", or invokes /newsletter. Searches contacts by tag, converts markdown to branded HTML, and sends through GHL Conversations API. Do NOT use for social media posting — use /distribute instead.
compatibility: Requires jq, curl, python3. macOS or Linux. GHL API key in .env.
metadata:
  author: content-engine
  version: 2.0.0
  argument-hint: '"content_file" --tag "newsletter" [--location ces] [--subject "..."] [--test]'
  user-invokable: true
---

# /newsletter — Email Newsletter Skill

> **Trigger:** User says `/newsletter`, "send newsletter", "email this to subscribers", "send this as an email", or similar.

## Role

You send NotebookLM-generated content (reports, summaries, study guides) as styled HTML email newsletters through GoHighLevel's Conversations API. You search for recipients by tag, convert markdown to branded HTML, and send personalized emails.

---

## Constants

```
NEWSLETTER_SCRIPTS_DIR: ${CLAUDE_PLUGIN_ROOT}/skills/newsletter/scripts
BRAND_DOCS_DIR: Resolved in Step 0 — $PWD/brands/<LOCATION>/ if it exists,
                else ${CLAUDE_PLUGIN_ROOT}/skills/distribute/references (fallback)
EMAIL_VOICE_PATH: <BRAND_DOCS_DIR>/email-voice.md
BRAND_VOICE_PATH: <BRAND_DOCS_DIR>/brand-voice.md
```

---

## Content Types

| NotebookLM Output | Extension | Email Action |
|---|---|---|
| Report / Summary | `.md` | Convert to HTML email body |
| Study Guide | `.md` | Convert to HTML email body |
| Briefing Doc | `.md` | Convert to HTML email body |
| Quiz | `.md`/`.json` | Extract questions as email content |
| Flashcards | `.md` | Format as email content |
| Infographic | `.png` | Embed as inline image in email |
| Audio (Podcast) | `.mp3` | Text announcement with link |
| Video | `.mp4` | Text announcement with link |

---

## Workflow

### Step 0: Resolve Location

1. If `--location <shorthand>` is provided, use that location.
2. If no `--location`, read `locations.json`:
   - **Single location:** Use it automatically.
   - **Multiple locations:** Ask: "Which GHL location? Available: ces, client_b, ..."
3. Read `locations.json[<location>]` to get `senderEmail` and `senderName`.
4. If `senderEmail` is empty, **stop and ask the user** to provide one. GHL requires a valid sender email.

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve_location.sh" \
  --export --location <LOCATION>
```

### Step 1: Identify Content

Three invocation patterns:

1. **File path given:** `/newsletter ./report.md --tag "newsletter"` — use the file directly.
2. **After generation:** User just ran `notebooklm generate report` — use that output.
3. **No file given:** User says "send the latest report as newsletter" — run `notebooklm artifact list --json`, find the latest artifact, download it, then proceed.

**Text content only.** If the content is markdown or text, proceed normally. If it's a media file (image, video, audio), generate a text announcement email instead of trying to embed it.

### Step 2: Resolve Recipients

Run the search script:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/newsletter/scripts/ghl_search_contacts.sh" \
  --tag "<tag_name>" \
  --location <LOCATION>
```

Show the user: **"Found [N] contacts with tag '[tag]' ([M] with email addresses). Proceed?"**

If `--test` flag is set, send only to the first contact (or a specified test email).

### Step 3: Convert to HTML

For markdown content:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/newsletter/scripts/md_to_html.py" \
  "<content_file>" > /tmp/newsletter_email.html
```

If content is already HTML, skip conversion. The output includes:
- Branded inline-CSS styling (ivory background, charcoal text, gold accents)
- Responsive table layout (600px max-width)
- Footer with unsubscribe note

**Hero image (optional):** To add a topic-relevant hero image, fetch from Unsplash and embed the public URL directly in the markdown (email clients need hosted URLs, not local files):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/unsplash_fetch.py" \
  --query "<topic>" --raw-json
```

Use the `urls.regular` from the API response in the markdown: `![Hero](https://images.unsplash.com/...)`. Do NOT include photographer name or Unsplash attribution text in the email content.

### Step 4: Write Subject Line

**CRITICAL:** Before writing the subject, read the EMAIL_VOICE_PATH for email-specific rules and the BRAND_VOICE_PATH for brand voice rules.

Key rules:
- 6-10 words, curiosity-driven, no clickbait
- No em dashes, no banned words
- No ALL CAPS words

Present to user: **"Subject: '[proposed subject]'. Approve, edit, or regenerate?"**

Do NOT proceed until the user approves the subject line.

### Step 5: Deliver — Template or Send Now

Present the user with two options:

**"How would you like to deliver this newsletter?"**
1. **Save as GHL template** — Uploads the HTML to GHL Email Builder so you can send it from the GHL UI (with open/click tracking via campaigns).
2. **Send now** — Sends immediately to all [N] contacts via the Conversations API.

#### Option A: Save as GHL Template

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/newsletter/scripts/ghl_create_template.sh" \
  --name "<approved_subject>" \
  --html-file "/tmp/newsletter_email.html" \
  --location <LOCATION>
```

Tell the user: **"Template '[name]' saved to GHL Email Builder. You can now use it in Marketing > Emails or Workflows to send with full open/click tracking."**

Skip to Step 7 (Log & Confirm).

#### Option B: Send Now

First, send a draft to the sender for inbox preview:

1. Look up the sender's own contact in GHL:
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/newsletter/scripts/ghl_search_contacts.sh" \
  --query "<senderEmail>" --location <LOCATION>
```

2. Send the draft email to the sender's contact ID:
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/newsletter/scripts/ghl_send_email.sh" \
  --contact-id "<sender_contact_id>" \
  --subject "[DRAFT] <approved_subject>" \
  --html-file "/tmp/newsletter_email.html" \
  --from "<senderEmail>" \
  --location <LOCATION>
```

Tell the user: **"Draft sent to <senderEmail>. Check your inbox to preview. Approve to send to all [N] contacts, or request changes?"**

Do NOT proceed until the user confirms the draft looks good.

Then loop through contacts and send one email per contact:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/newsletter/scripts/ghl_send_email.sh" \
  --contact-id "<contact_id>" \
  --subject "<approved_subject>" \
  --html-file "/tmp/newsletter_email.html" \
  --from "<senderEmail>" \
  --location <LOCATION>
```

**Rate limiting:** Wait 1 second between sends to avoid GHL throttling (429).

Show progress: **"Sent 12/47..."**

If a send fails for a specific contact, log the error and continue with remaining contacts. Report failures at the end.

### Step 7: Log & Confirm

Append to `newsletter_send_log.md` at project root:

```
| <LOCATION> | <subject> | <recipient_count> | <datetime> | sent |
```

If some sends failed:
```
| <LOCATION> | <subject> | <success_count>/<total_count> | <datetime> | partial (N failed) |
```

Confirm: **"Newsletter sent to [N] contacts. Subject: '[subject]'. [failures if any]"**

---

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| 401 Unauthorized | GHL token expired | Notify user to refresh GHL API key |
| 400/422 Bad Request | Invalid payload | Show raw response, check contactId and emailFrom |
| 429 Rate Limited | Too many API calls | Wait 10s, retry the failed send |
| Empty senderEmail | Not configured | Stop and ask user to update locations.json |
| No contacts found | Tag doesn't exist | Suggest available tags or broader search |
| HTML conversion fails | Malformed markdown | Show error, offer to send as plain text |
| Validation hook fails | Banned words/dashes in subject | Fix subject and retry |

---

## Autonomy Rules

**Run automatically (no confirmation):**
- Reading `locations.json`
- Searching contacts (`ghl_search_contacts.sh`)
- Converting markdown to HTML (`md_to_html.py`)
- Reading email voice and brand voice docs

**Ask before running:**
- Saving as GHL template (`ghl_create_template.sh`) — confirm user chose this option
- Sending draft email to sender — wait for inbox preview approval
- Sending emails to all recipients (`ghl_send_email.sh`) — only after draft approval
- Downloading artifacts from NotebookLM
- Writing to `newsletter_send_log.md`

---

## Examples

**Basic usage:**
```
/newsletter ./report.md --tag "newsletter" --location ces
```

**Test mode (single recipient):**
```
/newsletter ./summary.md --tag "newsletter" --test
```

**Custom subject:**
```
/newsletter ./study-guide.md --tag "vip" --subject "This week's AI insights"
```

**After NotebookLM generation:**
```
User: "Generate a report from the notebook and email it to newsletter subscribers"
→ Generate report → Download → Convert to HTML → Search contacts → Send
```
