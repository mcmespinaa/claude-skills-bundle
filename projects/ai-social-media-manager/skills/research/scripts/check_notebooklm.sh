#!/usr/bin/env bash
# check_notebooklm.sh — Verify NotebookLM CLI is installed and authenticated.
#
# Usage:
#   bash .claude/skills/research/scripts/check_notebooklm.sh
#
# Exit codes:
#   0 — CLI installed and authenticated
#   1 — CLI not installed
#   2 — CLI installed but not authenticated

set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  echo "Usage: bash check_notebooklm.sh"
  echo ""
  echo "Verify NotebookLM CLI is installed and authenticated."
  echo ""
  echo "Exit codes:"
  echo "  0 — CLI installed and authenticated"
  echo "  1 — CLI not installed"
  echo "  2 — CLI installed but not authenticated"
  exit 0
fi

# Check if notebooklm CLI is installed
if ! command -v notebooklm &>/dev/null; then
  echo "ERROR: notebooklm CLI not found." >&2
  echo "Install with: pip install notebooklm-py && notebooklm skill install && notebooklm login" >&2
  exit 1
fi

VERSION=$(notebooklm --version 2>&1 || true)
echo "CLI: $VERSION"

# Check authentication
STATUS=$(notebooklm status 2>&1 || true)
if echo "$STATUS" | grep -qi "authenticated"; then
  echo "Auth: OK"
  echo "$STATUS"
  exit 0
else
  echo "ERROR: Not authenticated." >&2
  echo "Run: notebooklm login" >&2
  echo "$STATUS" >&2
  exit 2
fi
