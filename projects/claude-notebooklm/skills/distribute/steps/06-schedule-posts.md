# Step 6: Schedule & Create Posts

**Calculate next slot:**
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/next_slot.sh" \
  --log "$PWD/ghl_post_log.md" \
  --location <LOCATION>
```

Present the proposed schedule: **"Scheduling for [datetime]. Change?"**

If user provides a custom datetime, use that instead.

**Create post for each platform:**
```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/ghl_create_post.sh" \
  --account-id "<account_id>" \
  --summary "<platform_caption>" \
  --scheduled-at "<ISO_8601_datetime>" \
  --media-url "<uploaded_media_url>" \
  --media-type "<image/jpeg|image/png|video/mp4>" \
  --user-id "<locationId>" \
  --location <LOCATION>
```

**Important:** `--user-id` is required by the GHL API. Use the resolved locationId as the userId. The `--media-type` must be a MIME type, not a generic type like "image".

The `validate_ghl_post.py` hook fires automatically before each `ghl_create_post.sh` call. If validation fails, fix the caption issues and retry.

For text-only posts (reports, quiz teasers), omit `--media-url` and `--media-type`.
