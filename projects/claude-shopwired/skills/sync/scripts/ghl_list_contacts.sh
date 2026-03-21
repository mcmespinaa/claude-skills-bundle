#!/usr/bin/env bash
# ghl_list_contacts.sh — List contacts from GHL
# Usage: ./ghl_list_contacts.sh [--location ces] [--limit 20] [--query "email"]

set -euo pipefail

: "${GHL_API_KEY:?Error: GHL_API_KEY is not set}"
: "${GHL_VERSION:=2021-07-28}"

API_BASE="https://services.leadconnectorhq.com"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOCATION_ARGS=()
LIMIT=20
QUERY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --location) LOCATION_ARGS=(--location "$2"); shift 2 ;;
    --limit)    LIMIT="$2"; shift 2 ;;
    --query)    QUERY="$2"; shift 2 ;;
    *)          shift ;;
  esac
done

LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh" "${LOCATION_ARGS[@]}")

URL="${API_BASE}/contacts/?locationId=${LOCATION_ID}&limit=${LIMIT}"
if [[ -n "$QUERY" ]]; then
  URL="${URL}&query=${QUERY}"
fi

curl -s -X GET "$URL" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Accept: application/json" | jq .
