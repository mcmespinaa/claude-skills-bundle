#!/usr/bin/env bash
# sw_update_blog_post.sh — Update an existing ShopWired blog post.
#
# Usage:
#   ./sw_update_blog_post.sh \
#     --post-id 123 \
#     --title "Updated Title" \
#     --slug "updated-slug" \
#     --html-file "/tmp/blog.html" \
#     --meta-title "New SEO Title" \
#     --meta-description "Updated desc" \
#     --active true \
#     --location ces
#
# Output: JSON response to stdout. Progress/errors to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/skills/shopwired-sync/scripts/sw_api.sh"

POST_ID=""
TITLE=""
SLUG=""
HTML=""
HTML_FILE=""
META_TITLE=""
META_DESC=""
META_KEYWORDS=""
IMAGE_URL=""
EXCERPT=""
CATEGORY_ID=""
TAGS=""
ACTIVE=""
RELEASE_DATE=""

while [[ ${#SCRIPT_ARGS[@]+"${#SCRIPT_ARGS[@]}"} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --post-id)          POST_ID="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --title)            TITLE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --slug)             SLUG="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --html)             HTML="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --html-file)        HTML_FILE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --meta-title)       META_TITLE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --meta-description) META_DESC="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --meta-keywords)    META_KEYWORDS="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --image-url)        IMAGE_URL="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --excerpt)          EXCERPT="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --category-id)      CATEGORY_ID="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --tags)             TAGS="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --active)           ACTIVE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --release-date)     RELEASE_DATE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    *)                  echo "Unknown arg: ${SCRIPT_ARGS[0]}" >&2; exit 1 ;;
  esac
done

if [[ -z "$POST_ID" ]]; then echo "Error: --post-id is required" >&2; exit 1; fi

# Read HTML from file if provided
if [[ -n "$HTML_FILE" ]]; then
  if [[ ! -f "$HTML_FILE" ]]; then
    echo "Error: HTML file not found: $HTML_FILE" >&2
    exit 1
  fi
  HTML=$(cat "$HTML_FILE")
fi

# Build payload with only provided fields
PAYLOAD=$(python3 -c "
import json, sys

payload = {}

html = sys.stdin.read().strip()
if html:
    payload['content'] = html

title = '$TITLE'
if title: payload['title'] = title

slug = '$SLUG'
if slug: payload['slug'] = slug

active = '$ACTIVE'
if active: payload['active'] = active.lower() in ('true', '1', 'yes')

meta_title = '$META_TITLE'
if meta_title: payload['metaTitle'] = meta_title

meta_desc = '$META_DESC'
if meta_desc: payload['metaDescription'] = meta_desc

meta_kw = '$META_KEYWORDS'
if meta_kw: payload['metaKeywords'] = meta_kw

image = '$IMAGE_URL'
if image: payload['image'] = image

excerpt = '$EXCERPT'
if excerpt: payload['excerpt'] = excerpt

cat_id = '$CATEGORY_ID'
if cat_id: payload['categoryId'] = int(cat_id)

tags = '$TAGS'
if tags: payload['tags'] = tags

release = '$RELEASE_DATE'
if release: payload['releaseDate'] = release

print(json.dumps(payload))
" <<< "$HTML")

echo "Updating ShopWired blog post ID: $POST_ID" >&2

RESULT=$(sw_put "/blog-posts/${POST_ID}" "$PAYLOAD")

echo "Blog post updated successfully" >&2
echo "$RESULT"
