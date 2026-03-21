#!/usr/bin/env bash
# ghl_get_categories.sh — List blog categories for a GHL location
# Usage: ./ghl_get_categories.sh [--location ces]

set -euo pipefail

API_BASE="https://services.leadconnectorhq.com"
: "${GHL_API_KEY:?Error: GHL_API_KEY is not set}"
: "${GHL_VERSION:=2021-07-28}"

LOCATION_FLAG=""
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --location) LOCATION_FLAG="$2"; shift 2 ;;
    *)          echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -n "$LOCATION_FLAG" ]]; then
  GHL_LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh" --location "$LOCATION_FLAG")
else
  GHL_LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh")
fi

echo "Fetching categories for location: $GHL_LOCATION_ID" >&2

curl -s -X GET "$API_BASE/blogs/categories?locationId=$GHL_LOCATION_ID&limit=10&offset=0" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Accept: application/json"
