# Distribution, Helper Scripts & Troubleshooting

## Step 9 — Distribution (Optional)

If the user passes `--youtube` or `--drive`, run these after scheduling:

### `--youtube` — Upload Video to YouTube

Only applies when the post contains a video file (carousel video slides or a standalone video post).

```bash
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/youtube_upload.py \
  --file /path/to/video.mp4 \
  --title "<post topic as video title>" \
  --description "<caption adapted for YouTube>" \
  --tags "ai,social media,content" \
  --privacy unlisted \
  --thumbnail /path/to/slide_01.png
```

**Rules:**
- Default privacy: `unlisted` (safe default, user can override with `--youtube public` or `--youtube private`).
- Title: derived from the post hook/topic, under 100 characters.
- Description: use the longest caption (LinkedIn or IG) adapted for YouTube (remove emoji, add paragraph breaks).
- Tags: extract 5-10 keywords from the caption.
- Thumbnail: use the hook slide (slide 1) if it exists, otherwise skip.
- If `--publish-at` is provided, schedule the YouTube publish to match the GHL schedule date.
- **Requires OAuth setup.** If `~/.notebooklm/youtube_credentials.json` does not exist, inform the user and skip (do not fail the whole post).

Report: **"Also uploaded to YouTube (unlisted): https://youtube.com/watch?v=..."**

### `--drive` — Backup to Google Drive

Backs up generated carousel slides or post images to Google Drive.

```bash
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/drive_upload.py \
  --file /path/to/slide.png \
  --folder "Social Media/Carousels/<date>"
```

**Rules:**
- Folder structure: `Social Media/Carousels/YYYY-MM-DD` for carousels, `Social Media/Posts/YYYY-MM-DD` for single images.
- Upload all slides in the carousel (loop over files).
- If `--share` email is provided, share the folder with that email.
- **Requires OAuth setup.** If `~/.notebooklm/drive_credentials.json` does not exist, inform the user and skip.

Report: **"Carousel backed up to Drive: [link]"**

---

## Helper Scripts

All shared scripts are in `${CLAUDE_SKILL_DIR}/../../shared/scripts/`:

| Script                    | Purpose                                          |
| ------------------------- | ------------------------------------------------ |
| `ghl_upload_media.sh`     | Upload a single file or URL to GHL Media Storage. Auto-resizes local images to 4:5 (1080x1350) with ivory padding. Videos (.mp4, .mov) skip resize. Pass `--no-resize` to skip. |
| `ghl_upload_carousel.sh`  | Batch upload multiple files/URLs for carousels. Auto-resizes local images to 4:5 (1080x1350) with ivory padding. Videos skip resize. Use `--multimodal` for JSON manifest output with URL+type pairs. |
| `ghl_create_post.sh`      | Create/schedule a post (single, carousel, or mixed-media). Supports comma-separated `--media-type` for per-URL types (e.g., `"image/jpeg,video/mp4,image/jpeg"`). |
| `ghl_get_accounts.sh`     | Fetch connected social media accounts            |
| `next_slot.sh`            | Calculate next available 24h slot from the log   |
| `resize_to_4x5.py`        | Resize an image to 1080x1350 (4:5) with ivory (#f7f4ef) padding. Used automatically by the upload scripts. |
| `gen_video_slide.py`      | Generate a single video slide via Veo 3.1. Modes: `text-to-video` and `image-to-video`. Async polling with 10-min timeout. |
| `gen_multimodal_slides.py` | Batch orchestrator: generates mixed image+video carousel. Round 1: images (Gemini 3.1 Flash). Round 2: videos (Veo 3.1). Auto-fallback on video failure. |

---

## Troubleshooting

### Gemini returns blurry or off-brand images
**Cause:** Prompt included CSS-like specs (font names with px sizes, hex codes) that Gemini rendered as visible text.
**Solution:** Describe styles abstractly. Instead of "DM Sans, 12px, #7a7268", use "smaller clean sans-serif font, muted warm gray tone". Only put actual content text in quotes.

### GHL rejects media upload with "Invalid File Type"
**Cause:** Video file uploaded without explicit MIME type.
**Solution:** Use `file=@path.mp4;type=video/mp4` in curl calls. The upload scripts handle this automatically.

### Post blocked by quality gate hook
**Cause:** Caption contains em dashes, banned words, or exceeds character limit.
**Solution:** Read the hook's error message. Replace em dashes with commas or "...", remove banned words, or trim the caption. Then retry. Never bypass with --no-verify.

### GHL returns 422 on text-only post
**Cause:** Missing `"media": []` in the request body.
**Solution:** The `ghl_create_post.sh` script auto-adds an empty media array. If calling the API directly, always include `"media": []`.

### LinkedIn post fails with unsupported media type
**Cause:** Attempted to upload PDF or document type via API.
**Solution:** LinkedIn API only accepts image/jpeg, image/png, image/gif, video/mp4. Use multi-image carousel (same as IG/FB) for LinkedIn. PDF carousels are UI-only.

### Veo 3.1 returns 400 error
**Cause:** Common issues: using `generateContent` endpoint (should be `predictLongRunning`), including `personGeneration: "dont_allow"` (not supported), or requesting 4s/6s video at 1080p (requires 8s).
**Solution:** Use the `gen_video_slide.py` script which handles routing correctly. For 1080p, always use 8-second duration. For shorter clips, use 720p.
