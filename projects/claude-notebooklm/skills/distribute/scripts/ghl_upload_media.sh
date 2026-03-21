#!/usr/bin/env bash
# ghl_upload_media.sh — Upload a file or hosted URL to GHL Media Storage
# Usage:
#   ./ghl_upload_media.sh --file /path/to/image.png [--name "my-image"]
#   ./ghl_upload_media.sh --url https://example.com/image.png [--name "my-image"]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"

API_BASE="https://services.leadconnectorhq.com"

FILE_PATH=""
FILE_URL=""
NAME="media-$(date +%Y%m%d-%H%M%S)"
NO_RESIZE=false

while [[ ${#SCRIPT_ARGS[@]} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --file)      FILE_PATH="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --url)       FILE_URL="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --name)      NAME="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --no-resize) NO_RESIZE=true; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:1}") ;;
    *)           echo "Unknown arg: ${SCRIPT_ARGS[0]}"; exit 1 ;;
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
  # Auto-resize to 4:5 (1080x1350) unless --no-resize
  UPLOAD_PATH="$FILE_PATH"
  if [[ "$NO_RESIZE" == false ]] && python3 -c "from PIL import Image" 2>/dev/null; then
    RESIZED_TMP=$(mktemp /tmp/resized_XXXXXX.png)
    python3 "$SCRIPT_DIR/resize_to_4x5.py" "$FILE_PATH" "$RESIZED_TMP" >&2
    UPLOAD_PATH="$RESIZED_TMP"
  fi
  echo "Uploading local file: $FILE_PATH"
  curl -s -X POST "$API_BASE/medias/upload-file" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION" \
    -F "file=@$UPLOAD_PATH" \
    -F "name=$NAME"
  # Clean up temp file if we resized
  [[ "$UPLOAD_PATH" != "$FILE_PATH" ]] && rm -f "$UPLOAD_PATH"
else
  echo "Error: Provide --file or --url" >&2
  exit 1
fi
