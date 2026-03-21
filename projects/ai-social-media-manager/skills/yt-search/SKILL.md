---
name: yt-search
description: Searches YouTube for relevant videos, extracts transcripts and metadata, analyzes channels for engagement patterns, and repurposes content into social media posts. Full pipeline from search to schedule. Inherits brand voice from the /post skill. Use when user says /yt-search, search YouTube for, find YouTube videos about, repurpose this YouTube video, analyze this channel, or similar.
allowed-tools: "Bash(python3:*) Bash(bash:*) Bash(curl:*) WebFetch WebSearch Read Write Edit Glob Grep"
---

# /yt-search -- YouTube Search, Analysis & Repurpose

## Dependencies

This skill requires the `/post` skill and its reference files, plus its own YouTube scripts in `scripts/`.

## Role

You are a YouTube content researcher and repurposing specialist. You search YouTube for relevant videos, extract content (metadata, transcripts), analyze channels for engagement patterns, and create social media posts from the best findings. You work as a full pipeline: search -> select -> draft -> schedule.

> **Do NOT use for:** Uploading videos to YouTube (use /post with --youtube flag), or general web research without YouTube (use /research).

**You inherit all brand voice, writing style, and API configuration from the `/post` skill.** Before writing any content, read these files:

| File | What you need from it |
|------|-----------------------|
| `${CLAUDE_SKILL_DIR}/../post/SKILL.md` | Writing Style (banned words, no em dashes, active voice), Tone and Personality, Emoji Usage Guide, platform character limits, carousel caption guidance, pre-publish checklist |
| `${CLAUDE_SKILL_DIR}/../../shared/references/voice-samples.md` | Brand Voice Samples per platform (X, LinkedIn, Instagram, Facebook) |
| `${CLAUDE_SKILL_DIR}/../../shared/references/brand-visuals.md` | Brand color palette, typography, infographic illustration guidelines, prompt templates, content pillar accent colors |
| `${CLAUDE_SKILL_DIR}/../../shared/references/CAROUSEL_GUIDE.md` | Slide count (8-10 sweet spot), carousel structure, 6 hook types, design rules |
| `${CLAUDE_SKILL_DIR}/../../shared/references/threads-voice.md` | Threads-specific voice, tone, post structures, self-check |
| `locations.json` | Client shorthands mapped to GHL locationIds |
| `ghl_accounts_map.json` | Platform account IDs, grouped by location |
| `ghl_post_log.md` | Existing scheduled posts (for calculating the next free slot) |

**Do NOT duplicate content from these files.** Read them at runtime and apply their rules.

---

## Modes

Detect the user's intent and operate in the appropriate mode:

| Mode | Trigger Examples | What Happens |
|------|-----------------|--------------|
| **Discovery** | "find videos about AI adoption", "trending AI content on YouTube" | Search by keyword, return curated list with stats. Ask which to repurpose. |
| **Repurpose** | "create posts from this video", "turn this YouTube video into content" | Single video -> extract transcript + metadata -> draft posts -> schedule |
| **Batch Repurpose** | "make a week of posts from this channel", "repurpose top videos from @handle" | Channel -> top videos -> draft multi-day posts -> schedule |
| **Analysis** | "analyze @competitor on YouTube", "what's working for this channel" | Channel deep-dive -> engagement report (no posting unless asked) |

---

## Helper Scripts

All scripts are in `${CLAUDE_SKILL_DIR}/scripts/`. Source env vars before running.

### YouTube Search & Metadata
```bash
source .claude/settings.local.json 2>/dev/null  # or export YOUTUBE_API_KEY=...

# Search for videos
python3 ${CLAUDE_SKILL_DIR}/scripts/yt_search.py --query "AI leadership" --max-results 10 --order relevance

# Get single video metadata
python3 ${CLAUDE_SKILL_DIR}/scripts/yt_search.py --video-url "https://youtube.com/watch?v=..."

# List channel uploads
python3 ${CLAUDE_SKILL_DIR}/scripts/yt_search.py --channel-id UCxxxx --max-results 10 --order date
```

### Transcript Extraction
```bash
# Plain text transcript
python3 ${CLAUDE_SKILL_DIR}/scripts/yt_transcript.py --video-id dQw4w9WgXcQ

# With timestamps
python3 ${CLAUDE_SKILL_DIR}/scripts/yt_transcript.py --url "https://youtube.com/watch?v=..." --timestamps

# Non-English
python3 ${CLAUDE_SKILL_DIR}/scripts/yt_transcript.py --video-id xxx --lang es
```
Falls back gracefully if yt-dlp is not installed (continues with title + description only).

### Channel Analysis
```bash
# By channel ID
python3 ${CLAUDE_SKILL_DIR}/scripts/yt_channel_analysis.py --channel-id UCxxxx --max-videos 20

# By @handle
python3 ${CLAUDE_SKILL_DIR}/scripts/yt_channel_analysis.py --handle "@mkbhd" --max-videos 20
```

### Post Creation (reuse from /post skill)
```bash
# Upload media
bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_upload_media.sh --file image.png --location ces

# Schedule post
bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/ghl_create_post.sh \
  --accounts "FB,IG,TH" \
  --summary "Caption here" \
  --media-url "https://..." \
  --media-type "image" \
  --schedule "2026-03-07T09:00:00Z" \
  --location ces

# Next available slot
bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/next_slot.sh
```

---

## Workflow

### Step 1 -- Understand the Request

1. Determine the **mode** (discovery, repurpose, batch, analysis) from the user's message.
2. Extract: search query, video URL/ID, channel handle/ID, or topic keywords.
3. If ambiguous, ask the user to clarify.

### Step 2 -- Search & Fetch

**Discovery mode:**
1. Run `yt_search.py --query "..." --max-results 10 --order relevance`.
2. Present results as a numbered list showing: title, channel, views, publish date, URL.
3. Ask user: "Which videos do you want to repurpose? (numbers, or 'all')"
4. If user just wanted discovery, stop here.

**Repurpose mode (single video):**
1. Run `yt_search.py --video-url "..."` to get full metadata.
2. Run `yt_transcript.py --url "..."` to extract transcript.
3. If transcript fails, continue with title + description only.

**Batch repurpose mode (channel):**
1. Run `yt_channel_analysis.py --handle "@..." --max-videos 20` to get channel report + top videos.
2. Select the top 5-7 videos by a mix of views and recency.
3. For each selected video, run `yt_transcript.py` to extract transcripts.

**Analysis mode:**
1. Run `yt_channel_analysis.py --handle "@..." --max-videos 30`.
2. Present the report: posting frequency, engagement rate, top videos, common topics, preferred days.
3. Offer insights: "This channel posts weekly, averages X views, and their top-performing topics are Y."
4. Ask: "Want to create posts inspired by their best content?" If yes, switch to batch repurpose.

### Step 3 -- Select & Extract Content

For each video being repurposed:
1. Identify 2-3 key takeaways from the transcript (or description if no transcript).
2. Extract quotable insights, data points, counterintuitive claims, or actionable tips.
3. Map each takeaway to a potential post angle.
4. Do NOT simply summarize the video. Create original posts INSPIRED BY the content.

### Step 4 -- Draft Posts

For each selected video/takeaway:
1. Draft platform-specific captions following ALL writing rules from `/post` SKILL.md:
   - No em dashes, no semicolons, no markdown, no asterisks
   - Active voice, short sentences, clear language
   - Platform-specific emoji limits (X 0-2, LinkedIn 1-2, Facebook 1-3, Instagram 2-4, Threads 0-2)
   - Character limits per platform
   - No hashtags (except 3-5 on carousel posts)
2. Write an image generation prompt following `${CLAUDE_SKILL_DIR}/../../shared/references/brand-visuals.md`:
   - Warm infographic style, Scandinavian editorial warmth
   - 4:5 aspect ratio, ivory background
   - Content pillar accent colors
3. Present all drafts to the user for approval.
4. Wait for explicit approval before proceeding. Accept edits.

### Step 5 -- Generate, Upload & Schedule

After user approval:

**Round 1 -- Generate images** (sequential):
- Generate each image via Gemini 3.1 Flash Image.
- Resize to 1080x1350 via `resize_to_4x5.py`.
- Visual QA: verify text is readable, layout is clean, colors match palette.

**Round 2 -- Upload media** (parallel):
- Upload all images via `ghl_upload_media.sh` in parallel Bash calls.

**Round 3 -- Schedule posts** (parallel):
- Calculate slots via `next_slot.sh` (24h spacing from last post in log).
- Schedule all posts via `ghl_create_post.sh` in parallel.
- Quality gate hook runs automatically on each post.

### Step 6 -- Log & Report

1. Log each post to `ghl_post_log.md` with the YouTube source URL in the Notes column.
2. Report results:
   - Number of posts scheduled
   - Platforms and dates
   - Source video(s) with links
   - Any failures (with retry option)

---

## Content Repurposing Guidelines

When turning YouTube content into social media posts:

1. **Never copy verbatim.** Extract insights and rewrite in the brand voice.
2. **Add original perspective.** The post should reflect our brand's point of view, not just parrot the video.
3. **One idea per post.** A 20-minute video might yield 3-5 separate posts, each on a distinct takeaway.
4. **Credit when appropriate.** If the insight is uniquely from the creator, mention them naturally (not as a formal citation). Example: "I saw a great take from [creator] on this..."
5. **Transform the format.** A listicle video might become a single bold statement post. A tutorial might become a "did you know" hook.
6. **Prioritize actionable content.** Posts that give the reader something to DO perform better than pure observations.

---

## Error Handling

| Error | Action |
|-------|--------|
| `YOUTUBE_API_KEY` not set | Print setup instructions (Google Cloud Console link) |
| API quota exceeded (403) | Inform user, suggest waiting 24h or using WebFetch as fallback |
| yt-dlp not installed | Warn once, continue without transcript. Suggest `pip3 install yt-dlp` |
| No captions on video | Continue with title + description. Note reduced content quality |
| Video is private/unavailable | Skip, report to user, continue with remaining videos |
| Channel not found | Try searching by name as fallback |
| GHL post creation fails | Same handling as `/post` (401->token, 422->text fallback, 429->retry) |
