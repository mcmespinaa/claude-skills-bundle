#!/usr/bin/env bash
# ghl_create_post.sh — Create/schedule a post via GHL Social Planner
# Usage:
#   Single image:
#     ./ghl_create_post.sh --account-id <id> --summary "caption" --scheduled-at "2026-02-20T10:00:00Z" --media-url <url> --user-id <locationId>
#   Carousel (comma-separated URLs):
#     ./ghl_create_post.sh --account-id <id> --summary "caption" --scheduled-at "2026-02-20T10:00:00Z" --media-url "url1,url2,url3" --user-id <locationId>
#   Text-only:
#     ./ghl_create_post.sh --account-id <id> --summary "caption" --scheduled-at "2026-02-20T10:00:00Z" --user-id <locationId>
#   Multi-location:
#     ./ghl_create_post.sh --location client_a --account-id <id> --summary "caption" --scheduled-at "..." --user-id <locationId>
# Note: --user-id is required by GHL API. Use the locationId as the userId for sub-account PIT tokens.
# Note: --media-type accepts MIME types: image/jpeg, image/png, video/mp4 (default: image/jpeg)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"

API_BASE="https://services.leadconnectorhq.com"

ACCOUNT_ID=""
SUMMARY=""
SCHEDULED_AT=""
MEDIA_URL=""
MEDIA_TYPE="image/jpeg"
TAGS=""
USER_ID="${USER_ID:-}"

while [[ ${#SCRIPT_ARGS[@]} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --account-id)   ACCOUNT_ID="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --summary)      SUMMARY="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --scheduled-at) SCHEDULED_AT="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --media-url)    MEDIA_URL="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --media-type)   MEDIA_TYPE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --tags)         TAGS="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --user-id)      USER_ID="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    *)              echo "Unknown arg: ${SCRIPT_ARGS[0]}"; exit 1 ;;
  esac
done

if [[ -z "$ACCOUNT_ID" || -z "$SUMMARY" || -z "$SCHEDULED_AT" ]]; then
  echo "Error: --account-id, --summary, and --scheduled-at are required" >&2
  exit 1
fi

# Build base payload
BASE_PAYLOAD=$(jq -n \
  --arg accountId "$ACCOUNT_ID" \
  --arg summary "$SUMMARY" \
  --arg scheduleDate "$SCHEDULED_AT" \
  '{
    accountIds: [$accountId],
    summary: $summary,
    status: "scheduled",
    scheduleDate: $scheduleDate,
    type: "post"
  }')

# Add userId if provided
if [[ -n "$USER_ID" ]]; then
  BASE_PAYLOAD=$(echo "$BASE_PAYLOAD" | jq --arg userId "$USER_ID" '. + { userId: $userId }')
fi

# Build media array (supports single URL or comma-separated URLs for carousels)
if [[ -n "$MEDIA_URL" ]]; then
  MEDIA_ARRAY="[]"
  IFS=',' read -ra URLS <<< "$MEDIA_URL"
  for url in ${URLS[@]+"${URLS[@]}"}; do
    url=$(echo "$url" | xargs) # trim whitespace
    MEDIA_ARRAY=$(echo "$MEDIA_ARRAY" | jq --arg u "$url" --arg t "$MEDIA_TYPE" '. + [{ url: $u, type: $t }]')
  done
  PAYLOAD=$(echo "$BASE_PAYLOAD" | jq --argjson media "$MEDIA_ARRAY" '. + { media: $media }')
else
  PAYLOAD=$(echo "$BASE_PAYLOAD" | jq '. + { media: [] }')
fi

# Add tags if provided
if [[ -n "$TAGS" ]]; then
  PAYLOAD=$(echo "$PAYLOAD" | jq --arg tags "$TAGS" '. + { tags: ($tags | split(",")) }')
fi

URL_COUNT=$(echo "$MEDIA_URL" | tr ',' '\n' | grep -c . || echo 0)
if [[ "$URL_COUNT" -gt 1 ]]; then
  echo "Creating carousel post ($URL_COUNT slides) for account $ACCOUNT_ID scheduled at $SCHEDULED_AT"
else
  echo "Creating post for account $ACCOUNT_ID scheduled at $SCHEDULED_AT"
fi

curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST \
  "$API_BASE/social-media-posting/$GHL_LOCATION_ID/posts" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"
