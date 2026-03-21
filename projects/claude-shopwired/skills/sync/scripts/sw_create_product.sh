#!/usr/bin/env bash
# sw_create_product.sh — Create a product in ShopWired
# Usage: ./sw_create_product.sh --title "Product Name" --price 29.99 [--sku "ABC-123"] [--description "..."] [--stock 100]

set -euo pipefail

: "${SHOPWIRED_API_KEY:?Error: SHOPWIRED_API_KEY is not set}"
: "${SHOPWIRED_API_SECRET:?Error: SHOPWIRED_API_SECRET is not set}"

SW_BASE="https://api.shopwired.co.uk/v1"
TITLE=""
PRICE=""
SKU=""
DESCRIPTION=""
STOCK=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --title)       TITLE="$2"; shift 2 ;;
    --price)       PRICE="$2"; shift 2 ;;
    --sku)         SKU="$2"; shift 2 ;;
    --description) DESCRIPTION="$2"; shift 2 ;;
    --stock)       STOCK="$2"; shift 2 ;;
    *)             shift ;;
  esac
done

if [[ -z "$TITLE" || -z "$PRICE" ]]; then
  echo "Error: --title and --price are required" >&2
  exit 1
fi

AUTH=$(echo -n "${SHOPWIRED_API_KEY}:${SHOPWIRED_API_SECRET}" | base64)

# Build JSON payload
PAYLOAD=$(jq -n \
  --arg title "$TITLE" \
  --argjson price "$PRICE" \
  --arg sku "$SKU" \
  --arg desc "$DESCRIPTION" \
  --arg stock "$STOCK" \
  '{title: $title, price: $price} +
   (if $sku != "" then {sku: $sku} else {} end) +
   (if $desc != "" then {description: $desc} else {} end) +
   (if $stock != "" then {stock: ($stock | tonumber)} else {} end)')

curl -s -X POST "${SW_BASE}/products" \
  -H "Authorization: Basic ${AUTH}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "$PAYLOAD" | jq .
