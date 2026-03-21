---
name: distribute
description: Distribute NotebookLM-generated content to GoHighLevel (GHL) social media, Google Drive, and/or YouTube. Use when user says "distribute this", "post to Instagram", "post to LinkedIn", "schedule this on all platforms", "upload to Drive", "upload to YouTube", "send to GHL", or passes a file with platform shorthands like IG, FB, TH, LI, YT. Supports infographics, videos, podcasts, slide decks, reports, and quizzes. Do NOT use for writing content from scratch — use /linkedin or /newsletter instead.
compatibility: Requires jq, curl, python3. macOS or Linux. GHL API key in .env.
metadata:
  author: content-engine
  version: 2.0.0
  argument-hint: '"file_path" [IG|FB|TH|LI|All] [--location ces|...] [--drive] [--youtube] [--schedule "datetime"]'
  user-invokable: true
---

# Distribute NotebookLM Content to GHL

Bridge between NotebookLM artifact generation and distribution channels. Takes downloaded NotebookLM outputs and distributes them to:
- **GHL Social Media** — upload to media library, write captions, schedule posts
- **Google Drive** — organize in folders by notebook/date, share with collaborators
- **YouTube** — upload videos with title, description, tags, thumbnail, and scheduling

## When This Skill Activates

**Explicit:** `/distribute`, "distribute this", "send to GHL", "post this to social media", "upload to Drive", "upload to YouTube"

**Intent detection:**
- "Post this infographic to Instagram"
- "Schedule this video on all platforms"
- "Upload the podcast to GHL"
- "Share this report on Facebook"
- "Post this to LinkedIn"
- "Save this to Google Drive"
- "Upload the infographic to Drive and post to IG"
- "Upload this video to YouTube"
- "Post this to YouTube and IG"

## Constants

```
GHL_SCRIPTS_DIR: ${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts
BRAND_DOCS_DIR: Resolved in Step 0 — $PWD/brands/<LOCATION>/ if it exists,
                else ${CLAUDE_PLUGIN_ROOT}/skills/distribute/references (fallback)
BRAND_VOICE_PATH: <BRAND_DOCS_DIR>/brand-voice.md
```

## Content-Type Routing Table

| NotebookLM Output | Extension | GHL Action | Default Platforms | Preprocessing |
|---|---|---|---|---|
| Infographic | `.png` | Upload + Social Post | IG, FB, TH, LI | Auto-resize to 4:5 by upload script |
| Video | `.mp4` | Upload + Social Post + YouTube | IG, FB, TH, LI, YT | Size check (<500MB). No mixed-media on FB. YouTube via `youtube_upload.py`. |
| Audio (Podcast) | `.mp3` | Upload to Media Library | -- | Not directly postable. Optionally create text announcement |
| Slide Deck | `.pdf` | Upload to Media Library OR Carousel Post | -- or IG, FB, TH, LI | If user wants to post: run `pdf_to_slides.py` to extract PNGs, upload via `ghl_upload_carousel.sh`. LinkedIn also supports native PDF document posts. |
| Slide Deck | `.pptx` | Upload to Media Library OR Carousel Post | -- or IG, FB, TH, LI | Requires LibreOffice to convert to PDF first (`soffice --headless --convert-to pdf`). If unavailable, prompt user to use PDF version. |
| Report | `.md` | Text-only Post (excerpt) | FB, TH, LI | Summarize to 2-3 key points, respect char limits |
| Quiz | `.md`/`.json` | Text-only Post (teaser) | IG, FB, TH | Extract 1-2 questions as engagement teaser |
| Mind Map | `.json` | Upload to Media Library | -- | Not directly postable |
| Data Table | `.csv` | Upload to Media Library | -- | Not directly postable |
| Flashcards | `.md`/`.json` | Upload to Media Library | -- | Future: convert to carousel slides |

**Platform shorthands:** IG = Instagram, FB = Facebook, TH = Threads, LI = LinkedIn, YT = YouTube

## Workflow

Execute steps by reading the relevant file from `steps/`. Read each step file only when needed — do not read all steps upfront.

| Step | File | When |
|------|------|------|
| 0 | steps/00-resolve-location.md | Always |
| 1 | steps/01-identify-content.md | Always |
| 2 | steps/02-resolve-platforms.md | Always |
| 3 | steps/03-write-captions.md | When posting (not media-library-only) |
| 4 | steps/04-preprocess.md | When file needs conversion |
| 5 | steps/05-upload-media.md | Always |
| 6 | steps/06-schedule-posts.md | When posting (not media-library-only) |
| 7 | steps/07-log-confirm.md | Always |
| 8 | steps/08-drive-upload.md | When --drive flag |
| 9 | steps/09-youtube-upload.md | When --youtube or YT platform |



| Error | Cause | Action |
|-------|-------|--------|
| 401 Unauthorized | GHL token expired | Notify user to refresh GHL API key |
| 400/422 Bad Request | Invalid payload | Fall back to media-library-only upload |
| 429 Rate Limited | Too many API calls | Wait 10s, retry once |
| File >25MB (image) | File too large | Warn user, suggest compression |
| File >500MB (video) | File too large | Warn user, suggest compression |
| Upload returns no URL | API error | Show raw response, ask user to retry |
| Validation hook fails | Banned words/dashes/char limit | Fix caption issues, re-run |
| NotebookLM download fails | Artifact not ready | Check `notebooklm artifact list` |
| PDF render fails | pypdfium2 error or corrupt PDF | Show error from `pdf_to_slides.py` stderr, offer media-library-only upload of original PDF |
| PPTX, no LibreOffice | `soffice` not installed | Prompt user to `brew install libreoffice` or use the PDF version of the slide deck |
| Drive: No credentials.json | Drive API not set up | Guide user through one-time setup (see Drive Setup section) |
| Drive: Token expired | OAuth token needs refresh | Script auto-refreshes; if it fails, delete `drive_token.json` and re-auth |
| Drive: Quota exceeded | Drive storage full | Notify user to free up Drive space |
| YouTube: No credentials.json | YouTube API not set up | Guide user through one-time setup (see YouTube Setup section) |
| YouTube: Token expired | OAuth token needs refresh | Script auto-refreshes; if it fails, delete `youtube_token.json` and re-auth |
| YouTube: Quota exceeded | 10,000 units/day, ~6 uploads | Notify user to wait until midnight PT or request quota increase |
| YouTube: Private-only | Unaudited API project | Videos upload as private. User can change in YouTube Studio or apply for compliance audit |

## Autonomy Rules

**Run automatically (no confirmation):**
- Reading `locations.json`, `ghl_accounts_map.json`
- Running `next_slot.sh` to calculate schedule
- Uploading to GHL media library
- Running `pdf_to_slides.py` to extract PNGs from a PDF (read-only, writes to /tmp)

**Ask before running:**
- Creating social media posts (`ghl_create_post.sh`) -- always show captions first
- Uploading to YouTube (`youtube_upload.py`) -- always show title/description first
- Downloading artifacts from NotebookLM
- Writing to `ghl_post_log.md`

## Adding a New GHL Subaccount

To add a new client/subaccount for distribution:

**1. Get the GHL Location ID** from the GoHighLevel dashboard (Settings > Business Info > Location ID).

**2. Add to `locations.json`** (local copy — edits only affect this project):
```json
{
  "default": "my-brand",
  "locations": {
    "my-brand": { "locationId": "YOUR_LOCATION_ID", "name": "My Brand" },
    "new_client": {
      "locationId": "NEW_LOCATION_ID_HERE",
      "name": "New Client Name",
      "senderEmail": "client@example.com",
      "senderName": "Client Name"
    }
  }
}
```

**3. Fetch connected social accounts:**
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/ghl_get_accounts.sh" --location new_client
```
This returns all social accounts connected to that GHL subaccount.

**4. Add account mapping to `ghl_accounts_map.json`:**
```json
{
  "ces": { ... },
  "new_client": {
    "name": "New Client Name",
    "accounts": {
      "FB": { "id": "<from step 3>", "name": "Client Facebook", "platform": "facebook" },
      "IG": { "id": "<from step 3>", "name": "Client Instagram", "platform": "instagram" },
      "TH": { "id": "<from step 3>", "name": "Client Threads", "platform": "threads" },
      "LI": { "id": "<from step 3>", "name": "Client LinkedIn", "platform": "linkedin" }
    }
  }
}
```

**5. Use it:**
```
/distribute ./infographic.png IG FB --location new_client
```

**Notes:**
- The same `GHL_API_KEY` works for all subaccounts (set in this project's `.env`)
- Brand voice rules are shared across all locations
- Each location gets its own scheduling timeline via `next_slot.sh --location <loc>`
- The post log tracks which location each post belongs to
