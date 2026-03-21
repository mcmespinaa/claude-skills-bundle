#!/usr/bin/env bash
# ghl_upload_carousel.sh — Batch upload multiple files/URLs to GHL Media Storage
# Usage:
#   ./ghl_upload_carousel.sh --url "https://img1.png" --url "https://img2.png" --platform ig
#   ./ghl_upload_carousel.sh --file /path/slide1.png --file /path/slide2.png --platform fb
#   ./ghl_upload_carousel.sh --file /path/slide1.png --no-resize --platform ig
# Local files are auto-resized to 4:5 (1080x1350) with ivory padding unless --no-resize is passed.
# Output: comma-separated list of returned media URLs

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"

API_BASE="https://services.leadconnectorhq.com"

URLS=()
FILES=()
PLATFORM=""
NO_RESIZE=false

while [[ ${#SCRIPT_ARGS[@]} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --url)       URLS+=("${SCRIPT_ARGS[1]}"); SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --file)      FILES+=("${SCRIPT_ARGS[1]}"); SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --platform)  PLATFORM="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --no-resize) NO_RESIZE=true; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:1}") ;;
    *)           echo "Unknown arg: ${SCRIPT_ARGS[0]}"; exit 1 ;;
  esac
done

TOTAL=$(( ${#URLS[@]} + ${#FILES[@]} ))

if [[ "$TOTAL" -eq 0 ]]; then
  echo "Error: Provide at least one --url or --file" >&2
  exit 1
fi

# Validate slide count against platform max (bash 3.2 compatible — no declare -A)
if [[ -n "$PLATFORM" ]]; then
  PLATFORM_LOWER=$(echo "$PLATFORM" | tr '[:upper:]' '[:lower:]')
  MAX=0
  case "$PLATFORM_LOWER" in
    ig|instagram)  MAX=10 ;;
    fb|facebook)   MAX=10 ;;
    li|linkedin)
      echo "Warning: LinkedIn carousels use PDF uploads, not multiple images." >&2
      echo "Upload a single PDF via ghl_upload_media.sh instead." >&2
      exit 1 ;;
    tiktok)        MAX=35 ;;
    x|twitter)     MAX=4 ;;
    gmb)           MAX=1 ;;
    threads)       MAX=1 ;;
  esac
  if [[ "$MAX" -gt 0 && "$TOTAL" -gt "$MAX" ]]; then
    echo "Error: $PLATFORM supports max $MAX slides, got $TOTAL" >&2
    exit 1
  fi
fi

echo "Uploading $TOTAL slides..." >&2

# Check if Pillow is available for auto-resize
HAS_PILLOW=false
if python3 -c "from PIL import Image" 2>/dev/null; then
  HAS_PILLOW=true
fi

TEMP_FILES=()
RESULT_URLS=()

# Upload hosted URLs
for url in ${URLS[@]+"${URLS[@]}"}; do
  NAME="carousel-slide-$(date +%Y%m%d-%H%M%S)-${#RESULT_URLS[@]}"
  RESPONSE=$(curl -s -X POST "$API_BASE/medias/upload-file" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION" \
    -F "hosted=true" \
    -F "fileUrl=$url" \
    -F "name=$NAME")

  MEDIA_URL=$(echo "$RESPONSE" | jq -r '.url // empty')
  if [[ -z "$MEDIA_URL" ]]; then
    echo "Error uploading $url: $RESPONSE" >&2
    exit 1
  fi
  RESULT_URLS+=("$MEDIA_URL")
  echo "  Uploaded slide $((${#RESULT_URLS[@]}))/$TOTAL" >&2
done

# Upload local files
for filepath in ${FILES[@]+"${FILES[@]}"}; do
  if [[ ! -f "$filepath" ]]; then
    echo "Error: File not found: $filepath" >&2
    exit 1
  fi
  FILE_SIZE=$(wc -c < "$filepath")
  MAX_SIZE=$((25 * 1024 * 1024))
  if [[ "$FILE_SIZE" -gt "$MAX_SIZE" ]]; then
    echo "Error: $filepath exceeds 25 MB limit ($FILE_SIZE bytes)" >&2
    exit 1
  fi

  # Auto-resize to 4:5 (1080x1350) unless --no-resize
  UPLOAD_PATH="$filepath"
  if [[ "$NO_RESIZE" == false ]] && [[ "$HAS_PILLOW" == true ]]; then
    RESIZED_TMP="/tmp/resized_$(date +%s%N)_${#RESULT_URLS[@]}.png"
    python3 "$SCRIPT_DIR/resize_to_4x5.py" "$filepath" "$RESIZED_TMP" >&2
    UPLOAD_PATH="$RESIZED_TMP"
    TEMP_FILES+=("$RESIZED_TMP")
  fi

  NAME="carousel-slide-$(date +%Y%m%d-%H%M%S)-${#RESULT_URLS[@]}"
  RESPONSE=$(curl -s -X POST "$API_BASE/medias/upload-file" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION" \
    -F "file=@$UPLOAD_PATH" \
    -F "name=$NAME")

  MEDIA_URL=$(echo "$RESPONSE" | jq -r '.url // empty')
  if [[ -z "$MEDIA_URL" ]]; then
    echo "Error uploading $filepath: $RESPONSE" >&2
    exit 1
  fi
  RESULT_URLS+=("$MEDIA_URL")
  echo "  Uploaded slide $((${#RESULT_URLS[@]}))/$TOTAL" >&2
done

# Clean up temp resized files
for tmp in ${TEMP_FILES[@]+"${TEMP_FILES[@]}"}; do
  rm -f "$tmp"
done

# Output comma-separated URLs (stdout, not stderr)
IFS=','
echo "${RESULT_URLS[*]}"
