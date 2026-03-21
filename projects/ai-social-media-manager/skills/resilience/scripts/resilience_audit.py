#!/usr/bin/env python3
"""resilience_audit.py -- Static analysis resilience auditor for bash and Python scripts.

Scans scripts for resilience anti-patterns grounded in:
- Netflix Chaos Engineering principles
- OWASP A10 (Mishandling Exceptional Conditions)
- CWE-835 (Loop with Unreachable Exit Condition)
- Bash strict mode best practices

Usage:
    python3 resilience_audit.py                    # Audit all scripts
    python3 resilience_audit.py --path script.sh   # Audit one file
    python3 resilience_audit.py --severity high     # Only HIGH+ findings
    python3 resilience_audit.py --json             # Machine-readable output
    python3 resilience_audit.py --fix-hints        # Include remediation hints

Output: Graded report (A-F) with per-finding severity, evidence, and fix hints.
Errors go to stderr, report to stdout.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent  # .claude/skills/resilience/scripts -> project root

# Directories to scan (relative to project root)
SCAN_DIRS = [
    ".claude/shared/scripts",
    ".claude/skills",
    ".claude/hooks",
    "carousel_slides",
    "carousel_temp",
]

# Severity weights for grading
SEVERITY_WEIGHT = {"CRITICAL": 10, "HIGH": 5, "MEDIUM": 2, "LOW": 1}
SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

# Grade thresholds (total weighted demerits)
GRADE_THRESHOLDS = [
    (0, "A+"),
    (2, "A"),
    (5, "A-"),
    (10, "B+"),
    (15, "B"),
    (25, "B-"),
    (40, "C+"),
    (60, "C"),
    (80, "C-"),
    (100, "D"),
]

# Terminal colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

SEVERITY_COLOR = {
    "CRITICAL": RED,
    "HIGH": RED,
    "MEDIUM": YELLOW,
    "LOW": CYAN,
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    check_id: str
    severity: str
    title: str
    file: str
    line: int = 0
    evidence: str = ""
    fix_hint: str = ""


# ---------------------------------------------------------------------------
# Check registry
# ---------------------------------------------------------------------------

# Each check is a function(filepath, content, lines) -> list[Finding]
CHECKS: list = []


def check(check_id, severity, title, filetypes, fix_hint=""):
    """Decorator to register a resilience check."""
    def decorator(fn):
        fn._check_id = check_id
        fn._severity = severity
        fn._title = title
        fn._filetypes = filetypes
        fn._fix_hint = fix_hint
        CHECKS.append(fn)
        return fn
    return decorator


# ---------------------------------------------------------------------------
# CRITICAL checks
# ---------------------------------------------------------------------------

@check("C1", "CRITICAL", "Missing HTTP timeout (curl)", {".sh"},
       fix_hint="Add --max-time 30 to every curl call")
def check_curl_timeout(filepath, content, lines):
    findings = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "curl " in line or "curl\t" in line:
            # Check if this curl call or its continuation has --max-time or --connect-timeout
            # Look at this line and the next 5 lines for multi-line curl commands
            block = "\n".join(lines[max(0, i - 1):min(len(lines), i + 5)])
            if "--max-time" not in block and "--connect-timeout" not in block:
                findings.append(Finding(
                    check_id="C1", severity="CRITICAL",
                    title="curl call without --max-time",
                    file=filepath, line=i,
                    evidence=stripped[:100],
                    fix_hint="Add --max-time 30 to prevent indefinite hangs",
                ))
    return findings


@check("C2", "CRITICAL", "Missing HTTP timeout (Python)", {".py"},
       fix_hint="Add timeout= parameter to every network call")
def check_python_timeout(filepath, content, lines):
    findings = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # urllib.request.urlopen without timeout
        if "urlopen(" in line and "timeout" not in line:
            # Check next 2 lines for multiline calls
            block = "\n".join(lines[max(0, i - 1):min(len(lines), i + 2)])
            if "timeout" not in block:
                findings.append(Finding(
                    check_id="C2", severity="CRITICAL",
                    title="urlopen() without timeout",
                    file=filepath, line=i,
                    evidence=stripped[:100],
                    fix_hint="Add timeout=15 parameter",
                ))
        # requests.get/post/put/delete without timeout
        for method in ("get", "post", "put", "delete", "patch"):
            pattern = f"requests.{method}("
            if pattern in line and "timeout" not in line:
                block = "\n".join(lines[max(0, i - 1):min(len(lines), i + 2)])
                if "timeout" not in block:
                    findings.append(Finding(
                        check_id="C2", severity="CRITICAL",
                        title=f"requests.{method}() without timeout",
                        file=filepath, line=i,
                        evidence=stripped[:100],
                        fix_hint=f"Add timeout=15 parameter",
                    ))
    return findings


@check("C3", "CRITICAL", "Missing bash strict mode", {".sh"},
       fix_hint="Add set -euo pipefail after shebang")
def check_bash_strict_mode(filepath, content, lines):
    findings = []
    # Check first 25 lines for strict mode (usage headers can push it down)
    head = "\n".join(lines[:25])
    has_set_e = "set -e" in head or "set -euo" in head
    if not has_set_e:
        findings.append(Finding(
            check_id="C3", severity="CRITICAL",
            title="Missing set -e (or set -euo pipefail)",
            file=filepath, line=1,
            evidence="No strict mode in first 10 lines",
            fix_hint="Add set -euo pipefail after the shebang line",
        ))
    return findings


@check("C4", "CRITICAL", "Missing Playwright browser timeout", {".py"},
       fix_hint="Add timeout=30000 to page.goto() and page.set_content()")
def check_playwright_timeout(filepath, content, lines):
    findings = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for method in ("page.goto(", "page.set_content("):
            if method in line:
                # Check this line and next 2 for timeout param
                block = "\n".join(lines[max(0, i - 1):min(len(lines), i + 2)])
                if "timeout" not in block:
                    findings.append(Finding(
                        check_id="C4", severity="CRITICAL",
                        title=f"{method.rstrip('(')} without timeout",
                        file=filepath, line=i,
                        evidence=stripped[:100],
                        fix_hint="Add timeout=30000 (30s) parameter",
                    ))
    return findings


@check("C5", "CRITICAL", "Missing browser cleanup (try/finally)", {".py"},
       fix_hint="Wrap browser usage in try: ... finally: browser.close()")
def check_browser_cleanup(filepath, content, lines):
    findings = []
    # Skip self (this script references chromium.launch as a string literal)
    if Path(filepath).name == "resilience_audit.py":
        return findings
    if "chromium.launch(" not in content:
        return findings

    # Check that browser.close() is inside a finally block
    has_try_finally = False
    in_try = False
    in_finally = False
    browser_close_in_finally = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "try:" in stripped:
            in_try = True
        elif "finally:" in stripped and in_try:
            in_finally = True
        elif in_finally and "browser.close()" in stripped:
            browser_close_in_finally = True
            break
        elif stripped and not stripped.startswith("#") and in_finally and not stripped.startswith(("pass", "browser")):
            in_finally = False

    if not browser_close_in_finally:
        # Find the launch line
        for i, line in enumerate(lines, 1):
            if "chromium.launch(" in line:
                findings.append(Finding(
                    check_id="C5", severity="CRITICAL",
                    title="browser.close() not in finally block",
                    file=filepath, line=i,
                    evidence=line.strip()[:100],
                    fix_hint="Add try: ... finally: browser.close() to prevent zombie processes",
                ))
                break

    return findings


# ---------------------------------------------------------------------------
# HIGH checks
# ---------------------------------------------------------------------------

@check("H1", "HIGH", "No retry logic on API calls", {".sh"},
       fix_hint="Add retry loop with MAX_RETRIES on 429/5xx")
def check_bash_retry(filepath, content, lines):
    findings = []
    # If the script makes curl calls to APIs but has no while/retry pattern
    has_curl_api = bool(re.search(r"curl\b.*https?://", content))
    has_retry = "retry" in content.lower() or "MAX_RETRIES" in content or "ATTEMPT" in content
    has_while = "while " in content or "while\t" in content

    if has_curl_api and not has_retry and not has_while:
        # Find the first curl call
        for i, line in enumerate(lines, 1):
            if "curl " in line and "http" in line:
                findings.append(Finding(
                    check_id="H1", severity="HIGH",
                    title="API curl call without retry logic",
                    file=filepath, line=i,
                    evidence=line.strip()[:100],
                    fix_hint="Wrap in retry loop: while true; do ... if [[ 429 ]]; then sleep; continue; fi; break; done",
                ))
                break
    return findings


@check("H2", "HIGH", "No HTTP status code check", {".sh"},
       fix_hint='Extract status with -w "\\nHTTP_STATUS:%{http_code}" and check before processing')
def check_bash_status_check(filepath, content, lines):
    findings = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # curl piped directly to jq without status extraction
        if re.search(r"curl\b.*\|\s*jq\b", line):
            # Check if the surrounding context has HTTP_STATUS extraction
            block = "\n".join(lines[max(0, i - 6):min(len(lines), i + 5)])
            if "HTTP_STATUS" not in block and "http_code" not in block and "-f " not in line:
                findings.append(Finding(
                    check_id="H2", severity="HIGH",
                    title="curl piped to jq without HTTP status check",
                    file=filepath, line=i,
                    evidence=stripped[:100],
                    fix_hint='Use -w "\\nHTTP_STATUS:%{http_code}" and check status before processing',
                ))
    return findings


@check("H3", "HIGH", "No trap cleanup for temp files", {".sh"},
       fix_hint='Add trap \'rm -f "$TMPFILE"\' EXIT after mktemp')
def check_bash_trap(filepath, content, lines):
    findings = []
    has_mktemp = "mktemp" in content
    has_trap = "trap " in content or "trap\t" in content
    if has_mktemp and not has_trap:
        for i, line in enumerate(lines, 1):
            if "mktemp" in line:
                findings.append(Finding(
                    check_id="H3", severity="HIGH",
                    title="mktemp without trap cleanup",
                    file=filepath, line=i,
                    evidence=line.strip()[:100],
                    fix_hint="Add trap 'rm -f \"$tmpfile\"' EXIT to clean up on any exit",
                ))
                break
    return findings


@check("H4", "HIGH", "Unbounded retry count", {".sh", ".py"},
       fix_hint="Cap MAX_RETRIES at 5 or fewer")
def check_unbounded_retry(filepath, content, lines):
    findings = []
    for i, line in enumerate(lines, 1):
        # Check for MAX_RETRIES > 5
        m = re.search(r"MAX_RETRIES\s*=\s*(\d+)", line)
        if m:
            val = int(m.group(1))
            if val > 5:
                findings.append(Finding(
                    check_id="H4", severity="HIGH",
                    title=f"MAX_RETRIES = {val} (too high)",
                    file=filepath, line=i,
                    evidence=line.strip()[:100],
                    fix_hint="Cap at 5. On sustained outage, more retries burn quota without benefit.",
                ))
        # Check for max_retries > 5
        m = re.search(r"max_retries\s*=\s*(\d+)", line)
        if m:
            val = int(m.group(1))
            if val > 5:
                findings.append(Finding(
                    check_id="H4", severity="HIGH",
                    title=f"max_retries = {val} (too high)",
                    file=filepath, line=i,
                    evidence=line.strip()[:100],
                    fix_hint="Cap at 5.",
                ))
    return findings


@check("H5", "HIGH", "Sensitive data in error output", {".sh", ".py"},
       fix_hint="Never echo/print API keys. Use in headers only.")
def check_credential_leak(filepath, content, lines):
    findings = []
    sensitive_vars = [
        "GHL_API_KEY", "GEMINI_API_KEY", "YOUTUBE_API_KEY",
        "UNSPLASH_ACCESS_KEY", "api_key", "access_token",
    ]
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        for var in sensitive_vars:
            # Check if key is in an echo/print statement (not in a header assignment)
            if var in line:
                low = line.lower()
                if any(kw in low for kw in ("echo", "print(", "print ", "log(", "logger.")):
                    # Exclude lines that are instructions/checks, not actual leaks
                    if any(kw in low for kw in ("not set", "missing", "****", "update ", "expired", "invalid")):
                        continue
                    findings.append(Finding(
                        check_id="H5", severity="HIGH",
                        title=f"Potential credential in output: {var}",
                        file=filepath, line=i,
                        evidence=stripped[:100],
                        fix_hint=f"Never echo {var}. Use in Authorization headers only.",
                    ))
    return findings


# ---------------------------------------------------------------------------
# MEDIUM checks
# ---------------------------------------------------------------------------

@check("M1", "MEDIUM", "No exponential backoff in retry", {".sh", ".py"},
       fix_hint="Use exponential delay: sleep $((2 ** attempt)) or time.sleep(2 ** attempt)")
def check_backoff(filepath, content, lines):
    findings = []
    # Only relevant if there IS a retry loop
    has_retry = "retry" in content.lower() or "MAX_RETRIES" in content or "ATTEMPT" in content
    if not has_retry:
        return findings

    # Check if backoff is exponential or constant
    has_exp = bool(re.search(r"2\s*\*\*\s*(attempt|retry|ATTEMPT)", content))
    has_exp = has_exp or "exponential" in content.lower()
    has_exp = has_exp or bool(re.search(r"wait\s*\*=", content))  # wait *= 1.5

    if not has_exp:
        # Check for constant sleep in retry context
        for i, line in enumerate(lines, 1):
            if re.search(r"sleep\s+\d+", line):
                # Is this inside a retry loop? Check surrounding context
                block = "\n".join(lines[max(0, i - 10):i])
                if "retry" in block.lower() or "attempt" in block.lower() or "while" in block.lower():
                    findings.append(Finding(
                        check_id="M1", severity="MEDIUM",
                        title="Constant sleep in retry loop (no backoff)",
                        file=filepath, line=i,
                        evidence=line.strip()[:100],
                        fix_hint="Use exponential backoff: sleep $((2 ** ATTEMPT))",
                    ))
                    break
    return findings


@check("M2", "MEDIUM", "No input validation on batch operations", {".py"},
       fix_hint="Add MAX_ITEMS cap and validate required fields before processing")
def check_batch_validation(filepath, content, lines):
    findings = []
    # Look for batch processing patterns without bounds
    batch_patterns = [
        (r"for\s+\w+\s+in\s+slides", "slides"),
        (r"for\s+\w+\s+in\s+files", "files"),
        (r"for\s+\w+\s+in\s+pages", "pages"),
    ]
    for pattern, item_type in batch_patterns:
        if re.search(pattern, content):
            # Check if there's a length validation before the loop
            has_max = bool(re.search(rf"len\({item_type}\)\s*>", content))
            has_max = has_max or bool(re.search(rf"MAX_\w+", content))
            if not has_max:
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        findings.append(Finding(
                            check_id="M2", severity="MEDIUM",
                            title=f"Batch loop over '{item_type}' without size cap",
                            file=filepath, line=i,
                            evidence=line.strip()[:100],
                            fix_hint=f"Add MAX_{item_type.upper()} cap before processing",
                        ))
                        break
    return findings


@check("M3", "MEDIUM", "File operation without size validation", {".py"},
       fix_hint="Check os.path.getsize() before processing files")
def check_file_size_validation(filepath, content, lines):
    findings = []
    # base64.b64encode of file data without size check
    if "b64encode" in content or "base64.b64encode" in content:
        has_size_check = "stat().st_size" in content or "getsize" in content or "file_size" in content.lower()
        if not has_size_check:
            for i, line in enumerate(lines, 1):
                if "b64encode" in line:
                    findings.append(Finding(
                        check_id="M3", severity="MEDIUM",
                        title="base64 encoding without file size check",
                        file=filepath, line=i,
                        evidence=line.strip()[:100],
                        fix_hint="Check file size before encoding to prevent OOM on large files",
                    ))
                    break
    return findings


@check("M4", "MEDIUM", "No async polling timeout", {".py"},
       fix_hint="Add wall-clock timeout: if time.time() - start > MAX_WAIT: break")
def check_polling_timeout(filepath, content, lines):
    findings = []
    # Skip self (this script references polling patterns as string literals)
    if Path(filepath).name == "resilience_audit.py":
        return findings
    # Look for polling patterns without timeout
    if "operations" not in content.lower() and "poll" not in content.lower() and "status" not in content.lower():
        return findings

    # Find while loops that check status
    for i, line in enumerate(lines, 1):
        if re.search(r"while\b.*(?:status|state|done|complete|running)", line, re.IGNORECASE):
            # Check if there's a timeout in the surrounding block
            block = "\n".join(lines[max(0, i - 2):min(len(lines), i + 15)])
            has_timeout = "timeout" in block.lower() or "elapsed" in block or "time.time()" in block
            if not has_timeout:
                findings.append(Finding(
                    check_id="M4", severity="MEDIUM",
                    title="Polling loop without wall-clock timeout",
                    file=filepath, line=i,
                    evidence=line.strip()[:100],
                    fix_hint="Track elapsed time and break after MAX_WAIT seconds",
                ))
    return findings


# ---------------------------------------------------------------------------
# LOW checks
# ---------------------------------------------------------------------------

@check("L1", "LOW", "Error output to stdout instead of stderr", {".sh"},
       fix_hint="Use echo '...' >&2 for errors and warnings")
def check_stderr_usage(filepath, content, lines):
    findings = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # echo "Error: ..." without >&2
        if re.search(r'echo\s+"Error:', line) and ">&2" not in line:
            findings.append(Finding(
                check_id="L1", severity="LOW",
                title="Error message to stdout (should be stderr)",
                file=filepath, line=i,
                evidence=stripped[:100],
                fix_hint="Add >&2 to redirect errors to stderr",
            ))
    return findings


@check("L2", "LOW", "Bash 3.2 incompatible syntax", {".sh"},
       fix_hint="Replace with case statement or ${VAR:-default}")
def check_bash_compat(filepath, content, lines):
    findings = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "declare -A" in line:
            findings.append(Finding(
                check_id="L2", severity="LOW",
                title="declare -A (requires bash 4.0+, macOS has 3.2)",
                file=filepath, line=i,
                evidence=stripped[:100],
                fix_hint="Replace associative array with case statement function",
            ))
        if "[[ -v " in line:
            findings.append(Finding(
                check_id="L2", severity="LOW",
                title="[[ -v ]] (requires bash 4.3+)",
                file=filepath, line=i,
                evidence=stripped[:100],
                fix_hint="Use ${VAR:-default} instead of [[ -v VAR ]]",
            ))
        if "declare -n" in line:
            findings.append(Finding(
                check_id="L2", severity="LOW",
                title="declare -n (nameref, requires bash 4.3+)",
                file=filepath, line=i,
                evidence=stripped[:100],
                fix_hint="Avoid namerefs; use eval or indirect expansion",
            ))
    return findings


@check("L3", "LOW", "Missing output directory creation", {".py"},
       fix_hint="Add os.makedirs(os.path.dirname(path), exist_ok=True)")
def check_output_dir(filepath, content, lines):
    findings = []
    # Look for file writes to args.output or output_path without makedirs
    if "output" not in content.lower():
        return findings

    writes_output = bool(re.search(r'open\(\s*(?:output_path|args\.output|out_path)', content))
    has_makedirs = "makedirs" in content

    if writes_output and not has_makedirs:
        for i, line in enumerate(lines, 1):
            if re.search(r'open\(\s*(?:output_path|args\.output|out_path)', line):
                findings.append(Finding(
                    check_id="L3", severity="LOW",
                    title="Writing to output path without ensuring directory exists",
                    file=filepath, line=i,
                    evidence=line.strip()[:100],
                    fix_hint="Add os.makedirs(os.path.dirname(path), exist_ok=True) before writing",
                ))
                break
    return findings


# ---------------------------------------------------------------------------
# Scanner engine
# ---------------------------------------------------------------------------

def discover_scripts(project_root: Path) -> list[Path]:
    """Find all bash and Python scripts in scan directories."""
    scripts = []
    for scan_dir in SCAN_DIRS:
        full_dir = project_root / scan_dir
        if not full_dir.is_dir():
            continue
        for ext in ("*.sh", "*.py"):
            scripts.extend(full_dir.rglob(ext))
    return sorted(set(scripts))


def audit_file(filepath: Path) -> list[Finding]:
    """Run all applicable checks on a single file."""
    ext = filepath.suffix.lower()
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"Warning: Cannot read {filepath}: {e}", file=sys.stderr)
        return []

    lines = content.split("\n")
    all_findings = []

    for check_fn in CHECKS:
        if ext not in check_fn._filetypes:
            continue
        try:
            results = check_fn(str(filepath), content, lines)
            all_findings.extend(results)
        except Exception as e:
            print(f"Warning: Check {check_fn._check_id} failed on {filepath.name}: {e}", file=sys.stderr)

    return all_findings


def compute_grade(findings: list[Finding]) -> tuple[str, int]:
    """Compute letter grade from weighted demerits."""
    total = sum(SEVERITY_WEIGHT.get(f.severity, 0) for f in findings)
    grade = "F"
    for threshold, letter in GRADE_THRESHOLDS:
        if total <= threshold:
            grade = letter
            break
    else:
        grade = "F"
    return grade, total


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def relative_path(filepath: str, project_root: Path) -> str:
    """Make path relative to project root for readability."""
    try:
        return str(Path(filepath).relative_to(project_root))
    except ValueError:
        return filepath


def print_report(findings: list[Finding], scripts_scanned: int,
                 project_root: Path, show_hints: bool = False,
                 min_severity: Optional[str] = None):
    """Print human-readable report to stdout."""
    # Filter by severity
    if min_severity:
        idx = SEVERITY_ORDER.index(min_severity.upper())
        allowed = set(SEVERITY_ORDER[:idx + 1])
        findings = [f for f in findings if f.severity in allowed]

    grade, demerits = compute_grade(findings)

    # Group by severity
    by_severity = {}
    for sev in SEVERITY_ORDER:
        by_severity[sev] = [f for f in findings if f.severity == sev]

    # Header
    print(f"\n{BOLD}RESILIENCE AUDIT REPORT{RESET}")
    print("=" * 60)
    print(f"  Scripts scanned: {scripts_scanned}")
    print(f"  Findings:        {len(findings)}")
    print(f"  Demerits:        {demerits}")

    grade_color = GREEN if grade.startswith("A") else YELLOW if grade.startswith("B") else RED
    print(f"  Grade:           {grade_color}{BOLD}{grade}{RESET}")
    print("=" * 60)

    if not findings:
        print(f"\n  {GREEN}All checks passed. System is resilient.{RESET}\n")
        return

    # Print findings grouped by severity
    for sev in SEVERITY_ORDER:
        group = by_severity.get(sev, [])
        if not group:
            continue

        color = SEVERITY_COLOR[sev]
        print(f"\n{color}{BOLD}  {sev} ({len(group)}){RESET}")
        print(f"  {'-' * 40}")

        for f in group:
            rel = relative_path(f.file, project_root)
            loc = f"{rel}:{f.line}" if f.line else rel
            print(f"  {color}[{f.check_id}]{RESET} {f.title}")
            print(f"       {DIM}{loc}{RESET}")
            if f.evidence:
                print(f"       {DIM}Evidence: {f.evidence}{RESET}")
            if show_hints and f.fix_hint:
                print(f"       {CYAN}Fix: {f.fix_hint}{RESET}")

    # Summary
    print(f"\n{'=' * 60}")
    counts = ", ".join(
        f"{len(by_severity.get(s, []))} {s}"
        for s in SEVERITY_ORDER
        if by_severity.get(s)
    )
    print(f"  {counts}")

    if grade.startswith("A"):
        print(f"  {GREEN}System resilience is strong.{RESET}")
    elif grade.startswith("B"):
        print(f"  {YELLOW}Good resilience. Address HIGH findings for Grade A.{RESET}")
    elif grade.startswith("C"):
        print(f"  {YELLOW}Moderate resilience. Address CRITICAL and HIGH findings.{RESET}")
    else:
        print(f"  {RED}Poor resilience. Prioritize CRITICAL findings immediately.{RESET}")
    print()


def print_json_report(findings: list[Finding], scripts_scanned: int, project_root: Path):
    """Print machine-readable JSON report."""
    grade, demerits = compute_grade(findings)
    report = {
        "grade": grade,
        "demerits": demerits,
        "scripts_scanned": scripts_scanned,
        "finding_count": len(findings),
        "by_severity": {
            s: len([f for f in findings if f.severity == s])
            for s in SEVERITY_ORDER
        },
        "findings": [
            {
                "check_id": f.check_id,
                "severity": f.severity,
                "title": f.title,
                "file": relative_path(f.file, project_root),
                "line": f.line,
                "evidence": f.evidence,
                "fix_hint": f.fix_hint,
            }
            for f in findings
        ],
    }
    print(json.dumps(report, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Resilience auditor for bash and Python scripts"
    )
    parser.add_argument(
        "--path", default=None,
        help="Audit a single file instead of all scripts"
    )
    parser.add_argument(
        "--severity", default=None,
        choices=["critical", "high", "medium", "low"],
        help="Only show findings at this severity or above"
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Output machine-readable JSON"
    )
    parser.add_argument(
        "--fix-hints", action="store_true",
        help="Include remediation hints in output"
    )
    parser.add_argument(
        "--project-root", default=None,
        help="Override project root detection"
    )
    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else PROJECT_ROOT
    if not project_root.is_dir():
        print(f"Error: Project root not found: {project_root}", file=sys.stderr)
        sys.exit(1)

    # Discover scripts
    if args.path:
        target = Path(args.path)
        if not target.is_file():
            print(f"Error: File not found: {args.path}", file=sys.stderr)
            sys.exit(1)
        scripts = [target]
    else:
        scripts = discover_scripts(project_root)
        if not scripts:
            print("Warning: No scripts found in scan directories", file=sys.stderr)
            sys.exit(0)

    print(f"Scanning {len(scripts)} scripts...", file=sys.stderr)

    # Run audit
    all_findings = []
    for script in scripts:
        findings = audit_file(script)
        all_findings.extend(findings)

    # Sort by severity then file
    sev_idx = {s: i for i, s in enumerate(SEVERITY_ORDER)}
    all_findings.sort(key=lambda f: (sev_idx.get(f.severity, 99), f.file, f.line))

    # Output
    if args.json_output:
        print_json_report(all_findings, len(scripts), project_root)
    else:
        print_report(
            all_findings, len(scripts), project_root,
            show_hints=args.fix_hints,
            min_severity=args.severity,
        )

    # Exit code: 1 if any CRITICAL findings
    has_critical = any(f.severity == "CRITICAL" for f in all_findings)
    sys.exit(1 if has_critical else 0)


if __name__ == "__main__":
    main()
