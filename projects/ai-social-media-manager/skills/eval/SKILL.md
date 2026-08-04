---
name: eval
description: >-
  Evaluates LLM-generated content quality against brand voice rules, platform
  optimization, and golden reference samples. Runs deterministic checks and
  Claude-as-judge scoring. Use when user says /eval, evaluate content quality,
  score this caption, run content evals, check brand voice, or benchmark
  outputs.
allowed-tools: "Bash(python3:*) Read Glob Grep"
---

# /eval -- Content Quality Evaluator

> **Trigger:** `/eval`, `/eval --caption "text"`, `/eval --deterministic-only`, "evaluate content quality", "score this caption", "run content evals", "check brand voice"
> **Do NOT use for:** Skill structure validation (use `/qa`), script resilience auditing (use `/resilience`), live MCP tool testing (use `/qa-test`), or general code review.

## Purpose

Systematic evaluation of LLM-generated content against brand voice rules, platform optimization standards, and golden reference samples. Produces a scored report with letter grade.

Unlike `/qa-test` (which tests MCP tool functionality), `/eval` tests the quality of content the system produces.

## Usage

- `/eval` -- Run full eval suite (all golden set test cases)
- `/eval --caption "text" --platform linkedin` -- Score a single caption
- `/eval --skill post` -- Run only test cases for `/post`
- `/eval --deterministic-only` -- Skip LLM judge (fast, free)
- `/eval --json` -- Machine-readable output
- `/eval --verbose` -- Show per-check details

## Architecture

### Three evaluation layers

| Layer | What it checks | Cost | Speed |
|-------|---------------|------|-------|
| **Deterministic** (D1-D10) | Rules: banned words, char limits, emoji count, formatting | Free | <1s |
| **LLM Judge** (J1-J6) | Subjective: brand voice match, hook quality, authenticity | ~$0.01/caption | ~3s |
| **Golden Set** | Regression: scores vs known-good baselines | Free + LLM | ~30s |

### Deterministic Checks (D1-D10)

| Check | What | Pass criteria |
|-------|------|---------------|
| D1 | Em/en dash detection | Zero dashes |
| D2 | Hard-banned words | Zero matches (40+ words) |
| D3 | Soft-banned word density | Fewer than 3 per caption |
| D4 | Character limit compliance | Within platform limit |
| D5 | Emoji count compliance | Within platform range |
| D6 | Formatting (semicolons, markdown, asterisks) | Zero violations |
| D7 | Hashtag policy | 0 for single posts, 3-5 for carousels |
| D8 | Active voice ratio | <10% passive sentences |
| D9 | Sentence length | Avg <20 words, max <35 words |
| D10 | Platform structure | Platform-specific formatting rules |

### LLM Judge Dimensions (J1-J6)

| Dimension | Weight | What | Scale |
|-----------|--------|------|-------|
| J1 Brand Voice | 3x | Matches reference samples | 1-5 |
| J2 Hook Quality | 2x | Opening line stops scrollers | 1-5 |
| J3 Platform Fit | 2x | Optimized for platform culture | 1-5 |
| J4 Authenticity | 2x | Reads human, not AI-generated | 1-5 |
| J5 CTA | 1x | Natural call to action | 1-5 |
| J6 Substance | 1x | Specific, actionable insight | 1-5 |

### Scoring

- **Deterministic score** (0-100): passed checks / total checks * 100
- **LLM judge score** (0-100): weighted average of J1-J6, normalized
- **Composite**: 40% deterministic + 60% LLM judge

| Grade | Score | Meaning |
|-------|-------|---------|
| A+ | 95-100 | Publish-ready |
| A | 90-94 | Strong, minor polish |
| B+ | 80-89 | Acceptable with edits |
| B | 70-79 | Needs revision |
| C | 60-69 | Significant drift |
| F | <60 | Reject and rewrite |

## Test Runner

```
python3 ${CLAUDE_SKILL_DIR}/scripts/eval_runner.py [OPTIONS]
```

### Options

| Flag | Description |
|------|-------------|
| `--caption "text"` | Evaluate a single caption |
| `--platform NAME` | Target platform (with --caption) |
| `--skill NAME` | Filter golden set by skill |
| `--deterministic-only` | Skip LLM judge (fast, free) |
| `--json` | JSON output |
| `--verbose` | Per-check details |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All cases grade B+ or above |
| 1 | Any case below B+ |
| 2 | Setup error |

## Prerequisites

- Python 3.10+
- For LLM judge: `ANTHROPIC_API_KEY` environment variable
- Golden set file: `${CLAUDE_SKILL_DIR}/references/golden-set.json`
- Voice samples: `${CLAUDE_SKILL_DIR}/../../shared/references/voice-samples.md`

## Relationship to Other QA Tools

| Tool | Tests | When |
|------|-------|------|
| `pytest` (226 tests) | Code correctness with mocks | After code changes |
| `/qa` | Skill file structure | After editing SKILL.md |
| `/qa-test` (52 tests) | Live MCP tool functionality | Before releases |
| **`/eval`** | **Content quality and brand voice** | **After prompt changes, model updates** |
