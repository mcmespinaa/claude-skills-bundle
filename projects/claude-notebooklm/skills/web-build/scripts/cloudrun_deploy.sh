#!/usr/bin/env bash
# cloudrun_deploy.sh — Deploy a containerized site to Google Cloud Run.
#
# Usage:
#   bash cloudrun_deploy.sh --project-dir /tmp/web-build/my-app \
#     --project-id psyched-runner-489120-r6 \
#     --service my-app [--region us-central1] [--location ces]
#
# Prerequisites:
#   - gcloud CLI: https://cloud.google.com/sdk/docs/install
#   - Authenticated: gcloud auth login
#
# Supports:
#   - Next.js, Nuxt, SvelteKit (SSR frameworks)
#   - Any project with a Dockerfile
#   - Auto-generates Dockerfile for common frameworks if missing
#
# Output (stdout): JSON with service URL, region, project.
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
SERVICE=""
REGION="us-central1"
PORT=3000

# Parse args
ARGS=("${SCRIPT_ARGS[@]+"${SCRIPT_ARGS[@]}"}")
while [[ ${#ARGS[@]} -gt 0 ]]; do
  case "${ARGS[0]}" in
    --project-dir) PROJECT_DIR="${ARGS[1]}"; ARGS=("${ARGS[@]:2}") ;;
    --project-id)  GCP_PROJECT="${ARGS[1]}"; ARGS=("${ARGS[@]:2}") ;;
    --service)     SERVICE="${ARGS[1]}"; ARGS=("${ARGS[@]:2}") ;;
    --region)      REGION="${ARGS[1]}"; ARGS=("${ARGS[@]:2}") ;;
    --port)        PORT="${ARGS[1]}"; ARGS=("${ARGS[@]:2}") ;;
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

if [[ -z "$SERVICE" ]]; then
  SERVICE=$(basename "$PROJECT_DIR" | tr '[:upper:]' '[:lower:]' | tr ' _' '-' | sed 's/[^a-z0-9-]//g')
  echo "Auto-detected service name: $SERVICE" >&2
fi

# Check gcloud CLI
if ! command -v gcloud &>/dev/null; then
  echo "Error: gcloud CLI not installed. See: https://cloud.google.com/sdk/docs/install" >&2
  exit 1
fi

# Detect framework
detect_framework() {
  if [[ -f "$PROJECT_DIR/next.config.js" ]] || [[ -f "$PROJECT_DIR/next.config.mjs" ]] || [[ -f "$PROJECT_DIR/next.config.ts" ]]; then
    echo "nextjs"
  elif [[ -f "$PROJECT_DIR/nuxt.config.ts" ]] || [[ -f "$PROJECT_DIR/nuxt.config.js" ]]; then
    echo "nuxtjs"
  elif [[ -f "$PROJECT_DIR/svelte.config.js" ]]; then
    echo "sveltekit"
  elif [[ -f "$PROJECT_DIR/astro.config.mjs" ]] || [[ -f "$PROJECT_DIR/astro.config.ts" ]]; then
    echo "astro"
  elif [[ -f "$PROJECT_DIR/package.json" ]]; then
    echo "node"
  else
    echo "unknown"
  fi
}

FRAMEWORK=$(detect_framework)
echo "Detected framework: $FRAMEWORK" >&2

# Generate Dockerfile if missing
if [[ ! -f "$PROJECT_DIR/Dockerfile" ]]; then
  echo "Generating Dockerfile for $FRAMEWORK..." >&2

  case "$FRAMEWORK" in
    nextjs)
      cat > "$PROJECT_DIR/Dockerfile" << 'DOCKERFILE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
DOCKERFILE
      PORT=3000
      ;;
    nuxtjs)
      cat > "$PROJECT_DIR/Dockerfile" << 'DOCKERFILE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.output ./
EXPOSE 3000
ENV PORT=3000
CMD ["node", ".output/server/index.mjs"]
DOCKERFILE
      PORT=3000
      ;;
    astro)
      cat > "$PROJECT_DIR/Dockerfile" << 'DOCKERFILE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
EXPOSE 4321
ENV PORT=4321 HOST=0.0.0.0
CMD ["node", "./dist/server/entry.mjs"]
DOCKERFILE
      PORT=4321
      ;;
    *)
      cat > "$PROJECT_DIR/Dockerfile" << 'DOCKERFILE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build 2>/dev/null || true

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app ./
EXPOSE 3000
ENV PORT=3000
CMD ["npm", "start"]
DOCKERFILE
      PORT=3000
      ;;
  esac

  echo "Generated Dockerfile (port: $PORT)" >&2
fi

# Generate .dockerignore if not present
if [[ ! -f "$PROJECT_DIR/.dockerignore" ]]; then
  cat > "$PROJECT_DIR/.dockerignore" << 'DOCKERIGNORE'
node_modules
.git
.env
.env.local
*.md
.firebase
.firebaserc
firebase.json
DOCKERIGNORE
fi

# Build and deploy using Cloud Build (no local Docker needed)
IMAGE="gcr.io/$GCP_PROJECT/$SERVICE"

echo "Building with Cloud Build..." >&2
gcloud builds submit "$PROJECT_DIR" \
  --tag "$IMAGE" \
  --project "$GCP_PROJECT" \
  --quiet 2>&1 | tail -5 >&2

echo "Deploying to Cloud Run..." >&2
DEPLOY_OUTPUT=$(gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --project "$GCP_PROJECT" \
  --port "$PORT" \
  --allow-unauthenticated \
  --quiet \
  --format json 2>/dev/null || echo "{}")

SERVICE_URL=$(echo "$DEPLOY_OUTPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',{}).get('url',''))" 2>/dev/null || echo "")

if [[ -z "$SERVICE_URL" ]]; then
  SERVICE_URL=$(gcloud run services describe "$SERVICE" \
    --region "$REGION" \
    --project "$GCP_PROJECT" \
    --format "value(status.url)" 2>/dev/null || echo "")
fi

# Output JSON result
python3 -c "
import json
print(json.dumps({
    'url': '$SERVICE_URL',
    'service': '$SERVICE',
    'region': '$REGION',
    'project': '$GCP_PROJECT',
    'framework': '$FRAMEWORK',
    'image': '$IMAGE',
    'port': $PORT,
}))
"
