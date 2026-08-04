---
name: save-to-drive
description: >-
  Upload any file to Google Drive with automatic folder organization. Works with
  any output from other skills (documents, reports, infographics, presentations,
  etc.). Supports subfolder paths and file sharing.
argument-hint: '"file_path" [--folder "subfolder/path"] [--share email@example.com]'
user-invokable: true
---

# Save to Google Drive

Upload any file directly to Google Drive. This is the standalone "save" companion to `/distribute` — use it when you just want a file in Drive without social media posting.

## When This Skill Activates

**Explicit:** `/save-to-drive`, "save to Drive", "upload to Drive", "put this on Drive", "save output to Drive"

**Intent detection:**
- "Save that document to Drive"
- "Upload the report to my Drive"
- "Put this in Drive so I can access it later"
- "Send the output to Google Drive"
- "Can you save this to Drive automatically?"

**Auto-save pattern:** When another skill produces an output file AND the user previously said "save everything to Drive" or "always upload to Drive", chain this skill automatically after the primary skill completes.

## Constants

```
SCRIPTS_DIR: ${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts
DRIVE_UPLOAD: ${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/drive_upload.py
```

The upload script lives in `distribute/scripts/` because it was built as part of the distribute pipeline. This skill reuses it directly.

## Prerequisites

1. **Google OAuth credentials** at `~/.notebooklm/drive_credentials.json`
   - Download from [Google Cloud Console > Credentials](https://console.cloud.google.com/apis/credentials)
   - Must be OAuth 2.0 Client ID (Desktop application type)
2. **Python packages:** `pip3 install google-api-python-client google-auth google-auth-oauthlib`
3. **First run:** The script opens a browser window for OAuth consent. After that, tokens auto-refresh from `~/.notebooklm/drive_token.json`.

## Workflow

### Step 1: Identify the File

Three patterns:

1. **Explicit path:** `/save-to-drive ./report.docx` — use the file directly.
2. **After generation:** Claude just created a file (e.g., a .docx, .pptx, .xlsx) — use that file path.
3. **Latest output:** User says "save that to Drive" — find the most recently created file in the project output/ directory or the file just discussed in conversation.

### Step 2: Determine Destination Folder

- **Default:** `NotebookLM Exports` (the project's shared Drive folder)
- **Custom subfolder:** `--folder "Reports/March 2026"` creates nested folders automatically
- **Direct folder ID:** `--folder-id "GOOGLE_DRIVE_FOLDER_ID"` for targeting a specific folder

Folder hierarchy is auto-created if it doesn't exist.

### Step 3: Upload

```bash
python3 "$SCRIPTS_DIR/drive_upload.py" \
  --file "<file_path>" \
  --folder "<folder_path>"
```

The script outputs JSON to stdout:
```json
{
  "id": "1abc...",
  "name": "report.docx",
  "link": "https://drive.google.com/file/d/1abc.../view",
  "folder": "Reports/March 2026"
}
```

### Step 4: Share (Optional)

If `--share email@example.com` is provided:

```bash
python3 "$SCRIPTS_DIR/drive_upload.py" \
  --file "<file_path>" \
  --folder "<folder_path>" \
  --share "user@example.com"
```

### Step 5: Report

Tell the user:
- File name uploaded
- Google Drive link (clickable)
- Folder location
- Sharing status (if applicable)

## Examples

```bash
# Save a document to the default Drive folder
/save-to-drive ./report.docx

# Save with a subfolder
/save-to-drive ./analysis.xlsx --folder "Q1 Reports"

# Save and share
/save-to-drive ./presentation.pptx --folder "Client Decks" --share client@company.com

# After generating output, auto-save
# (Claude creates a file, then uploads it)
/save-to-drive ./output/Project Review.docx --folder "Reviews/2026"
```

## Chaining with Other Skills

This skill is designed to be called **after** any skill that produces a file. Pattern:

1. User asks: "Create a report about X and save it to Drive"
2. Claude runs the appropriate skill (e.g., generates a .docx)
3. Claude immediately runs `/save-to-drive` on the output file
4. User gets both the local file link AND the Drive link

To make this automatic for all future outputs, the user can say:
- "From now on, always save outputs to Drive"
- "Auto-upload everything to Drive"

When this instruction is active, append a Drive upload step to every file-producing workflow.

## Supported File Types

All common formats are supported via MIME type mapping:

| Extension | Type |
|-----------|------|
| `.png`, `.jpg`, `.gif` | Images |
| `.mp3` | Audio |
| `.mp4` | Video |
| `.pdf` | PDF |
| `.pptx` | Presentations |
| `.docx` | Word documents |
| `.xlsx` | Spreadsheets |
| `.md` | Markdown |
| `.html` | HTML |
| `.json` | JSON |
| `.csv` | CSV |
| `.txt` | Plain text |

Any unlisted extension uploads as `application/octet-stream`.

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| No credentials file | `~/.notebooklm/drive_credentials.json` missing | Tell user to download from Google Cloud Console |
| Token expired | OAuth refresh failed | Delete `~/.notebooklm/drive_token.json` and re-auth |
| File not found | Bad path | Check the file exists before calling the script |
| Permission denied | Drive folder not accessible | Verify folder ID or create a new subfolder |
| Import error | Python packages missing | Run `pip3 install google-api-python-client google-auth google-auth-oauthlib` |
