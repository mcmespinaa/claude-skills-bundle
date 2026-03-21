#!/usr/bin/env bash
# sw_list_webhooks.sh — List all registered webhooks in ShopWired
# Usage: ./sw_list_webhooks.sh

set -euo pipefail

: "${SHOPWIRED_API_KEY:?Error: SHOPWIRED_API_KEY is not set}"
: "${SHOPWIRED_API_SECRET:?Error: SHOPWIRED_API_SECRET is not set}"

SW_BASE="https://api.shopwired.co.uk/v1"

AUTH=$(echo -n "${SHOPWIRED_API_KEY}:${SHOPWIRED_API_SECRET}" | base64)

curl -s -X GET "${SW_BASE}/webhooks" \
  -H "Authorization: Basic ${AUTH}" \
  -H "Accept: application/json" | jq .
