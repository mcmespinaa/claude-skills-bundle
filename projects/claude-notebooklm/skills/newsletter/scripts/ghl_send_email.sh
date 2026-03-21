#!/usr/bin/env bash
# ghl_send_email.sh — Send a single email to a GHL contact via the Conversations API.
# Usage:
#   ./ghl_send_email.sh \
#     --contact-id "abc123" \
#     --subject "Weekly Newsletter" \
#     --html "<html>...</html>" \
#     --from "ces@example.com" \
#     --location ces
#
#   ./ghl_send_email.sh \
#     --contact-id "abc123" \
#     --subject "Weekly Newsletter" \
#     --html-file "/path/to/email.html" \
#     --from "ces@example.com" \
#     --location ces
#
# Output: JSON response with conversation/message details to stdout.
#         Progress/errors go to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"

API_BASE="https://services.leadconnectorhq.com"

CONTACT_ID=""
SUBJECT=""
HTML=""
HTML_FILE=""
EMAIL_FROM=""

while [[ ${#SCRIPT_ARGS[@]} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --contact-id) CONTACT_ID="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --subject)    SUBJECT="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --html)       HTML="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --html-file)  HTML_FILE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --from)       EMAIL_FROM="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    *)            echo "Unknown arg: ${SCRIPT_ARGS[0]}" >&2; exit 1 ;;
  esac
done

# Validate required fields
if [[ -z "$CONTACT_ID" ]]; then
  echo "Error: --contact-id is required" >&2
  exit 1
fi

if [[ -z "$SUBJECT" ]]; then
  echo "Error: --subject is required" >&2
  exit 1
fi

if [[ -z "$HTML" && -z "$HTML_FILE" ]]; then
  echo "Error: --html or --html-file is required" >&2
  exit 1
fi

if [[ -z "$EMAIL_FROM" ]]; then
  echo "Error: --from is required" >&2
  exit 1
fi

# Read HTML from file if --html-file was provided
if [[ -n "$HTML_FILE" ]]; then
  if [[ ! -f "$HTML_FILE" ]]; then
    echo "Error: HTML file not found: $HTML_FILE" >&2
    exit 1
  fi
  HTML=$(cat "$HTML_FILE")
fi

# Build JSON payload using jq for safe escaping
PAYLOAD=$(jq -n \
  --arg type "Email" \
  --arg contactId "$CONTACT_ID" \
  --arg subject "$SUBJECT" \
  --arg html "$HTML" \
  --arg emailFrom "$EMAIL_FROM" \
  '{type: $type, contactId: $contactId, subject: $subject, html: $html, emailFrom: $emailFrom}')

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X POST "${API_BASE}/conversations/messages" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')

if [[ "$HTTP_STATUS" -ne 200 && "$HTTP_STATUS" -ne 201 ]]; then
  echo "Error: API returned HTTP $HTTP_STATUS" >&2
  echo "$BODY" >&2
  exit 1
fi

echo "$BODY"
