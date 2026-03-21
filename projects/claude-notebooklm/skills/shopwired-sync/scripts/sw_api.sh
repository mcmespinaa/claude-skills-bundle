#!/usr/bin/env bash
# sw_api.sh — Shared ShopWired API helper.
#
# Source this after init.sh to get ShopWired credentials and helper functions.
#
# Usage in a skill script:
#   source "${CLAUDE_PLUGIN_ROOT}/scripts/init.sh" "$@"
#   source "${CLAUDE_PLUGIN_ROOT}/skills/shopwired-sync/scripts/sw_api.sh"
#   sw_get "/customers?count=50"
#   sw_post "/webhooks" '{"topic":"order.created","url":"https://..."}'
#
# Provides:
#   SHOPWIRED_API_KEY, SHOPWIRED_API_SECRET — resolved from locations.json
#   SW_API_BASE — https://api.ecommerceapi.uk/v1
#   sw_get <path>        — GET request, returns JSON body, exits on error
#   sw_post <path> <json> — POST request
#   sw_put <path> <json>  — PUT request
#   sw_delete <path>      — DELETE request
#   sw_paginate <path> <jq_key> [max] — Auto-paginate using offset/count, returns merged array
#   sw_parse_since <window> — Convert "24h"/"7d" to UNIX timestamp
#
# Rate limiting: 2 req/s sustained. Sleeps 0.5s between calls.

SW_API_BASE="https://api.ecommerceapi.uk/v1"
_SW_LAST_CALL=0

# --- Resolve ShopWired credentials from locations.json ---
_SW_LOCATIONS_FILE=""
if [[ -f "$PWD/locations.json" ]]; then
  _SW_LOCATIONS_FILE="$PWD/locations.json"
fi

if [[ -z "$_SW_LOCATIONS_FILE" ]]; then
  echo "Error: locations.json not found in $PWD" >&2
  exit 1
fi

_SW_KEY_VAR=$(jq -r --arg k "$LOCATION_KEY" \
  '.locations[$k].shopwiredApiKeyVar // empty' "$_SW_LOCATIONS_FILE")
_SW_SECRET_VAR=$(jq -r --arg k "$LOCATION_KEY" \
  '.locations[$k].shopwiredApiSecretVar // empty' "$_SW_LOCATIONS_FILE")

if [[ -z "$_SW_KEY_VAR" || -z "$_SW_SECRET_VAR" ]]; then
  echo "Error: Add shopwiredApiKeyVar and shopwiredApiSecretVar to locations.json for '$LOCATION_KEY'" >&2
  echo "" >&2
  echo "Example:" >&2
  echo '  "ces": {' >&2
  echo '    ...existing fields...' >&2
  echo '    "shopwiredApiKeyVar": "SHOPWIRED_API_KEY_CES",' >&2
  echo '    "shopwiredApiSecretVar": "SHOPWIRED_API_SECRET_CES"' >&2
  echo '  }' >&2
  exit 1
fi

SHOPWIRED_API_KEY="${!_SW_KEY_VAR:-}"
SHOPWIRED_API_SECRET="${!_SW_SECRET_VAR:-}"

if [[ -z "$SHOPWIRED_API_KEY" || -z "$SHOPWIRED_API_SECRET" ]]; then
  echo "Error: $_SW_KEY_VAR or $_SW_SECRET_VAR is not set in .env" >&2
  exit 1
fi

export SHOPWIRED_API_KEY SHOPWIRED_API_SECRET SW_API_BASE

# --- Sync state directory ---
SW_SYNC_STATE_DIR="${HOME}/.notebooklm/shopwired-sync/${LOCATION_KEY}"
mkdir -p "$SW_SYNC_STATE_DIR"
export SW_SYNC_STATE_DIR

# --- Rate limiting (0.5s between calls for 2 req/s) ---
_sw_rate_limit() {
  local now
  now=$(python3 -c "import time; print(int(time.time()*1000))")
  local elapsed=$(( now - _SW_LAST_CALL ))
  if [[ "$elapsed" -lt 500 && "$_SW_LAST_CALL" -gt 0 ]]; then
    local wait_ms=$(( 500 - elapsed ))
    sleep "$(python3 -c "print($wait_ms/1000)")"
  fi
  _SW_LAST_CALL=$(python3 -c "import time; print(int(time.time()*1000))")
}

# --- Core HTTP functions ---

# sw_get <path> — GET request, prints JSON body, exits on HTTP error
sw_get() {
  local path="$1"
  _sw_rate_limit

  local response
  response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -u "$SHOPWIRED_API_KEY:$SHOPWIRED_API_SECRET" \
    "${SW_API_BASE}${path}")

  local status body
  status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
  body=$(echo "$response" | sed '/HTTP_STATUS:/d')

  if [[ "$status" -eq 429 ]]; then
    local retry_after
    retry_after=$(echo "$body" | jq -r '.retryAfter // 2')
    echo "Rate limited, waiting ${retry_after}s..." >&2
    sleep "$retry_after"
    sw_get "$path"
    return
  fi

  if [[ "$status" -lt 200 || "$status" -ge 300 ]]; then
    echo "Error: ShopWired GET ${path} returned HTTP $status" >&2
    echo "$body" >&2
    exit 1
  fi

  echo "$body"
}

# sw_post <path> <json_body>
sw_post() {
  local path="$1" json_body="${2:-}"
  _sw_rate_limit

  local response
  response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X POST \
    -u "$SHOPWIRED_API_KEY:$SHOPWIRED_API_SECRET" \
    -H "Content-Type: application/json" \
    -d "$json_body" \
    "${SW_API_BASE}${path}")

  local status body
  status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
  body=$(echo "$response" | sed '/HTTP_STATUS:/d')

  if [[ "$status" -lt 200 || "$status" -ge 300 ]]; then
    echo "Error: ShopWired POST ${path} returned HTTP $status" >&2
    echo "$body" >&2
    exit 1
  fi

  echo "$body"
}

# sw_put <path> <json_body>
sw_put() {
  local path="$1" json_body="${2:-}"
  _sw_rate_limit

  local response
  response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X PUT \
    -u "$SHOPWIRED_API_KEY:$SHOPWIRED_API_SECRET" \
    -H "Content-Type: application/json" \
    -d "$json_body" \
    "${SW_API_BASE}${path}")

  local status body
  status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
  body=$(echo "$response" | sed '/HTTP_STATUS:/d')

  if [[ "$status" -lt 200 || "$status" -ge 300 ]]; then
    echo "Error: ShopWired PUT ${path} returned HTTP $status" >&2
    echo "$body" >&2
    exit 1
  fi

  echo "$body"
}

# sw_delete <path>
sw_delete() {
  local path="$1"
  _sw_rate_limit

  local response
  response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X DELETE \
    -u "$SHOPWIRED_API_KEY:$SHOPWIRED_API_SECRET" \
    "${SW_API_BASE}${path}")

  local status body
  status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
  body=$(echo "$response" | sed '/HTTP_STATUS:/d')

  if [[ "$status" -lt 200 || "$status" -ge 300 ]]; then
    echo "Error: ShopWired DELETE ${path} returned HTTP $status" >&2
    echo "$body" >&2
    exit 1
  fi

  echo "$body"
}

# --- Pagination helper ---
# sw_paginate <base_path> <jq_array_expression> [max_records]
# Example: sw_paginate "/customers" "." 500
# Returns: merged JSON array of all pages
sw_paginate() {
  local base_path="$1"
  local jq_expr="${2:-.}"
  local max_records="${3:-0}"
  local page_size=250
  local offset=0
  local all="[]"
  local separator="?"

  # Check if base_path already has query params
  if [[ "$base_path" == *"?"* ]]; then
    separator="&"
  fi

  while true; do
    local page_data
    page_data=$(sw_get "${base_path}${separator}count=${page_size}&offset=${offset}")

    local page_items
    page_items=$(echo "$page_data" | jq -c "$jq_expr")

    local page_count
    page_count=$(echo "$page_items" | jq 'if type == "array" then length else 0 end')

    if [[ "$page_count" -eq 0 ]]; then
      break
    fi

    all=$(echo "$all" "$page_items" | jq -s '.[0] + .[1]')
    offset=$(( offset + page_count ))

    local total
    total=$(echo "$all" | jq 'length')
    echo "  Fetched $total records so far..." >&2

    if [[ "$max_records" -gt 0 && "$total" -ge "$max_records" ]]; then
      all=$(echo "$all" | jq --argjson m "$max_records" '.[:$m]')
      break
    fi

    if [[ "$page_count" -lt "$page_size" ]]; then
      break
    fi
  done

  echo "$all"
}

# --- Time window parser ---
# sw_parse_since <window> — Convert "1h"/"24h"/"7d"/"30d" to UNIX timestamp
sw_parse_since() {
  local window="$1"
  python3 -c "
import time, re, sys
m = re.match(r'^(\d+)(h|d)$', '$window')
if not m:
    print('Error: Invalid time window: $window (use 1h, 24h, 7d, 30d)', file=sys.stderr)
    sys.exit(1)
val, unit = int(m.group(1)), m.group(2)
seconds = val * 3600 if unit == 'h' else val * 86400
print(int(time.time() - seconds))
"
}

# --- GHL contact helpers (reusable across subcommands) ---

GHL_API_BASE="https://services.leadconnectorhq.com"

# ghl_find_contact <email> — Search GHL for contact by email, returns contact JSON or "null"
ghl_find_contact() {
  local email="$1"
  _sw_rate_limit

  local response
  response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    "${GHL_API_BASE}/contacts/?locationId=${GHL_LOCATION_ID}&query=${email}&limit=1" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION")

  local status body
  status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
  body=$(echo "$response" | sed '/HTTP_STATUS:/d')

  if [[ "$status" -ne 200 ]]; then
    echo "null"
    return
  fi

  echo "$body" | jq '.contacts[0] // null'
}

# ghl_create_contact <json_body> — Create a GHL contact, returns contact JSON
ghl_create_contact() {
  local json_body="$1"
  _sw_rate_limit

  local response
  response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X POST "${GHL_API_BASE}/contacts/" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION" \
    -H "Content-Type: application/json" \
    -d "$json_body")

  local status body
  status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
  body=$(echo "$response" | sed '/HTTP_STATUS:/d')

  if [[ "$status" -lt 200 || "$status" -ge 300 ]]; then
    echo "Error: GHL create contact returned HTTP $status" >&2
    echo "$body" >&2
    return 1
  fi

  echo "$body" | jq '.contact // .'
}

# ghl_update_contact <contact_id> <json_body> — Update a GHL contact
ghl_update_contact() {
  local contact_id="$1" json_body="$2"
  _sw_rate_limit

  local response
  response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X PUT "${GHL_API_BASE}/contacts/${contact_id}" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION" \
    -H "Content-Type: application/json" \
    -d "$json_body")

  local status body
  status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
  body=$(echo "$response" | sed '/HTTP_STATUS:/d')

  if [[ "$status" -lt 200 || "$status" -ge 300 ]]; then
    echo "Error: GHL update contact $contact_id returned HTTP $status" >&2
    echo "$body" >&2
    return 1
  fi

  echo "$body" | jq '.contact // .'
}

# ghl_add_tags <contact_id> <tag1,tag2,...> — Add tags to a GHL contact
ghl_add_tags() {
  local contact_id="$1" tags="$2"
  local json
  json=$(jq -n --arg t "$tags" '{tags: ($t | split(","))}')
  _sw_rate_limit

  curl -s -X POST "${GHL_API_BASE}/contacts/${contact_id}/tags" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION" \
    -H "Content-Type: application/json" \
    -d "$json" > /dev/null
}
