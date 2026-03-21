# Task 6 -- Publish (Parallel Execution)

Three rounds of execution with error isolation per post.

## Round 1 -- Generate Images (sequential)

For each day with `visual_source: gemini`:
1. Generate the image using Gemini with the prompt from `content-plan.md`.
2. Save generated images locally.
3. Sequential because Gemini has rate limits.
4. For carousel days, generate all slides (8-10 images per carousel).

**Round 1b -- Visual QA (per day, within Round 1):**
After generating each day's images:
1. Run Visual QA from `/post` SKILL.md Step 4b and `${CLAUDE_SKILL_DIR}/../../shared/references/visual-qa.md`.
2. Read each image, compare text against `content-plan.md`.
3. Check brand consistency and layout.
4. Score PASS/FAIL. Regenerate failures (up to 2 retries per slide).

## Round 2 -- Upload Media (parallel)

Issue parallel Bash calls to upload all media in a single response:

- Single image days:
  ```bash
  bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_upload_media.sh \
    --file <path> --name "plan-week-dayN"
  ```
- Carousel days:
  ```bash
  bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_upload_carousel.sh \
    --file <slide1> --file <slide2> ... --platform <platform>
  ```

Collect all returned media URLs from the responses.

## Round 3 -- Schedule Posts (parallel)

Issue parallel Bash calls to schedule all posts in a single response:

```bash
bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_create_post.sh \
  --account-id "<id from ghl_accounts_map.json>" \
  --summary "<full caption text>" \
  --scheduled-at "<ISO 8601 datetime>" \
  --media-url "<url or comma-separated for carousel>"
```

Each post is independent (different account ID + schedule date). Fire all simultaneously.

The validation hook fires automatically on every `ghl_create_post.sh` call. If validation fails on a specific post, fix the issue (replace em dash, remove banned word, trim length) and retry just that post.

## Error Isolation

If post 7 of 14 fails, posts 1-6 and 8-14 still succeed.
Report: "[N] of [total] posts scheduled. Post [X] ([platform], [day]) failed: [error]. Retry?"

Proceed to Task 7 when all posts are scheduled (or user declines retry of failures).
