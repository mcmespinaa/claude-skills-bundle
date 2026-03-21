#!/usr/bin/env bash
# ghl_create_blog.sh — Create/publish a blog post via GHL Blog API
# Usage:
#   ./ghl_create_blog.sh --blog-id <id> --title "Title" --content-file blog.html \
#     --description "Meta description" --tags "tag1,tag2" \
#     --status DRAFT [--publish-at "2026-03-25T09:00:00Z"] [--location ces]
#
# GHL Blog API field reference (verified 2026-03-10):
#   Required: blogId, locationId, title, status (DRAFT|PUBLISHED|SCHEDULED)
#   Optional: rawHTML, description, tags (string[]), imageUrl, publishedAt
#   NOT valid: content, metaDescription, slug, category, author (string), featuredImage

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_BASE="https://services.leadconnectorhq.com"

: "${GHL_API_KEY:?Error: GHL_API_KEY is not set}"
: "${GHL_VERSION:=2021-07-28}"

BLOG_ID=""
TITLE=""
CONTENT_FILE=""
DESCRIPTION=""
TAGS=""
IMAGE_URL=""
STATUS="DRAFT"
PUBLISH_AT=""
LOCATION_FLAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --blog-id)           BLOG_ID="$2"; shift 2 ;;
    --title)             TITLE="$2"; shift 2 ;;
    --content-file)      CONTENT_FILE="$2"; shift 2 ;;
    --description)       DESCRIPTION="$2"; shift 2 ;;
    --meta-description)  DESCRIPTION="$2"; shift 2 ;;  # backward compat alias
    --tags)              TAGS="$2"; shift 2 ;;
    --image-url)         IMAGE_URL="$2"; shift 2 ;;
    --featured-image)    IMAGE_URL="$2"; shift 2 ;;    # backward compat alias
    --status)            STATUS="$2"; shift 2 ;;
    --publish-at)        PUBLISH_AT="$2"; shift 2 ;;
    --location)          LOCATION_FLAG="$2"; shift 2 ;;
    # Deprecated flags (ignored with warning)
    --url-slug|--category|--author)
      echo "Warning: $1 is not supported by GHL Blog API, ignoring" >&2; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# Normalize status to uppercase
STATUS=$(echo "$STATUS" | tr '[:lower:]' '[:upper:]')

# Validate required fields
[[ -z "$BLOG_ID" ]] && { echo "Error: --blog-id required" >&2; exit 1; }
[[ -z "$TITLE" ]] && { echo "Error: --title required" >&2; exit 1; }

# Resolve location (shared script, with fallback to legacy path)
RESOLVE_SCRIPT=""
for candidate in \
  "$SCRIPT_DIR/../../../shared/scripts/resolve_location.sh" \
  "$SCRIPT_DIR/../../post/scripts/resolve_location.sh"; do
  if [[ -f "$candidate" ]]; then
    RESOLVE_SCRIPT="$candidate"
    break
  fi
done

if [[ -z "$RESOLVE_SCRIPT" ]]; then
  if [[ -n "${GHL_LOCATION_ID:-}" ]]; then
    echo "Warning: resolve_location.sh not found, using GHL_LOCATION_ID env var" >&2
  else
    echo "Error: resolve_location.sh not found and GHL_LOCATION_ID not set" >&2
    exit 1
  fi
elif [[ -n "$LOCATION_FLAG" ]]; then
  GHL_LOCATION_ID=$(bash "$RESOLVE_SCRIPT" --location "$LOCATION_FLAG")
else
  GHL_LOCATION_ID=$(bash "$RESOLVE_SCRIPT")
fi

# Read content file (if provided)
RAW_HTML=""
if [[ -n "$CONTENT_FILE" ]]; then
  [[ ! -f "$CONTENT_FILE" ]] && { echo "Error: Content file not found: $CONTENT_FILE" >&2; exit 1; }
  RAW_HTML=$(cat "$CONTENT_FILE")
fi

# Build tags array
if [[ -n "$TAGS" ]]; then
  IFS=',' read -ra TAG_ARRAY <<< "$TAGS"
  TAGS_JSON=$(printf '%s\n' "${TAG_ARRAY[@]}" | jq -R . | jq -s .)
else
  TAGS_JSON="[]"
fi

# Build payload with only valid GHL Blog API fields
PAYLOAD=$(jq -n \
  --arg blogId "$BLOG_ID" \
  --arg locationId "$GHL_LOCATION_ID" \
  --arg title "$TITLE" \
  --arg rawHTML "$RAW_HTML" \
  --arg description "$DESCRIPTION" \
  --arg imageUrl "$IMAGE_URL" \
  --arg status "$STATUS" \
  --arg publishedAt "$PUBLISH_AT" \
  --argjson tags "$TAGS_JSON" \
  '{
    blogId: $blogId,
    locationId: $locationId,
    title: $title,
    status: $status,
    tags: $tags
  }
  + if $rawHTML != "" then {rawHTML: $rawHTML} else {} end
  + if $description != "" then {description: $description} else {} end
  + if $imageUrl != "" then {imageUrl: $imageUrl} else {} end
  + if $publishedAt != "" then {publishedAt: $publishedAt} else {} end')

echo "Creating blog post: $TITLE"
echo "Status: $STATUS"
if [[ -n "$PUBLISH_AT" ]]; then
  echo "Scheduled for: $PUBLISH_AT"
fi

# Create blog post with retry on 429
MAX_RETRIES=2
ATTEMPT=0

while true; do
  RESPONSE=$(curl -s --max-time 30 -w "\nHTTP_STATUS:%{http_code}" -X POST \
    "${API_BASE}/blogs/posts" \
    -H "Authorization: Bearer ${GHL_API_KEY}" \
    -H "Version: ${GHL_VERSION}" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

  HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
  BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')

  if [[ "$HTTP_STATUS" == "429" ]] && [[ $ATTEMPT -lt $MAX_RETRIES ]]; then
    ATTEMPT=$((ATTEMPT + 1))
    WAIT=$((5 + 2 ** ATTEMPT))
    echo "Rate limited (429). Waiting ${WAIT}s (retry $ATTEMPT/$MAX_RETRIES)..." >&2
    sleep "$WAIT"
    continue
  fi
  break
done

if [[ "$HTTP_STATUS" == "401" ]]; then
  echo "Error: Authentication failed (401). Update GHL_API_KEY." >&2
  echo "$BODY" >&2
  exit 1
fi

echo "$BODY" | jq .

# Check for success (GHL returns blogPost object on success, not {success: true})
if echo "$BODY" | jq -e '.blogPost._id' > /dev/null 2>&1; then
  POST_ID=$(echo "$BODY" | jq -r '.blogPost._id')
  URL_SLUG=$(echo "$BODY" | jq -r '.blogPost.urlSlug // "unknown"')
  echo ""
  echo "Blog post created"
  echo "Post ID: $POST_ID"
  echo "URL slug: $URL_SLUG"
else
  echo ""
  echo "Blog post creation failed (HTTP $HTTP_STATUS)"
  echo "$BODY" >&2
  exit 1
fi
