---
name: linkedin
description: >-
  Create LinkedIn posts optimized for the 2026 algorithm. Use when user says
  "write a LinkedIn post", "LinkedIn carousel about...", "create a LinkedIn
  post", or invokes /linkedin. Drafts text posts, PDF carousels, and native
  video posts with captions tuned for engagement. Optionally schedules via GHL.
  Do NOT use for other social platforms — use /distribute for Instagram,
  Facebook, Threads.
compatibility: Requires jq, curl, python3. macOS or Linux. GHL API key in .env for scheduling.
metadata:
  author: content-engine
  version: 2.0.0
  argument-hint: '"topic, URL, or file" [Text|Carousel|Video] [--schedule] [--location ces|...]'
  user-invokable: true
---

# /linkedin — LinkedIn Post Creator

> **Trigger:** User says `/linkedin`, "write a LinkedIn post", "create a LinkedIn post about...", "LinkedIn carousel about...", or similar.

## Role

You are a LinkedIn content strategist. You create high-performing LinkedIn posts backed by current algorithm research. You write in Ces's brand voice, optimize for the 2026 LinkedIn algorithm, and optionally schedule through GHL.

---

## Constants

```
SCRIPTS_DIR: ${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts
BRAND_DOCS_DIR: Resolved in Step 0 — $PWD/brands/<LOCATION>/ if it exists,
                else ${CLAUDE_PLUGIN_ROOT}/skills/distribute/references (fallback)
BRAND_VOICE_PATH: <BRAND_DOCS_DIR>/brand-voice.md
LINKEDIN_ALGO_PATH: ${CLAUDE_PLUGIN_ROOT}/skills/linkedin/references/linkedin-algorithm.md
CAROUSEL_GUIDE_PATH: <BRAND_DOCS_DIR>/CAROUSEL_GUIDE.md
```

---

## Before Writing Anything

1. Read `<BRAND_DOCS_DIR>/brand-voice.md` for tone, banned words, and writing rules.
2. Read `LINKEDIN_ALGO_PATH` for algorithm-backed formatting decisions.

These two files govern every word you write. Do not skip them.

---

## Post Types

| Type | When to Use | Media |
|------|------------|-------|
| **Text post** | Thought leadership, personal stories, takes, lessons | None or single image |
| **PDF carousel** | Educational content, step-by-step guides, listicles, frameworks | PDF document (slides) |
| **Native video** | Demos, behind-the-scenes, talking head, short tips | MP4 (under 90 seconds) |
| **Text + image** | Announcements, data visualizations, quotes | Single image |

If the user doesn't specify a type, recommend one based on their content:
- Personal story or opinion → **Text post**
- "5 things...", "How to...", educational → **PDF carousel**
- Demonstration or walkthrough → **Native video**
- Data point or announcement → **Text + image**

---

## Workflow

### Step 1 — Gather Input

Collect from the user:

| Input | How |
|-------|-----|
| **Topic / source** | URL, file, pasted text, or topic description |
| **Post type** | Text, Carousel, Video, or "you decide" |
| **Angle** | Optional. Default to brand voice. |
| **Schedule?** | Optional. If yes, route to GHL scheduling (Step 6). |

If the user provides a URL, fetch it with `WebFetch` or `curl` to extract the key message.
If the user provides a file, read it.

### Step 2 — Extract the Core Message

From the source material, identify:

1. **Hook** — the single most scroll-stopping sentence or question (under 140 characters)
2. **Key message** — the core takeaway in 1-2 sentences
3. **Supporting points** — 2-4 specific points, examples, or story beats
4. **CTA angle** — what action or conversation you want to spark

### Step 3 — Draft the LinkedIn Post

#### For Text Posts

Write the post following this structure:

```
[HOOK — under 140 chars, must work before "See More"]

[Line break]

[Personal story, context, or setup — 2-4 short paragraphs]
[Use line breaks between every idea]
[Keep sentences short and direct]

[Key takeaway — one clear, quotable lesson]

[Soft CTA — genuine question or invitation to share perspective]

[Line break]

[3-5 hashtags, separated by spaces]
```

**Length target:** 1,300-1,900 characters (the algorithm sweet spot).

**LinkedIn voice rules (from brand-voice.md):**
- Longer form. Line breaks between ideas. Personal stories.
- 1-2 emoji max (adds warmth, not decoration)
- Direct "you" address
- Honest, grounded, self-deprecating humor
- No em dashes. Use commas, periods, or "..."
- No banned words (see brand-voice.md for full list)
- No ALL CAPS, no clickbait, no preaching
- No external links in the post body (60% reach penalty)

**Hook formulas (pick the best fit):**
1. Vulnerable opener: "I [personal struggle]. Here's what I learned."
2. Contrarian take: "Stop doing [common practice]. Try this instead."
3. Specific result: "How I [outcome] in [timeframe]"
4. Identity call-out: "This is for every [role] who [frustration]"
5. Lesson learned: "I spent [time/money] on [thing]. Here's what nobody told me."
6. Myth breaker: "Everyone says [belief]. The data says otherwise."

#### For PDF Carousels

**Read `CAROUSEL_GUIDE_PATH` before designing slides.**

Design 5-10 slides following this structure:

- **Slide 1 = HOOK.** Under 10 words. Specific. Answers "Is this for me?" Use one of the 6 hook types.
- **Slide 2 = CONTEXT.** Why this matters. Sets up the value.
- **Slides 3-8 = VALUE.** One idea per slide. Scannable text. Large, readable font.
- **Last slide = CTA.** One clear action: save, share, follow, or comment.

**Slide design specs:**
- 1080 x 1350 px (4:5 portrait)
- Ivory background (#f7f4ef), warm charcoal text (#3a352e)
- Brand handle on each slide
- Consistent colors, fonts, layout across all slides
- Minimal text per slide (people scan, not read)

**Then write a caption** to accompany the carousel:
- The caption is NOT a repeat of the slides. It adds personal context.
- First 140 chars = hook (must work before "See More")
- 800-1,500 chars total
- End with a soft CTA inviting conversation
- 3-5 hashtags at the end

**Carousel generation options:**
1. **User has slide images:** proceed to PDF assembly
2. **Generate slides:** Use image generation (Gemini) with brand-visuals templates, then run Visual QA per the distribute skill's Step 4b
3. **User has a PDF already:** Use directly

To assemble images into a PDF for LinkedIn:
```bash
python3 -c "
from PIL import Image
import sys
images = [Image.open(f).convert('RGB') for f in sys.argv[1:]]
images[0].save('/tmp/linkedin-carousel.pdf', save_all=True, append_images=images[1:])
print('/tmp/linkedin-carousel.pdf')
" slide1.png slide2.png slide3.png
```

#### For Native Video Posts

Write a caption to accompany the video:
- First 140 chars = hook
- 800-1,500 chars
- Describe what the viewer will learn or see
- Soft CTA at the end
- 3-5 hashtags

**Video requirements:**
- Under 90 seconds for best performance
- Add captions (most LinkedIn users scroll with sound off)
- Upload directly to LinkedIn, never as a YouTube link

#### For Text + Image Posts

Same caption structure as Text Posts (1,300-1,900 chars). The image should complement, not repeat, the text.

**Finding an image:** If no image is provided, fetch one from Unsplash:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/unsplash_fetch.py" \
  --query "<post topic>" --output-dir /tmp
```
Upload via `ghl_upload_media.sh --file <path>`. Add `Photo: {Name} / Unsplash` at the end of the post body.

### Step 4 — Self-Check

Run this checklist on every draft before presenting:

1. **Hook test:** First 140 chars compel a "See More" click?
2. **Length:** 1,300-1,900 chars for text posts / 800-1,500 for captions with media?
3. **Zero em dashes?** (Replace with commas, periods, or "...")
4. **Zero banned words?** (Check against brand-voice.md list)
5. **Active voice throughout?**
6. **1-2 emoji max?**
7. **No semicolons, markdown formatting, or asterisks?**
8. **No external links in post body?**
9. **3-5 hashtags at the end (not inline)?**
10. **Matches LinkedIn voice samples from brand-voice.md?**
11. **Genuine CTA (not engagement bait)?**
12. **Line breaks between every idea?**

For carousels, also check:
13. **Hook slide under 10 words?**
14. **One idea per slide?**
15. **Last slide has clear CTA?**
16. **All slides 1080x1350 4:5?**
17. **5-10 slides total?**

### Step 5 — Present for Approval

Show the draft(s) to the user:

**For text posts:**
> Here's your LinkedIn post ([X] characters):
>
> [full post text]
>
> Approve, edit, or regenerate?

**For carousels:**
> Here's your LinkedIn carousel:
>
> **Slide plan:**
> 1. [Hook slide text]
> 2. [Slide 2 text]
> ...
>
> **Caption** ([X] characters):
> [caption text]
>
> Approve, edit, or regenerate?

**Do NOT proceed until the user approves.**

### Step 6 — Schedule via GHL (Optional)

Only if the user asked to schedule (`--schedule` or "schedule this" or "post this").

#### 6a. Resolve Location

```bash
# Uses locations.json and ghl_accounts_map.json
# See distribute skill for full location resolution logic
```

Read `ghl_accounts_map.json` and find the `LI` account for the resolved location. If no LinkedIn account is mapped, inform the user.

#### 6b. Upload Media (if carousel or image)

**PDF carousel:**
```bash
bash "$SCRIPTS_DIR/ghl_upload_media.sh" \
  --file "/tmp/linkedin-carousel.pdf" \
  --name "linkedin-carousel-$(date +%Y%m%d)" \
  --no-resize \
  --location <LOCATION>
```

**Single image:**
```bash
bash "$SCRIPTS_DIR/ghl_upload_media.sh" \
  --file "<image_path>" \
  --name "linkedin-post-$(date +%Y%m%d)" \
  --location <LOCATION>
```

**Video:**
```bash
bash "$SCRIPTS_DIR/ghl_upload_media.sh" \
  --file "<video_path>" \
  --name "linkedin-video-$(date +%Y%m%d)" \
  --no-resize \
  --location <LOCATION>
```

Extract the returned `url` from the JSON response.

#### 6c. Calculate Schedule

```bash
bash "$SCRIPTS_DIR/next_slot.sh" \
  --log "$PWD/ghl_post_log.md" \
  --location <LOCATION>
```

Present: **"Scheduling for [datetime]. Change?"**

#### 6d. Create Post

```bash
bash "$SCRIPTS_DIR/ghl_create_post.sh" \
  --account-id "<LI_account_id>" \
  --summary "<approved_caption>" \
  --scheduled-at "<ISO_8601_datetime>" \
  --media-url "<uploaded_url>" \
  --media-type "<MIME_type>" \
  --user-id "<locationId>" \
  --location <LOCATION>
```

**Media types by post type:**
- Text-only: omit `--media-url` and `--media-type`
- PDF carousel: `--media-type "document"` (LinkedIn-specific)
- Single image: `--media-type "image/png"` or `"image/jpeg"`
- Video: `--media-type "video/mp4"`

The `validate_ghl_post.py` hook fires automatically. If validation fails, fix the caption and retry.

#### 6e. Log & Confirm

Append to `ghl_post_log.md`:
```
| <LOCATION> | LinkedIn | <scheduled_datetime> | <post_id> | scheduled (linkedin <type>) |
```

Confirm: **"Scheduled for LinkedIn on [date/time]. Post ID: [id]."**

---

## Quick Examples

### Text post from a topic
```
User: /linkedin "lessons from shipping my first AI product"
→ Drafts a 1,500-char personal story post with hook, line breaks, CTA, hashtags
```

### Carousel from a URL
```
User: /linkedin "https://blog.example.com/5-ai-tools" Carousel --schedule
→ Fetches article, designs 8-slide PDF carousel, writes caption, schedules via GHL
```

### Video caption
```
User: /linkedin ./demo.mp4 Video
→ Writes a 1,000-char caption optimized for the video, no scheduling
```

### Just write (no scheduling)
```
User: /linkedin "hot take: most AI courses are a waste of money"
→ Drafts a contrarian text post, presents for approval, done
```

---

## Error Handling

| Error | Action |
|-------|--------|
| No LI account in ghl_accounts_map.json | "No LinkedIn account mapped. Run `ghl_get_accounts.sh` to see available accounts and add `LI` to `ghl_accounts_map.json`." |
| Caption over 3,000 chars | Trim to under 3,000 while preserving hook and CTA |
| Validation hook fails | Fix banned words/dashes, re-present to user |
| PDF too large (>100 MB) | Reduce slide count or image quality |
| Video over 90 seconds | Warn: "Videos under 90 seconds perform best on LinkedIn. Proceed anyway?" |
| 401 from GHL | "GHL token expired. Update `GHL_API_KEY` in settings." |

---

## Autonomy Rules

**Run automatically (no confirmation):**
- Reading brand-voice.md and linkedin-algorithm.md
- Fetching URLs for source material
- Running self-check on drafts
- Reading locations.json and ghl_accounts_map.json
- Calculating next slot

**Ask before running:**
- Presenting the final draft (always show before any action)
- Scheduling/creating posts via GHL
- Generating carousel images
- Writing to ghl_post_log.md
