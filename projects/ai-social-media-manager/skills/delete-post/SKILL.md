---
name: delete-post
description: >-
  Deletes a previously scheduled social media post from the GoHighLevel Social
  Planner. This cannot be undone. Use when user says /delete-post, delete post,
  remove post, cancel scheduled post, or provides a GHL Post ID to remove.
allowed-tools: "Bash(bash:*) Bash(curl:*) Read Write Edit"
---

# /delete-post -- Delete a Scheduled Post

## Role

You are a post management assistant. You delete scheduled posts from the GoHighLevel Social Planner and keep the post log accurate. You always confirm before deleting and clearly communicate the consequences.

> **Do NOT use for:** Editing post content (use /edit-post), or removing posts already published on social platforms (GHL deletion only affects the schedule).

---

## Important

- Deletion from GHL is **permanent and cannot be undone**.
- Deleting a post that has already been published removes it from the GHL schedule but does **NOT** remove it from the social media platform itself.
- Always update `ghl_post_log.md` after deletion so the timeline logic in `/post` and `/plan-week` stays accurate.

---

## Workflow

### Step 1 -- Identify the Post

Accept the post to delete from one of these sources:

| Input | How to resolve |
|-------|---------------|
| GHL Post ID (e.g., `69a2f3b19d733f697a8fb48c`) | Use directly. Verify it exists in `ghl_post_log.md`. |
| Date + platform (e.g., "delete the IG post on March 13") | Search `ghl_post_log.md` for matching rows. If multiple matches, list them and ask which one. |
| "Delete the last post" / "delete today's post" | Read `ghl_post_log.md`, find the most recent entry matching the criteria. |
| "Delete all posts on [date]" | Find all rows for that date. List them. Confirm the batch. |

Before proceeding, read `ghl_post_log.md` and verify:
- The post ID exists in the log.
- The status is not already `deleted`.
- Note the platform, schedule date, and any notes (slide count, etc.) for the confirmation message.

### Step 2 -- Confirm with User

**Always confirm before deleting.** Present the post details clearly:

"Delete this post?"

| Field | Value |
|-------|-------|
| Post ID | `[id]` |
| Platform | [Facebook / Instagram / Threads / LinkedIn / etc.] |
| Scheduled for | [date and time] |
| Notes | [carousel 10 slides / video post / etc.] |

"This cannot be undone. Proceed?"

**For batch deletions** (multiple posts), list all posts in a table and confirm the full set:

"Delete these [N] posts?"

| # | Post ID | Platform | Scheduled At | Notes |
|---|---------|----------|-------------|-------|
| 1 | `[id]` | Instagram | 2026-03-13T09:00:00Z | carousel 10 slides |
| 2 | `[id]` | Facebook | 2026-03-13T09:00:00Z | carousel 10 slides |
| 3 | `[id]` | Threads | 2026-03-13T09:00:00Z | |

"This cannot be undone. Proceed with all [N]?"

**Do NOT delete without explicit user confirmation.**

### Step 3 -- Delete via GHL API

Run the delete script for each confirmed post:

```bash
bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_delete_post.sh --post-id <id> --location <shorthand>
```

**Flags:**
- `--post-id <id>` (required): The GHL Post ID to delete.
- `--location <shorthand>` (optional): Location shorthand from `locations.json`. Defaults to the "default" location if omitted.

**What the script does:**
1. Resolves the location to a GHL locationId via `resolve_location.sh`.
2. Sends `DELETE /social-media-posting/{locationId}/posts/{postId}` to the GHL API.
3. Returns `200` or `204` on success, or exits with an error code.

**For batch deletions:** Run each delete sequentially (not parallel) to avoid rate limiting. If one fails, continue with the rest and report the failure.

### Step 4 -- Update the Post Log

After each successful deletion, edit `ghl_post_log.md`:

1. Find the row matching the deleted Post ID.
2. Change the **Status** column from `scheduled` to `deleted`.
3. Add a reason in the **Notes** column:
   - `"replaced by [new Post ID]"` if the user is replacing with a new version.
   - `"user requested deletion"` for standalone deletions.
   - `"batch cleanup"` for multi-post removals.
   - Or whatever reason the user provides.

**Example before:**
```
| ces | Instagram | 2026-03-13T09:00:00Z | 69a2f3b19d733f697a8fb48c | scheduled | carousel 10 slides |
```

**Example after:**
```
| ces | Instagram | 2026-03-13T09:00:00Z | 69a2f3b19d733f697a8fb48c | deleted | replaced by 69a2fb14 |
```

### Step 5 -- Confirm to User

After all deletions are complete, confirm with a summary:

**Single post:**
"Post `[id]` deleted from [platform]. It was scheduled for [datetime]."

**Batch:**
"[N] posts deleted:"

| Post ID | Platform | Was scheduled for | Status |
|---------|----------|-------------------|--------|
| `[id]` | Instagram | 2026-03-13 09:00 UTC | deleted |
| `[id]` | Facebook | 2026-03-13 09:00 UTC | deleted |

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GHL_API_KEY` | Private Integration Token (Sub-Account) | Yes |
| `GHL_VERSION` | API version header (default `2021-07-28`) | No (has default) |
| `GHL_LOCATION_ID` | Fallback location ID if no `locations.json` exists | Only if no locations.json |

---

## Multi-Location Support

The delete script supports multi-location via `--location <shorthand>`. Resolution order:
1. `--location <shorthand>` flag -> looks up locationId in `locations.json`
2. No flag -> uses the `"default"` key from `locations.json`
3. No `locations.json` -> falls back to `$GHL_LOCATION_ID` env var

If the user has multiple locations, check which location the post belongs to in `ghl_post_log.md` (Location column) and pass the correct `--location` flag.

---

## Examples

### Example 1: Delete by Post ID

User says: "Delete post 69a2f3b19d733f697a8fb48c"

Actions:
1. Search `ghl_post_log.md` for that ID. Found: Instagram, 2026-03-13T09:00:00Z, carousel 10 slides.
2. Confirm: "Delete this Instagram carousel (March 13, 10 slides)? This cannot be undone."
3. User confirms. Run `ghl_delete_post.sh --post-id 69a2f3b19d733f697a8fb48c`.
4. Update log: status -> `deleted`, notes -> `user requested deletion`.
5. Confirm: "Post deleted from Instagram."

Result: One post deleted, log updated.

### Example 2: Delete by date

User says: "Delete all posts scheduled for March 15"

Actions:
1. Search `ghl_post_log.md` for `2026-03-15`. Found 3 posts (IG, FB, Threads).
2. Present all 3 in a table. Confirm: "Delete these 3 posts? This cannot be undone."
3. User confirms. Run delete script 3 times (sequentially).
4. Update all 3 rows in log: status -> `deleted`, notes -> `batch cleanup`.
5. Confirm: "3 posts deleted (IG, FB, Threads) for March 15."

Result: Three posts deleted, all log entries updated.

### Example 3: Delete and replace

User says: "Delete the Threads post for March 13, I want to redo it"

Actions:
1. Search log for Threads + March 13. Found: `69a2f3d7633dfb1455dffe9a`.
2. Confirm deletion.
3. Delete via script.
4. Update log: status -> `deleted`, notes -> leave blank for now (will fill "replaced by [new ID]" when the replacement is scheduled).
5. Confirm: "Threads post for March 13 deleted. Ready to create the replacement with /post."

Result: Old post deleted, slot freed for a new post.

---

## Troubleshooting

### Post Not Found (404)
**Cause:** The Post ID does not exist in GHL. It may have already been deleted, or the ID is wrong.
**Solution:**
1. Check `ghl_post_log.md` for the correct ID.
2. If the status is already `deleted`, notify: "This post was already deleted."
3. If the ID is not in the log at all, notify: "Post ID not found in the log or GHL. Verify the ID."

### Token Expired (401)
**Cause:** The GHL API key has expired or is invalid.
**Solution:** Notify: "Your GHL token appears expired. Please update `GHL_API_KEY` in `.claude/settings.local.json`."

### Already Published Post
**Cause:** The post's scheduled time is in the past, meaning it has likely already been published to the social platform.
**Solution:**
1. GHL may still accept the delete (removes from schedule history).
2. Warn the user: "This post was scheduled for [past date] and may have already been published. Deleting from GHL will NOT remove it from [platform]. To remove the published post, go to [platform] directly."
3. Proceed with deletion if the user still wants to clean up the GHL schedule.

### Rate Limited (429)
**Cause:** Too many API calls in quick succession (common during batch deletions).
**Solution:** Wait 10 seconds, retry once. If still failing, notify and offer to retry later.

### Wrong Post Deleted
**Cause:** User provided the wrong ID or confirmed the wrong post.
**Solution:** Deletion from GHL cannot be undone. The post must be recreated using `/post` or `/plan-week`. The log entry will show `deleted` status for audit purposes.
