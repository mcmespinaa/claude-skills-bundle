#!/usr/bin/env bash
set -euo pipefail

# Update an existing email template in GHL.
# Two-step process:
#   1. POST /emails/builder/data to update HTML content (if --html-file provided)
#   2. PATCH /emails/builder/:templateId to update settings (subject, sender, preview text)

: "${GHL_API_KEY:?Missing GHL_API_KEY}"
: "${GHL_VERSION:?Missing GHL_VERSION}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCATION_FLAG=""
TEMPLATE_ID=""
HTML_FILE=""
SUBJECT=""
FROM_NAME="${GHL_SENDER_NAME:-}"
FROM_EMAIL="${GHL_SENDER_EMAIL:-}"
PREVIEW_TEXT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --template-id) TEMPLATE_ID="$2"; shift 2 ;;
    --html-file) HTML_FILE="$2"; shift 2 ;;
    --subject) SUBJECT="$2"; shift 2 ;;
    --from-name) FROM_NAME="$2"; shift 2 ;;
    --from-email) FROM_EMAIL="$2"; shift 2 ;;
    --preview-text) PREVIEW_TEXT="$2"; shift 2 ;;
    --location) LOCATION_FLAG="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# Resolve location
if [[ -n "$LOCATION_FLAG" ]]; then
  GHL_LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh" --location "$LOCATION_FLAG")
else
  GHL_LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh")
fi

if [[ -z "$TEMPLATE_ID" ]]; then
  echo "Error: --template-id is required" >&2
  exit 1
fi

# Step 1: Update HTML content (if html-file provided)
if [[ -n "$HTML_FILE" ]]; then
  if [[ ! -f "$HTML_FILE" ]]; then
    echo "Error: HTML file not found: $HTML_FILE" >&2
    exit 1
  fi

  HTML_CONTENT=$(cat "$HTML_FILE")

  echo "Updating HTML content for template: $TEMPLATE_ID" >&2

  DATA_BODY=$(jq -n \
    --arg locationId "$GHL_LOCATION_ID" \
    --arg templateId "$TEMPLATE_ID" \
    --arg html "$HTML_CONTENT" \
    '{
      locationId: $locationId,
      templateId: $templateId,
      editorType: "html",
      html: $html,
      updatedBy: $locationId
    }')

  RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X POST "https://services.leadconnectorhq.com/emails/builder/data" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION" \
    -H "Content-Type: application/json" \
    -d "$DATA_BODY")

  HTTP_STATUS=$(echo "$RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')
  BODY=$(echo "$RESPONSE" | sed '$d')

  if [[ "$HTTP_STATUS" != "200" && "$HTTP_STATUS" != "201" ]]; then
    echo "Error updating HTML. HTTP $HTTP_STATUS" >&2
    echo "$BODY" >&2
    exit 1
  fi

  echo "HTML content updated" >&2
fi

# Step 2: Update settings via PATCH (if any settings provided)
# Build patch body dynamically with only non-empty fields
PATCH_BODY=$(jq -n --arg locationId "$GHL_LOCATION_ID" '{locationId: $locationId}')

if [[ -n "$SUBJECT" ]]; then
  PATCH_BODY=$(echo "$PATCH_BODY" | jq --arg v "$SUBJECT" '. + {subject: $v}')
fi
if [[ -n "$FROM_NAME" ]]; then
  PATCH_BODY=$(echo "$PATCH_BODY" | jq --arg v "$FROM_NAME" '. + {fromName: $v}')
fi
if [[ -n "$FROM_EMAIL" ]]; then
  PATCH_BODY=$(echo "$PATCH_BODY" | jq --arg v "$FROM_EMAIL" '. + {fromEmail: $v}')
fi
if [[ -n "$PREVIEW_TEXT" ]]; then
  PATCH_BODY=$(echo "$PATCH_BODY" | jq --arg v "$PREVIEW_TEXT" '. + {previewText: $v}')
fi

# Only PATCH if we have fields to update
FIELD_COUNT=$(echo "$PATCH_BODY" | jq 'length')
if [[ "$FIELD_COUNT" -gt 0 ]]; then
  echo "Updating template settings ($FIELD_COUNT fields)" >&2

  RESPONSE2=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X PATCH "https://services.leadconnectorhq.com/emails/builder/$TEMPLATE_ID" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION" \
    -H "Content-Type: application/json" \
    -d "$PATCH_BODY")

  HTTP_STATUS2=$(echo "$RESPONSE2" | tail -1 | sed 's/HTTP_STATUS://')
  BODY2=$(echo "$RESPONSE2" | sed '$d')

  if [[ "$HTTP_STATUS2" != "200" && "$HTTP_STATUS2" != "201" ]]; then
    echo "Error updating settings. HTTP $HTTP_STATUS2" >&2
    echo "$BODY2" >&2
    exit 1
  fi

  echo "Template settings updated" >&2
else
  echo "No settings to update" >&2
fi

echo "Done. Template ID: $TEMPLATE_ID"
