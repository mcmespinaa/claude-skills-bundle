---
name: edit-post
description: >-
  Edits a previously scheduled social media post via the GoHighLevel API. Can
  update caption, media, or schedule time. Use when user says /edit-post, edit
  post, update post, change the caption, reschedule post, or provides a GHL Post
  ID to modify.
allowed-tools: "Bash(bash:*) Bash(curl:*) Read Write Edit"
---

# /edit-post -- Edit a Scheduled Post

> **Do NOT use for:** Creating new posts (use /post), or removing posts entirely (use /delete-post). Only edits posts still in the GHL schedule.

## Workflow

1. **Identify the post.** Accept a GHL Post ID, or look up by date/platform in `ghl_post_log.md`.

2. **Fetch current content** from GHL API:
   ```bash
   bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_update_post.sh --post-id <id> --location <shorthand> --get
   ```

3. **Show current caption** to the user. Ask: "What would you like to change?"

4. **Apply edits.** Run the pre-publish checklist from `/post` SKILL.md (no em dashes, no banned words, character limits, etc.).

5. **Update the post** via GHL API:
   ```bash
   bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_update_post.sh \
     --post-id <id> \
     --location <shorthand> \
     --summary "updated caption" \
     [--media-url <url>] \
     [--scheduled-at <ISO 8601>]
   ```

6. **Update `ghl_post_log.md`:** Add a Notes entry like "edited: updated caption".

7. **Confirm:** "Post [ID] updated on [platform]. New schedule: [datetime]."

## Script Reference

`ghl_update_post.sh` flags:
- `--post-id <id>` (required): GHL Post ID
- `--location <shorthand>` (optional): Location from `locations.json`
- `--get`: Fetch the post (read-only, returns current data)
- `--summary "text"`: New caption text
- `--media-url <url>`: New media URL (replaces existing)
- `--scheduled-at <ISO 8601>`: New schedule datetime

## Error Handling

### Post Not Found (404)
- Verify the Post ID in `ghl_post_log.md`. It may have been deleted.
- Notify: "Post [ID] not found. It may have been deleted or the ID is incorrect."

### Token Expired (401)
- Notify: "Your GHL token appears expired. Please update `GHL_API_KEY` in `.claude/settings.local.json`."

### Invalid Update (422)
- Common causes: empty caption, invalid date format, invalid media URL.
- Show the full error response and ask the user to fix the input.

### Already Published
- If the post's `scheduledAt` is in the past, GHL may reject edits.
- Notify: "This post may have already been published. Check the GHL Social Planner UI."
