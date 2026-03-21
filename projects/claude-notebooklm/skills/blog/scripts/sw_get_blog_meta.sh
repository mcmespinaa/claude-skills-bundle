#!/usr/bin/env bash
# sw_get_blog_meta.sh — Fetch ShopWired blog metadata (categories, tags, posts).
#
# Usage:
#   ./sw_get_blog_meta.sh --action categories --location ces
#   ./sw_get_blog_meta.sh --action tags --location ces
#   ./sw_get_blog_meta.sh --action posts --location ces [--count 10]
#   ./sw_get_blog_meta.sh --action count --location ces
#
# Output: JSON to stdout. Progress to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/skills/shopwired-sync/scripts/sw_api.sh"

ACTION=""
COUNT=50

while [[ ${#SCRIPT_ARGS[@]+"${#SCRIPT_ARGS[@]}"} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --action) ACTION="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --count)  COUNT="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    *)        echo "Unknown arg: ${SCRIPT_ARGS[0]}" >&2; exit 1 ;;
  esac
done

if [[ -z "$ACTION" ]]; then
  echo "Error: --action is required (categories, tags, posts, count)" >&2
  exit 1
fi

case "$ACTION" in
  categories)
    echo "Fetching ShopWired blog categories..." >&2
    RESULT=$(sw_get "/blog-categories?count=100")
    CAT_COUNT=$(echo "$RESULT" | jq 'if type == "array" then length else 0 end')
    echo "Found $CAT_COUNT categories" >&2
    echo "$RESULT" | jq '[.[]? | {id: .id, title: .title, slug: .slug}]'
    ;;

  tags)
    echo "Fetching ShopWired blog tags..." >&2
    RESULT=$(sw_get "/blog-tags?count=100")
    TAG_COUNT=$(echo "$RESULT" | jq 'if type == "array" then length else 0 end')
    echo "Found $TAG_COUNT tags" >&2
    echo "$RESULT" | jq '[.[]? | {id: .id, title: .title, slug: .slug}]'
    ;;

  posts)
    echo "Fetching ShopWired blog posts..." >&2
    RESULT=$(sw_get "/blog-posts?count=${COUNT}&sort=created_desc&embed=category,tags")
    POST_COUNT=$(echo "$RESULT" | jq 'if type == "array" then length else 0 end')
    echo "Found $POST_COUNT posts" >&2
    echo "$RESULT" | jq '[.[]? | {id: .id, title: .title, slug: .slug, url: .url, active: .active, createdAt: .createdAt}]'
    ;;

  count)
    echo "Fetching ShopWired blog post count..." >&2
    RESULT=$(sw_get "/blog-posts/count")
    echo "$RESULT"
    ;;

  *)
    echo "Error: Unknown action '$ACTION'. Use: categories, tags, posts, count" >&2
    exit 1
    ;;
esac
