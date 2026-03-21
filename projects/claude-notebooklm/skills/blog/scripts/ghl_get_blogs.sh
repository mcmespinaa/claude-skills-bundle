#!/usr/bin/env bash
# ghl_get_blogs.sh — Query GHL Blog API for sites, categories, authors, posts, and slug checks.
#
# Usage:
#   ./ghl_get_blogs.sh --action sites --location ces
#   ./ghl_get_blogs.sh --action categories --location ces
#   ./ghl_get_blogs.sh --action authors --location ces
#   ./ghl_get_blogs.sh --action posts --blog-id "abc123" --location ces
#   ./ghl_get_blogs.sh --action check-slug --slug "my-post" --location ces
#
# Output: JSON response to stdout. Progress/errors to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"

API_BASE="https://services.leadconnectorhq.com"

ACTION=""
BLOG_ID=""
SLUG=""
POST_ID=""
LIMIT="10"
OFFSET="0"

while [[ ${#SCRIPT_ARGS[@]} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --action)   ACTION="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --blog-id)  BLOG_ID="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --slug)     SLUG="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --post-id)  POST_ID="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --limit)    LIMIT="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --offset)   OFFSET="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    *)          echo "Unknown arg: ${SCRIPT_ARGS[0]}" >&2; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:1}") ;;
  esac
done

if [[ -z "$ACTION" ]]; then
  echo "Error: --action is required (sites|categories|authors|posts|check-slug)" >&2
  exit 1
fi

make_request() {
  local url="$1"
  local label="$2"

  echo "Fetching $label for location $LOCATION_KEY..." >&2

  RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
    "$url" \
    -H "Authorization: Bearer $GHL_API_KEY" \
    -H "Version: $GHL_VERSION" \
    -H "Content-Type: application/json")

  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  BODY=$(echo "$RESPONSE" | sed '$d')

  if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
    echo "$BODY"
  else
    echo "Error fetching $label (HTTP $HTTP_CODE):" >&2
    echo "$BODY" >&2
    exit 1
  fi
}

case "$ACTION" in
  sites)
    make_request \
      "$API_BASE/blogs/site/all?locationId=$GHL_LOCATION_ID" \
      "blog sites"
    ;;
  categories)
    make_request \
      "$API_BASE/blogs/categories?locationId=$GHL_LOCATION_ID&limit=$LIMIT&offset=$OFFSET" \
      "categories"
    ;;
  authors)
    make_request \
      "$API_BASE/blogs/authors?locationId=$GHL_LOCATION_ID&limit=$LIMIT&offset=$OFFSET" \
      "authors"
    ;;
  posts)
    if [[ -z "$BLOG_ID" ]]; then
      echo "Error: --blog-id is required for action 'posts'" >&2
      exit 1
    fi
    make_request \
      "$API_BASE/blogs/posts/all?locationId=$GHL_LOCATION_ID&blogId=$BLOG_ID&limit=$LIMIT&offset=$OFFSET" \
      "blog posts"
    ;;
  check-slug)
    if [[ -z "$SLUG" ]]; then
      echo "Error: --slug is required for action 'check-slug'" >&2
      exit 1
    fi
    local_url="$API_BASE/blogs/posts/url-slug-exists?locationId=$GHL_LOCATION_ID&urlSlug=$SLUG"
    if [[ -n "$POST_ID" ]]; then
      local_url="$local_url&postId=$POST_ID"
    fi
    make_request "$local_url" "slug check"
    ;;
  *)
    echo "Error: Unknown action '$ACTION'. Use: sites|categories|authors|posts|check-slug" >&2
    exit 1
    ;;
esac
