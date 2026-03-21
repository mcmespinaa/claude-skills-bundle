---
name: youtube-search
description: Search YouTube for videos, channels, and playlists. Use when user says "search YouTube for...", "find YouTube videos about...", "look up on YouTube", "collect all videos from this channel", "import this YouTuber into NotebookLM", or invokes /youtube-search. Returns structured results with stats enrichment. Supports filters for date, duration, channel, region. Uses yt-dlp as quota-free fallback. Do NOT use for uploading videos — use /distribute with --youtube instead.
compatibility: Requires curl, python3. Optional yt-dlp for quota-free mode. YouTube API key in .env.
metadata:
  author: content-engine
  version: 2.0.0
  argument-hint: '"search query" [--max N] [--order date|views|relevance] [--duration short|medium|long] [--channel ID] [--enrich] [--yt-dlp]'
  user-invokable: true
---

# /youtube-search — YouTube Search

> **Trigger:** User says `/youtube-search`, "search YouTube for...", "find YouTube videos about...", "look up on YouTube", "collect all videos from this channel", "import this YouTuber into NotebookLM", or similar.

## Role

You search YouTube and return structured results. You can filter by date, duration, channel, region, HD, captions, and more. You enrich results with view counts and duration when asked.

---

## Constants

```
SCRIPTS_DIR: ${CLAUDE_PLUGIN_ROOT}/skills/youtube-search/scripts
API_KEY_FILE: ~/.notebooklm/youtube_api_key
```

---

## Quota Awareness

- `search.list` costs **100 units** per call
- `videos.list` (enrichment) costs **1 unit** per call
- Daily quota: **10,000 units** = ~100 searches/day
- Each paginated page costs another 100 units
- **yt-dlp fallback** has zero quota cost but fewer filters

Be mindful of quota. Avoid unnecessary pagination. Use `--enrich` only when the user needs stats.

---

## Workflow

### Step 1 — Parse the User's Request

Extract from the user's message:

| Input | Maps to | Default |
|-------|---------|---------|
| Search terms | `--query` | Required |
| Number of results | `--max` | 10 |
| Sort order | `--order` (relevance, date, viewCount, rating) | relevance |
| Date filter | `--published-after` / `--published-before` (RFC 3339) | None |
| Duration | `--duration` (short <4m, medium 4-20m, long >20m) | any |
| Specific channel | `--channel` (channel ID) | None |
| Region | `--region` (ISO 3166-1 alpha-2) | None |
| Language | `--language` (ISO 639-1) | None |
| HD only | `--definition high` | any |
| Has captions | `--captions closedCaption` | any |
| Result type | `--type` (video, channel, playlist) | video |
| Want stats | `--enrich` | No |
| Live streams | `--event-type` (live, upcoming, completed) | None |

### Step 2 — Execute the Search

**Primary method — YouTube Data API:**

```bash
bash "$SCRIPTS_DIR/youtube_search.sh" \
  --query "search terms" \
  --max 10 \
  --order relevance
```

Add filters as needed:
```bash
bash "$SCRIPTS_DIR/youtube_search.sh" \
  --query "AI agents" \
  --max 20 \
  --order date \
  --published-after "2026-01-01T00:00:00Z" \
  --duration medium \
  --definition high \
  --enrich
```

**Fallback — yt-dlp (quota-free):**

Use when the user says `--yt-dlp`, when quota is a concern, or when the API key is not set up:

```bash
yt-dlp --flat-playlist -j "ytsearch10:search terms" 2>/dev/null | python3 -c "
import sys, json
results = []
for line in sys.stdin:
    d = json.loads(line)
    results.append({
        'type': 'video',
        'id': d.get('id', ''),
        'title': d.get('title', ''),
        'channel': d.get('channel', d.get('uploader', '')),
        'channelId': d.get('channel_id', ''),
        'url': d.get('url', f\"https://www.youtube.com/watch?v={d.get('id', '')}\"),
        'viewCount': d.get('view_count'),
        'duration': d.get('duration'),
        'publishedAt': d.get('upload_date', ''),
    })
print(json.dumps({'results': results, 'source': 'yt-dlp'}, indent=2))
"
```

For date-sorted results with yt-dlp, use `ytsearchdate` instead of `ytsearch`:
```bash
yt-dlp --flat-playlist -j "ytsearchdate10:search terms"
```

### Step 3 — Present Results

Format results as a clean table for the user:

```
Found X results for "query":

| # | Title | Channel | Published | Views | Duration | Link |
|---|-------|---------|-----------|-------|----------|------|
| 1 | ...   | ...     | ...       | ...   | ...      | [Link](url) |
```

- If `--enrich` was used, include Views and Duration columns
- If not enriched, omit Views/Duration or show "—"
- Always include the clickable URL
- Show `nextPageToken` if available: "More results available. Say 'next page' to continue."

### Step 4 — Follow-up Actions

After presenting results, the user may want to:

| Request | Action |
|---------|--------|
| "Get details on #3" | Call `videos.list` with the video ID for full stats, description, tags |
| "Next page" | Re-run search with `--page-token` |
| "Download #2" | Use `yt-dlp` to download |
| "Get transcript of #1" | Use `yt-dlp --write-auto-sub --skip-download` |
| "Upload to NotebookLM" | Pipe URL to /notebooklm as a YouTube source |

---

## Workflow: Collect Full Channel into NotebookLM

> **Trigger:** "collect all videos from this channel", "add this YouTuber's videos to NotebookLM", "import channel into NotebookLM"

This workflow scrapes every video from a YouTube channel and adds them as sources to NotebookLM notebooks. NotebookLM has source limits per notebook (Standard: 50), so large channels are split across multiple notebooks.

### Step 1 — Get Full Video List (yt-dlp, quota-free)

```bash
yt-dlp --flat-playlist -j "https://www.youtube.com/@CHANNEL_HANDLE/videos" 2>/dev/null | python3 -c "
import sys, json
videos = []
for line in sys.stdin:
    d = json.loads(line)
    videos.append({'id': d.get('id',''), 'title': d.get('title',''), 'url': f\"https://www.youtube.com/watch?v={d.get('id','')}\"})
print(f'Total videos: {len(videos)}')
for i, v in enumerate(videos):
    print(f\"{i+1}. {v['id']} | {v['title'][:80]} | {v['url']}\")
"
```

This returns ALL videos (not capped at 50 like the API). Zero quota cost.

### Step 2 — Calculate Notebook Split

- Standard plan: 50 sources/notebook
- Plus plan: 100 sources/notebook
- Pro plan: 300 sources/notebook
- Ultra plan: 600 sources/notebook

```
Total videos ÷ sources_per_notebook = number of notebooks needed
```

Name notebooks descriptively: `Creator Name — Videos 1-50`, `Creator Name — Videos 51-100`, etc.

### Step 3 — Create Notebooks

```bash
notebooklm create "Creator — Videos 1-50" --json
notebooklm create "Creator — Videos 51-100" --json
# ... etc
```

Save the notebook IDs from the JSON output.

### Step 4 — Add Videos as Sources

Use bash 3.2-compatible loops (no `${!array[@]}` — macOS limitation):

```bash
NB="<notebook_id>"
for URL in \
  "https://www.youtube.com/watch?v=VIDEO_ID_1" \
  "https://www.youtube.com/watch?v=VIDEO_ID_2" \
  "https://www.youtube.com/watch?v=VIDEO_ID_3"; do
  echo "Adding $URL"
  notebooklm source add "$URL" --notebook "$NB" 2>&1
done
```

**Parallelism:** Split each notebook's videos into 2 batches and run them as background tasks for speed. Use `--notebook <id>` flag (not `notebooklm use`) to avoid context conflicts.

**Error handling:** If a source add fails, log and continue. Retry failures after all others complete.

### Step 5 — Verify

```bash
notebooklm source list --notebook <id> --json | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'{len(d.get(\"sources\",[]))} sources')
"
```

### Timing

- yt-dlp channel scrape: ~5-15 seconds for 100+ videos
- Adding sources: ~3-5 seconds per video
- 120 videos across 3 notebooks (parallelized): ~5-8 minutes total
- Source processing (NotebookLM indexing): 30s-10min per source (runs server-side)

---

## Examples

### Basic search
```
User: /youtube-search "AI agents 2026"
→ Runs search, returns top 10 results sorted by relevance
```

### Recent videos with stats
```
User: /youtube-search "machine learning tutorial" --order date --enrich
→ Returns recent ML tutorials with view counts and duration
```

### Channel-specific search
```
User: Search YouTube for Fireship videos about React
→ Resolve channel ID, then: --query "React" --channel UCsBjURrPoezykLs9EqgamOA
```

### Short-form content
```
User: Find short YouTube videos about cooking pasta
→ --query "cooking pasta" --duration short
```

### Live streams
```
User: Find upcoming live streams about AI
→ --query "AI" --event-type upcoming
```

### Quota-free search
```
User: /youtube-search "python tutorial" --yt-dlp
→ Uses yt-dlp, no API quota consumed
```

### Collect full channel into NotebookLM
```
User: collect all youtube videos from https://www.youtube.com/@Chase-H-AI
→ Scrapes 120 videos via yt-dlp
→ Creates 3 notebooks (50 + 50 + 20)
→ Adds all videos as sources in parallel
→ Reports success/failure counts
```

---

## Error Handling

| Error | Action |
|-------|--------|
| No API key | Show setup instructions (Cloud Console > YouTube Data API v3 > API Key > save to `~/.notebooklm/youtube_api_key`) |
| 403 quota exceeded | Switch to yt-dlp fallback automatically, inform user |
| 403 API not enabled | "Enable YouTube Data API v3 in your Google Cloud Console" |
| No results | Suggest broadening the query or relaxing filters |
| yt-dlp not installed | "Install with: brew install yt-dlp" |

---

## Autonomy Rules

**Run automatically (no confirmation):**
- Executing searches
- Formatting and presenting results
- Switching to yt-dlp fallback on quota error

**Ask before running:**
- Downloading videos
- Paginating (costs 100 more units)
- Any action that modifies data
