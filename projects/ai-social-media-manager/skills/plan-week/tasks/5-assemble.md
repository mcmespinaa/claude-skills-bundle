# Task 5 -- Assemble content-plan.md

Combine all outputs from Tasks 1-4 into the staging file.

## Format

Write `content-plan.md` in the project root using the exact format from `${CLAUDE_SKILL_DIR}/references/content-plan-format.md`.

Key rules:
- Days delimited by `## Day N` headers
- Posts within days delimited by `### Post N` headers
- Key-value fields use `**key:** value` pattern
- Draft text in ` ```draft ` fences
- Visual prompts in ` ```prompt ` fences
- All `**Status:**` fields set to `draft`
- All `**Post ID:**` fields left empty

## Present to User

Show a summary:

> Here is your weekly content plan for [start date] to [end date]. [N] posts across [platforms]. Review `content-plan.md`, make any edits, then tell me to publish.

Follow with a quick table:

```
| Day | Date | Theme | Type | Platforms |
| ... | ...  | ...   | ...  | ...       |
```

## Wait for Approval

The user can:
1. **Approve all** -- "Looks good, publish" or "Schedule it"
2. **Edit the file** -- User edits `content-plan.md` directly, then says "Updated, go ahead"
3. **Request changes** -- "Change day 3 topic to X" or "Make Tuesday a carousel"
4. **Approve partial** -- "Only publish days 1-3 for now"

If the user edits `content-plan.md`, re-read the file to pick up all changes before publishing.

**Do NOT proceed to Task 6 without explicit approval.**
