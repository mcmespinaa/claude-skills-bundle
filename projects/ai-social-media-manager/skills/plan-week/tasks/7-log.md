# Task 7 -- Log and Confirm

Record results and present final summary.

## Steps

1. Append each successful post to `ghl_post_log.md`:
   ```
   | <Location> | <Platform> | <Scheduled DateTime> | <GHL Post ID> | <Status> | <Notes> |
   ```
   Status values: `scheduled`, `deleted`, `text-fallback`, `failed`. Metadata (slide count, model, topic) goes in Notes.

2. Update `content-plan.md`: change `**Status:** draft` to `**Status:** scheduled` and fill in `**Post ID:**` for each published post.

3. Present a summary table:
   ```
   Weekly Plan Published!

   | Day | Platform | Scheduled At | Post ID | Status |
   | ... | ...      | ...          | ...     | ...    |

   Total: [N] posts scheduled across [date range].
   ```

## Resume Support

If the workflow was interrupted and resumed with `--resume`:
1. Read `content-plan.md`, find posts with `**Status:** draft`
2. Cross-check against `ghl_post_log.md` to confirm genuinely unpublished
3. Re-run only the unpublished posts through Tasks 6-7
4. Update `content-plan.md` status and post IDs
