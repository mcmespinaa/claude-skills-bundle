#!/usr/bin/env bash
# sw_register_webhook.sh — Register a webhook with ShopWired
# Usage: ./sw_register_webhook.sh --event customer.created --url https://your-project.supabase.co/functions/v1/sw-customer-sync

set -euo pipefail

: "${SHOPWIRED_API_KEY:?Error: SHOPWIRED_API_KEY is not set}"
: "${SHOPWIRED_API_SECRET:?Error: SHOPWIRED_API_SECRET is not set}"

SW_BASE="https://api.shopwired.co.uk/v1"
EVENT=""
WEBHOOK_URL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --event) EVENT="$2"; shift 2 ;;
    --url)   WEBHOOK_URL="$2"; shift 2 ;;
    *)       shift ;;
  esac
done

if [[ -z "$EVENT" || -z "$WEBHOOK_URL" ]]; then
  echo "Error: --event and --url are required" >&2
  echo "Events: customer.created, customer.updated, order.finalized, order.status_changed, product.created, product.updated, product.deleted" >&2
  exit 1
fi

AUTH=$(echo -n "${SHOPWIRED_API_KEY}:${SHOPWIRED_API_SECRET}" | base64)

PAYLOAD=$(jq -n --arg event "$EVENT" --arg url "$WEBHOOK_URL" \
  '{event: $event, url: $url}')

echo "Registering webhook: $EVENT -> $WEBHOOK_URL"

curl -s -X POST "${SW_BASE}/webhooks" \
  -H "Authorization: Basic ${AUTH}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "$PAYLOAD" | jq .
