#!/usr/bin/env bash
# sw_incomplete_orders.sh — Fetch abandoned carts from ShopWired, tag in GHL.
# Usage:
#   ./sw_incomplete_orders.sh --location ces [--since 24h] [--dry-run] [--recover]
# Output: JSON summary to stdout. Progress to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"
source "$SCRIPT_DIR/sw_api.sh"

SINCE=""
DRY_RUN=false
RECOVER=false

while [[ ${#SCRIPT_ARGS[@]+"${#SCRIPT_ARGS[@]}"} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --since)   SINCE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --dry-run) DRY_RUN=true; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:1}") ;;
    --recover) RECOVER=true; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:1}") ;;
    *)         echo "Unknown arg: ${SCRIPT_ARGS[0]}" >&2; exit 1 ;;
  esac
done

# --- 1. Fetch incomplete orders ---
echo "Fetching incomplete orders (abandoned carts)..." >&2
IC_PATH="/incomplete-orders?sort=date_desc"
if [[ -n "$SINCE" ]]; then
  FROM_TS=$(sw_parse_since "$SINCE")
  IC_PATH="${IC_PATH}&from=${FROM_TS}"
fi
INCOMPLETE=$(sw_paginate "$IC_PATH" ".")

TOTAL=$(echo "$INCOMPLETE" | jq 'length')
echo "Found $TOTAL incomplete orders" >&2

# --- 2. Filter out archived, extract those with email ---
ACTIVE=$(echo "$INCOMPLETE" | jq '[.[] | select(.archived != true)]')
ACTIVE_COUNT=$(echo "$ACTIVE" | jq 'length')

WITH_EMAIL=$(echo "$ACTIVE" | jq '[.[] | select(.billingAddress.emailAddress != null and .billingAddress.emailAddress != "")]')
EMAIL_COUNT=$(echo "$WITH_EMAIL" | jq 'length')

TOTAL_VALUE=$(echo "$WITH_EMAIL" | jq '[.[].total // 0] | add // 0')

echo "Active: $ACTIVE_COUNT (archived filtered out: $(( TOTAL - ACTIVE_COUNT )))" >&2
echo "With email: $EMAIL_COUNT" >&2
echo "Total abandoned value: $(python3 -c "print(f'£{$TOTAL_VALUE:.2f}')")" >&2

# --- 3. Process each abandoned cart ---
TAGGED=0
ALREADY_TAGGED=0
SKIPPED=0
RECOVERY_LIST="[]"

for i in $(seq 0 $(( EMAIL_COUNT - 1 ))); do
  CART=$(echo "$WITH_EMAIL" | jq -c ".[$i]")
  EMAIL=$(echo "$CART" | jq -r '.billingAddress.emailAddress' | tr '[:upper:]' '[:lower:]')
  NAME=$(echo "$CART" | jq -r '.billingAddress.name // ""')
  CART_ID=$(echo "$CART" | jq -r '.id')
  CART_TOTAL=$(echo "$CART" | jq -r '.total // 0')
  CART_DATE=$(echo "$CART" | jq -r '.created // ""')
  PRODUCTS=$(echo "$CART" | jq -c '[.products[]? | {title: .title, price: .price, quantity: .quantity, sku: .sku}]')

  echo "  [$((i+1))/$EMAIL_COUNT] $EMAIL (cart #$CART_ID, $(python3 -c "print(f'£{$CART_TOTAL:.2f}')"))" >&2

  if [[ "$DRY_RUN" == true ]]; then
    echo "    [DRY RUN] Would tag: $EMAIL with sw-abandoned-cart" >&2
    TAGGED=$((TAGGED + 1))
    continue
  fi

  # Look up in GHL
  EXISTING=$(ghl_find_contact "$EMAIL")

  if [[ "$EXISTING" == "null" ]]; then
    # Split name into first/last
    FIRST=$(echo "$NAME" | awk '{print $1}')
    LAST=$(echo "$NAME" | awk '{$1=""; print}' | sed 's/^ //')

    GHL_BODY=$(jq -n \
      --arg email "$EMAIL" \
      --arg first "$FIRST" \
      --arg last "$LAST" \
      --arg loc "$GHL_LOCATION_ID" \
      '{
        locationId: $loc,
        email: $email,
        firstName: $first,
        lastName: $last,
        tags: ["shopwired", "sw-abandoned-cart"]
      }')

    RESULT=$(ghl_create_contact "$GHL_BODY" 2>&1) || true
    GHL_ID=$(echo "$RESULT" | jq -r '.id // empty' 2>/dev/null)

    if [[ -n "$GHL_ID" ]]; then
      TAGGED=$((TAGGED + 1))
      echo "    Created + tagged (GHL: $GHL_ID)" >&2
    else
      echo "    Failed to create: $RESULT" >&2
      SKIPPED=$((SKIPPED + 1))
      continue
    fi
  else
    GHL_ID=$(echo "$EXISTING" | jq -r '.id')
    EXISTING_TAGS=$(echo "$EXISTING" | jq -r '[.tags[]?] | join(",")')

    if echo "$EXISTING_TAGS" | grep -q "sw-abandoned-cart"; then
      ALREADY_TAGGED=$((ALREADY_TAGGED + 1))
      echo "    Already tagged (GHL: $GHL_ID)" >&2
    else
      ghl_add_tags "$GHL_ID" "shopwired,sw-abandoned-cart"
      TAGGED=$((TAGGED + 1))
      echo "    Tagged (GHL: $GHL_ID)" >&2
    fi
  fi

  # Add cart note to contact
  NOTE="Abandoned cart #${CART_ID} (${CART_DATE}): $(python3 -c "print(f'£{$CART_TOTAL:.2f}')") — $(echo "$PRODUCTS" | jq -r '[.[] | "\(.title) x\(.quantity)"] | join(", ")')"
  NOTE_BODY=$(jq -n --arg body "$NOTE" '{body: $body}')
  curl -s -X POST "${GHL_API_BASE}/contacts/${GHL_ID}/notes" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION" \
    -H "Content-Type: application/json" \
    -d "$NOTE_BODY" > /dev/null 2>&1 || true

  # Build recovery list for /newsletter
  RECOVERY_LIST=$(echo "$RECOVERY_LIST" | jq \
    --arg email "$EMAIL" \
    --arg name "$NAME" \
    --argjson products "$PRODUCTS" \
    --argjson total "$CART_TOTAL" \
    '. + [{"email": $email, "name": $name, "products": $products, "total": $total}]')
done

# --- 4. Save sync state ---
if [[ "$DRY_RUN" == false ]]; then
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  jq -n \
    --arg ts "$TIMESTAMP" \
    --argjson found "$EMAIL_COUNT" \
    --argjson tagged "$TAGGED" \
    --argjson already "$ALREADY_TAGGED" \
    --argjson skipped "$SKIPPED" \
    --argjson recover "$RECOVER" \
    '{timestamp: $ts, found: $found, tagged: $tagged, already_tagged: $already, skipped: $skipped, recovery_triggered: $recover}' \
    > "$SW_SYNC_STATE_DIR/abandoned_last_sync.json"
fi

# --- 5. Recovery output ---
if [[ "$RECOVER" == true && "$DRY_RUN" == false ]]; then
  RECOVERY_COUNT=$(echo "$RECOVERY_LIST" | jq 'length')
  echo "" >&2
  echo "=== Recovery Ready ===" >&2
  echo "$RECOVERY_COUNT contacts tagged with sw-abandoned-cart." >&2
  echo "To send recovery emails, run:" >&2
  echo "  /newsletter --tag \"sw-abandoned-cart\" --location $LOCATION_KEY" >&2
  echo "" >&2
  echo "Recovery data saved for email template generation." >&2

  # Save recovery data for newsletter skill to pick up
  echo "$RECOVERY_LIST" > "$SW_SYNC_STATE_DIR/recovery_carts.json"
fi

# --- 6. Output summary ---
echo "" >&2
echo "=== Abandoned Cart Summary ===" >&2
echo "Total incomplete:  $TOTAL" >&2
echo "Active with email: $EMAIL_COUNT" >&2
echo "Newly tagged:      $TAGGED" >&2
echo "Already tagged:    $ALREADY_TAGGED" >&2
echo "Skipped:           $SKIPPED" >&2
echo "Total value:       $(python3 -c "print(f'£{$TOTAL_VALUE:.2f}')")" >&2
if [[ "$DRY_RUN" == true ]]; then
  echo "(dry run - no changes made)" >&2
fi

jq -n \
  --argjson total "$TOTAL" \
  --argjson active "$ACTIVE_COUNT" \
  --argjson with_email "$EMAIL_COUNT" \
  --argjson tagged "$TAGGED" \
  --argjson already_tagged "$ALREADY_TAGGED" \
  --argjson skipped "$SKIPPED" \
  --argjson total_value "$TOTAL_VALUE" \
  --argjson dry_run "$DRY_RUN" \
  --argjson recover "$RECOVER" \
  '{total: $total, active: $active, with_email: $with_email, tagged: $tagged, already_tagged: $already_tagged, skipped: $skipped, total_value: $total_value, dry_run: $dry_run, recovery_triggered: $recover}'
