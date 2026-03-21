# Step 5: Upload to GHL Media

Call the upload script by absolute path:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/ghl_upload_media.sh" \
  --file "<file_path>" \
  --name "notebooklm-<type>-$(date +%Y%m%d)" \
  --location <LOCATION>
```

For videos, add `--no-resize`:
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/ghl_upload_media.sh" \
  --file "<file_path>" \
  --name "notebooklm-video-$(date +%Y%m%d)" \
  --no-resize \
  --location <LOCATION>
```

**Parse the response:** The upload returns JSON. Extract the media URL from the response (look for `"url"` field in the returned JSON).

If this is a media-library-only upload, stop here and confirm to the user.

**For slide deck carousels (PDF path):** Use `ghl_upload_carousel.sh` instead:
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/ghl_upload_carousel.sh" \
  --file "/tmp/slides-.../slide-01.png" \
  --file "/tmp/slides-.../slide-02.png" \
  ... \
  --platform ig \
  --location <LOCATION>
```
Pass each slide PNG as a separate `--file` argument. The script outputs a comma-separated list of GHL media URLs. Pass these to `ghl_create_post.sh` as `--media-url` in Step 6.
