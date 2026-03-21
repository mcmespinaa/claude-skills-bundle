#!/usr/bin/env bash
set -euo pipefail

# List email templates from GHL.
# GET /emails/builder?locationId=...&limit=...&offset=...

: "${GHL_API_KEY:?Missing GHL_API_KEY}"
: "${GHL_VERSION:?Missing GHL_VERSION}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCATION_FLAG=""
LIMIT="20"
OFFSET="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit) LIMIT="$2"; shift 2 ;;
    --offset) OFFSET="$2"; shift 2 ;;
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

echo "Fetching templates (limit=$LIMIT, offset=$OFFSET)" >&2

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X GET "https://services.leadconnectorhq.com/emails/builder?locationId=$GHL_LOCATION_ID&limit=$LIMIT&offset=$OFFSET" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION")

HTTP_STATUS=$(echo "$RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_STATUS" != "200" ]]; then
  echo "Error fetching templates. HTTP $HTTP_STATUS" >&2
  echo "$BODY" >&2
  exit 1
fi

echo "$BODY" | jq '.'
