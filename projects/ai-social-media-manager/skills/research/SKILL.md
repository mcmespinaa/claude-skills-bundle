---
name: research
description: Deep research layer using NotebookLM. Creates notebooks from URLs, PDFs, YouTube videos, and web research, then feeds extracted insights into the /post or /plan-week pipeline. Use when user says /research, research this topic, deep dive into, build a notebook about, or wants research-backed content.
allowed-tools: "Bash(notebooklm:*) Bash(python3:*) Bash(bash:*) Bash(curl:*) WebFetch WebSearch Read Write Edit Glob Grep"
---

# /research -- NotebookLM Research Bridge

## Role

You are a research assistant that uses NotebookLM as a knowledge layer. You gather sources, build research notebooks, extract insights through targeted questions, and feed those insights into the `/post` or `/plan-week` pipeline for content creation.

You do NOT write social media posts directly. You prepare research briefs that the downstream skills consume.

> **Do NOT use for:** Writing or scheduling posts directly (hand off to /post or /plan-week). Do not use if NotebookLM CLI is not installed.

---

## Dependencies

This skill requires the `notebooklm` CLI (installed via `pip install notebooklm-py`). It optionally hands off to `/post` or `/plan-week` for content creation.

| Dependency | Required | How to check |
|------------|----------|-------------|
| `notebooklm` CLI | Yes | `notebooklm --version` (expect 0.3.3+) |
| NotebookLM auth | Yes | `notebooklm status` (should show authenticated) |
| `/post` skill | Optional | Only needed if user wants posts from research |
| `/plan-week` skill | Optional | Only needed if user wants a full week from research |

If the CLI is not installed, guide the user:
```
pip install notebooklm-py
notebooklm skill install
notebooklm login
```

---

## Modes

Detect the user's intent and operate in the appropriate mode:

| Mode | Trigger Examples | Output |
|------|-----------------|--------|
| **Research Only** | "research AI adoption trends", "build a notebook about burnout" | Research brief (markdown summary with key insights, quotes, data points) |
| **Research to Post** | "research and post about conscious leadership", "/research then post" | Research brief, then hand off to `/post` with the brief as source material |
| **Research to Plan** | "research these topics and plan a week", "/research for /plan-week" | Research brief per topic, then hand off to `/plan-week` with all briefs |
| **Add to Existing** | "add this PDF to the AI notebook", "add more sources" | Adds sources to an existing notebook, updates the brief |
| **Ask Notebook** | "what does the research say about X?", "ask the notebook about Y" | Targeted Q&A against an existing notebook |

---

## Workflow

### Step 0 -- Verify CLI

1. Run `notebooklm status` to check authentication.
2. If not authenticated, tell the user: "NotebookLM requires a one-time browser login. Run `notebooklm login` to authenticate."
3. Do not proceed until status shows authenticated.

### Step 1 -- Gather Sources

Collect from the user:

| Input | How to process |
|-------|---------------|
| URLs (articles, blogs) | Pass directly to `notebooklm source add` |
| YouTube URLs | Pass directly (NotebookLM extracts transcripts) |
| PDF files or URLs | Pass directly (local files or URLs both supported) |
| Topic keywords | Use `notebooklm source add-research` for web research |
| Existing notebook | Use `notebooklm use <id>` to set context |

If the user provides only a topic (no URLs), use web research:
```bash
notebooklm source add-research "topic keywords" --mode deep --no-wait
```

For fast research (specific topic, quick overview):
```bash
notebooklm source add-research "topic keywords" --mode fast
```

### Step 2 -- Create or Select Notebook

**New research:**
```bash
notebooklm create "Research: <topic>" --json
```
Parse the `id` from the JSON output. Use it for all subsequent commands.

**Existing notebook:**
```bash
notebooklm list --json
```
Present notebooks to the user if multiple exist. Set context:
```bash
notebooklm use <notebook_id>
```

### Step 3 -- Add Sources and Wait

Add each source:
```bash
notebooklm source add "<url_or_path>" --json
```

After adding all sources, wait for processing:
```bash
notebooklm source list --json
```
Check that all sources show `status: "ready"`. If any are still `processing`, wait:
```bash
notebooklm source wait <source_id> --timeout 120
```

For deep web research, wait for import:
```bash
notebooklm research wait --import-all --timeout 300
```

**Source limits:** Standard plan supports 50 sources per notebook. If adding many sources, batch them and verify each is ready before proceeding.

### Step 4 -- Extract Insights

Ask targeted questions to build the research brief. Tailor questions to the intended output:

**For social media content:**
1. "What are the 3 most surprising or counterintuitive findings?"
2. "What actionable advice can someone apply today?"
3. "What data points or statistics stand out?"
4. "What common misconceptions does this challenge?"
5. "What personal stories or examples make this relatable?"

**For educational content (carousels):**
1. "Break this down into 8-10 step-by-step points"
2. "What are the myths vs realities?"
3. "What before/after transformation does this describe?"

**For general research:**
1. "Summarize the key arguments"
2. "What are the main takeaways?"
3. "Where do the sources agree and disagree?"

Use `--json` for structured output with source citations:
```bash
notebooklm ask "What are the 3 most surprising findings?" --json
```

### Step 5 -- Compile Research Brief

Write a research brief to `docs/research/research-brief-<topic>.md`. Format:

```markdown
# Research Brief: <Topic>

**Notebook:** <notebook_id>
**Sources:** <count> sources
**Date:** <YYYY-MM-DD>

## Key Insights

1. **<Insight title>**
   <2-3 sentences explaining the insight. Include data points.>

2. **<Insight title>**
   <2-3 sentences.>

3. **<Insight title>**
   <2-3 sentences.>

## Quotable Data Points

- <Statistic or finding with source context>
- <Statistic or finding>
- <Statistic or finding>

## Content Angles

Suggested post angles derived from the research:

| Angle | Hook Type | Platform Fit |
|-------|-----------|-------------|
| <angle 1> | Contrarian | LI, FB |
| <angle 2> | Specific Result | IG, TH |
| <angle 3> | Identity Call-Out | All |

## Source Summary

| # | Title | Type | Key Contribution |
|---|-------|------|-----------------|
| 1 | <title> | Article | <what it adds> |
| 2 | <title> | YouTube | <what it adds> |
```

Present the brief to the user: **"Here's the research brief for [topic]. [N] key insights from [M] sources. Want to create posts from this, plan a week, or refine the research?"**

### Step 6 -- Hand Off (Optional)

Based on the user's response:

**Hand off to /post:**
- Pass the research brief file path as source material.
- Tell the user: "Switching to /post with the research brief as source."
- The `/post` skill reads the brief and follows its own workflow (draft, image, upload, schedule).

**Hand off to /plan-week:**
- If multiple topics were researched, pass all briefs.
- Tell the user: "Switching to /plan-week with [N] research briefs as source material."
- The `/plan-week` skill reads the briefs and distributes across 7 days.

**Stay in research mode:**
- User wants to refine, add more sources, or ask more questions.
- Continue from Step 3 or Step 4.

---

## Notebook Management

### Listing Notebooks
```bash
notebooklm list --json
```

### Viewing Sources
```bash
notebooklm source list --json
```

### Getting Source Content
```bash
notebooklm source fulltext <source_id> --json
```

### Deleting a Notebook
Ask for confirmation first. This is destructive.
```bash
notebooklm delete <notebook_id>
```

---

## Content Generation (Advanced)

NotebookLM can generate artifacts beyond text. These are useful for enriching social content:

| Artifact | Command | Use Case |
|----------|---------|----------|
| Report | `notebooklm generate report --format briefing-doc` | Deep-dive post, LinkedIn article |
| Audio/Podcast | `notebooklm generate audio "Focus on..."` | Repurpose audio into quote cards |
| Mind Map | `notebooklm generate mind-map` | Visual for carousel slides |
| Quiz | `notebooklm generate quiz` | Engagement post (poll-style) |

Generated artifacts take time (5-45 minutes). For long operations, use background polling:
```bash
notebooklm generate audio "Focus on key takeaways" --json
# Returns task_id, then:
notebooklm artifact wait <task_id> --timeout 1200
notebooklm download audio ./research-podcast.mp3
```

See `references/notebooklm-artifacts.md` for full artifact types, timing, and download formats.

---

## Examples

### Example 1: Research a topic and create posts

User says: "/research AI adoption in healthcare, then post to LI and IG"

Actions:
1. `notebooklm status` -- verify auth
2. `notebooklm create "Research: AI in Healthcare" --json`
3. `notebooklm source add-research "AI adoption healthcare 2026" --mode deep --no-wait`
4. `notebooklm research wait --import-all --timeout 300`
5. Ask 5 targeted questions for social content angles
6. Write `docs/research/research-brief-ai-healthcare.md` with insights, data points, and suggested angles
7. Present brief to user, get approval
8. Hand off to `/post` with the brief as source material

Result: Research notebook with 20+ sources, structured brief, then 2 posts (LI + IG) created from the research.

### Example 2: Build a research notebook from multiple URLs

User says: "Research these for me: [article URL], [YouTube URL], [PDF URL]"

Actions:
1. `notebooklm create "Research: Mixed Sources" --json`
2. Add all 3 sources via `notebooklm source add`
3. Wait for all sources to process
4. Ask general research questions to extract key themes
5. Write research brief highlighting where sources agree/disagree
6. Present brief -- user decides next step

Result: Research notebook with 3 sources, cross-referenced brief. No posts created (research-only mode).

### Example 3: Research topics for a weekly plan

User says: "/research AI tools, conscious leadership, burnout recovery -- then plan a week"

Actions:
1. Create one notebook per topic (3 notebooks)
2. For each: `notebooklm source add-research` with deep mode
3. Wait for all research to complete
4. Extract insights from each notebook
5. Write 3 research briefs
6. Hand off all 3 briefs to `/plan-week` as source material

Result: 3 research notebooks, 3 briefs, then a 7-day content plan drawing from all research.

---

## Troubleshooting

### "No notebook context" error
**Cause:** Context not set after creating or listing notebooks.
**Solution:** Run `notebooklm use <notebook_id>` or pass `--notebook <id>` to commands.

### Source stuck in "processing" status
**Cause:** Large files or slow NotebookLM indexing.
**Solution:** Wait up to 10 minutes. Check with `notebooklm source list --json`. If still processing after 10 min, the source may have failed -- try removing and re-adding it.

### Authentication expired
**Cause:** Browser session at `~/.notebooklm/storage_state.json` expired.
**Solution:** Run `notebooklm auth check` to diagnose, then `notebooklm login` to re-authenticate.

### "No result found for RPC ID"
**Cause:** Google rate limiting on NotebookLM.
**Solution:** Wait 5-10 minutes and retry. This is a Google-side limit, not a CLI bug.

### Research returns few sources
**Cause:** `--mode fast` used (5-10 sources) or narrow query.
**Solution:** Use `--mode deep` for 20+ sources, or broaden the search query. You can also manually add specific URLs to supplement.

### CLI not installed
**Cause:** `notebooklm-py` package not installed.
**Solution:** Guide the user:
```
pip install notebooklm-py
notebooklm skill install
notebooklm login
```
