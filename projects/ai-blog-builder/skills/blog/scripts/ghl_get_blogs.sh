#!/usr/bin/env bash
# ghl_get_blogs.sh — List blogs for a GHL location
# Usage: ./ghl_get_blogs.sh [--location ces] [--limit 20] [--offset 0]

set -euo pipefail

API_BASE="https://services.leadconnectorhq.com"
: "${GHL_API_KEY:?Error: GHL_API_KEY is not set}"
: "${GHL_VERSION:=2021-07-28}"

LOCATION_FLAG=""
LIMIT=20
OFFSET=0
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --location) LOCATION_FLAG="$2"; shift 2 ;;
    --limit)    LIMIT="$2"; shift 2 ;;
    --offset)   OFFSET="$2"; shift 2 ;;
    *)          echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -n "$LOCATION_FLAG" ]]; then
  GHL_LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh" --location "$LOCATION_FLAG")
else
  GHL_LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh")
fi

echo "Fetching blogs for location: $GHL_LOCATION_ID" >&2

curl -s -X GET "$API_BASE/blogs/site/all?locationId=$GHL_LOCATION_ID&limit=$LIMIT&skip=$OFFSET" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Accept: application/json"
