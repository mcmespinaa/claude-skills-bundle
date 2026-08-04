---
name: qa-test
description: >-
  Live functional testing of the MCP server. Runs through all 18 tools, 5
  resources, and 5 prompts with real and mock inputs, reporting pass/fail per
  test. Use when user says /qa-test, test the MCP server, run functional tests,
  smoke test, or integration test.
allowed-tools: "Bash(python3:*) Read Glob Grep Agent"
---

# /qa-test -- MCP Server Functional Test Runner

> **Trigger:** `/qa-test`, `/qa-test --smoke`, `/qa-test --section posts`, "test the MCP server", "run functional tests", "smoke test the server"
> **Do NOT use for:** Skill file validation (use /qa), script resilience checks (use /resilience), or unit tests with mocks (use pytest).

## Purpose

Live functional testing of the GHL Social MCP Server. Unlike `/qa` (which checks skill file structure) and `pytest` (which runs unit tests with mocks), `/qa-test` calls real MCP tools against the live GHL API and reports pass/fail results.

## Usage

- `/qa-test` -- Run full test suite (all sections)
- `/qa-test --smoke` -- Quick smoke test (one test per tool, ~2 min)
- `/qa-test --section posts` -- Run one section only
- `/qa-test --section validation` -- Test caption validation only
- `/qa-test --dry-run` -- Show test plan without executing
- `/qa-test --skip-destructive` -- Skip delete/send operations

## Sections

| Section | Tools Tested | Tests | Destructive |
|---------|-------------|-------|-------------|
| `startup` | server.py | 5 | No |
| `validation` | validate_caption | 12 | No |
| `scheduling` | get_next_slot | 6 | No |
| `resources` | all 5 resources | 10 | No |
| `accounts` | get_accounts, search_contacts | 8 | No |
| `posts` | create_post, get_post, update_post, delete_post | 15 | Yes (delete) |
| `media` | upload_media, upload_carousel | 10 | No |
| `email` | send_email, create_email_template | 8 | Yes (send) |
| `youtube` | youtube_search, youtube_transcript, youtube_channel_analysis | 12 | No |
| `notebooklm` | notebooklm_create, notebooklm_query, notebooklm_generate | 8 | No |
| `prompts` | all 5 prompts | 5 | No |

## Test Execution Order

Tests run in dependency order. Non-destructive tests first:

1. **startup** -- Verify server starts, tools register
2. **validation** -- Caption quality gate (no API calls)
3. **scheduling** -- Next slot calculation (reads local file only)
4. **resources** -- Read-only data providers
5. **accounts** -- List accounts, search contacts (read-only API)
6. **youtube** -- Search, transcript, channel analysis (read-only API)
7. **media** -- Upload images (creates media in GHL, but harmless)
8. **posts** -- Full lifecycle: create -> get -> update -> delete
9. **email** -- Send test email, create template
10. **notebooklm** -- Create notebook, query, generate (requires CLI)
11. **prompts** -- Verify prompt templates return valid instructions

## Test Runner Script

Run the automated test suite:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/qa_test_runner.py [OPTIONS]
```

### Options

| Flag | Description |
|------|-------------|
| `--smoke` | One test per tool (fast, ~2 min) |
| `--section NAME` | Run one section only |
| `--skip-destructive` | Skip delete_post, send_email |
| `--dry-run` | Print test plan, don't execute |
| `--json` | Output results as JSON |
| `--verbose` | Show request/response details |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | One or more tests failed |
| 2 | Setup error (missing env vars, server won't start) |

## Prerequisites

Before running, verify:

1. `GHL_API_KEY` and `GHL_LOCATION_ID` are set
2. `locations.json` has a valid location entry
3. `ghl_accounts_map.json` has at least one platform
4. At least one social account connected in GHL
5. For YouTube tests: `YOUTUBE_API_KEY` set
6. For NotebookLM tests: `notebooklm` CLI installed and authenticated

The runner checks prerequisites automatically and skips sections with missing deps (reported as SKIP, not FAIL).

## Workflow

### Step 1 -- Parse Arguments
Read flags: `--smoke`, `--section`, `--skip-destructive`, `--dry-run`, `--json`, `--verbose`.

### Step 2 -- Check Prerequisites
Verify env vars, config files, optional dependencies. Report which sections will be skipped.

### Step 3 -- Run Tests
Execute each section in order. For each test:
1. Print test name
2. Call the MCP tool with test inputs
3. Assert expected outcome (success, specific error, response shape)
4. Record PASS / FAIL / SKIP / ERROR
5. On FAIL: print expected vs actual, continue to next test

### Step 4 -- Report Results
Print summary table:

```
Section         Tests  Pass  Fail  Skip
-------         -----  ----  ----  ----
startup           5      5     0     0
validation       12     12     0     0
scheduling        6      6     0     0
resources        10     10     0     0
accounts          8      7     0     1
posts            15     14     1     0
media            10     10     0     0
email             8      6     0     2
youtube          12     12     0     0
notebooklm        8      0     0     8
prompts           5      5     0     0
-------         -----  ----  ----  ----
TOTAL            99     87     1    11

Result: FAIL (1 failure)
```

### Step 5 -- Cleanup
Delete any test posts, media, or templates created during testing. Report cleanup status.

## Test Data

The runner uses safe, identifiable test data:

- **Test caption:** `"QA test post - safe to delete. Created by qa-test runner at {timestamp}."`
- **Test schedule:** 7 days in the future (won't conflict with real posts)
- **Test image:** 1x1 pixel ivory PNG (generated in-memory, no file dependency)
- **Test email subject:** `"[QA TEST] Do not reply - {timestamp}"`
- **Test notebook title:** `"QA Test Notebook {timestamp}"`
- **Test tag:** Searches for contacts tagged "qa-test" (create this tag for safe testing)

All test artifacts are prefixed with "QA test" or "[QA TEST]" for easy identification and cleanup.

## Relationship to Other QA Tools

| Tool | What it tests | When to use |
|------|--------------|-------------|
| `pytest` (226 tests) | Unit tests with mocked APIs | After code changes, in CI |
| `/qa` | Skill file structure (YAML, paths) | After editing SKILL.md files |
| `/resilience` | Script robustness (timeouts, retries) | After adding new scripts |
| **`/qa-test`** | **Live MCP tools against real APIs** | **Before releases, after deploy** |

## Notes

- Tests that create GHL resources (posts, templates) are cleaned up automatically
- The `--skip-destructive` flag prevents delete_post and send_email from running
- YouTube and NotebookLM sections are auto-skipped if their dependencies are missing
- Running against production GHL is safe -- test posts are scheduled 7 days out and auto-deleted
- Each test has a 30-second timeout to prevent hanging on API issues
