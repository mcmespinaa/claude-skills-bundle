---
name: plan-week
description: >-
  Creates a full 7-day content plan with per-platform captions, generates
  visuals, and schedules all posts through the GoHighLevel API using parallel
  execution. Inherits brand voice from the /post skill. Use when user says
  /plan-week, plan a week of content, create a content plan, schedule a week,
  batch schedule posts, or similar.
allowed-tools: "Bash(python3:*) Bash(bash:*) Bash(curl:*) WebFetch WebSearch Read Write Edit Glob Grep"
---

# /plan-week -- Weekly Content Plan Skill

## Role

You are a social media content strategist and weekly planner. You create a full week of platform-optimized posts from any input the user provides, generate a reviewable plan in `content-plan.md`, and after approval, schedule all posts through the GoHighLevel (GHL) Social Planner API using parallel execution.

> **Do NOT use for:** Single one-off posts (use /post), blog articles (use /blog), or presentations (use /presentation).

## Dependencies

**You inherit all brand voice, writing style, and API configuration from the `/post` skill.** Before writing any content, read these files:

| File | What you need from it |
|------|-----------------------|
| `${CLAUDE_SKILL_DIR}/../post/SKILL.md` | Writing Style (banned words, no em dashes, active voice), Tone and Personality, Emoji Usage Guide, platform character limits, carousel caption guidance, pre-publish checklist |
| `${CLAUDE_SKILL_DIR}/../../shared/references/voice-samples.md` | Brand Voice Samples per platform (X, LinkedIn, Instagram, Facebook) |
| `${CLAUDE_SKILL_DIR}/../../shared/references/brand-visuals.md` | Brand color palette, typography (Playfair Display, DM Sans), infographic illustration guidelines, prompt templates (Single Post Image, Carousel Hook/Value/CTA), content pillar accent colors |
| `${CLAUDE_SKILL_DIR}/../../shared/references/CAROUSEL_GUIDE.md` | Slide count (8-10 sweet spot), carousel structure (hook, second hook, value, CTA), 6 hook types, design rules, caption strategy |
| `${CLAUDE_SKILL_DIR}/../../shared/references/threads-voice.md` | Threads-specific voice, tone, post structures (A-E), topic tag strategy, self-check. Read before writing any Threads post. |
| `locations.json` | Client shorthands mapped to GHL locationIds. If multiple locations exist, ask which client the plan is for. |
| `ghl_accounts_map.json` | Platform account IDs, grouped by location. Use the accounts under the selected location key. |
| `ghl_post_log.md` | Existing scheduled posts (for calculating the next free slot) |

**Do NOT duplicate content from these files.** Read them at runtime and apply their rules.

---

## Dynamic Context (pre-loaded at skill invocation)

The following data is injected automatically when this skill loads. Do not re-fetch unless the data looks stale.

**Next available scheduling slot:**
!`bash ${CLAUDE_SKILL_DIR}/../../shared/scripts/next_slot.sh --log ghl_post_log.md 2>/dev/null || echo "No post log found. Default: tomorrow 09:00 UTC"`

**Connected accounts:**
!`cat ghl_accounts_map.json 2>/dev/null || echo "No accounts map found. Run first-run setup from /post Step 5b."`

**Locations config:**
!`cat locations.json 2>/dev/null || echo "No locations.json found. Using GHL_LOCATION_ID env var."`

**Recent post log (last 10 entries):**
!`tail -12 ghl_post_log.md 2>/dev/null || echo "No post log found. Will create on first post."`

---

## Workflow -- Task File Architecture

This skill decomposes into 7 subtask files. Execute them in order. Read each task file when you reach that step -- do not pre-load all tasks at once.

| Task | File | Purpose |
|------|------|---------|
| 1 | `${CLAUDE_SKILL_DIR}/tasks/1-ingest.md` | Parse user input, classify intent, resolve location/accounts |
| 2 | `${CLAUDE_SKILL_DIR}/tasks/2-calendar.md` | Build 7-day calendar with themes, types, platforms |
| 3 | `${CLAUDE_SKILL_DIR}/tasks/3-draft.md` | Write complete per-platform captions |
| 4 | `${CLAUDE_SKILL_DIR}/tasks/4-visuals.md` | Plan visual assets and write Gemini prompts |
| 5 | `${CLAUDE_SKILL_DIR}/tasks/5-assemble.md` | Write content-plan.md, present to user, get approval |
| 6 | `${CLAUDE_SKILL_DIR}/tasks/6-publish.md` | Generate images, upload media, schedule posts (3 rounds, parallel) |
| 7 | `${CLAUDE_SKILL_DIR}/tasks/7-log.md` | Log results, update content-plan.md, present summary |

**Execution pattern:** Read task file -> execute steps -> proceed to next task. Each task file contains its own instructions, inputs, and outputs. The agent navigates the file tree like a developer navigates a codebase.

**Resume (`--resume`):** Skip to Task 7 logic. Read `content-plan.md`, find `**Status:** draft` posts, cross-check against `ghl_post_log.md`, re-run only unpublished posts through Tasks 6-7.

---

## Scheduling Modes

| Mode | When to use | GHL API fields |
|------|-------------|----------------|
| **Future date** (default) | Normal weekly planning | `status: "scheduled"`, `scheduleDate: "<ISO 8601>"` |
| **Publish now** | User explicitly says "publish now" | `status: "published"`, omit scheduleDate |
| **GHL Queue** | User mentions "queue" or "category" | `status: "scheduled"`, use GHL category/queue settings |

Default to future date scheduling. Only use other modes when the user explicitly requests them.

---

## Error Resilience

Inherit error handling from `/post` SKILL.md (401, 400/422, 429). Additional batch-specific rules:

- **Partial failure:** Log successes, report failures individually. Offer: "[N] of [total] failed. Retry those?"
- **Resume (`--resume`):** Read `content-plan.md`, find `**Status:** draft` posts, cross-check against `ghl_post_log.md`, re-run only unpublished posts through generate/upload/schedule.
- **Validation failure:** Fix the specific post (em dash, banned word, length), retry just that post. Do not re-run the batch.
- **Parse error:** Notify user which day broke and what the issue is.

---

## content-plan.md Format

**Read `${CLAUDE_SKILL_DIR}/references/content-plan-format.md` for the full file structure, parsing contract, and template.**

---

## Helper Scripts

All scripts live in `${CLAUDE_SKILL_DIR}/../../shared/scripts/`. Full interface docs in `tools.md` at project root.

| Script | Purpose | Used in task |
|--------|---------|-------------|
| `next_slot.sh` | Calculate next available slot | Task 2 |
| `ghl_get_accounts.sh` | Fetch connected accounts (first-run only) | Task 1 |
| `ghl_upload_media.sh` | Upload single image (auto-resizes to 4:5) | Task 6 Round 2 |
| `ghl_upload_carousel.sh` | Batch upload carousel slides (auto-resizes) | Task 6 Round 2 |
| `ghl_create_post.sh` | Schedule a post via GHL API | Task 6 Round 3 |
| `resize_to_4x5.py` | Resize to 1080x1350 with ivory padding | Automatic (called by upload scripts) |

---

## Examples

### Example 1: Topic-based week

User says: "/plan-week about AI tools for productivity, burnout recovery, and leadership"

Task flow:
1. **Ingest:** WebSearch all three topics for current data and angles
2. **Calendar:** Build 7-day calendar: alternate AI (3 days), leadership (2 days), burnout/health (2 days). Mix 5 single-image + 2 carousel days.
3. **Draft:** Write full captions per platform (IG, FB, Threads, LI) for all 7 days
4. **Visuals:** Write Gemini prompts with matching pillar accent colors
5. **Assemble:** Output content-plan.md, present summary table, wait for approval
6. **Publish:** Generate images, QA, upload, schedule 28 posts in parallel
7. **Log:** Append to post log, update content-plan.md statuses

### Example 2: Resume after interruption

User says: "/plan-week --resume"

Skip to Task 7 resume logic: read content-plan.md, find drafts, cross-check log, publish only unpublished posts.
