#!/usr/bin/env bash
# ghl_list_products.sh — List products from GHL
# Usage: ./ghl_list_products.sh [--location ces]

set -euo pipefail

: "${GHL_API_KEY:?Error: GHL_API_KEY is not set}"
: "${GHL_VERSION:=2021-07-28}"

API_BASE="https://services.leadconnectorhq.com"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOCATION_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --location) LOCATION_ARGS=(--location "$2"); shift 2 ;;
    *)          shift ;;
  esac
done

LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh" "${LOCATION_ARGS[@]}")

curl -s -X GET "${API_BASE}/products?locationId=${LOCATION_ID}" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Accept: application/json" | jq .
