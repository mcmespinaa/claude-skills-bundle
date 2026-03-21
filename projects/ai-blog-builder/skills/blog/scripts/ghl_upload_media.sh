#!/usr/bin/env bash
# ghl_upload_media.sh — Upload a file or hosted URL to GHL Media Storage
# Usage:
#   ./ghl_upload_media.sh --file /path/to/image.png [--name "my-image"]
#   ./ghl_upload_media.sh --url https://example.com/image.png [--name "my-image"]

set -euo pipefail

API_BASE="https://services.leadconnectorhq.com"
: "${GHL_API_KEY:?Error: GHL_API_KEY is not set}"
: "${GHL_VERSION:=2021-07-28}"

FILE_PATH=""
FILE_URL=""
NAME="media-$(date +%Y%m%d-%H%M%S)"
LOCATION_FLAG=""
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)  FILE_PATH="$2"; shift 2 ;;
    --url)   FILE_URL="$2"; shift 2 ;;
    --name)  NAME="$2"; shift 2 ;;
    --location) LOCATION_FLAG="$2"; shift 2 ;;
    *)       echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -n "$FILE_URL" ]]; then
  echo "Uploading hosted URL: $FILE_URL"
  curl -s -X POST "$API_BASE/medias/upload-file" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION" \
    -F "hosted=true" \
    -F "fileUrl=$FILE_URL" \
    -F "name=$NAME"
elif [[ -n "$FILE_PATH" ]]; then
  if [[ ! -f "$FILE_PATH" ]]; then
    echo "Error: File not found: $FILE_PATH" >&2
    exit 1
  fi
  FILE_SIZE=$(wc -c < "$FILE_PATH")
  MAX_SIZE=$((25 * 1024 * 1024))
  if [[ "$FILE_SIZE" -gt "$MAX_SIZE" ]]; then
    echo "Error: File exceeds 25 MB limit ($FILE_SIZE bytes)" >&2
    exit 1
  fi
  echo "Uploading local file: $FILE_PATH"
  curl -s -X POST "$API_BASE/medias/upload-file" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION" \
    -F "file=@$FILE_PATH" \
    -F "name=$NAME"
else
  echo "Error: Provide --file or --url" >&2
  exit 1
fi
