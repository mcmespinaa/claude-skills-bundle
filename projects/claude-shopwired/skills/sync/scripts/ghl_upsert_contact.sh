#!/usr/bin/env bash
# ghl_upsert_contact.sh — Create or update a GHL contact (dedup by email/phone)
# Usage: ./ghl_upsert_contact.sh --email "test@example.com" --first-name "John" --last-name "Doe" [--phone "+44..."] [--location ces]

set -euo pipefail

: "${GHL_API_KEY:?Error: GHL_API_KEY is not set}"
: "${GHL_VERSION:=2021-07-28}"

API_BASE="https://services.leadconnectorhq.com"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOCATION_ARGS=()
EMAIL=""
FIRST_NAME=""
LAST_NAME=""
PHONE=""
COMPANY=""
ADDRESS=""
CITY=""
STATE=""
POSTAL=""
COUNTRY=""
SOURCE="ShopWired"
TAGS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --location)   LOCATION_ARGS=(--location "$2"); shift 2 ;;
    --email)      EMAIL="$2"; shift 2 ;;
    --first-name) FIRST_NAME="$2"; shift 2 ;;
    --last-name)  LAST_NAME="$2"; shift 2 ;;
    --phone)      PHONE="$2"; shift 2 ;;
    --company)    COMPANY="$2"; shift 2 ;;
    --address)    ADDRESS="$2"; shift 2 ;;
    --city)       CITY="$2"; shift 2 ;;
    --state)      STATE="$2"; shift 2 ;;
    --postal)     POSTAL="$2"; shift 2 ;;
    --country)    COUNTRY="$2"; shift 2 ;;
    --source)     SOURCE="$2"; shift 2 ;;
    --tags)       TAGS="$2"; shift 2 ;;
    *)            shift ;;
  esac
done

if [[ -z "$EMAIL" ]]; then
  echo "Error: --email is required" >&2
  exit 1
fi

LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh" "${LOCATION_ARGS[@]}")

# Build JSON payload
PAYLOAD=$(jq -n \
  --arg locationId "$LOCATION_ID" \
  --arg email "$EMAIL" \
  --arg firstName "$FIRST_NAME" \
  --arg lastName "$LAST_NAME" \
  --arg phone "$PHONE" \
  --arg company "$COMPANY" \
  --arg address "$ADDRESS" \
  --arg city "$CITY" \
  --arg state "$STATE" \
  --arg postal "$POSTAL" \
  --arg country "$COUNTRY" \
  --arg source "$SOURCE" \
  --arg tags "$TAGS" \
  '{locationId: $locationId, email: $email, source: $source} +
   (if $firstName != "" then {firstName: $firstName} else {} end) +
   (if $lastName != "" then {lastName: $lastName} else {} end) +
   (if $phone != "" then {phone: $phone} else {} end) +
   (if $company != "" then {companyName: $company} else {} end) +
   (if $address != "" then {address1: $address} else {} end) +
   (if $city != "" then {city: $city} else {} end) +
   (if $state != "" then {state: $state} else {} end) +
   (if $postal != "" then {postalCode: $postal} else {} end) +
   (if $country != "" then {country: $country} else {} end) +
   (if $tags != "" then {tags: ($tags | split(","))} else {} end)')

echo "Upserting contact: $EMAIL"

curl -s -X POST "${API_BASE}/contacts/upsert" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | jq .
