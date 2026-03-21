#!/usr/bin/env bash
# sw_get_product.sh — Get a single product from ShopWired by ID
# Usage: ./sw_get_product.sh --id 12345

set -euo pipefail

: "${SHOPWIRED_API_KEY:?Error: SHOPWIRED_API_KEY is not set}"
: "${SHOPWIRED_API_SECRET:?Error: SHOPWIRED_API_SECRET is not set}"

SW_BASE="https://api.shopwired.co.uk/v1"
PRODUCT_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --id) PRODUCT_ID="$2"; shift 2 ;;
    *)    shift ;;
  esac
done

if [[ -z "$PRODUCT_ID" ]]; then
  echo "Error: --id is required" >&2
  exit 1
fi

AUTH=$(echo -n "${SHOPWIRED_API_KEY}:${SHOPWIRED_API_SECRET}" | base64)

curl -s -X GET "${SW_BASE}/products/${PRODUCT_ID}" \
  -H "Authorization: Basic ${AUTH}" \
  -H "Accept: application/json" | jq .
