#!/usr/bin/env bash
# ghl_search_contacts.sh — Search GHL contacts by tag, list name, or query string.
# Usage:
#   ./ghl_search_contacts.sh --tag "newsletter" --location ces
#   ./ghl_search_contacts.sh --query "some search" --location ces
#   ./ghl_search_contacts.sh --limit 10 --location ces
# Output: JSON array of {id, email, firstName, lastName} to stdout.
#         Progress/errors go to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"

API_BASE="https://services.leadconnectorhq.com"

TAG=""
QUERY=""
LIMIT=0

while [[ ${#SCRIPT_ARGS[@]} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --tag)   TAG="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --query) QUERY="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --limit) LIMIT="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    *)       echo "Unknown arg: ${SCRIPT_ARGS[0]}" >&2; exit 1 ;;
  esac
done

# Build query params
PARAMS="locationId=$GHL_LOCATION_ID"
if [[ -n "$TAG" ]]; then
  PARAMS="${PARAMS}&query=tag:${TAG}"
elif [[ -n "$QUERY" ]]; then
  PARAMS="${PARAMS}&query=${QUERY}"
fi

echo "Searching contacts (location: $GHL_LOCATION_ID)..." >&2

ALL_CONTACTS="[]"
PAGE=1
FETCHED=0

while true; do
  RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    "${API_BASE}/contacts/?${PARAMS}&limit=100&page=${PAGE}" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION")

  HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
  BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')

  if [[ "$HTTP_STATUS" -ne 200 ]]; then
    echo "Error: API returned HTTP $HTTP_STATUS" >&2
    echo "$BODY" >&2
    exit 1
  fi

  # Extract contacts from this page
  PAGE_CONTACTS=$(echo "$BODY" | jq '[.contacts[]? | {id: .id, email: .email, firstName: .firstName, lastName: .lastName}]')
  PAGE_COUNT=$(echo "$PAGE_CONTACTS" | jq 'length')

  if [[ "$PAGE_COUNT" -eq 0 ]]; then
    break
  fi

  ALL_CONTACTS=$(echo "$ALL_CONTACTS" "$PAGE_CONTACTS" | jq -s '.[0] + .[1]')
  FETCHED=$(echo "$ALL_CONTACTS" | jq 'length')

  echo "  Fetched $FETCHED contacts so far..." >&2

  # Check if we've hit the user-specified limit
  if [[ "$LIMIT" -gt 0 && "$FETCHED" -ge "$LIMIT" ]]; then
    ALL_CONTACTS=$(echo "$ALL_CONTACTS" | jq --argjson limit "$LIMIT" '.[:$limit]')
    break
  fi

  # Check if there are more pages
  HAS_MORE=$(echo "$BODY" | jq -r '.meta.nextPageUrl // empty')
  if [[ -z "$HAS_MORE" ]]; then
    break
  fi

  PAGE=$((PAGE + 1))
done

TOTAL=$(echo "$ALL_CONTACTS" | jq 'length')

# Filter out contacts without email
ALL_CONTACTS=$(echo "$ALL_CONTACTS" | jq '[.[] | select(.email != null and .email != "")]')
EMAIL_COUNT=$(echo "$ALL_CONTACTS" | jq 'length')

echo "Found $TOTAL contacts ($EMAIL_COUNT with email addresses)" >&2

echo "$ALL_CONTACTS"
