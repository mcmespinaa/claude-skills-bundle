#!/usr/bin/env bash
# youtube_search.sh — Search YouTube via Data API v3
#
# Usage:
#   youtube_search.sh --query "AI agents 2026"
#   youtube_search.sh --query "podcast tips" --max 20 --order date
#   youtube_search.sh --query "machine learning" --channel UCxxxxxx --duration short
#   youtube_search.sh --query "news" --published-after "2026-03-01T00:00:00Z" --region US
#   youtube_search.sh --query "cooking" --type channel
#   youtube_search.sh --query "react tutorial" --captions true --definition high
#
# Output (stdout): JSON array of results.
# Errors go to stderr.
#
# Requires: YOUTUBE_API_KEY in .env, ~/.notebooklm/youtube_api_key,
#           or as environment variable YOUTUBE_API_KEY
#
# Quota cost: 100 units per search (10,000 daily limit = 100 searches/day)

set -euo pipefail

ENV_FILE="$(cd "$(dirname "$0")/../../../.." && pwd)/.env"
API_KEY_FILE="$HOME/.notebooklm/youtube_api_key"

# --- Defaults ---
QUERY=""
MAX_RESULTS=10
ORDER="relevance"
TYPE="video"
PUBLISHED_AFTER=""
PUBLISHED_BEFORE=""
CHANNEL_ID=""
REGION_CODE=""
LANGUAGE=""
DURATION=""
DEFINITION=""
CAPTIONS=""
CATEGORY_ID=""
LICENSE=""
EVENT_TYPE=""
SAFE_SEARCH="moderate"
PAGE_TOKEN=""
ENRICH="false"

# --- Parse args ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --query|-q)         QUERY="$2"; shift 2 ;;
        --max|-n)           MAX_RESULTS="$2"; shift 2 ;;
        --order|-o)         ORDER="$2"; shift 2 ;;
        --type|-t)          TYPE="$2"; shift 2 ;;
        --published-after)  PUBLISHED_AFTER="$2"; shift 2 ;;
        --published-before) PUBLISHED_BEFORE="$2"; shift 2 ;;
        --channel)          CHANNEL_ID="$2"; shift 2 ;;
        --region)           REGION_CODE="$2"; shift 2 ;;
        --language)         LANGUAGE="$2"; shift 2 ;;
        --duration)         DURATION="$2"; shift 2 ;;
        --definition)       DEFINITION="$2"; shift 2 ;;
        --captions)         CAPTIONS="$2"; shift 2 ;;
        --category)         CATEGORY_ID="$2"; shift 2 ;;
        --license)          LICENSE="$2"; shift 2 ;;
        --event-type)       EVENT_TYPE="$2"; shift 2 ;;
        --safe-search)      SAFE_SEARCH="$2"; shift 2 ;;
        --page-token)       PAGE_TOKEN="$2"; shift 2 ;;
        --enrich)           ENRICH="true"; shift ;;
        --help|-h)
            sed -n '2,16p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

if [[ -z "$QUERY" ]]; then
    echo "Error: --query is required" >&2
    exit 1
fi

# --- Resolve API key ---
if [[ -z "${YOUTUBE_API_KEY:-}" ]]; then
    # Try .env first, then fallback file
    if [[ -f "$ENV_FILE" ]]; then
        YOUTUBE_API_KEY="$(grep -E '^YOUTUBE_API_KEY=' "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '[:space:]')" || true
    fi
    if [[ -z "${YOUTUBE_API_KEY:-}" && -f "$API_KEY_FILE" ]]; then
        YOUTUBE_API_KEY="$(cat "$API_KEY_FILE" | tr -d '[:space:]')"
    fi
    if [[ -z "${YOUTUBE_API_KEY:-}" ]]; then
        echo "Error: No API key found." >&2
        echo "Add YOUTUBE_API_KEY=<key> to .env or save key to $API_KEY_FILE" >&2
        echo "" >&2
        echo "To get an API key:" >&2
        echo "  1. Go to https://console.cloud.google.com/" >&2
        echo "  2. Enable 'YouTube Data API v3'" >&2
        echo "  3. Create an API key (Credentials > Create Credentials > API Key)" >&2
        echo "  4. Add YOUTUBE_API_KEY=<key> to your .env file" >&2
        exit 1
    fi
fi

# --- Build search URL ---
BASE_URL="https://www.googleapis.com/youtube/v3/search"
PARAMS="part=snippet&q=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUERY'))")&maxResults=$MAX_RESULTS&order=$ORDER&type=$TYPE&safeSearch=$SAFE_SEARCH&key=$YOUTUBE_API_KEY"

[[ -n "$PUBLISHED_AFTER" ]]  && PARAMS="$PARAMS&publishedAfter=$PUBLISHED_AFTER"
[[ -n "$PUBLISHED_BEFORE" ]] && PARAMS="$PARAMS&publishedBefore=$PUBLISHED_BEFORE"
[[ -n "$CHANNEL_ID" ]]       && PARAMS="$PARAMS&channelId=$CHANNEL_ID"
[[ -n "$REGION_CODE" ]]      && PARAMS="$PARAMS&regionCode=$REGION_CODE"
[[ -n "$LANGUAGE" ]]         && PARAMS="$PARAMS&relevanceLanguage=$LANGUAGE"
[[ -n "$DURATION" ]]         && PARAMS="$PARAMS&videoDuration=$DURATION"
[[ -n "$DEFINITION" ]]       && PARAMS="$PARAMS&videoDefinition=$DEFINITION"
[[ -n "$CAPTIONS" ]]         && PARAMS="$PARAMS&videoCaption=$CAPTIONS"
[[ -n "$CATEGORY_ID" ]]      && PARAMS="$PARAMS&videoCategoryId=$CATEGORY_ID"
[[ -n "$LICENSE" ]]          && PARAMS="$PARAMS&videoLicense=$LICENSE"
[[ -n "$EVENT_TYPE" ]]       && PARAMS="$PARAMS&eventType=$EVENT_TYPE"
[[ -n "$PAGE_TOKEN" ]]       && PARAMS="$PARAMS&pageToken=$PAGE_TOKEN"

echo "Searching YouTube for: $QUERY" >&2

# --- Execute search ---
RESPONSE=$(curl -s -f "$BASE_URL?$PARAMS" 2>&1) || {
    echo "Error: API request failed" >&2
    echo "$RESPONSE" >&2
    exit 1
}

# --- Check for API errors ---
ERROR=$(echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'error' in data:
    err = data['error']
    print(f\"API Error {err['code']}: {err['message']}\")
" 2>/dev/null || true)

if [[ -n "$ERROR" ]]; then
    echo "$ERROR" >&2
    exit 1
fi

# --- Format results ---
FORMATTED=$(echo "$RESPONSE" | python3 -c "
import sys, json

data = json.load(sys.stdin)
results = []
for item in data.get('items', []):
    snippet = item.get('snippet', {})
    id_obj = item.get('id', {})

    kind = id_obj.get('kind', '')
    if 'video' in kind:
        item_type = 'video'
        item_id = id_obj.get('videoId', '')
        url = f'https://www.youtube.com/watch?v={item_id}'
    elif 'channel' in kind:
        item_type = 'channel'
        item_id = id_obj.get('channelId', '')
        url = f'https://www.youtube.com/channel/{item_id}'
    elif 'playlist' in kind:
        item_type = 'playlist'
        item_id = id_obj.get('playlistId', '')
        url = f'https://www.youtube.com/playlist?list={item_id}'
    else:
        item_type = 'unknown'
        item_id = ''
        url = ''

    results.append({
        'type': item_type,
        'id': item_id,
        'title': snippet.get('title', ''),
        'channel': snippet.get('channelTitle', ''),
        'channelId': snippet.get('channelId', ''),
        'publishedAt': snippet.get('publishedAt', ''),
        'description': snippet.get('description', ''),
        'url': url,
        'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
    })

output = {
    'query': '$QUERY' if '$QUERY' else data.get('q', ''),
    'totalResults': data.get('pageInfo', {}).get('totalResults', 0),
    'resultsPerPage': data.get('pageInfo', {}).get('resultsPerPage', 0),
    'nextPageToken': data.get('nextPageToken', None),
    'prevPageToken': data.get('prevPageToken', None),
    'results': results,
}
print(json.dumps(output, indent=2))
")

# --- Optional enrichment with video stats (costs 1 unit) ---
if [[ "$ENRICH" == "true" && "$TYPE" == *"video"* ]]; then
    VIDEO_IDS=$(echo "$FORMATTED" | python3 -c "
import sys, json
data = json.load(sys.stdin)
ids = [r['id'] for r in data['results'] if r['type'] == 'video']
print(','.join(ids))
")

    if [[ -n "$VIDEO_IDS" ]]; then
        echo "Enriching with video statistics..." >&2
        STATS=$(curl -s -f "https://www.googleapis.com/youtube/v3/videos?part=statistics,contentDetails&id=$VIDEO_IDS&key=$YOUTUBE_API_KEY")

        FORMATTED=$(echo "$FORMATTED" | python3 -c "
import sys, json

search_data = json.load(sys.stdin)
stats_raw = '''$STATS'''
stats_data = json.loads(stats_raw)

stats_map = {}
for item in stats_data.get('items', []):
    vid = item['id']
    s = item.get('statistics', {})
    cd = item.get('contentDetails', {})
    stats_map[vid] = {
        'viewCount': int(s.get('viewCount', 0)),
        'likeCount': int(s.get('likeCount', 0)),
        'commentCount': int(s.get('commentCount', 0)),
        'duration': cd.get('duration', ''),
    }

for r in search_data['results']:
    if r['id'] in stats_map:
        r['stats'] = stats_map[r['id']]

print(json.dumps(search_data, indent=2))
")
    fi
fi

echo "$FORMATTED"
RESULT_COUNT=$(echo "$FORMATTED" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['results']))")
echo "Found $RESULT_COUNT results." >&2
