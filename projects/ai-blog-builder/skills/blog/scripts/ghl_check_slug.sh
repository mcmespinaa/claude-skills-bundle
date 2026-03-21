#!/usr/bin/env bash
# ghl_check_slug.sh — Validate a blog post URL slug in GHL
# Usage: ./ghl_check_slug.sh --blog-id "BLOG_ID" --slug "my-post-slug" [--location ces]

set -euo pipefail

API_BASE="https://services.leadconnectorhq.com"
: "${GHL_API_KEY:?Error: GHL_API_KEY is not set}"
: "${GHL_VERSION:=2021-07-28}"

BLOG_ID=""
SLUG=""
POST_ID=""
LOCATION_FLAG=""
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --blog-id)   BLOG_ID="$2"; shift 2 ;;
    --slug)      SLUG="$2"; shift 2 ;;
    --post-id)   POST_ID="$2"; shift 2 ;;
    --location)  LOCATION_FLAG="$2"; shift 2 ;;
    *)           echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$BLOG_ID" ]]; then
  echo "Error: --blog-id is required" >&2
  exit 1
fi
if [[ -z "$SLUG" ]]; then
  echo "Error: --slug is required" >&2
  exit 1
fi

if [[ -n "$LOCATION_FLAG" ]]; then
  GHL_LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh" --location "$LOCATION_FLAG")
else
  GHL_LOCATION_ID=$(bash "$SCRIPT_DIR/resolve_location.sh")
fi

echo "Checking slug availability: $SLUG" >&2

QUERY_URL="$API_BASE/blogs/posts/url-slug-exists?locationId=$GHL_LOCATION_ID&urlSlug=$SLUG"
if [[ -n "$POST_ID" ]]; then
  QUERY_URL="$QUERY_URL&postId=$POST_ID"
fi

curl -s -X GET "$QUERY_URL" \
  -H "Authorization: Bearer $GHL_API_KEY" \
  -H "Version: $GHL_VERSION" \
  -H "Accept: application/json"
