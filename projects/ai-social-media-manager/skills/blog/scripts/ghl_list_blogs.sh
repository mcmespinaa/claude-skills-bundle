#!/usr/bin/env bash
# ghl_list_blogs.sh — List all blog sites for a location

set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  echo "Usage: bash ghl_list_blogs.sh"
  echo ""
  echo "List all blog sites for the current GHL location."
  echo "Output: JSON array of blog sites (id, name, url)."
  echo ""
  echo "Environment variables (required):"
  echo "  Requires: GHL API key, location ID, and version env vars."
  echo "  See .claude/settings.local.json for configuration."
  exit 0
fi

: "${GHL_API_KEY:?Error: GHL_API_KEY is not set}"
: "${GHL_LOCATION_ID:?Error: GHL_LOCATION_ID is not set}"
: "${GHL_VERSION:=2021-07-28}"

API_BASE="https://services.leadconnectorhq.com"

echo "Fetching blogs for location: $GHL_LOCATION_ID" >&2

MAX_RETRIES=2
ATTEMPT=0

while true; do
  RESPONSE=$(curl -s --max-time 30 -w "\nHTTP_STATUS:%{http_code}" -X GET \
    "${API_BASE}/blogs/site/all?locationId=${GHL_LOCATION_ID}" \
    -H "Authorization: Bearer ${GHL_API_KEY}" \
    -H "Version: ${GHL_VERSION}")

  HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
  BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')

  if [[ "$HTTP_STATUS" == "429" ]] && [[ $ATTEMPT -lt $MAX_RETRIES ]]; then
    ATTEMPT=$((ATTEMPT + 1))
    WAIT=$((5 + 2 ** ATTEMPT))
    echo "Rate limited (429). Waiting ${WAIT}s (retry $ATTEMPT/$MAX_RETRIES)..." >&2
    sleep "$WAIT"
    continue
  fi
  break
done

case "$HTTP_STATUS" in
  200)
    echo "$BODY" | jq .
    ;;
  401)
    echo "Error: Authentication failed (401). Update GHL_API_KEY." >&2
    echo "$BODY" >&2
    exit 1
    ;;
  *)
    echo "Error: API returned HTTP $HTTP_STATUS" >&2
    echo "$BODY" >&2
    exit 1
    ;;
esac
