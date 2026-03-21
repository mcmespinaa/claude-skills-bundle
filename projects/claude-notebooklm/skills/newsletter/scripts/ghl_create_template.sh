#!/usr/bin/env bash
# ghl_create_template.sh — Upload HTML as a GHL Email Builder template.
#
# Two-step process:
#   1. POST /emails/builder → create template shell, get templateId
#   2. POST /emails/builder/data → upload HTML content
#
# Usage:
#   ./ghl_create_template.sh \
#     --name "March Newsletter" \
#     --html-file "/tmp/newsletter_email.html" \
#     --location ces
#
# Output: JSON with templateId to stdout. Progress/errors to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"

API_BASE="https://services.leadconnectorhq.com"

TEMPLATE_NAME=""
HTML_FILE=""

while [[ ${#SCRIPT_ARGS[@]} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --name)      TEMPLATE_NAME="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --html-file) HTML_FILE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    *)           echo "Unknown arg: ${SCRIPT_ARGS[0]}" >&2; exit 1 ;;
  esac
done

# Validate required fields
if [[ -z "$TEMPLATE_NAME" ]]; then
  echo "Error: --name is required" >&2
  exit 1
fi

if [[ -z "$HTML_FILE" ]]; then
  echo "Error: --html-file is required" >&2
  exit 1
fi

if [[ ! -f "$HTML_FILE" ]]; then
  echo "Error: HTML file not found: $HTML_FILE" >&2
  exit 1
fi

LOCATION_ID="$GHL_LOCATION_ID"

echo "Creating template '$TEMPLATE_NAME' in location $LOCATION_ID..." >&2

# Step 1: Create template shell
STEP1_PAYLOAD=$(jq -n \
  --arg locationId "$LOCATION_ID" \
  --arg name "$TEMPLATE_NAME" \
  --arg type "html" \
  '{locationId: $locationId, name: $name, type: $type}')

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X POST "${API_BASE}/emails/builder" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Content-Type: application/json" \
  -d "$STEP1_PAYLOAD")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')

if [[ "$HTTP_STATUS" -ne 200 && "$HTTP_STATUS" -ne 201 ]]; then
  echo "Error: Create template returned HTTP $HTTP_STATUS" >&2
  echo "$BODY" >&2
  exit 1
fi

TEMPLATE_ID=$(echo "$BODY" | jq -r '.redirect // .id // empty')

if [[ -z "$TEMPLATE_ID" ]]; then
  echo "Error: Could not extract templateId from response" >&2
  echo "$BODY" >&2
  exit 1
fi

echo "Template shell created: $TEMPLATE_ID" >&2

# Step 2: Upload HTML content
STEP2_PAYLOAD=$(python3 -c "
import json, sys
html = open('$HTML_FILE').read()
data = {
    'locationId': '$LOCATION_ID',
    'templateId': '$TEMPLATE_ID',
    'updatedBy': '$LOCATION_ID',
    'editorType': 'html',
    'dnd': {'elements': [], 'attrs': {}, 'templateSettings': {}},
    'html': html
}
print(json.dumps(data))
")

RESPONSE2=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X POST "${API_BASE}/emails/builder/data" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Content-Type: application/json" \
  -d "$STEP2_PAYLOAD")

HTTP_STATUS2=$(echo "$RESPONSE2" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY2=$(echo "$RESPONSE2" | sed '/HTTP_STATUS:/d')

if [[ "$HTTP_STATUS2" -ne 200 && "$HTTP_STATUS2" -ne 201 ]]; then
  echo "Error: Upload HTML returned HTTP $HTTP_STATUS2" >&2
  echo "$BODY2" >&2
  exit 1
fi

echo "HTML content uploaded successfully" >&2

# Output result
jq -n \
  --arg templateId "$TEMPLATE_ID" \
  --arg name "$TEMPLATE_NAME" \
  --arg locationId "$LOCATION_ID" \
  '{templateId: $templateId, name: $name, locationId: $locationId}'
