#!/usr/bin/env bash
# firebase_deploy.sh — Deploy a static site to Firebase Hosting.
#
# Usage:
#   bash firebase_deploy.sh --project-dir /tmp/web-build/my-site \
#     --project-id psyched-runner-489120-r6 \
#     [--channel preview|live] [--site my-site] [--location ces]
#
# Prerequisites:
#   - firebase-tools: npm install -g firebase-tools
#   - Authenticated:  firebase login
#
# Output (stdout): JSON with hosting URL, channel, project.
# Errors go to stderr.

set -euo pipefail

# Source shared prelude if available
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../../.." && pwd)}"
if [[ -f "$PLUGIN_ROOT/scripts/init.sh" ]]; then
  source "$PLUGIN_ROOT/scripts/init.sh" "$@"
fi

# Defaults
PROJECT_DIR=""
GCP_PROJECT="${GCP_PROJECT_ID:-gen-lang-client-0715587042}"
CHANNEL="preview"
SITE=""

# Parse args (init.sh already consumed --location, remaining in SCRIPT_ARGS)
ARGS=("${SCRIPT_ARGS[@]+"${SCRIPT_ARGS[@]}"}")
while [[ ${#ARGS[@]} -gt 0 ]]; do
  case "${ARGS[0]}" in
    --project-dir) PROJECT_DIR="${ARGS[1]}"; ARGS=("${ARGS[@]:2}") ;;
    --project-id)  GCP_PROJECT="${ARGS[1]}"; ARGS=("${ARGS[@]:2}") ;;
    --channel)     CHANNEL="${ARGS[1]}"; ARGS=("${ARGS[@]:2}") ;;
    --site)        SITE="${ARGS[1]}"; ARGS=("${ARGS[@]:2}") ;;
    *) ARGS=("${ARGS[@]:1}") ;;
  esac
done

if [[ -z "$PROJECT_DIR" ]]; then
  echo "Error: --project-dir is required" >&2
  exit 1
fi

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "Error: Project directory not found: $PROJECT_DIR" >&2
  exit 1
fi

# Check firebase CLI
if ! command -v firebase &>/dev/null; then
  echo "Error: firebase-tools not installed. Run: npm install -g firebase-tools" >&2
  exit 1
fi

# Detect public directory (Astro builds to dist/, static sites may use public/)
PUBLIC_DIR="$PROJECT_DIR"
for candidate in dist public build out _site; do
  if [[ -d "$PROJECT_DIR/$candidate" ]]; then
    PUBLIC_DIR="$PROJECT_DIR/$candidate"
    break
  fi
done

# Generate firebase.json if not present
if [[ ! -f "$PROJECT_DIR/firebase.json" ]]; then
  cat > "$PROJECT_DIR/firebase.json" << FIREBASE_JSON
{
  "hosting": {
    "public": "$(basename "$PUBLIC_DIR")",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      { "source": "**", "destination": "/index.html" }
    ],
    "headers": [
      {
        "source": "**/*.@(jpg|jpeg|gif|png|svg|webp|avif|ico)",
        "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
      },
      {
        "source": "**/*.@(js|css)",
        "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
      }
    ]
  }
}
FIREBASE_JSON
  echo "Generated firebase.json in $PROJECT_DIR" >&2
fi

# Generate .firebaserc if not present
if [[ ! -f "$PROJECT_DIR/.firebaserc" ]]; then
  cat > "$PROJECT_DIR/.firebaserc" << FIREBASERC
{
  "projects": {
    "default": "$GCP_PROJECT"
  }
}
FIREBASERC
  echo "Generated .firebaserc in $PROJECT_DIR" >&2
fi

# Deploy
DEPLOY_ARGS=(--project "$GCP_PROJECT")
SITE_FLAG=""
if [[ -n "$SITE" ]]; then
  DEPLOY_ARGS+=(--only "hosting:$SITE")
  SITE_FLAG="$SITE"
fi

HOSTING_URL=""

if [[ "$CHANNEL" == "live" ]]; then
  echo "Deploying to LIVE channel..." >&2
  firebase deploy "${DEPLOY_ARGS[@]}" --cwd "$PROJECT_DIR" 2>&1 | tee /tmp/firebase-deploy.log >&2
  HOSTING_URL="https://${SITE_FLAG:-$GCP_PROJECT}.web.app"
else
  echo "Deploying to preview channel '$CHANNEL'..." >&2
  OUTPUT=$(firebase hosting:channel:deploy "$CHANNEL" "${DEPLOY_ARGS[@]}" --cwd "$PROJECT_DIR" --json 2>/dev/null || true)

  # Extract URL from JSON output
  HOSTING_URL=$(echo "$OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['$CHANNEL']['url'])" 2>/dev/null || echo "")

  if [[ -z "$HOSTING_URL" ]]; then
    # Fallback: run without --json and parse
    firebase hosting:channel:deploy "$CHANNEL" "${DEPLOY_ARGS[@]}" --cwd "$PROJECT_DIR" 2>&1 | tee /tmp/firebase-deploy.log >&2
    HOSTING_URL=$(grep -oE 'https://[^ ]+' /tmp/firebase-deploy.log | head -1 || echo "")
  fi
fi

# Output JSON result
python3 -c "
import json
print(json.dumps({
    'url': '$HOSTING_URL',
    'channel': '$CHANNEL',
    'project': '$GCP_PROJECT',
    'site': '${SITE_FLAG:-default}',
    'public_dir': '$PUBLIC_DIR',
}))
"
