# Step 9: YouTube Upload (conditional)

**When to execute:** User passes `--youtube` flag or `YT` platform shorthand. Only applicable to `.mp4` video files.

Can be combined with GHL + Drive: `/distribute ./video.mp4 IG FB --youtube --drive`

## Workflow

1. **Write title and description** for the YouTube upload (follow brand voice rules). Present to user for approval alongside social captions.

2. **Upload the video:**
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/youtube_upload.py" \
     --file "<video.mp4>" \
     --title "<title>" \
     --description "<description>" \
     --tags "<comma,separated,tags>" \
     --privacy private \
     --thumbnail "<thumbnail.png>"
   ```

3. **Parse the JSON output:**
   ```json
   {
     "id": "<video_id>",
     "title": "<title>",
     "link": "https://www.youtube.com/watch?v=<video_id>",
     "privacy": "private",
     "publish_at": null
   }
   ```

4. **Confirm to user:** "Uploaded to YouTube: [title]. Link: [youtube_link]. Privacy: [status]."

**Scheduling:** Use `--publish-at` with ISO 8601 datetime. Video uploads as private, auto-publishes at the specified time.

**Thumbnail:** Optional. JPEG or PNG, max 2 MB, recommended 1280x720 (16:9). Channel must be phone-verified.

## Quota

- Each upload costs **1,600 quota units** out of 10,000 daily (~6 uploads/day)
- Thumbnail upload costs ~50 units

## Privacy Note

API projects created after July 2020 can only upload **private** videos until a compliance audit is passed. Videos can be shared via direct link, scheduled via `--publish-at`, or changed to public in YouTube Studio.

## Setup (One-Time)

1. Google Cloud Console, enable **YouTube Data API v3**
2. Create OAuth 2.0 credentials (Desktop app)
3. Download to `~/.notebooklm/youtube_credentials.json`
4. Add your Google account as a test user (OAuth consent screen)
