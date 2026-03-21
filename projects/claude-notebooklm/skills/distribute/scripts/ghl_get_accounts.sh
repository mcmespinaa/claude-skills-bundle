#!/usr/bin/env bash
# ghl_get_accounts.sh — Fetch connected social media accounts from GHL
# Usage:
#   ./ghl_get_accounts.sh
#   ./ghl_get_accounts.sh --location client_a

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"

API_BASE="https://services.leadconnectorhq.com"

echo "Fetching social media accounts for location: $GHL_LOCATION_ID"

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  "$API_BASE/social-media-posting/$GHL_LOCATION_ID/accounts" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')

if [[ "$HTTP_STATUS" -ne 200 ]]; then
  echo "Error: API returned HTTP $HTTP_STATUS" >&2
  echo "$BODY" >&2
  exit 1
fi

echo "$BODY" | jq '.'
