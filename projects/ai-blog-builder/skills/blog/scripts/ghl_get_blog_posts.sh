#!/usr/bin/env bash
# ghl_get_blog_posts.sh — List posts for a specific blog
# Usage: ./ghl_get_blog_posts.sh --blog-id "BLOG_ID" [--location ces] [--limit 20] [--offset 0]

set -euo pipefail

API_BASE="https://services.leadconnectorhq.com"
: "${GHL_API_KEY:?Error: GHL_API_KEY is not set}"
: "${GHL_VERSION:=2021-07-28}"

BLOG_ID=""
LOCATION_FLAG=""
LIMIT=20
OFFSET=0
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --blog-id)   BLOG_ID="$2"; shift 2 ;;
    --location)  LOCATION_FLAG="$2"; shift 2 ;;
    --limit)     LIMIT="$2"; shift 2 ;;
    --offset)    OFFSET="$2"; shift 2 ;;
    *)           echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$BLOG_ID" ]]; then
  echo "Error: --blog-id is required. Run ghl_get_blogs.sh first." >&2
  exit 1
fi

echo "Fetching posts for blog: $BLOG_ID" >&2

curl -s -X GET "$API_BASE/blogs/$BLOG_ID/posts?limit=$LIMIT&offset=$OFFSET" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Accept: application/json"
