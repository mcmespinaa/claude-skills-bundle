#!/usr/bin/env python3
"""drive_upload.py — Upload a file to Google Drive with folder organization.

Usage:
  python3 drive_upload.py --file ./infographic.png --folder "NotebookLM Exports/My Research"
  python3 drive_upload.py --file ./podcast.mp3 --folder-id "DRIVE_FOLDER_ID"
  python3 drive_upload.py --file ./report.md --folder "Exports" --share user@example.com
"""

import argparse
import json
import os
import sys

CREDENTIALS_PATH = os.path.expanduser("~/.notebooklm/drive_credentials.json")
TOKEN_PATH = os.path.expanduser("~/.notebooklm/drive_token.json")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
DEFAULT_FOLDER_ID = "1tF0v7oV0JpC_Ei7TBjk-h730U3sSp0BP"

MIME_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".mp3": "audio/mpeg",
    ".mp4": "video/mp4",
    ".pdf": "application/pdf",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".md": "text/markdown",
    ".json": "application/json",
    ".csv": "text/csv",
    ".html": "text/html",
    ".txt": "text/plain",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def get_credentials():
    """Get or refresh OAuth credentials."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Error: Google API libraries not installed.", file=sys.stderr)
        print("Run: pip3 install google-api-python-client google-auth google-auth-oauthlib", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(CREDENTIALS_PATH):
        print(f"Error: No credentials file at {CREDENTIALS_PATH}", file=sys.stderr)
        print("Download OAuth credentials from Google Cloud Console and save there.", file=sys.stderr)
        sys.exit(1)

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return creds


def get_or_create_folder(service, folder_path, parent_id="root"):
    """Navigate/create a folder hierarchy like 'NotebookLM Exports/My Research'."""
    parts = [p.strip() for p in folder_path.split("/") if p.strip()]
    current_parent = parent_id

    for part in parts:
        query = (
            f"name = '{part}' and "
            f"'{current_parent}' in parents and "
            f"mimeType = 'application/vnd.google-apps.folder' and "
            f"trashed = false"
        )
        results = service.files().list(q=query, fields="files(id, name)", pageSize=1).execute()
        files = results.get("files", [])

        if files:
            current_parent = files[0]["id"]
        else:
            metadata = {
                "name": part,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [current_parent],
            }
            folder = service.files().create(body=metadata, fields="id").execute()
            current_parent = folder["id"]

    return current_parent


def upload_file(service, file_path, folder_id):
    """Upload a file to a specific Drive folder."""
    from googleapiclient.http import MediaFileUpload

    file_name = os.path.basename(file_path)
    ext = os.path.splitext(file_name)[1].lower()
    mime_type = MIME_MAP.get(ext, "application/octet-stream")

    metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    file = service.files().create(body=metadata, media_body=media, fields="id, name, webViewLink").execute()
    return file


def share_file(service, file_id, email):
    """Share a file with a specific email."""
    permission = {"type": "user", "role": "reader", "emailAddress": email}
    service.permissions().create(fileId=file_id, body=permission, sendNotificationEmail=False).execute()


def main():
    parser = argparse.ArgumentParser(description="Upload file to Google Drive")
    parser.add_argument("--file", required=True, help="Path to the file to upload")
    parser.add_argument("--folder", default="NotebookLM Exports", help="Drive folder path (e.g. 'NotebookLM Exports/My Research')")
    parser.add_argument("--folder-id", help="Direct Drive folder ID (overrides --folder)")
    parser.add_argument("--share", help="Email to share the file with")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    creds = get_credentials()

    try:
        from googleapiclient.discovery import build
    except ImportError:
        print("Error: google-api-python-client not installed.", file=sys.stderr)
        print("Run: pip3 install google-api-python-client", file=sys.stderr)
        sys.exit(1)

    service = build("drive", "v3", credentials=creds)

    # Determine target folder
    if args.folder_id:
        folder_id = args.folder_id
    elif args.folder != "NotebookLM Exports":
        # User specified a custom folder path — create subfolders inside the default folder
        folder_id = get_or_create_folder(service, args.folder, parent_id=DEFAULT_FOLDER_ID)
    else:
        # No custom folder — upload directly to the default Drive folder
        folder_id = DEFAULT_FOLDER_ID

    # Upload
    result = upload_file(service, args.file, folder_id)

    # Share if requested
    if args.share:
        share_file(service, result["id"], args.share)

    # Output JSON for parsing
    output = {
        "id": result["id"],
        "name": result["name"],
        "link": result.get("webViewLink", ""),
        "folder": args.folder,
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
