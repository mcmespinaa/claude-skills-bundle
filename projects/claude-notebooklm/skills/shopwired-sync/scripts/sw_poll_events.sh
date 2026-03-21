#!/usr/bin/env bash
# sw_poll_events.sh — Poll ShopWired Events API for changes since last sync.
# Usage:
#   ./sw_poll_events.sh --location ces [--since 24h] [--subject-type order]
# Output: JSON array of events to stdout. Progress to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"
source "$SCRIPT_DIR/sw_api.sh"

SINCE=""
SUBJECT_TYPE=""

while [[ ${#SCRIPT_ARGS[@]+"${#SCRIPT_ARGS[@]}"} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --since)        SINCE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --subject-type) SUBJECT_TYPE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    *)              echo "Unknown arg: ${SCRIPT_ARGS[0]}" >&2; exit 1 ;;
  esac
done

# --- 1. Read cursor from last sync ---
CURSOR_FILE="$SW_SYNC_STATE_DIR/events_cursor.json"
LAST_EVENT_ID=0

if [[ -f "$CURSOR_FILE" ]]; then
  LAST_EVENT_ID=$(jq -r '.last_event_id // 0' "$CURSOR_FILE")
  LAST_TS=$(jq -r '.timestamp // "never"' "$CURSOR_FILE")
  echo "Last sync: $LAST_TS (event ID: $LAST_EVENT_ID)" >&2
else
  echo "First run - no cursor found" >&2
fi

# --- 2. Build events query ---
EVENTS_PATH="/events?count=250"
if [[ -n "$SUBJECT_TYPE" ]]; then
  EVENTS_PATH="${EVENTS_PATH}&subjectType=${SUBJECT_TYPE}"
fi
if [[ -n "$SINCE" ]]; then
  FROM_TS=$(sw_parse_since "$SINCE")
  EVENTS_PATH="${EVENTS_PATH}&from=${FROM_TS}"
fi

echo "Fetching events..." >&2
EVENTS=$(sw_paginate "$EVENTS_PATH" ".")

TOTAL=$(echo "$EVENTS" | jq 'length')
echo "Fetched $TOTAL events" >&2

# --- 3. Filter events newer than cursor ---
if [[ "$LAST_EVENT_ID" -gt 0 ]]; then
  NEW_EVENTS=$(echo "$EVENTS" | jq --argjson cursor "$LAST_EVENT_ID" \
    '[.[] | select(.id > $cursor)]')
else
  NEW_EVENTS="$EVENTS"
fi

NEW_COUNT=$(echo "$NEW_EVENTS" | jq 'length')
echo "New events since last sync: $NEW_COUNT" >&2

if [[ "$NEW_COUNT" -eq 0 ]]; then
  echo "No new events." >&2
  echo "[]"
  exit 0
fi

# --- 4. Summarize by subject type ---
echo "" >&2
echo "=== Event Summary ===" >&2
echo "$NEW_EVENTS" | jq -r '
  group_by(.subjectType) |
  .[] |
  "  \(.[0].subjectType): \(length) events"
' >&2

# --- 5. Categorize actionable events ---
SUMMARY=$(echo "$NEW_EVENTS" | python3 -c "
import json, sys

events = json.loads(sys.stdin.read())
actions = {
    'contact_sync': [],
    'order_sync': [],
    'subscriber_sync': [],
    'refund': [],
    'other': []
}

for e in events:
    st = e.get('subjectType', '')
    sid = e.get('subjectId', '')
    topic = e.get('topic', '')

    if st == 'customer':
        actions['contact_sync'].append({'event_id': e['id'], 'subject_id': sid, 'topic': topic})
    elif st == 'order':
        actions['order_sync'].append({'event_id': e['id'], 'subject_id': sid, 'topic': topic})
    elif st == 'newsletter_subscriber':
        actions['subscriber_sync'].append({'event_id': e['id'], 'subject_id': sid, 'topic': topic})
    elif st == 'order_refund':
        actions['refund'].append({'event_id': e['id'], 'subject_id': sid, 'topic': topic})
    else:
        actions['other'].append({'event_id': e['id'], 'subject_type': st, 'subject_id': sid, 'topic': topic})

print(json.dumps(actions))
")

echo "" >&2
echo "Actionable:" >&2
echo "$SUMMARY" | jq -r '
  "  Contacts to sync: \(.contact_sync | length)",
  "  Orders to sync:   \(.order_sync | length)",
  "  Subscribers:       \(.subscriber_sync | length)",
  "  Refunds:           \(.refund | length)",
  "  Other:             \(.other | length)"
' >&2

# --- 6. Update cursor ---
MAX_EVENT_ID=$(echo "$NEW_EVENTS" | jq '[.[].id] | max')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

jq -n \
  --argjson eid "$MAX_EVENT_ID" \
  --arg ts "$TIMESTAMP" \
  '{last_event_id: $eid, timestamp: $ts}' \
  > "$CURSOR_FILE"

echo "" >&2
echo "Cursor updated to event ID: $MAX_EVENT_ID" >&2

# --- 7. Output structured result ---
echo "$SUMMARY" | jq --argjson total "$NEW_COUNT" --argjson cursor "$MAX_EVENT_ID" \
  '. + {total_events: $total, cursor: $cursor}'
