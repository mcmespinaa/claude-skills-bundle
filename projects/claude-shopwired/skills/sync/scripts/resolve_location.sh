#!/usr/bin/env bash
# resolve_location.sh — Resolve a location shorthand to config values.
#
# Usage:
#   LOCATION_ID=$(bash "$(dirname "$0")/resolve_location.sh" --location ces)
#   LOCATION_ID=$(bash "$(dirname "$0")/resolve_location.sh")   # uses default
#
# Resolution order:
#   1. --location <shorthand> -> lookup in locations.json
#   2. No --location -> use "default" key from locations.json
#   3. No locations.json -> fall back to $GHL_LOCATION_ID env var

set -euo pipefail

LOCATION_KEY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --location) LOCATION_KEY="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Find locations.json (walk up from script dir to project root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOCATIONS_FILE=""
CHECK_DIR="$SCRIPT_DIR"
for _ in 1 2 3 4 5 6; do
  if [[ -f "$CHECK_DIR/locations.json" ]]; then
    LOCATIONS_FILE="$CHECK_DIR/locations.json"
    break
  fi
  CHECK_DIR="$(dirname "$CHECK_DIR")"
done

if [[ -z "$LOCATIONS_FILE" ]]; then
  if [[ -n "${GHL_LOCATION_ID:-}" ]]; then
    echo "$GHL_LOCATION_ID"
    exit 0
  else
    echo "Error: No locations.json found and GHL_LOCATION_ID not set" >&2
    exit 1
  fi
fi

if [[ -z "$LOCATION_KEY" ]]; then
  LOCATION_KEY=$(jq -r '.default // empty' "$LOCATIONS_FILE")
  if [[ -z "$LOCATION_KEY" ]]; then
    if [[ -n "${GHL_LOCATION_ID:-}" ]]; then
      echo "$GHL_LOCATION_ID"
      exit 0
    else
      echo "Error: No default location in locations.json and GHL_LOCATION_ID not set" >&2
      exit 1
    fi
  fi
fi

LOCATION_ID=$(jq -r --arg key "$LOCATION_KEY" '.locations[$key].locationId // empty' "$LOCATIONS_FILE")

if [[ -z "$LOCATION_ID" ]]; then
  AVAILABLE=$(jq -r '.locations | keys | join(", ")' "$LOCATIONS_FILE")
  echo "Error: Location '$LOCATION_KEY' not found. Available: $AVAILABLE" >&2
  exit 1
fi

echo "$LOCATION_ID"
