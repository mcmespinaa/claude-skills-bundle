#!/usr/bin/env bash
# sw_sync_contacts.sh — Sync ShopWired customers + newsletter subscribers to GHL contacts.
# Usage:
#   ./sw_sync_contacts.sh --location ces [--since 24h] [--dry-run] [--tag "shopwired"]
# Output: JSON summary to stdout. Progress to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"
source "$SCRIPT_DIR/sw_api.sh"

SINCE=""
DRY_RUN=false
EXTRA_TAG="shopwired"

while [[ ${#SCRIPT_ARGS[@]+"${#SCRIPT_ARGS[@]}"} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --since)   SINCE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --dry-run) DRY_RUN=true; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:1}") ;;
    --tag)     EXTRA_TAG="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    *)         echo "Unknown arg: ${SCRIPT_ARGS[0]}" >&2; exit 1 ;;
  esac
done

# --- 1. Fetch ShopWired customers ---
echo "Fetching ShopWired customers..." >&2
CUSTOMERS_PATH="/customers"
if [[ -n "$SINCE" ]]; then
  FROM_TS=$(sw_parse_since "$SINCE")
  CUSTOMERS_PATH="/customers?from=${FROM_TS}"
fi
CUSTOMERS=$(sw_paginate "$CUSTOMERS_PATH" ".")

CUSTOMER_COUNT=$(echo "$CUSTOMERS" | jq 'length')
echo "Found $CUSTOMER_COUNT customers" >&2

# --- 2. Fetch newsletter subscribers ---
echo "Fetching ShopWired newsletter subscribers..." >&2
SUBSCRIBERS=$(sw_paginate "/newsletter-subscribers" ".")
SUB_COUNT=$(echo "$SUBSCRIBERS" | jq 'length')
echo "Found $SUB_COUNT newsletter subscribers" >&2

# --- 3. Merge by email ---
# Build a combined list: customers get "sw-customer" tag, subscribers get "sw-subscriber"
MERGED=$(python3 -c "
import json, sys

customers = json.loads(sys.stdin.read())
subscribers = json.loads(open('/dev/fd/3').read())

contacts = {}

for c in customers:
    email = (c.get('email') or '').strip().lower()
    if not email:
        continue
    contacts[email] = {
        'email': email,
        'firstName': c.get('firstName', ''),
        'lastName': c.get('lastName', ''),
        'phone': c.get('phone', ''),
        'company': c.get('company', ''),
        'shopwired_id': c.get('id', ''),
        'source': 'customer',
        'tags': ['sw-customer']
    }

for s in subscribers:
    email = (s.get('emailAddress') or '').strip().lower()
    if not email:
        continue
    if email in contacts:
        contacts[email]['tags'].append('sw-subscriber')
        contacts[email]['source'] = 'both'
    else:
        contacts[email] = {
            'email': email,
            'firstName': s.get('name', ''),
            'lastName': '',
            'phone': '',
            'company': '',
            'shopwired_id': '',
            'source': 'subscriber',
            'tags': ['sw-subscriber']
        }

print(json.dumps(list(contacts.values())))
" <<< "$CUSTOMERS" 3<<< "$SUBSCRIBERS")

TOTAL=$(echo "$MERGED" | jq 'length')
echo "Merged to $TOTAL unique contacts" >&2

# --- 4. Check each against GHL ---
CREATED=0
UPDATED=0
SKIPPED=0
ACTIONS="[]"

for i in $(seq 0 $(( TOTAL - 1 ))); do
  CONTACT=$(echo "$MERGED" | jq -c ".[$i]")
  EMAIL=$(echo "$CONTACT" | jq -r '.email')
  FIRST=$(echo "$CONTACT" | jq -r '.firstName')
  LAST=$(echo "$CONTACT" | jq -r '.lastName')
  PHONE=$(echo "$CONTACT" | jq -r '.phone')
  COMPANY=$(echo "$CONTACT" | jq -r '.company')
  SW_ID=$(echo "$CONTACT" | jq -r '.shopwired_id')
  TAGS=$(echo "$CONTACT" | jq -r '[.tags[], "'"$EXTRA_TAG"'"] | unique | join(",")')

  echo "  [$((i+1))/$TOTAL] $EMAIL..." >&2

  # Look up in GHL
  EXISTING=$(ghl_find_contact "$EMAIL")

  if [[ "$EXISTING" == "null" ]]; then
    ACTION="create"
    if [[ "$DRY_RUN" == true ]]; then
      echo "    [DRY RUN] Would create: $EMAIL (tags: $TAGS)" >&2
      CREATED=$((CREATED + 1))
    else
      GHL_BODY=$(jq -n \
        --arg email "$EMAIL" \
        --arg first "$FIRST" \
        --arg last "$LAST" \
        --arg phone "$PHONE" \
        --arg company "$COMPANY" \
        --arg loc "$GHL_LOCATION_ID" \
        --arg tags "$TAGS" \
        '{
          locationId: $loc,
          email: $email,
          firstName: $first,
          lastName: $last,
          phone: $phone,
          companyName: $company,
          tags: ($tags | split(","))
        } | with_entries(select(.value != ""))')

      RESULT=$(ghl_create_contact "$GHL_BODY" 2>&1) || true
      if echo "$RESULT" | jq -e '.id' > /dev/null 2>&1; then
        CREATED=$((CREATED + 1))
        echo "    Created (GHL ID: $(echo "$RESULT" | jq -r '.id'))" >&2
      else
        echo "    Failed to create: $RESULT" >&2
        SKIPPED=$((SKIPPED + 1))
      fi
    fi
  else
    ACTION="update"
    GHL_ID=$(echo "$EXISTING" | jq -r '.id')

    if [[ "$DRY_RUN" == true ]]; then
      echo "    [DRY RUN] Would update: $EMAIL (GHL: $GHL_ID, tags: +$TAGS)" >&2
      UPDATED=$((UPDATED + 1))
    else
      # Update contact fields
      UPDATE_BODY=$(jq -n \
        --arg first "$FIRST" \
        --arg last "$LAST" \
        --arg phone "$PHONE" \
        --arg company "$COMPANY" \
        '{
          firstName: $first,
          lastName: $last,
          phone: $phone,
          companyName: $company
        } | with_entries(select(.value != ""))')

      ghl_update_contact "$GHL_ID" "$UPDATE_BODY" > /dev/null 2>&1 || true

      # Add tags
      ghl_add_tags "$GHL_ID" "$TAGS"

      UPDATED=$((UPDATED + 1))
      echo "    Updated (GHL: $GHL_ID)" >&2
    fi
  fi

  ACTIONS=$(echo "$ACTIONS" | jq --arg e "$EMAIL" --arg a "$ACTION" '. + [{"email":$e,"action":$a}]')
done

# --- 5. Save sync state ---
if [[ "$DRY_RUN" == false ]]; then
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  jq -n \
    --arg ts "$TIMESTAMP" \
    --argjson total "$TOTAL" \
    --argjson created "$CREATED" \
    --argjson updated "$UPDATED" \
    --argjson skipped "$SKIPPED" \
    '{timestamp: $ts, synced: $total, created: $created, updated: $updated, skipped: $skipped}' \
    > "$SW_SYNC_STATE_DIR/contacts_last_sync.json"
fi

# --- 6. Output summary ---
echo "" >&2
echo "=== Contact Sync Summary ===" >&2
echo "Total:   $TOTAL" >&2
echo "Created: $CREATED" >&2
echo "Updated: $UPDATED" >&2
echo "Skipped: $SKIPPED" >&2
if [[ "$DRY_RUN" == true ]]; then
  echo "(dry run — no changes made)" >&2
fi

jq -n \
  --argjson total "$TOTAL" \
  --argjson created "$CREATED" \
  --argjson updated "$UPDATED" \
  --argjson skipped "$SKIPPED" \
  --argjson dry_run "$DRY_RUN" \
  '{total: $total, created: $created, updated: $updated, skipped: $skipped, dry_run: $dry_run}'
