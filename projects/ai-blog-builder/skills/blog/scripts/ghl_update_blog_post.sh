#!/usr/bin/env bash
# ghl_update_blog_post.sh — Update an existing blog post in GHL
# Usage:
#   ./ghl_update_blog_post.sh \
#     --post-id "POST_ID" \
#     [--title "New Title"] \
#     [--content-file "path/to/content.html"] \
#     [--status "PUBLISHED"] \
#     [--category-id "CAT_ID"] \
#     [--author "Author Name"] \
#     [--slug "new-slug"] \
#     [--image-url "https://..."] \
#     [--image-alt "Alt text"] \
#     [--meta-title "SEO Title"] \
#     [--meta-description "SEO Description"] \
#     [--tags "tag1,tag2,tag3"] \
#     [--location ces]
#
# Only provided fields are updated. Omitted fields remain unchanged.
# Output: JSON response with updated post details

set -euo pipefail

API_BASE="https://services.leadconnectorhq.com"

: "${GHL_API_KEY:?Error: GHL_API_KEY is not set}"
: "${GHL_VERSION:=2021-07-28}"

POST_ID=""
TITLE=""
CONTENT_FILE=""
STATUS=""
CATEGORY_ID=""
AUTHOR=""
SLUG=""
IMAGE_URL=""
IMAGE_ALT=""
META_TITLE=""
META_DESC=""
TAGS=""
LOCATION_FLAG=""
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --post-id)          POST_ID="$2"; shift 2 ;;
    --title)            TITLE="$2"; shift 2 ;;
    --content-file)     CONTENT_FILE="$2"; shift 2 ;;
    --status)           STATUS="$2"; shift 2 ;;
    --category-id)      CATEGORY_ID="$2"; shift 2 ;;
    --author)           AUTHOR="$2"; shift 2 ;;
    --slug)             SLUG="$2"; shift 2 ;;
    --image-url)        IMAGE_URL="$2"; shift 2 ;;
    --image-alt)        IMAGE_ALT="$2"; shift 2 ;;
    --meta-title)       META_TITLE="$2"; shift 2 ;;
    --meta-description) META_DESC="$2"; shift 2 ;;
    --tags)             TAGS="$2"; shift 2 ;;
    --location)         LOCATION_FLAG="$2"; shift 2 ;;
    *)                  echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$POST_ID" ]]; then
  echo "Error: --post-id is required" >&2
  exit 1
fi

# Resolve location
if [[ -n "$LOCATION_FLAG" ]]; then
  GHL_LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh" --location "$LOCATION_FLAG")
else
  GHL_LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh")
fi

# Read content from file if provided
CONTENT=""
if [[ -n "$CONTENT_FILE" ]]; then
  if [[ ! -f "$CONTENT_FILE" ]]; then
    echo "Error: Content file not found: $CONTENT_FILE" >&2
    exit 1
  fi
  CONTENT=$(cat "$CONTENT_FILE")
fi

# Build JSON payload (only include non-empty fields)
JSON_PAYLOAD=$(jq -n \
  --arg title "$TITLE" \
  --arg content "$CONTENT" \
  --arg status "$STATUS" \
  --arg categoryId "$CATEGORY_ID" \
  --arg author "$AUTHOR" \
  --arg slug "$SLUG" \
  --arg imageUrl "$IMAGE_URL" \
  --arg imageAlt "$IMAGE_ALT" \
  --arg metaTitle "$META_TITLE" \
  --arg metaDesc "$META_DESC" \
  --arg tags "$TAGS" \
  '{}
  + (if $title != "" then {title: $title} else {} end)
  + (if $content != "" then {content: $content} else {} end)
  + (if $status != "" then {status: $status} else {} end)
  + (if $categoryId != "" then {categoryId: $categoryId} else {} end)
  + (if $author != "" then {author: $author} else {} end)
  + (if $slug != "" then {urlSlug: $slug} else {} end)
  + (if $imageUrl != "" then {imageUrl: $imageUrl} else {} end)
  + (if $imageAlt != "" then {imageAltText: $imageAlt} else {} end)
  + (if $metaTitle != "" then {metaTitle: $metaTitle} else {} end)
  + (if $metaDesc != "" then {metaDescription: $metaDesc} else {} end)
  + (if $tags != "" then {tags: ($tags | split(",") | map(gsub("^\\s+|\\s+$"; "")))} else {} end)
  ')

echo "Updating blog post: $POST_ID" >&2

curl -s -X PUT "$API_BASE/blogs/posts/$POST_ID" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "$JSON_PAYLOAD"
