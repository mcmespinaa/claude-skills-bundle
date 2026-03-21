#!/usr/bin/env bash
# sw_setup_webhooks.sh — Register ShopWired webhooks for real-time sync.
# Usage:
#   ./sw_setup_webhooks.sh --location ces --url https://hooks.example.com/sw
#   ./sw_setup_webhooks.sh --location ces --list
# Output: JSON summary to stdout. Progress to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"
source "$SCRIPT_DIR/sw_api.sh"

WEBHOOK_URL=""
LIST_ONLY=false

while [[ ${#SCRIPT_ARGS[@]+"${#SCRIPT_ARGS[@]}"} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --url)  WEBHOOK_URL="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --list) LIST_ONLY=true; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:1}") ;;
    *)      echo "Unknown arg: ${SCRIPT_ARGS[0]}" >&2; exit 1 ;;
  esac
done

# Recommended webhook topics for GHL integration
RECOMMENDED_TOPICS="order.created order.updated customer.created customer.updated"

# --- 1. List existing webhooks ---
echo "Fetching existing webhooks..." >&2
EXISTING=$(sw_get "/webhooks")
EXISTING_COUNT=$(echo "$EXISTING" | jq 'if type == "array" then length else 0 end')

echo "" >&2
echo "=== Current Webhooks ($EXISTING_COUNT) ===" >&2
if [[ "$EXISTING_COUNT" -gt 0 ]]; then
  echo "$EXISTING" | jq -r '.[] | "  [\(.id)] \(.topic) -> \(.url) (enabled: \(.enabled // "?"), verified: \(.verified // "?"))"' >&2
else
  echo "  (none)" >&2
fi

if [[ "$LIST_ONLY" == true ]]; then
  echo "$EXISTING"
  exit 0
fi

# --- 2. Validate URL ---
if [[ -z "$WEBHOOK_URL" ]]; then
  echo "" >&2
  echo "Error: --url is required (must be HTTPS)" >&2
  echo "Usage: sw_setup_webhooks.sh --location $LOCATION_KEY --url https://your-receiver.com/shopwired" >&2
  exit 1
fi

if [[ "$WEBHOOK_URL" != https://* ]]; then
  echo "Error: Webhook URL must use HTTPS (got: $WEBHOOK_URL)" >&2
  exit 1
fi

# --- 3. Check which topics need registration ---
echo "" >&2
echo "Checking recommended topics..." >&2

TO_CREATE=""
ALREADY_EXISTS=""

for TOPIC in $RECOMMENDED_TOPICS; do
  MATCH=$(echo "$EXISTING" | jq -r --arg t "$TOPIC" --arg u "$WEBHOOK_URL" \
    '[.[]? | select(.topic == $t and .url == $u)] | length')

  if [[ "$MATCH" -gt 0 ]]; then
    echo "  $TOPIC -> already registered" >&2
    ALREADY_EXISTS="${ALREADY_EXISTS}${TOPIC} "
  else
    echo "  $TOPIC -> needs registration" >&2
    TO_CREATE="${TO_CREATE}${TOPIC} "
  fi
done

if [[ -z "$TO_CREATE" ]]; then
  echo "" >&2
  echo "All recommended webhooks are already registered." >&2
  jq -n '{status: "all_registered", created: 0}'
  exit 0
fi

# --- 4. Show plan and output for confirmation ---
echo "" >&2
echo "Will register webhooks for: $TO_CREATE" >&2
echo "Target URL: $WEBHOOK_URL" >&2
echo "" >&2
echo "WAITING_FOR_CONFIRMATION" >&2

# --- 5. Create webhooks ---
CREATED=0
FAILED=0
RESULTS="[]"

for TOPIC in $TO_CREATE; do
  echo "  Creating webhook: $TOPIC -> $WEBHOOK_URL" >&2

  BODY=$(jq -n --arg topic "$TOPIC" --arg url "$WEBHOOK_URL" \
    '{topic: $topic, url: $url}')

  RESULT=$(sw_post "/webhooks" "$BODY" 2>&1) || true
  WH_ID=$(echo "$RESULT" | jq -r '.id // empty' 2>/dev/null)

  if [[ -n "$WH_ID" ]]; then
    CREATED=$((CREATED + 1))
    echo "    Created (ID: $WH_ID)" >&2

    # Verify the webhook
    echo "    Verifying..." >&2
    sw_post "/webhooks/${WH_ID}/verify" "{}" > /dev/null 2>&1 || echo "    Verification request sent" >&2

    RESULTS=$(echo "$RESULTS" | jq \
      --arg topic "$TOPIC" \
      --arg id "$WH_ID" \
      '. + [{"topic": $topic, "id": $id, "status": "created"}]')
  else
    FAILED=$((FAILED + 1))
    echo "    Failed: $RESULT" >&2
    RESULTS=$(echo "$RESULTS" | jq \
      --arg topic "$TOPIC" \
      '. + [{"topic": $topic, "status": "failed"}]')
  fi
done

# --- 6. Output summary ---
echo "" >&2
echo "=== Webhook Setup Summary ===" >&2
echo "Created:  $CREATED" >&2
echo "Failed:   $FAILED" >&2
echo "Skipped:  $(echo "$ALREADY_EXISTS" | wc -w | tr -d ' ')" >&2

jq -n \
  --argjson created "$CREATED" \
  --argjson failed "$FAILED" \
  --argjson results "$RESULTS" \
  --arg url "$WEBHOOK_URL" \
  '{created: $created, failed: $failed, url: $url, webhooks: $results}'
