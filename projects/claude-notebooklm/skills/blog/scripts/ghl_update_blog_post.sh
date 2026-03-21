#!/usr/bin/env bash
# ghl_update_blog_post.sh — Update an existing blog post via the GHL Blog API.
#
# Usage:
#   ./ghl_update_blog_post.sh \
#     --post-id "66c381b38be80858b9af62b6" \
#     --title "Updated Title" \
#     --blog-id "abc123" \
#     --description "Updated meta description" \
#     --html-file "/tmp/blog.html" \
#     --status "PUBLISHED" \
#     --image-url "https://..." \
#     --image-alt "Alt text" \
#     --slug "updated-slug" \
#     --author "author_id" \
#     --categories "cat1,cat2" \
#     --tags "tag1,tag2" \
#     --published-at "2026-03-10T09:00:00.000Z" \
#     --location ces
#
# Output: JSON response with updated blog post data to stdout.
#         Progress/errors go to stderr.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CLAUDE_PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}/scripts/init.sh" "$@"

API_BASE="https://services.leadconnectorhq.com"

POST_ID=""
TITLE=""
BLOG_ID=""
DESCRIPTION=""
HTML=""
HTML_FILE=""
STATUS=""
IMAGE_URL=""
IMAGE_ALT=""
SLUG=""
AUTHOR=""
CATEGORIES=""
TAGS=""
PUBLISHED_AT=""
CANONICAL_LINK=""

while [[ ${#SCRIPT_ARGS[@]} -gt 0 ]]; do
  case "${SCRIPT_ARGS[0]}" in
    --post-id)      POST_ID="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --title)        TITLE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --blog-id)      BLOG_ID="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --description)  DESCRIPTION="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --html)         HTML="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --html-file)    HTML_FILE="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --status)       STATUS="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --image-url)    IMAGE_URL="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --image-alt)    IMAGE_ALT="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --slug)         SLUG="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --author)       AUTHOR="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --categories)   CATEGORIES="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --tags)         TAGS="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --published-at) PUBLISHED_AT="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    --canonical)    CANONICAL_LINK="${SCRIPT_ARGS[1]}"; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:2}") ;;
    *)              echo "Unknown arg: ${SCRIPT_ARGS[0]}" >&2; SCRIPT_ARGS=("${SCRIPT_ARGS[@]:1}") ;;
  esac
done

# Validate required fields
for field in POST_ID TITLE BLOG_ID DESCRIPTION STATUS IMAGE_URL IMAGE_ALT SLUG AUTHOR; do
  if [[ -z "${!field}" ]]; then
    echo "Error: --$(echo "$field" | tr '[:upper:]' '[:lower:]' | tr '_' '-') is required" >&2
    exit 1
  fi
done

# Read HTML from file if provided
if [[ -n "$HTML_FILE" ]]; then
  if [[ ! -f "$HTML_FILE" ]]; then
    echo "Error: HTML file not found: $HTML_FILE" >&2
    exit 1
  fi
  HTML=$(cat "$HTML_FILE")
elif [[ -z "$HTML" ]]; then
  echo "Error: --html or --html-file is required" >&2
  exit 1
fi

# Default publishedAt to now if not provided
if [[ -z "$PUBLISHED_AT" ]]; then
  PUBLISHED_AT=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
fi

# Build categories JSON array
if [[ -n "$CATEGORIES" ]]; then
  CATEGORIES_JSON=$(echo "$CATEGORIES" | tr ',' '\n' | jq -R . | jq -s .)
else
  CATEGORIES_JSON="[]"
fi

# Build tags JSON array
if [[ -n "$TAGS" ]]; then
  TAGS_JSON=$(echo "$TAGS" | tr ',' '\n' | jq -R . | jq -s .)
else
  TAGS_JSON="[]"
fi

# Build the JSON payload
PAYLOAD=$(jq -n \
  --arg title "$TITLE" \
  --arg locationId "$GHL_LOCATION_ID" \
  --arg blogId "$BLOG_ID" \
  --arg imageUrl "$IMAGE_URL" \
  --arg description "$DESCRIPTION" \
  --arg rawHTML "$HTML" \
  --arg status "$STATUS" \
  --arg imageAltText "$IMAGE_ALT" \
  --argjson categories "$CATEGORIES_JSON" \
  --argjson tags "$TAGS_JSON" \
  --arg author "$AUTHOR" \
  --arg urlSlug "$SLUG" \
  --arg publishedAt "$PUBLISHED_AT" \
  '{
    title: $title,
    locationId: $locationId,
    blogId: $blogId,
    imageUrl: $imageUrl,
    description: $description,
    rawHTML: $rawHTML,
    status: $status,
    imageAltText: $imageAltText,
    categories: $categories,
    tags: $tags,
    author: $author,
    urlSlug: $urlSlug,
    publishedAt: $publishedAt
  }')

if [[ -n "$CANONICAL_LINK" ]]; then
  PAYLOAD=$(echo "$PAYLOAD" | jq --arg cl "$CANONICAL_LINK" '. + {canonicalLink: $cl}')
fi

echo "Updating blog post: $POST_ID" >&2
echo "Title: $TITLE | Status: $STATUS | Location: $LOCATION_KEY" >&2

RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT \
  "$API_BASE/blogs/posts/$POST_ID" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
  echo "Blog post updated successfully (HTTP $HTTP_CODE)" >&2
  echo "$BODY"
else
  echo "Error updating blog post (HTTP $HTTP_CODE):" >&2
  echo "$BODY" >&2
  exit 1
fi
