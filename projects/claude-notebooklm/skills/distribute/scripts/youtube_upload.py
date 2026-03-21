#!/usr/bin/env python3
"""youtube_upload.py — Upload a video to YouTube with metadata and optional thumbnail.

Usage:
  python3 youtube_upload.py --file ./video.mp4 --title "My Video"
  python3 youtube_upload.py --file ./video.mp4 --title "My Video" --description "..." --tags "ai,gemini"
  python3 youtube_upload.py --file ./video.mp4 --title "My Video" --privacy unlisted --thumbnail thumb.png
  python3 youtube_upload.py --file ./video.mp4 --title "My Video" --privacy private --publish-at "2026-04-01T12:00:00Z"

Output (stdout): JSON with video id, title, link, privacy status.
Progress and errors go to stderr.
"""

import argparse
import json
import os
import random
import sys
import time

CREDENTIALS_PATH = os.path.expanduser("~/.notebooklm/youtube_credentials.json")
TOKEN_PATH = os.path.expanduser("~/.notebooklm/youtube_token.json")
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

MAX_RETRIES = 10
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


def get_credentials():
    """Get or refresh OAuth credentials for YouTube."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Error: Google API libraries not installed.", file=sys.stderr)
        print(
            "Run: pip3 install google-api-python-client google-auth google-auth-oauthlib",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.path.exists(CREDENTIALS_PATH):
        print(f"Error: No credentials file at {CREDENTIALS_PATH}", file=sys.stderr)
        print(
            "To set up YouTube uploads:\n"
            "  1. Go to https://console.cloud.google.com/\n"
            "  2. Enable 'YouTube Data API v3'\n"
            "  3. Create OAuth 2.0 credentials (Desktop app)\n"
            f"  4. Download and save to {CREDENTIALS_PATH}\n"
            "  5. Add your Google account as a test user",
            file=sys.stderr,
        )
        sys.exit(1)

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return creds


def upload_video(youtube, file_path, title, description, tags, category_id, privacy, publish_at):
    """Upload a video with resumable upload and exponential backoff."""
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,
        },
    }

    if publish_at:
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = publish_at

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print(f"Uploading {os.path.basename(file_path)}...", file=sys.stderr)

    response = None
    retry = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"  Upload {pct}% complete.", file=sys.stderr)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                retry += 1
                if retry > MAX_RETRIES:
                    print(f"Error: Max retries exceeded. Last error: {e}", file=sys.stderr)
                    sys.exit(1)
                wait = random.uniform(0, 2**retry)
                print(
                    f"  Retriable error {e.resp.status}. Waiting {wait:.1f}s (retry {retry}/{MAX_RETRIES})...",
                    file=sys.stderr,
                )
                time.sleep(wait)
            else:
                print(f"Error uploading video: {e}", file=sys.stderr)
                sys.exit(1)

    video_id = response["id"]
    print(f"Upload complete! Video ID: {video_id}", file=sys.stderr)
    return response


def set_thumbnail(youtube, video_id, thumbnail_path):
    """Upload a custom thumbnail for a video."""
    from googleapiclient.http import MediaFileUpload

    if not os.path.exists(thumbnail_path):
        print(f"Warning: Thumbnail not found: {thumbnail_path}", file=sys.stderr)
        return

    file_size = os.path.getsize(thumbnail_path)
    if file_size > 2 * 1024 * 1024:
        print(f"Warning: Thumbnail exceeds 2 MB limit ({file_size} bytes), skipping.", file=sys.stderr)
        return

    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_path),
    ).execute()
    print(f"  Thumbnail set for video {video_id}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Upload a video to YouTube")
    parser.add_argument("--file", required=True, help="Path to the video file")
    parser.add_argument("--title", required=True, help="Video title")
    parser.add_argument("--description", default="", help="Video description")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument(
        "--category", default="22", help="YouTube category ID (default: 22 = People & Blogs)"
    )
    parser.add_argument(
        "--privacy",
        default="private",
        choices=["public", "unlisted", "private"],
        help="Privacy status (default: private)",
    )
    parser.add_argument(
        "--publish-at", default=None, help="Scheduled publish time (ISO 8601). Requires --privacy private."
    )
    parser.add_argument("--thumbnail", default=None, help="Path to custom thumbnail image (JPEG/PNG, max 2 MB)")
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

    youtube = build("youtube", "v3", credentials=creds)

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    response = upload_video(
        youtube,
        file_path=args.file,
        title=args.title,
        description=args.description,
        tags=tags,
        category_id=args.category,
        privacy=args.privacy,
        publish_at=args.publish_at,
    )

    video_id = response["id"]

    if args.thumbnail:
        set_thumbnail(youtube, video_id, args.thumbnail)

    output = {
        "id": video_id,
        "title": args.title,
        "link": f"https://www.youtube.com/watch?v={video_id}",
        "privacy": args.privacy if not args.publish_at else "private (scheduled)",
        "publish_at": args.publish_at,
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
