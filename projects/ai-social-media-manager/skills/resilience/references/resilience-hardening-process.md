# Resilience Hardening Process -- Complete Documentation

## Overview

This document describes the systematic resilience hardening process applied to the GHL Social Media Manager project. The process was conducted across 7 rounds (5 manual audit rounds + 2 automated rounds using the `/resilience` skill) and transformed the codebase from Grade D to Grade A+.

The approach is grounded in four industry standards:

1. **Netflix Chaos Engineering** -- assume every external call will fail; design for graceful degradation
2. **OWASP Top 10:2025 A10** -- mishandling exceptional conditions is a top security risk
3. **CWE-835** -- loop with unreachable exit condition (infinite hang prevention)
4. **Bash Strict Mode** (MIT SIPB / redsymbol.net) -- `set -euo pipefail` as foundational discipline

---

## The Audit Framework

### 20 Automated Checks

The `/resilience` skill performs 20 static analysis checks organized into 4 severity tiers:

| Tier | Weight | Count | Theme |
|------|--------|-------|-------|
| CRITICAL | 10 pts | 5 checks | Hangs, data loss, cascading failures |
| HIGH | 5 pts | 5 checks | Partial failures, security leaks, wasted retries |
| MEDIUM | 2 pts | 4 checks | Flakiness, resource waste, poor retry strategy |
| LOW | 1 pt | 3 checks | Portability, debugging, maintainability |

### Grading Scale

Total weighted demerits determine the letter grade:

| Grade | Demerits | Meaning |
|-------|----------|---------|
| A+ | 0 | Perfect resilience |
| A | 1-2 | Strong -- only LOW findings |
| A- | 3-5 | Strong with minor gaps |
| B+ | 6-10 | Good -- some MEDIUM findings |
| B | 11-15 | Good -- address HIGH items |
| B- | 16-25 | Moderate -- CRITICAL items may exist |
| C+ | 26-40 | Needs work |
| C/C- | 41-80 | Significant gaps |
| D | 81-100 | Poor resilience |
| F | 100+ | Systemic issues |

### Check Inventory

**CRITICAL checks (C1-C5):**
- C1: `curl` without `--max-time` (infinite hang on unresponsive API)
- C2: Python `urlopen()`/`requests` without `timeout=` (infinite block)
- C3: Bash script without `set -euo pipefail` (silent error propagation)
- C4: Playwright `page.goto()`/`page.set_content()` without `timeout=` (browser hang)
- C5: Browser launched without `try/finally: browser.close()` (zombie Chromium processes)

**HIGH checks (H1-H5):**
- H1: API curl call with no retry loop (single transient failure kills operation)
- H2: `curl | jq` pipe without HTTP status extraction (garbage data propagation)
- H3: `mktemp` without `trap ... EXIT` cleanup (temp file leak on interrupt)
- H4: `MAX_RETRIES > 5` (burns quota on sustained outage)
- H5: API key variable name in `echo`/`print` output (credential exposure risk)

**MEDIUM checks (M1-M4):**
- M1: Constant `sleep` in retry loop instead of exponential backoff (API hammering)
- M2: Batch loop without size cap (unbounded resource consumption)
- M3: `base64.b64encode()` without file size check (OOM on large files)
- M4: Async polling loop without wall-clock timeout (infinite wait)

**LOW checks (L1-L3):**
- L1: Error message to stdout instead of stderr (breaks piped workflows)
- L2: Bash 3.2 incompatible syntax (`declare -A`, `[[ -v ]]`) on macOS
- L3: File write without ensuring output directory exists (FileNotFoundError)

---

## Round-by-Round Progression

### Round 1 -- Baseline (Grade D)

**Scope:** 8 core GHL API scripts (create, upload, get_accounts, update, delete, carousel, next_slot, resolve_location).

**Findings:** Widespread lack of retry logic, no timeouts, no error isolation. Most scripts used bare `curl | jq` with no HTTP status checking.

**Fixes applied:**
- Added retry loops with `MAX_RETRIES=2` to all API scripts
- Added `--max-time 30` to curl calls in `ghl_get_accounts.sh`, `ghl_delete_post.sh`
- Added HTTP status extraction (`-w "\nHTTP_STATUS:%{http_code}"`) and `case` statements
- Added 401 detection with "Update GHL_API_KEY" user guidance
- Added 429 rate-limit handling with 10s backoff

### Round 2 -- Blog & Template Scripts (Grade C+)

**Scope:** Blog API scripts (`ghl_create_blog.sh`, `ghl_list_blogs.sh`) and template creation (`ghl_create_template.sh`).

**Fixes applied:**
- Full retry pattern applied to blog scripts
- `ghl_create_template.sh` hardened with retry on both API calls (create + upload HTML)
- Added `--max-time 30` to blog curl calls

### Round 3 -- Python Scripts & Distribution (Grade B-)

**Scope:** 6 Python scripts (drive_upload.py, pdf_to_slides.py, yt_search.py) and 3 bash scripts (ghl_delete_post.sh, ghl_list_blogs.sh, gws_backup_carousel.sh).

**Fixes applied:**
- `drive_upload.py`: Added MAX_FILE_SIZE (5GB), retry with exponential backoff on HttpError/ConnectionError
- `pdf_to_slides.py`: Wrapped page rendering in try/except with finally: page.close(), added skipped tracking
- `yt_search.py`: Rewrote `api_get()` with retry loop (max_retries=2, exponential backoff on 5xx)
- `gws_backup_carousel.sh`: Changed to `set -euo pipefail`, added fail count tracking
- All Python scripts: Added proper timeout parameters to network calls

### Round 4 -- Full Sweep (Grade A)

**Scope:** All remaining findings (2 CRITICAL, 3 HIGH, 3 MEDIUM, 1 LOW).

**Fixes applied:**
- `ghl_create_template.sh`: Added `--max-time 30` to both curl calls
- `ghl_create_blog.sh`: Added `--max-time 30`
- `render.py`: Added `timeout=30000` to Playwright calls, wrapped in try/finally
- `youtube_upload.py`: Reduced MAX_RETRIES from 10 to 5
- `rebrand.py`: Added logo file validation (empty check, 10MB limit), Playwright timeout, try/finally
- `gen_multimodal_slides.py`: Added input validation (max 20 slides, required fields)
- `create_pptx.py`: Added 100-slide safety cap
- `unsplash_fetch.py`: Added retry with exponential backoff to `api_request()`
- `gen_video_slide.py`: Added output directory auto-creation
- `ghl_upload_carousel.sh`: Fixed bash 3.2 compatibility (`[[ -v ]]` replaced with `${:-0}`)

### Round 5 -- Polish (Grade A)

**Scope:** 3 remaining LOW findings.

**Findings and disposition:**
1. `ghl_upload_carousel.sh` -- `declare -A` (bash 3.2 incompatible): **Fixed** -- replaced with `case` function
2. `unsplash_fetch.py` -- retry bounds (45s max): **Accepted** -- appropriate for stock photo API
3. `validate_ghl_post.py` -- relative hook path: **Accepted** -- by design, Claude Code hooks run from project root

### Round 6 -- /resilience Skill Created + First Automated Audit (Grade F -> A+)

**Scope:** Created the `/resilience` skill with 20 automated checks, then ran it against all 35 scripts.

**Initial automated scan found 27 genuine findings** that prior manual rounds had missed:
- 7 CRITICAL (6x curl without `--max-time`, 1x missing strict mode false positive)
- 1 HIGH (mktemp without trap cleanup)
- 11 MEDIUM (constant sleep in retry loops -- no exponential backoff)
- 8 LOW (7x error to stdout, 1x missing makedirs)

**All 27 findings fixed in this round:**
- Added `--max-time 30` (API calls) and `--max-time 60` (file uploads) to 6 remaining curl calls
- Added `trap cleanup_temps EXIT` to `ghl_upload_carousel.sh`
- Replaced `sleep 10` with `sleep $((5 + 2 ** ATTEMPT))` in all 11 retry loops across 11 scripts
- Added `>&2` to 7 error messages in `ghl_create_blog.sh`
- Added `os.makedirs()` to `generate_all.py`

**Final result: Grade A+ -- 0 findings across 35 scripts.**

---

## Patterns Established

### Standard Retry Pattern (Bash)

```bash
MAX_RETRIES=2
ATTEMPT=0

while true; do
  RESPONSE=$(curl -s --max-time 30 -w "\nHTTP_STATUS:%{http_code}" -X POST \
    "$API_BASE/endpoint" \
    -H "Authorization: Bearer ${GHL_API_KEY}" \
    -H "Version: ${GHL_VERSION}" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

  BODY=$(echo "$RESPONSE" | sed '/^HTTP_STATUS:/d')
  HTTP_CODE=$(echo "$RESPONSE" | grep '^HTTP_STATUS:' | cut -d: -f2)

  if [[ "$HTTP_CODE" == "429" ]] && [[ $ATTEMPT -lt $MAX_RETRIES ]]; then
    ATTEMPT=$((ATTEMPT + 1))
    WAIT=$((5 + 2 ** ATTEMPT))
    echo "Rate limited (429). Waiting ${WAIT}s (retry $ATTEMPT/$MAX_RETRIES)..." >&2
    sleep "$WAIT"
    continue
  fi
  break
done

case "$HTTP_CODE" in
  200|201)
    echo "$BODY"
    ;;
  401)
    echo "Error: Authentication failed (401). Update GHL_API_KEY." >&2
    exit 1
    ;;
  *)
    echo "Error: API returned HTTP $HTTP_CODE" >&2
    echo "$BODY" >&2
    exit 1
    ;;
esac
```

### Standard Retry Pattern (Python)

```python
import time
import urllib.error
import urllib.request

def api_request(url, headers=None, max_retries=2, timeout=15):
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (500, 502, 503) and attempt < max_retries:
                wait = 2 ** (attempt + 1)
                print(f"Warning: API {e.code}, retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            if e.code == 401:
                print("Error: Invalid API key (401).", file=sys.stderr)
            sys.exit(1)
        except urllib.error.URLError as e:
            if attempt < max_retries:
                wait = 2 ** (attempt + 1)
                time.sleep(wait)
                continue
            print(f"Error: Network request failed: {e.reason}", file=sys.stderr)
            sys.exit(1)
```

### Standard Playwright Pattern

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    try:
        page = browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=2,
        )
        page.set_content(html, wait_until="networkidle", timeout=30000)
        page.evaluate("() => document.fonts.ready")
        page.screenshot(path=output_path, full_page=False, type="png")
    finally:
        browser.close()
```

### Standard Temp File Pattern (Bash)

```bash
TEMP_FILES=()

cleanup() {
  for tmp in "${TEMP_FILES[@]}"; do rm -f "$tmp"; done
}
trap cleanup EXIT

# Create temp files, add to array
TMP=$(mktemp /tmp/work_XXXXXX.png)
TEMP_FILES+=("$TMP")
```

### Bash 3.2 Compatibility Rules

macOS ships bash 3.2.57. These features are NOT available:

| Feature | Bash version | Workaround |
|---------|-------------|------------|
| `declare -A` (associative arrays) | 4.0+ | Use `case` function |
| `[[ -v VAR ]]` (variable existence) | 4.3+ | Use `${VAR:-default}` |
| `declare -n` (namerefs) | 4.3+ | Use `eval` or indirect expansion |
| `readarray` / `mapfile` | 4.0+ | Use `while read` loop |

---

## Files Modified

### Bash Scripts (14 files)

| File | Changes |
|------|---------|
| `.claude/shared/scripts/ghl_create_post.sh` | --max-time 30, retry loop, 401 handling, backoff |
| `.claude/shared/scripts/ghl_upload_media.sh` | --max-time 30/60, retry loop, 401 handling, backoff |
| `.claude/shared/scripts/ghl_upload_carousel.sh` | --max-time 60, bash 3.2 compat (declare -A -> case), trap cleanup, backoff |
| `.claude/shared/scripts/ghl_get_accounts.sh` | --max-time 30, retry loop, 401 handling, backoff |
| `.claude/shared/scripts/ghl_update_post.sh` | --max-time 30, retry loop, 401 handling, backoff |
| `.claude/shared/scripts/ghl_delete_post.sh` | --max-time 30, retry loop, 401 handling, backoff |
| `.claude/shared/scripts/ghl_create_template.sh` | --max-time 30 (both calls), retry loops, 401 handling, backoff |
| `.claude/shared/scripts/ghl_search_contacts.sh` | --max-time 30, retry loop, backoff |
| `.claude/shared/scripts/ghl_send_email.sh` | --max-time 30, backoff |
| `.claude/shared/scripts/gws_backup_carousel.sh` | set -euo pipefail, unbound var fix, fail tracking |
| `.claude/shared/scripts/next_slot.sh` | (no API calls -- already clean) |
| `.claude/shared/scripts/resolve_location.sh` | (no API calls -- already clean) |
| `.claude/skills/blog/scripts/ghl_create_blog.sh` | --max-time 30, backoff, stderr for errors |
| `.claude/skills/blog/scripts/ghl_list_blogs.sh` | retry loop, 401 handling, backoff |

### Python Scripts (10 files)

| File | Changes |
|------|---------|
| `.claude/shared/scripts/render.py` | Playwright timeout=30000, try/finally browser cleanup |
| `.claude/shared/scripts/rebrand.py` | Logo validation (empty/10MB), Playwright timeout, try/finally |
| `.claude/shared/scripts/youtube_upload.py` | MAX_RETRIES 10->5, upload timeout, chunk timeout |
| `.claude/shared/scripts/drive_upload.py` | MAX_FILE_SIZE 5GB, retry with backoff on HttpError |
| `.claude/shared/scripts/unsplash_fetch.py` | Retry with backoff on 5xx, URLError |
| `.claude/shared/scripts/pdf_to_slides.py` | try/except with finally: page.close(), skipped tracking |
| `.claude/shared/scripts/gen_multimodal_slides.py` | Input validation (max 20 slides, required fields) |
| `.claude/shared/scripts/gen_video_slide.py` | Output directory auto-creation |
| `.claude/skills/yt-search/scripts/yt_search.py` | Retry with backoff in api_get() |
| `.claude/skills/presentation/scripts/create_pptx.py` | 100-slide safety cap |

### Audit Tooling (3 files)

| File | Purpose |
|------|---------|
| `.claude/skills/resilience/SKILL.md` | Skill definition (114 lines) |
| `.claude/skills/resilience/scripts/resilience_audit.py` | 20-check automated scanner (490 lines) |
| `.claude/skills/resilience/references/checklist.md` | Full checklist with CWE/OWASP sources |

---

## Running the Audit

### Full codebase audit

```bash
python3 .claude/skills/resilience/scripts/resilience_audit.py
```

### Single file audit

```bash
python3 .claude/skills/resilience/scripts/resilience_audit.py --path .claude/shared/scripts/ghl_create_post.sh
```

### Only CRITICAL + HIGH findings

```bash
python3 .claude/skills/resilience/scripts/resilience_audit.py --severity high
```

### With fix hints

```bash
python3 .claude/skills/resilience/scripts/resilience_audit.py --fix-hints
```

### Machine-readable JSON

```bash
python3 .claude/skills/resilience/scripts/resilience_audit.py --json
```

### Via Claude Code skill

```
/resilience
```

---

## Iterative Hardening Playbook

For applying this process to a new codebase:

1. **Run baseline audit** (`/resilience`). Record grade and finding count.
2. **Fix CRITICAL findings first.** These cause hangs and data loss. Target: eliminate all CRITICAL.
3. **Fix HIGH findings.** These cause partial failures and security issues. Target: B grade or better.
4. **Fix MEDIUM findings.** These cause flakiness and resource waste. Target: A- or better.
5. **Review LOW findings.** Fix or accept with rationale. Target: A/A+.
6. **Re-run audit after each round** to verify fixes and track progression.
7. **Run `/qa --all`** alongside to validate skill structure hasn't regressed.

Typical progression: F -> C+ -> B- -> A -> A+ across 3-4 focused rounds.

---

## Key Lessons

1. **Timeout everything.** Every HTTP call, every browser navigation, every polling loop needs a maximum duration. "No timeout" equals "infinite timeout."

2. **Retry only retriable errors.** 429 and 5xx are retriable. 400, 401, 403, 404 are not. Retrying client errors wastes time and masks bugs.

3. **Exponential backoff is mandatory.** Constant `sleep 10` hammers an already-overloaded API. Use `sleep $((5 + 2 ** ATTEMPT))` or equivalent.

4. **Always clean up.** `trap ... EXIT` for temp files. `try/finally` for browser processes. Resources leak on interrupt otherwise.

5. **Errors go to stderr.** Error messages on stdout corrupt piped data. Always use `>&2` in bash, `file=sys.stderr` in Python.

6. **Know your bash version.** macOS ships bash 3.2.57. `declare -A`, `[[ -v ]]`, and namerefs don't exist. Test with `bash -n` before deploying.

7. **Static analysis catches what manual review misses.** The automated audit found 27 issues after 5 manual rounds had already achieved "Grade A." The automation's consistency exposed systematic patterns (like constant sleep) that human reviewers normalized.

---

*Document created: 2026-03-08*
*Audit tool: `/resilience` (resilience_audit.py v1.0)*
*Final grade: A+ (0 findings, 35 scripts scanned)*
