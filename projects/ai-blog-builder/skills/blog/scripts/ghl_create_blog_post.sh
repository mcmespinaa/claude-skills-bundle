#!/usr/bin/env bash
# ghl_create_blog_post.sh — Create a new blog post in GHL
# Usage:
#   ./ghl_create_blog_post.sh \
#     --blog-id "BLOG_ID" \
#     --title "Post Title" \
#     --content-file "path/to/content.html" \
#     --status "DRAFT" \
#     [--category-id "CAT_ID"] \
#     [--author "Author Name"] \
#     [--slug "custom-slug"] \
#     [--image-url "https://..."] \
#     [--image-alt "Alt text"] \
#     [--meta-title "SEO Title"] \
#     [--meta-description "SEO Description"] \
#     [--tags "tag1,tag2,tag3"] \
#     [--location ces]
#
# Status options: DRAFT, PUBLISHED, SCHEDULED, ARCHIVED
# Output: JSON response with created post details

set -euo pipefail

API_BASE="https://services.leadconnectorhq.com"

: "${GHL_API_KEY:?Error: GHL_API_KEY is not set}"
: "${GHL_VERSION:=2021-07-28}"

BLOG_ID=""
TITLE=""
CONTENT_FILE=""
STATUS="DRAFT"
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
    --blog-id)          BLOG_ID="$2"; shift 2 ;;
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

# Validate required fields
if [[ -z "$BLOG_ID" ]]; then
  echo "Error: --blog-id is required. Run ghl_get_blogs.sh to list available blogs." >&2
  exit 1
fi
if [[ -z "$TITLE" ]]; then
  echo "Error: --title is required" >&2
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

# Build JSON payload
JSON_PAYLOAD=$(jq -n \
  --arg blogId "$BLOG_ID" \
  --arg title "$TITLE" \
  --arg rawHTML "$CONTENT" \
  --arg status "$STATUS" \
  --arg locationId "$GHL_LOCATION_ID" \
  --arg author "$AUTHOR" \
  --arg slug "$SLUG" \
  --arg imageUrl "$IMAGE_URL" \
  --arg imageAlt "$IMAGE_ALT" \
  --arg description "$META_DESC" \
  --arg tags "$TAGS" \
  --arg categoryId "$CATEGORY_ID" \
  '{
    blogId: $blogId,
    title: $title,
    status: $status,
    locationId: $locationId
  }
  + (if $rawHTML != "" then {rawHTML: $rawHTML} else {} end)
  + (if $author != "" then {author: $author} else {} end)
  + (if $slug != "" then {urlSlug: $slug} else {} end)
  + (if $imageUrl != "" then {imageUrl: $imageUrl} else {} end)
  + (if $imageAlt != "" then {imageAltText: $imageAlt} else {} end)
  + (if $description != "" then {description: $description} else {} end)
  + (if $categoryId != "" then {categories: [$categoryId]} else {} end)
  + (if $tags != "" then {tags: ($tags | split(",") | map(gsub("^\\s+|\\s+$"; "")))} else {} end)
  ')

echo "Creating blog post: $TITLE" >&2
echo "Status: $STATUS | Blog: $BLOG_ID | Location: $GHL_LOCATION_ID" >&2

curl -s -X POST "$API_BASE/blogs/posts" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "$JSON_PAYLOAD"
