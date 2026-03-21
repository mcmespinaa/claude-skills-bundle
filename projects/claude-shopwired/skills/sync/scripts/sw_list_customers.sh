#!/usr/bin/env bash
# sw_list_customers.sh — List customers from ShopWired API
# Usage: ./sw_list_customers.sh [--page 1] [--per-page 50]

set -euo pipefail

: "${SHOPWIRED_API_KEY:?Error: SHOPWIRED_API_KEY is not set}"
: "${SHOPWIRED_API_SECRET:?Error: SHOPWIRED_API_SECRET is not set}"

SW_BASE="https://api.shopwired.co.uk/v1"
PAGE=1
PER_PAGE=50

while [[ $# -gt 0 ]]; do
  case "$1" in
    --page)     PAGE="$2"; shift 2 ;;
    --per-page) PER_PAGE="$2"; shift 2 ;;
    *)          shift ;;
  esac
done

AUTH=$(echo -n "${SHOPWIRED_API_KEY}:${SHOPWIRED_API_SECRET}" | base64)

curl -s -X GET "${SW_BASE}/customers?page=${PAGE}&per_page=${PER_PAGE}" \
  -H "Authorization: Basic ${AUTH}" \
  -H "Accept: application/json" | jq .
