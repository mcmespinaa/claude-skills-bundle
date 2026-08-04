---
name: resilience
description: >-
  Static analysis resilience auditor for bash and Python scripts. Checks for
  timeout, retry, error handling, cleanup, and portability anti-patterns
  grounded in Netflix Chaos Engineering, OWASP A10, and CWE-835. Use when user
  says /resilience, audit resilience, stress test scripts, check error handling,
  how resilient is the system, or similar.
allowed-tools: "Bash(python3:*) Read Glob Grep"
---

# /resilience -- Resilience Auditor

> **Trigger:** `/resilience`, "audit resilience", "stress test scripts", "check error handling", "how resilient is the system", "capacity to absorb pressure"
> **Do NOT use for:** Skill structure validation (use /qa), unit testing (use pytest), or live API functional tests (use /qa-test).

## What It Checks

20 automated checks across 4 severity tiers, grounded in production engineering best practices:

| Tier | Checks | Theme | Sources |
|------|--------|-------|---------|
| CRITICAL (5) | C1-C5 | Hangs, data loss, cascading failures | CWE-835, OWASP A10 |
| HIGH (5) | H1-H5 | Partial failures, security leaks, wasted retries | Netflix Chaos Engineering |
| MEDIUM (4) | M1-M4 | Flakiness, resource waste, poor retry strategy | Bash strict mode, API best practices |
| LOW (3) | L1-L3 | Portability, debugging, maintainability | MIT SIPB Safe Shell |

### Check Reference

**CRITICAL** -- will cause hangs or silent failures:
- **C1** curl without `--max-time` (infinite hang)
- **C2** Python urlopen/requests without `timeout=` (infinite block)
- **C3** Bash script without `set -euo pipefail` (silent error propagation)
- **C4** Playwright navigation without `timeout=` (browser hang)
- **C5** Browser launched without `try/finally` cleanup (zombie processes)

**HIGH** -- will cause partial failures or security issues:
- **H1** API curl call with no retry loop (single failure kills operation)
- **H2** curl piped to jq without HTTP status check (garbage data)
- **H3** mktemp without trap cleanup (temp file leak)
- **H4** MAX_RETRIES > 5 (burns quota on sustained outage)
- **H5** API key in echo/print output (credential leak)

**MEDIUM** -- causes flakiness or resource waste:
- **M1** Constant sleep in retry loop (no exponential backoff)
- **M2** Batch loop without size cap (unbounded processing)
- **M3** base64 encoding without file size check (OOM risk)
- **M4** Polling loop without wall-clock timeout (infinite wait)

**LOW** -- portability and debugging:
- **L1** Error message to stdout instead of stderr
- **L2** Bash 3.2 incompatible syntax (declare -A, [[ -v ]])
- **L3** File write without output directory creation

## Usage

```bash
# Full audit (all scripts)
python3 ${CLAUDE_SKILL_DIR}/scripts/resilience_audit.py

# Audit a single file
python3 ${CLAUDE_SKILL_DIR}/scripts/resilience_audit.py --path .claude/shared/scripts/ghl_create_post.sh

# Only CRITICAL + HIGH findings
python3 ${CLAUDE_SKILL_DIR}/scripts/resilience_audit.py --severity high

# Include fix hints
python3 ${CLAUDE_SKILL_DIR}/scripts/resilience_audit.py --fix-hints

# Machine-readable JSON output
python3 ${CLAUDE_SKILL_DIR}/scripts/resilience_audit.py --json
```

## Grading

Letter grade based on weighted demerits (CRITICAL=10, HIGH=5, MEDIUM=2, LOW=1):

| Grade | Demerits | Meaning |
|-------|----------|---------|
| A+ | 0 | Perfect resilience |
| A | 1-2 | Strong. Only LOW findings |
| A- | 3-5 | Strong with minor gaps |
| B+ | 6-10 | Good. Some MEDIUM findings |
| B | 11-15 | Good. Address HIGH items |
| B- | 16-25 | Moderate. CRITICAL items may exist |
| C+ | 26-40 | Needs work |
| C | 41-60 | Significant gaps |
| D | 81-100 | Poor resilience |
| F | 100+ | Systemic issues |

## Workflow

1. **Run the audit** to get the current grade
2. **Review findings** grouped by severity (CRITICAL first)
3. **Fix findings** starting from CRITICAL, working down
4. **Re-run audit** to verify fixes and track grade progression
5. **Repeat** until target grade is reached

## Iterative Hardening Process

The audit is designed for rounds:

1. **Round 1 (Baseline):** Run full audit. Expect D-C on unhardened codebases.
2. **Round 2 (Critical):** Fix all CRITICAL findings. Target: C+ or better.
3. **Round 3 (High):** Fix HIGH findings. Target: B or better.
4. **Round 4 (Medium):** Fix MEDIUM findings. Target: A- or better.
5. **Round 5 (Polish):** Review LOW findings. Accept or fix. Target: A/A+.

Typical progression: D -> C+ -> B- -> A across 4-5 rounds.

## Integration

- **With /qa:** `/qa` checks skill structure. `/resilience` checks script robustness. Complementary.
- **Exit code:** Returns 0 if no CRITICAL findings, 1 if any CRITICAL found. Suitable for CI gates.
- **JSON output:** Use `--json` for programmatic consumption or logging.

## Checklist Reference

Full checklist with sources and rationale: `${CLAUDE_SKILL_DIR}/references/checklist.md`
