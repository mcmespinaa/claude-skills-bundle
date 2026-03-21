# Step 8: Google Drive Upload (conditional)

**When to execute:** User passes `--drive` flag, or says "upload to Drive", "save to Drive".

Can be combined with GHL: `/distribute ./file.png IG FB --drive` (posts to social AND uploads to Drive).

## Workflow

1. **Determine destination folder:**
   - Default: User's designated Drive folder (set `GOOGLE_DRIVE_FOLDER_ID` in `.env`)
   - With `--drive-folder "<name>"`: Creates a subfolder inside the default folder
   - With `--drive-folder-id "FOLDER_ID"`: Uploads directly to a specific folder ID

2. **Upload the file:**
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/drive_upload.py" \
     --file "<file_path>" \
     --folder "NotebookLM Exports/<notebook_title>" \
     --share "<email>" (optional)
   ```

3. **Confirm to user:** "Uploaded to Google Drive: [file name] in NotebookLM Exports/<notebook>/. [Share link]"

## Setup (One-Time)

1. Go to Google Cloud Console, create or select a project
2. Enable the **Google Drive API**
3. Create OAuth 2.0 credentials (Desktop app)
4. Download `credentials.json` to `~/.notebooklm/drive_credentials.json`
5. First upload will open a browser for OAuth consent

The script handles OAuth auth (token cached at `~/.notebooklm/drive_token.json`), auto-creates folder hierarchy, returns shareable link, and supports all file types.
