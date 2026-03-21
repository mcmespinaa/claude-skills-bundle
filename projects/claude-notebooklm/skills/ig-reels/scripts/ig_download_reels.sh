#!/usr/bin/env bash
set -euo pipefail

# ig_download_reels.sh — Download Instagram Reels and extract audio for transcription
#
# Usage:
#   ig_download_reels.sh <url1> [url2 ...] [--cookies <path>] [--output-dir <dir>] [--audio-only]
#
# Defaults:
#   cookies:    ~/.notebooklm/instagram_cookies.txt
#   output-dir: ~/.notebooklm/ig-reels/

COOKIES_FILE="${HOME}/.notebooklm/instagram_cookies.txt"
OUTPUT_DIR="${HOME}/.notebooklm/ig-reels"
AUDIO_ONLY=false
URLS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cookies)   COOKIES_FILE="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --audio-only) AUDIO_ONLY=true; shift ;;
    -*)          echo "Unknown flag: $1" >&2; exit 1 ;;
    *)           URLS+=("$1"); shift ;;
  esac
done

if [[ ${#URLS[@]} -eq 0 ]]; then
  echo "Usage: ig_download_reels.sh <url1> [url2 ...] [--cookies <path>] [--output-dir <dir>] [--audio-only]" >&2
  exit 1
fi

if [[ ! -f "$COOKIES_FILE" ]]; then
  echo "ERROR: Cookies file not found at $COOKIES_FILE" >&2
  echo "" >&2
  echo "To export cookies:" >&2
  echo "  1. Install 'Get cookies.txt LOCALLY' Chrome extension" >&2
  echo "  2. Go to instagram.com (make sure you're logged in)" >&2
  echo "  3. Click the extension → Export → Save as $COOKIES_FILE" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

DOWNLOADED=()
FAILED=()

for url in "${URLS[@]}"; do
  # Extract reel ID from URL
  reel_id=$(echo "$url" | grep -oE '(reel|p)/[A-Za-z0-9_-]+' | cut -d'/' -f2)
  if [[ -z "$reel_id" ]]; then
    echo "WARN: Could not extract reel ID from $url — skipping" >&2
    FAILED+=("$url")
    continue
  fi

  echo "Downloading reel: $reel_id ..."

  if $AUDIO_ONLY; then
    # Download audio only (mp3)
    if yt-dlp \
      --cookies "$COOKIES_FILE" \
      --extract-audio \
      --audio-format mp3 \
      --audio-quality 0 \
      --output "${OUTPUT_DIR}/${reel_id}.%(ext)s" \
      --write-info-json \
      --no-playlist \
      --quiet --no-warnings \
      "$url" 2>&1; then
      DOWNLOADED+=("${reel_id}")
      echo "  -> ${OUTPUT_DIR}/${reel_id}.mp3"
    else
      echo "  -> FAILED" >&2
      FAILED+=("$url")
    fi
  else
    # Download video (for archive) + extract audio
    if yt-dlp \
      --cookies "$COOKIES_FILE" \
      --output "${OUTPUT_DIR}/${reel_id}.%(ext)s" \
      --write-info-json \
      --no-playlist \
      --quiet --no-warnings \
      "$url" 2>&1; then
      # Also extract audio for transcription
      video_file=$(ls "${OUTPUT_DIR}/${reel_id}".{mp4,webm,mkv} 2>/dev/null | head -1)
      if [[ -n "$video_file" ]]; then
        ffmpeg -i "$video_file" -vn -acodec libmp3lame -q:a 2 "${OUTPUT_DIR}/${reel_id}.mp3" -y -loglevel error 2>&1
      fi
      DOWNLOADED+=("${reel_id}")
      echo "  -> ${OUTPUT_DIR}/${reel_id}.mp3"
    else
      echo "  -> FAILED" >&2
      FAILED+=("$url")
    fi
  fi

  # Rate limit: 3 second delay between downloads
  sleep 3
done

echo ""
echo "=== Summary ==="
echo "Downloaded: ${#DOWNLOADED[@]}"
echo "Failed:     ${#FAILED[@]}"

if [[ ${#DOWNLOADED[@]} -gt 0 ]]; then
  echo ""
  echo "Audio files ready for transcription:"
  for id in "${DOWNLOADED[@]}"; do
    echo "  ${OUTPUT_DIR}/${id}.mp3"
  done
fi

if [[ ${#FAILED[@]} -gt 0 ]]; then
  echo ""
  echo "Failed URLs:"
  for url in "${FAILED[@]}"; do
    echo "  $url"
  done
fi
