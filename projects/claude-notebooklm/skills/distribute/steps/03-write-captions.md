# Step 3: Write Captions

**CRITICAL:** Before writing captions, read `<BRAND_DOCS_DIR>/brand-voice.md` for the full brand voice rules, writing style, and banned words list. Follow those rules exactly.

Key rules summary:
- No em dashes or en dashes (use commas, periods, or "...")
- No banned words (see validation hook for the full list)
- Platform character limits: Instagram 2200, Facebook 63206, Threads 500, LinkedIn 3000, Twitter 280
- Write in the brand's voice and tone

For each target platform, write a tailored caption:
- **Instagram:** Visual-first, hashtags allowed, up to 2200 chars
- **Facebook:** Slightly longer, conversational, link-friendly
- **LinkedIn:** Professional tone, longer form with line breaks between ideas, 1300-1900 chars sweet spot. No external links in post body (60% reach penalty). 3-5 hashtags at end.
- **Threads:** Short and punchy, max 500 chars

Present all captions to the user: **"Here are your captions for [platforms]. Approve, edit, or regenerate?"**

Do NOT proceed to upload/post until the user approves the captions.

## Step 3.5: Fetch Stock Image (optional)

When the user wants a social post but has no image, or says "find an image for this":

```bash
RESULT=$(python3 "${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/unsplash_fetch.py" \
  --query "<topic keywords>" \
  --output-dir /tmp)
```

Parse the JSON output to get `images[0].file` (local path) and `images[0].attribution` (credit line).
- Upload the file via `ghl_upload_media.sh --file <path>`
- Append the attribution to the caption: `Photo by {Name} on Unsplash`
- For YouTube thumbnails, use `--orientation landscape --size full`
- Use `--no-brand-defaults` if the content needs a different aesthetic
