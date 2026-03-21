#!/usr/bin/env bash
# next_slot.sh — Calculate the next available 24h posting slot from the log
# Usage:
#   ./next_slot.sh [path/to/ghl_post_log.md]
#   ./next_slot.sh --log path/to/ghl_post_log.md [--location <name>]
# Output: ISO 8601 datetime for the next slot

set -euo pipefail

# Default to ghl_post_log.md in the user's working directory (project root)
LOG_FILE="${PWD}/ghl_post_log.md"
LOCATION_FILTER=""
DEFAULT_HOUR="10:00:00"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --log)
      LOG_FILE="$2"
      shift 2
      ;;
    --location)
      LOCATION_FILTER="$2"
      shift 2
      ;;
    *)
      # Backward compat: if positional arg, treat it as log file
      if [[ ! "$1" =~ ^-- ]]; then
        LOG_FILE="$1"
        shift
      else
        echo "Unknown arg: $1" >&2
        exit 1
      fi
      ;;
  esac
done

if [[ ! -f "$LOG_FILE" ]] || ! grep -qE '[0-9]{4}-[0-9]{2}-[0-9]{2}T' "$LOG_FILE" 2>/dev/null; then
  # No log or no timestamps — default to tomorrow at 10 AM UTC
  if command -v gdate &>/dev/null; then
    # macOS with GNU coreutils
    gdate -u -d "tomorrow $DEFAULT_HOUR" +%Y-%m-%dT%H:%M:%SZ
  else
    date -u -d "tomorrow $DEFAULT_HOUR" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
    date -u -v+1d -j -f "%H:%M:%S" "$DEFAULT_HOUR" +%Y-%m-%dT%H:%M:%SZ
  fi
  exit 0
fi

# Extract the most recent ISO timestamp from the log
# If --location provided, filter by location (case-insensitive)
if [[ -n "$LOCATION_FILTER" ]]; then
  LAST_TS=$(grep -iE "^\\| $LOCATION_FILTER " "$LOG_FILE" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z?' | sort | tail -1)
else
  LAST_TS=$(grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z?' "$LOG_FILE" | sort | tail -1)
fi

if [[ -z "$LAST_TS" ]]; then
  if command -v gdate &>/dev/null; then
    gdate -u -d "tomorrow $DEFAULT_HOUR" +%Y-%m-%dT%H:%M:%SZ
  else
    date -u -d "tomorrow $DEFAULT_HOUR" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
    date -u -v+1d -j -f "%H:%M:%S" "$DEFAULT_HOUR" +%Y-%m-%dT%H:%M:%SZ
  fi
  exit 0
fi

# Add 24 hours to the last timestamp
if command -v gdate &>/dev/null; then
  gdate -u -d "$LAST_TS + 24 hours" +%Y-%m-%dT%H:%M:%SZ
elif date -d "2000-01-01" &>/dev/null 2>&1; then
  # GNU date (Linux)
  date -u -d "$LAST_TS + 24 hours" +%Y-%m-%dT%H:%M:%SZ
else
  # BSD date (macOS) — parse and add 86400 seconds
  EPOCH=$(date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "$LAST_TS" +%s 2>/dev/null || \
          date -u -j -f "%Y-%m-%dT%H:%M:%S" "$LAST_TS" +%s)
  NEXT_EPOCH=$((EPOCH + 86400))
  date -u -r "$NEXT_EPOCH" +%Y-%m-%dT%H:%M:%SZ
fi
