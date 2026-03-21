#!/usr/bin/env bash
# sw_sync_orders.sh — Sync ShopWired orders to GHL pipeline opportunities + tag contacts.
# Usage:
#   ./sw_sync_orders.sh --location ces [--since 24h] [--dry-run] [--pipeline "shopwired-orders"]
# Output: JSON summary to stdout. Progress to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"
source "$SCRIPT_DIR/sw_api.sh"

SINCE=""
DRY_RUN=false
PIPELINE_NAME="shopwired-orders"

while [[ ${#SCRIPT_ARGS[@]+"${#SCRIPT_ARGS[@]}"} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --since)    SINCE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --dry-run)  DRY_RUN=true; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:1}") ;;
    --pipeline) PIPELINE_NAME="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    *)          echo "Unknown arg: ${SCRIPT_ARGS[0]}" >&2; exit 1 ;;
  esac
done

# --- Stage mapping: ShopWired status -> GHL pipeline stage name ---
sw_status_to_stage() {
  case "$(echo "$1" | tr '[:upper:]' '[:lower:]')" in
    pending)    echo "New Order" ;;
    processing) echo "Processing" ;;
    shipped)    echo "Shipped" ;;
    delivered)  echo "Delivered" ;;
    completed)  echo "Completed" ;;
    cancelled)  echo "Cancelled" ;;
    *)          echo "New Order" ;;
  esac
}

# --- 1. Resolve or create GHL pipeline ---
echo "Looking up GHL pipeline '$PIPELINE_NAME'..." >&2

PIPELINES_RESPONSE=$(curl -s \
  "${GHL_API_BASE}/opportunities/pipelines?locationId=${GHL_LOCATION_ID}" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION")

PIPELINE_ID=$(echo "$PIPELINES_RESPONSE" | jq -r \
  --arg name "$PIPELINE_NAME" \
  '[.pipelines[]? | select(.name == $name)] | .[0].id // empty')

if [[ -z "$PIPELINE_ID" ]]; then
  echo "Pipeline '$PIPELINE_NAME' not found." >&2
  echo "PIPELINE_NOT_FOUND" > /dev/fd/1
  echo "" >&2
  echo "Available pipelines:" >&2
  echo "$PIPELINES_RESPONSE" | jq -r '.pipelines[]? | "  - \(.name) (id: \(.id))"' >&2
  echo "" >&2
  echo "To create it, the skill needs these stages:" >&2
  echo "  New Order > Processing > Shipped > Delivered > Completed" >&2
  echo "" >&2
  echo "Ask the user whether to create the pipeline or use an existing one." >&2
  exit 0
fi

echo "Found pipeline: $PIPELINE_ID" >&2

# Build stage name -> ID mapping
STAGES=$(echo "$PIPELINES_RESPONSE" | jq -c \
  --arg pid "$PIPELINE_ID" \
  '[.pipelines[]? | select(.id == $pid) | .stages[]? | {name: .name, id: .id}]')

echo "Stages: $(echo "$STAGES" | jq -r '[.[].name] | join(" > ")')" >&2

# --- 2. Fetch ShopWired orders ---
echo "Fetching ShopWired orders..." >&2
ORDERS_PATH="/orders"
if [[ -n "$SINCE" ]]; then
  FROM_TS=$(sw_parse_since "$SINCE")
  ORDERS_PATH="/orders?from=${FROM_TS}"
fi
ORDERS=$(sw_paginate "$ORDERS_PATH" ".")

ORDER_COUNT=$(echo "$ORDERS" | jq 'length')
echo "Found $ORDER_COUNT orders" >&2

# --- 3. Process each order ---
CREATED_OPP=0
UPDATED_OPP=0
CONTACTS_TAGGED=0
SKIPPED=0

for i in $(seq 0 $(( ORDER_COUNT - 1 ))); do
  ORDER=$(echo "$ORDERS" | jq -c ".[$i]")
  ORDER_ID=$(echo "$ORDER" | jq -r '.id')
  ORDER_REF=$(echo "$ORDER" | jq -r '.reference // .orderReference // .id')
  ORDER_STATUS=$(echo "$ORDER" | jq -r '.status // "pending"')
  ORDER_TOTAL_RAW=$(echo "$ORDER" | jq -r '.total // 0')
  ORDER_DATE=$(echo "$ORDER" | jq -r '.createdAt // .created // ""')

  # ShopWired stores prices in pence — convert to pounds
  ORDER_TOTAL=$(python3 -c "
v = $ORDER_TOTAL_RAW
print(v / 100 if v > 1000 else v)
")

  # Get customer email from order
  CUSTOMER_EMAIL=$(echo "$ORDER" | jq -r '
    .customer.email //
    .billingAddress.emailAddress //
    .billingAddress.email //
    empty' 2>/dev/null | head -1)

  if [[ -z "$CUSTOMER_EMAIL" || "$CUSTOMER_EMAIL" == "null" ]]; then
    echo "  [$((i+1))/$ORDER_COUNT] Order #$ORDER_REF — no email, skipping" >&2
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  CUSTOMER_EMAIL=$(echo "$CUSTOMER_EMAIL" | tr '[:upper:]' '[:lower:]')
  STAGE_NAME=$(sw_status_to_stage "$ORDER_STATUS")
  STAGE_ID=$(echo "$STAGES" | jq -r --arg name "$STAGE_NAME" '[.[] | select(.name == $name)] | .[0].id // empty')

  # Fallback to first stage if mapping fails
  if [[ -z "$STAGE_ID" ]]; then
    STAGE_ID=$(echo "$STAGES" | jq -r '.[0].id // empty')
    STAGE_NAME=$(echo "$STAGES" | jq -r '.[0].name // "Unknown"')
  fi

  echo "  [$((i+1))/$ORDER_COUNT] Order #$ORDER_REF ($ORDER_STATUS -> $STAGE_NAME) $CUSTOMER_EMAIL $(python3 -c "print(f'£{$ORDER_TOTAL:.2f}')")" >&2

  if [[ "$DRY_RUN" == true ]]; then
    echo "    [DRY RUN] Would create opportunity + tag contact" >&2
    CREATED_OPP=$((CREATED_OPP + 1))
    CONTACTS_TAGGED=$((CONTACTS_TAGGED + 1))
    continue
  fi

  # --- Find or create GHL contact ---
  GHL_CONTACT=$(ghl_find_contact "$CUSTOMER_EMAIL")
  if [[ "$GHL_CONTACT" == "null" ]]; then
    CUST_NAME=$(echo "$ORDER" | jq -r '.billingAddress.name // .customer.firstName // ""')
    FIRST=$(echo "$CUST_NAME" | awk '{print $1}')
    LAST=$(echo "$CUST_NAME" | awk '{$1=""; print}' | sed 's/^ //')

    GHL_BODY=$(jq -n \
      --arg email "$CUSTOMER_EMAIL" \
      --arg first "$FIRST" \
      --arg last "$LAST" \
      --arg loc "$GHL_LOCATION_ID" \
      '{locationId: $loc, email: $email, firstName: $first, lastName: $last, tags: ["shopwired", "sw-buyer"]}')

    GHL_CONTACT=$(ghl_create_contact "$GHL_BODY" 2>&1) || true
  fi

  CONTACT_ID=$(echo "$GHL_CONTACT" | jq -r '.id // empty' 2>/dev/null)
  if [[ -z "$CONTACT_ID" ]]; then
    echo "    Could not find/create contact, skipping" >&2
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Tag contact
  ghl_add_tags "$CONTACT_ID" "shopwired,sw-buyer,sw-order-${ORDER_STATUS}"
  CONTACTS_TAGGED=$((CONTACTS_TAGGED + 1))

  # --- Create GHL opportunity ---
  OPP_BODY=$(jq -n \
    --arg name "Order #${ORDER_REF}" \
    --arg pid "$PIPELINE_ID" \
    --arg sid "$STAGE_ID" \
    --argjson value "$ORDER_TOTAL" \
    --arg cid "$CONTACT_ID" \
    --arg loc "$GHL_LOCATION_ID" \
    '{
      pipelineId: $pid,
      locationId: $loc,
      name: $name,
      stageId: $sid,
      monetaryValue: $value,
      contactId: $cid,
      status: "open"
    }')

  _sw_rate_limit
  OPP_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X POST "${GHL_API_BASE}/opportunities/" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION" \
    -H "Content-Type: application/json" \
    -d "$OPP_BODY")

  OPP_STATUS=$(echo "$OPP_RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
  OPP_RESULT=$(echo "$OPP_RESPONSE" | sed '/HTTP_STATUS:/d')

  if [[ "$OPP_STATUS" -ge 200 && "$OPP_STATUS" -lt 300 ]]; then
    OPP_ID=$(echo "$OPP_RESULT" | jq -r '.opportunity.id // .id // "unknown"')
    CREATED_OPP=$((CREATED_OPP + 1))
    echo "    Opportunity created: $OPP_ID" >&2
  else
    echo "    Failed to create opportunity: HTTP $OPP_STATUS" >&2
    echo "    $OPP_RESULT" >&2
    SKIPPED=$((SKIPPED + 1))
  fi
done

# --- 4. Save sync state ---
if [[ "$DRY_RUN" == false ]]; then
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  jq -n \
    --arg ts "$TIMESTAMP" \
    --argjson total "$ORDER_COUNT" \
    --argjson opportunities_created "$CREATED_OPP" \
    --argjson contacts_tagged "$CONTACTS_TAGGED" \
    --argjson skipped "$SKIPPED" \
    --arg pipeline "$PIPELINE_NAME" \
    '{timestamp: $ts, total: $total, opportunities_created: $opportunities_created, contacts_tagged: $contacts_tagged, skipped: $skipped, pipeline: $pipeline}' \
    > "$SW_SYNC_STATE_DIR/orders_last_sync.json"
fi

# --- 5. Output summary ---
echo "" >&2
echo "=== Order Sync Summary ===" >&2
echo "Total orders:       $ORDER_COUNT" >&2
echo "Opportunities:      $CREATED_OPP" >&2
echo "Contacts tagged:    $CONTACTS_TAGGED" >&2
echo "Skipped:            $SKIPPED" >&2
echo "Pipeline:           $PIPELINE_NAME" >&2
if [[ "$DRY_RUN" == true ]]; then
  echo "(dry run - no changes made)" >&2
fi

jq -n \
  --argjson total "$ORDER_COUNT" \
  --argjson opportunities_created "$CREATED_OPP" \
  --argjson contacts_tagged "$CONTACTS_TAGGED" \
  --argjson skipped "$SKIPPED" \
  --arg pipeline "$PIPELINE_NAME" \
  --argjson dry_run "$DRY_RUN" \
  '{total: $total, opportunities_created: $opportunities_created, contacts_tagged: $contacts_tagged, skipped: $skipped, pipeline: $pipeline, dry_run: $dry_run}'
