#!/usr/bin/env bash
# sw_create_blog_post.sh — Create a blog post via the ShopWired Blog API.
#
# Usage:
#   ./sw_create_blog_post.sh \
#     --title "My Blog Post" \
#     --slug "my-blog-post" \
#     --html-file "/tmp/blog.html" \
#     --meta-title "SEO Title" \
#     --meta-description "Meta description" \
#     --meta-keywords "keyword1, keyword2" \
#     --image-url "https://..." \
#     --excerpt "Short summary" \
#     --category-id 5 \
#     --tags "tag1,tag2,tag3" \
#     --active true \
#     --release-date "2026-03-10T09:00:00Z" \
#     --location ces
#
# Output: JSON response to stdout. Progress/errors to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/skills/shopwired-sync/scripts/sw_api.sh"

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
CATEGORY_TITLE=""
TAGS=""
ACTIVE="false"
RELEASE_DATE=""
CUSTOM_URL=""

while [[ ${#SCRIPT_ARGS[@]+"${#SCRIPT_ARGS[@]}"} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
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
    --category-title)   CATEGORY_TITLE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --tags)             TAGS="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --active)           ACTIVE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --release-date)     RELEASE_DATE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --custom-url)       CUSTOM_URL="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    *)                  echo "Unknown arg: ${SCRIPT_ARGS[0]}" >&2; exit 1 ;;
  esac
done

# Validate required fields
if [[ -z "$TITLE" ]]; then echo "Error: --title is required" >&2; exit 1; fi
if [[ -z "$SLUG" ]]; then echo "Error: --slug is required" >&2; exit 1; fi

# Read HTML from file if provided
if [[ -n "$HTML_FILE" ]]; then
  if [[ ! -f "$HTML_FILE" ]]; then
    echo "Error: HTML file not found: $HTML_FILE" >&2
    exit 1
  fi
  HTML=$(cat "$HTML_FILE")
fi

# Build JSON payload using python for safe string escaping
PAYLOAD=$(python3 -c "
import json, sys

payload = {
    'title': '$TITLE',
    'slug': '$SLUG',
}

# Read HTML from stdin if provided
html = sys.stdin.read().strip()
if html:
    payload['content'] = html

active = '$ACTIVE'
payload['active'] = active.lower() in ('true', '1', 'yes')

meta_title = '$META_TITLE'
if meta_title:
    payload['metaTitle'] = meta_title

meta_desc = '$META_DESC'
if meta_desc:
    payload['metaDescription'] = meta_desc

meta_kw = '$META_KEYWORDS'
if meta_kw:
    payload['metaKeywords'] = meta_kw

image = '$IMAGE_URL'
if image:
    payload['image'] = image

excerpt = '$EXCERPT'
if excerpt:
    payload['excerpt'] = excerpt

cat_id = '$CATEGORY_ID'
if cat_id:
    payload['categoryId'] = int(cat_id)

cat_title = '$CATEGORY_TITLE'
if cat_title:
    payload['categoryTitle'] = cat_title

tags = '$TAGS'
if tags:
    payload['tags'] = tags

release = '$RELEASE_DATE'
if release:
    payload['releaseDate'] = release

custom_url = '$CUSTOM_URL'
if custom_url:
    payload['customUrl'] = custom_url

print(json.dumps(payload))
" <<< "$HTML")

echo "Creating ShopWired blog post: $TITLE" >&2
echo "Slug: $SLUG | Active: $ACTIVE | Location: $LOCATION_KEY" >&2

RESULT=$(sw_post "/blog-posts" "$PAYLOAD")

POST_ID=$(echo "$RESULT" | jq -r '.id // empty')
POST_URL=$(echo "$RESULT" | jq -r '.url // empty')

if [[ -n "$POST_ID" ]]; then
  echo "Blog post created successfully (ID: $POST_ID)" >&2
  if [[ -n "$POST_URL" ]]; then
    echo "URL: $POST_URL" >&2
  fi
  echo "$RESULT"
else
  echo "Error: Unexpected response" >&2
  echo "$RESULT" >&2
  exit 1
fi
