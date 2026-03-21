# Resilience Audit Checklist

Grounded in Netflix Chaos Engineering, OWASP A10 (Mishandling Exceptional Conditions), CWE-835 (Infinite Loop), and bash strict mode best practices.

## CRITICAL (Hangs, data loss, cascading failures)

### C1: Missing HTTP timeout (curl)
- **Detect:** `curl` calls without `--max-time` or `--connect-timeout`
- **Pattern:** `curl` without `--max-time \d+`
- **Risk:** CWE-835. Unresponsive endpoint hangs the script forever.
- **Fix:** Add `--max-time 30` to every curl call.

### C2: Missing HTTP timeout (Python urllib/requests)
- **Detect:** `urlopen(`, `requests.get(`, `requests.post(` without `timeout=`
- **Pattern:** `urlopen\(` or `requests\.(get|post|put|delete)\(` without `timeout`
- **Risk:** Python's urllib and requests have no default timeout. Process blocks indefinitely.
- **Fix:** Add `timeout=15` (or appropriate value) to every network call.

### C3: Missing bash strict mode
- **Detect:** Bash scripts without `set -e`, `set -u`, or `set -o pipefail`
- **Pattern:** Absence of `set -euo pipefail` or individual `set -e` near top
- **Risk:** Failed commands silently ignored. Script continues in corrupted state.
- **Fix:** Add `set -euo pipefail` after shebang.

### C4: Missing Playwright browser timeout
- **Detect:** `page.goto(` or `page.set_content(` without `timeout=` parameter
- **Pattern:** `page\.(goto|set_content)\(` without `timeout`
- **Risk:** Browser automation hangs indefinitely on unresponsive pages.
- **Fix:** Add `timeout=30000` (30s) to navigation calls.

### C5: Missing browser cleanup (try/finally)
- **Detect:** `browser = p.chromium.launch(` without a surrounding `try/finally: browser.close()`
- **Pattern:** `browser.close()` not in a `finally:` block
- **Risk:** Browser process leak on exception. Accumulates zombie Chromium processes.
- **Fix:** Wrap browser usage in `try: ... finally: browser.close()`.

## HIGH (Partial failures, wasted retries, security issues)

### H1: No retry logic on API calls
- **Detect:** `curl` or `urlopen`/`requests` calls with no surrounding retry/loop
- **Pattern:** API call not inside a `while`/`for` loop with retry counter
- **Risk:** Single transient failure (429, 500, 502, 503) kills entire operation.
- **Fix:** Add retry loop with MAX_RETRIES, backoff on 429/5xx.

### H2: Retrying non-retriable errors
- **Detect:** Retry loops that don't distinguish HTTP status codes (retrying 400, 401, 403, 404)
- **Pattern:** Retry loop without `if` checking specific status codes
- **Risk:** Wastes time and API quota on errors that will never self-resolve.
- **Fix:** Only retry on 429, 500, 502, 503, 504. Exit immediately on 401, 400.

### H3: No HTTP status code check
- **Detect:** `curl` calls without `-f`, `-w '%{http_code}'`, or `$?` check
- **Pattern:** `curl` piped directly to `jq` with no status extraction
- **Risk:** 422/500 error body treated as valid data. Corrupts downstream processing.
- **Fix:** Extract HTTP status with `-w "\nHTTP_STATUS:%{http_code}"` and check before processing.

### H4: No trap cleanup handler (bash)
- **Detect:** Scripts using `mktemp` or writing to `/tmp/` without `trap ... EXIT`
- **Pattern:** `mktemp` without corresponding `trap`
- **Risk:** Temp files accumulate after Ctrl+C, crash, or error exit.
- **Fix:** Add `trap 'rm -f "$TMPFILE"' EXIT` after creating temp files.

### H5: Sensitive data in error output
- **Detect:** API keys interpolated into URLs or error messages; `curl -v` in production
- **Pattern:** `$GHL_API_KEY` or `$GEMINI_API_KEY` in echo/print statements
- **Risk:** OWASP A10. Credentials leak into logs or terminal history.
- **Fix:** Never echo credentials. Use `Bearer ${VAR}` in headers only.

### H6: Unbounded retry count
- **Detect:** Retry loops with MAX_RETRIES > 5 or no upper bound
- **Pattern:** `MAX_RETRIES` value > 5, or `while true` without retry counter
- **Risk:** On sustained outage, script runs for hours burning API quota.
- **Fix:** Cap retries at 2-5 with exponential backoff.

## MEDIUM (Flakiness, resource waste, poor observability)

### M1: No exponential backoff
- **Detect:** Retry loops with fixed `sleep` interval instead of increasing delays
- **Pattern:** `sleep 10` (constant) inside retry loop, no `2**attempt` or multiplier
- **Risk:** Hammers overloaded API. Can trigger rate limiting or IP bans.
- **Fix:** Use `sleep $((2 ** attempt))` or equivalent exponential formula.

### M2: No input validation on batch operations
- **Detect:** Scripts accepting arrays/lists without size caps or type checks
- **Pattern:** Processing `slides`, `files`, `urls` arrays without length validation
- **Risk:** Unbounded input causes OOM, excessive API calls, or hour-long runs.
- **Fix:** Add MAX_ITEMS cap. Validate required fields before processing.

### M3: No pipefail in piped commands
- **Detect:** Pipes like `curl ... | jq ...` in scripts without `set -o pipefail`
- **Pattern:** `|` in commands, script lacks `pipefail`
- **Risk:** Left side of pipe fails silently. jq parses empty input, produces garbage.
- **Fix:** Include `pipefail` in `set -euo pipefail`.

### M4: File size validation missing
- **Detect:** File uploads or processing without checking file size (empty or too large)
- **Pattern:** `open(`, `Image.open(`, `base64.b64encode(` without prior size check
- **Risk:** Empty files cause silent failures. Huge files exhaust memory or hit API limits.
- **Fix:** Check `os.path.getsize()` before processing. Set min/max bounds.

### M5: No async polling timeout
- **Detect:** Polling loops (checking operation status) without wall-clock timeout
- **Pattern:** `while` loop checking status without elapsed time comparison
- **Risk:** If upstream service never completes, polling runs forever.
- **Fix:** Track start time and enforce max duration (e.g., 600s).

## LOW (Maintainability, portability, debugging)

### L1: No structured error output
- **Detect:** Using bare `echo` for errors instead of stderr with context
- **Pattern:** `echo "Error..."` without `>&2` redirect
- **Risk:** Error messages mixed with stdout data. Hard to triage in pipelines.
- **Fix:** Always use `echo "..." >&2` or `print(..., file=sys.stderr)`.

### L2: Bash 3.2 incompatibility
- **Detect:** `declare -A` (associative arrays), `[[ -v ]]`, nameref (`declare -n`)
- **Pattern:** `declare -A`, `[[ -v`, `declare -n`
- **Risk:** macOS ships bash 3.2.57. These features require bash 4.0+.
- **Fix:** Replace with `case` statements or `${VAR:-default}` expansion.

### L3: Unquoted variable expansions
- **Detect:** `$VAR` instead of `"$VAR"` in file paths and command arguments
- **Pattern:** Unquoted `$` references not inside `$(())`
- **Risk:** Word splitting on filenames with spaces. Glob expansion on wildcards.
- **Fix:** Always double-quote: `"$VAR"`, `"${ARRAY[@]}"`.

### L4: Missing output directory creation
- **Detect:** Writing to `args.output` or file path without ensuring parent dir exists
- **Pattern:** `open(output_path, "w")` without prior `os.makedirs(dirname, exist_ok=True)`
- **Risk:** Script fails with FileNotFoundError on first run.
- **Fix:** Add `os.makedirs(os.path.dirname(path), exist_ok=True)` before writes.

## Sources

- Netflix Chaos Engineering Principles: https://principlesofchaos.org/
- OWASP Top 10:2025 A10 -- Mishandling Exceptional Conditions
- CWE-835: Loop with Unreachable Exit Condition
- CWE-728: Improper Error Handling
- Bash Strict Mode: http://redsymbol.net/articles/unofficial-bash-strict-mode/
- MIT SIPB Safe Shell Scripting: https://sipb.mit.edu/doc/safe-shell/
- Playwright Timeout Best Practices: https://playwright.dev/docs/test-timeouts
