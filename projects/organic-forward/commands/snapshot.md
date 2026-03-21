Create a versioned snapshot of the current project state: commit to git and back up to Google Drive.

## Arguments
- $ARGUMENTS — optional commit message override (default: auto-generated from changes)

## Steps

1. **Gather current state**
   - Run `git status` in /Users/MC/organic-forward/
   - Run `git diff --stat` to summarize changes
   - Run `git log --oneline -5` to see recent commits
   - Note the current branch

2. **Stage and commit**
   - Stage all modified and new files with `git add -A`
   - EXCLUDE secrets: check that no `.env`, credentials, or key files are staged — unstage them if found
   - Generate a commit message in this format (unless the user provided $ARGUMENTS as override):
     ```
     snapshot: [brief summary of changes]

     Files changed: [count]
     Snapshot taken: [ISO 8601 timestamp]
     ```
   - Create the commit

3. **Create backup archive**
   - Run: `git archive --format=tar.gz -o /tmp/organic-forward-snapshot-$(date +%Y%m%d-%H%M%S).tar.gz HEAD`
   - Copy to Google Drive: `rclone copy /tmp/organic-forward-snapshot-*.tar.gz gdrive:"AI Projects/Organic Forward/snapshots/" --no-traverse`
   - Clean up the /tmp file after successful upload

4. **Tag the snapshot** (lightweight tag)
   - Tag format: `snapshot/YYYY-MM-DD-HHMMSS`
   - Example: `snapshot/2026-03-16-143022`

5. **Output a snapshot receipt**

```
## Snapshot — [timestamp]

- Branch: [branch]
- Commit: [short hash] [message]
- Tag: [tag name]
- Files: [N] changed, [N] insertions, [N] deletions
- Backup: gdrive:AI Projects/Organic Forward/snapshots/[filename]
- Status: [success/partial — details if partial]
```

## Rules
- NEVER commit `.env`, `.env.*`, `credentials.json`, `serviceAccountKey.json`, or any file matching `*secret*`
- If `rclone` is not configured or the copy fails, still complete the git commit and tag — report the backup as skipped
- Do not push to remote unless the user explicitly says "and push"
- If there are no changes to commit, say so and skip — do not create empty commits
- Keep it fast — this is meant to be a quick save point, not a production release
