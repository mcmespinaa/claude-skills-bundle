#!/usr/bin/env bash
set -euo pipefail

# Generate a branded header image via Gemini API and upload to GHL media library.
# Three-step process:
#   1. Call Gemini API to generate the image
#   2. Decode base64 response and save locally
#   3. Upload to GHL media library and return hosted URL
#
# Usage:
#   bash generate_header_image.sh \
#     --prompt "A human and AI robot collaborating at a shared workspace" \
#     --output "newsletter-drafts/banner-topic.jpg" \
#     --location "ces"
#
# Output: prints the GHL-hosted image URL to stdout

: "${GEMINI_API_KEY:?Missing GEMINI_API_KEY}"
: "${GHL_API_KEY:?Missing GHL_API_KEY}"
: "${GHL_VERSION:?Missing GHL_VERSION}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCATION_FLAG=""
PROMPT=""
OUTPUT_FILE=""
MODEL="gemini-3.1-flash-image-preview"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt) PROMPT="$2"; shift 2 ;;
    --output) OUTPUT_FILE="$2"; shift 2 ;;
    --location) LOCATION_FLAG="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# Resolve location (needed for GHL media upload)
if [[ -n "$LOCATION_FLAG" ]]; then
  GHL_LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh" --location "$LOCATION_FLAG")
else
  GHL_LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh")
fi

if [[ -z "$PROMPT" ]]; then
  echo "Error: --prompt is required" >&2
  exit 1
fi

if [[ -z "$OUTPUT_FILE" ]]; then
  echo "Error: --output is required" >&2
  exit 1
fi

# --- Step 1: Call Gemini API ---
# Prepend brand style instructions to the user's content prompt
FULL_PROMPT="Generate an email banner image (600x300 pixels, 2:1 aspect ratio). Style: minimalist editorial illustration. Background: ivory/off-white (#f7f4ef). Color palette: warm charcoal (#3a352e) and soft gold (#b8a06a) accents. Style reference: flat geometric illustration, clean lines, no text or words in the image, no photorealism. Subject: ${PROMPT}"

echo "Generating header image via Gemini ($MODEL)..." >&2

GEMINI_BODY=$(jq -n \
  --arg prompt "$FULL_PROMPT" \
  '{
    contents: [{
      parts: [{ text: $prompt }]
    }],
    generationConfig: {
      responseModalities: ["TEXT", "IMAGE"]
    }
  }')

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X POST "https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$GEMINI_BODY")

HTTP_STATUS=$(echo "$RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_STATUS" != "200" ]]; then
  echo "Error: Gemini API returned HTTP $HTTP_STATUS" >&2
  echo "$BODY" | jq -r '.error.message // .' >&2
  exit 1
fi

# --- Step 2: Extract and decode the base64 image ---
IMAGE_DATA=$(echo "$BODY" | jq -r '
  .candidates[0].content.parts[]
  | select(.inlineData != null)
  | .inlineData.data
' | head -1)

if [[ -z "$IMAGE_DATA" ]]; then
  echo "Error: No image data in Gemini response" >&2
  echo "Response keys:" >&2
  echo "$BODY" | jq '[.candidates[0].content.parts[] | keys]' >&2
  exit 1
fi

MIME_TYPE=$(echo "$BODY" | jq -r '
  .candidates[0].content.parts[]
  | select(.inlineData != null)
  | .inlineData.mimeType
' | head -1)

echo "Image generated ($MIME_TYPE)" >&2

# Decode and save locally
echo "$IMAGE_DATA" | base64 --decode > "$OUTPUT_FILE"

if [[ ! -s "$OUTPUT_FILE" ]]; then
  echo "Error: Failed to save image to $OUTPUT_FILE" >&2
  exit 1
fi

FILE_SIZE=$(wc -c < "$OUTPUT_FILE" | tr -d ' ')
echo "Saved locally: $OUTPUT_FILE ($FILE_SIZE bytes)" >&2

# --- Step 3: Upload to GHL media library ---
echo "Uploading to GHL media library..." >&2

FILE_NAME=$(basename "$OUTPUT_FILE")

UPLOAD_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X POST "https://services.leadconnectorhq.com/medias/upload-file" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -F "file=@${OUTPUT_FILE};type=${MIME_TYPE}" \
  -F "name=${FILE_NAME}")

UPLOAD_STATUS=$(echo "$UPLOAD_RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')
UPLOAD_BODY=$(echo "$UPLOAD_RESPONSE" | sed '$d')

if [[ "$UPLOAD_STATUS" != "200" && "$UPLOAD_STATUS" != "201" ]]; then
  echo "Error: GHL media upload failed. HTTP $UPLOAD_STATUS" >&2
  echo "$UPLOAD_BODY" >&2
  exit 1
fi

# Extract the hosted URL from the response (check multiple possible paths)
IMAGE_URL=$(echo "$UPLOAD_BODY" | jq -r '.url // .fileUrl // .data.url // .data.fileUrl // empty')

if [[ -z "$IMAGE_URL" ]]; then
  echo "Error: Could not extract image URL from upload response" >&2
  echo "$UPLOAD_BODY" >&2
  exit 1
fi

echo "Uploaded to GHL: $IMAGE_URL" >&2

# Output the URL to stdout (for piping to the next step)
echo "$IMAGE_URL"
