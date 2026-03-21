#!/usr/bin/env python3
"""
Skill Quality Linter -- Validates skills against Agent Skills 2.0 standard.

Aligned with Anthropic's official spec (github.com/anthropics/skills),
agentskills.io specification, and SkillCheck best practices.

Usage:
    python3 qa_lint.py <skill_name>     # Lint one skill
    python3 qa_lint.py --all            # Lint all skills
    python3 qa_lint.py --template <name> # Generate scaffold for new skill
"""

import sys
import os
import re
import glob
import math

# Resolve skills root relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # .claude/skills/
SHARED_SCRIPTS = os.path.join(os.path.dirname(SKILLS_ROOT), "shared", "scripts")

# Agent Skills 2.0 standard fields (official spec: agentskills.io)
STANDARD_FIELDS = {"name", "description", "allowed-tools", "license", "compatibility", "metadata"}
# Claude Code runtime extensions (not portable to other agents)
CLAUDE_CODE_EXTENSIONS = {
    "disable-model-invocation", "user-invocable", "argument-hint",
    "model", "context", "agent", "hooks",
}
ALL_KNOWN_FIELDS = STANDARD_FIELDS | CLAUDE_CODE_EXTENSIONS

# Official spec limits
MAX_LINES = 500
MAX_DESCRIPTION_LEN = 1024   # Official spec: 1024 chars
MAX_NAME_LEN = 64            # Official spec: 64 chars
MAX_COMPATIBILITY_LEN = 500  # Official spec: 500 chars
TOKEN_BUDGET_WARN = 5000     # Anthropic best practices: <5000 tokens for SKILL.md body

# Name format: kebab-case (lowercase alphanumeric + hyphens)
NAME_PATTERN = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')

# Anti-slop phrases (AI-generated filler that weakens skill instructions)
SLOP_PHRASES = [
    r"\blet'?s dive in\b",
    r"\bin this section\b",
    r"\bas mentioned (?:above|earlier|previously)\b",
    r"\bit'?s worth noting\b",
    r"\bneedless to say\b",
    r"\bin today'?s (?:world|landscape|environment)\b",
    r"\bat the end of the day\b",
    r"\bwithout further ado\b",
    r"\bin conclusion\b",
    r"\blast but not least\b",
    r"\bthe bottom line is\b",
    r"\bhaving said that\b",
    r"\bthat being said\b",
    r"\bmoving forward\b",
    r"\ball things considered\b",
]

# Credential/PII patterns
CREDENTIAL_PATTERNS = [
    (r'(?:sk|pk)[-_](?:live|test)[-_][a-zA-Z0-9]{20,}', "API key literal"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub personal access token"),
    (r'AIza[a-zA-Z0-9_-]{35}', "Google API key"),
    (r'(?:AKIA|ASIA)[A-Z0-9]{16}', "AWS access key"),
    (r'xox[bprs]-[a-zA-Z0-9-]+', "Slack token"),
    (r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', "Private key"),
    (r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', "Email address"),
]

# Hardcoded OS paths
OS_PATH_PATTERNS = [
    (r'(?<!\$\{HOME\})(?<!\$HOME)/Users/[a-zA-Z0-9_]+/', "macOS home path"),
    (r'(?<!\$\{HOME\})(?<!\$HOME)/home/[a-zA-Z0-9_]+/', "Linux home path"),
    (r'[A-Z]:\\\\(?:Users|Documents)', "Windows path"),
]

# Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def parse_frontmatter(content):
    """Extract YAML frontmatter from SKILL.md content."""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, content

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None, content

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1:])

    # Simple YAML parser for flat key-value pairs
    fm = {}
    for line in fm_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r'^([a-zA-Z_-]+)\s*:\s*(.*)$', line)
        if match:
            key = match.group(1)
            value = match.group(2).strip().strip('"').strip("'")
            fm[key] = value
        else:
            fm.setdefault("_parse_errors", []).append(line)

    return fm, body


def estimate_tokens(text):
    """Rough token estimate: ~4 chars per token for English text."""
    return math.ceil(len(text) / 4)


# ---------------------------------------------------------------------------
# CHECK: Frontmatter (enhanced with official spec rules)
# ---------------------------------------------------------------------------
def check_frontmatter(fm, skill_name):
    """Check required and valid frontmatter fields per official spec."""
    results = []

    if fm is None:
        results.append(("FAIL", "Frontmatter", "No YAML frontmatter found (missing --- delimiters)"))
        return results

    if "_parse_errors" in fm:
        for err in fm["_parse_errors"]:
            results.append(("WARN", "Frontmatter", f"Unparseable line: {err}"))

    # --- name field ---
    if "name" not in fm:
        results.append(("FAIL", "Frontmatter", "Missing required field: name"))
    else:
        name = fm["name"]
        # Directory match (upgraded to FAIL per official validator)
        if name != skill_name:
            results.append(("FAIL", "Name", f"name '{name}' does not match directory name '{skill_name}'"))
        else:
            results.append(("PASS", "Name", "name field present and matches directory"))

        # Kebab-case format
        if not NAME_PATTERN.match(name):
            results.append(("FAIL", "Name format", f"'{name}' is not valid kebab-case (lowercase alphanumeric + hyphens)"))
        else:
            results.append(("PASS", "Name format", "Valid kebab-case"))

        # Length limit
        if len(name) > MAX_NAME_LEN:
            results.append(("FAIL", "Name length", f"name is {len(name)} chars (max: {MAX_NAME_LEN})"))

        # No leading/trailing/consecutive hyphens
        if name.startswith("-") or name.endswith("-") or "--" in name:
            results.append(("FAIL", "Name format", "No leading, trailing, or consecutive hyphens allowed"))

    # --- description field ---
    if "description" not in fm:
        results.append(("FAIL", "Frontmatter", "Missing required field: description"))
    else:
        desc = fm["description"]
        if len(desc) > MAX_DESCRIPTION_LEN:
            results.append(("WARN", "Description", f"Description is {len(desc)} chars (max: {MAX_DESCRIPTION_LEN})"))
        else:
            results.append(("PASS", "Description", f"Length OK ({len(desc)} chars)"))

        # Angle brackets (XML injection risk, per Anthropic's quick_validate.py)
        if re.search(r'[<>]', desc):
            results.append(("FAIL", "Description", "Angle brackets (<>) found -- potential XML injection"))
        else:
            results.append(("PASS", "Description", "No angle brackets"))

        # Trigger conditions (WHAT + WHEN)
        has_when = bool(re.search(r"[Uu]se when|[Tt]rigger|[Aa]ctivate", desc))
        has_what = bool(re.search(r"[Cc]reates?|[Vv]alidate|[Gg]enerate|[Ss]earch|[Aa]nalyz|[Rr]un|[Ss]end|[Dd]elete|[Ee]dit|[Ss]ave|[Rr]ender|[Dd]esign|[Pp]lan|[Pp]ublish|[Rr]esearch|[Cc]heck|[Aa]udit", desc))
        if has_when and has_what:
            results.append(("PASS", "Description", "WHAT + WHEN pattern present"))
        elif has_when:
            results.append(("PASS", "Description", "Trigger conditions present"))
        elif has_what:
            results.append(("WARN", "Description", "Describes WHAT but missing WHEN (add 'Use when...')"))
        else:
            results.append(("WARN", "Description", "No trigger conditions found (recommended: include 'Use when...')"))

    # --- allowed-tools ---
    if "allowed-tools" not in fm:
        results.append(("WARN", "Allowed-tools", "No allowed-tools field (skill may not be able to use tools)"))
    else:
        results.append(("PASS", "Allowed-tools", f"Present: {fm['allowed-tools'][:60]}..."))

    # --- compatibility length ---
    if "compatibility" in fm and len(fm["compatibility"]) > MAX_COMPATIBILITY_LEN:
        results.append(("WARN", "Compatibility", f"compatibility is {len(fm['compatibility'])} chars (max: {MAX_COMPATIBILITY_LEN})"))

    # --- Non-standard fields ---
    for key in fm:
        if key.startswith("_"):
            continue
        if key not in ALL_KNOWN_FIELDS:
            results.append(("WARN", "Non-standard field", f"'{key}' is not in the Agent Skills spec or Claude Code extensions"))
        elif key in CLAUDE_CODE_EXTENSIONS and key not in STANDARD_FIELDS:
            results.append(("INFO", "Claude Code extension", f"'{key}' is a Claude Code extension (not portable to other agents)"))

    return results


# ---------------------------------------------------------------------------
# CHECK: Paths (unchanged)
# ---------------------------------------------------------------------------
def check_paths(content, skill_dir):
    """Check for hardcoded paths that should use ${CLAUDE_SKILL_DIR}."""
    results = []
    hardcoded = []

    in_code_block = False
    for i, line in enumerate(content.split("\n"), 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if line.strip().startswith("#") and not line.strip().startswith("#!"):
            continue
        if "`.claude/skills/`" in line:
            continue
        matches = re.findall(r'(?<!\$\{CLAUDE_SKILL_DIR\}/)\.claude/skills/', line)
        if matches:
            hardcoded.append((i, line.strip()[:80]))

    if hardcoded:
        results.append(("FAIL", "Path variables", f"{len(hardcoded)} hardcoded .claude/skills/ path(s) found"))
        for lineno, text in hardcoded[:3]:
            results.append(("", "", f"  Line {lineno}: {text}"))
    else:
        results.append(("PASS", "Path variables", "No hardcoded paths found"))

    return results


# ---------------------------------------------------------------------------
# CHECK: File references (unchanged)
# ---------------------------------------------------------------------------
def check_file_references(content, skill_dir):
    """Verify that referenced scripts and files exist."""
    results = []
    found = 0
    missing = []

    refs = re.findall(r'\$\{CLAUDE_SKILL_DIR\}/([^\s\`\'")\]]+)', content)
    for ref in refs:
        if '<' in ref and '>' in ref:
            continue
        full_path = os.path.join(skill_dir, ref)
        if '*' in full_path:
            continue
        if os.path.exists(full_path):
            found += 1
        else:
            missing.append(ref)

    cross_refs = re.findall(r'\$\{CLAUDE_SKILL_DIR\}/\.\./([^\s\`\'")\]]+)', content)
    for ref in cross_refs:
        if '<' in ref and '>' in ref:
            continue
        full_path = os.path.join(skill_dir, "..", ref)
        if os.path.exists(full_path):
            found += 1
        else:
            missing.append(f"../{ref}")

    total = found + len(missing)
    if total == 0:
        results.append(("INFO", "File references", "No file references found in SKILL.md"))
    elif missing:
        results.append(("FAIL", "File references", f"{len(missing)}/{total} referenced files missing"))
        for m in missing[:5]:
            results.append(("", "", f"  Missing: {m}"))
    else:
        results.append(("PASS", "File references", f"{found}/{total} referenced files found"))

    return results


# ---------------------------------------------------------------------------
# CHECK: Line count + token budget
# ---------------------------------------------------------------------------
def check_line_count(content):
    """Check SKILL.md line count and estimated token budget."""
    results = []
    lines = len(content.split("\n"))

    if lines > MAX_LINES:
        results.append(("WARN", "Line count", f"{lines} lines (recommended: <{MAX_LINES}). Consider moving detail to references/"))
    else:
        results.append(("PASS", "Line count", f"{lines} lines"))

    # Token budget (only warn if line count is OK -- avoid double warning)
    if lines <= MAX_LINES:
        tokens = estimate_tokens(content)
        if tokens > TOKEN_BUDGET_WARN:
            results.append(("WARN", "Token budget", f"~{tokens} tokens (recommended: <{TOKEN_BUDGET_WARN}). Heavy context load on activation."))
        else:
            results.append(("PASS", "Token budget", f"~{tokens} tokens"))

    return results


# ---------------------------------------------------------------------------
# CHECK: Dynamic injection (unchanged)
# ---------------------------------------------------------------------------
def check_dynamic_injection(content):
    """Validate !`command` syntax is well-formed."""
    results = []
    injections = re.findall(r'!\`([^`]*)\`', content)
    if not injections:
        return []

    for cmd in injections:
        if not cmd.strip():
            results.append(("FAIL", "Dynamic injection", "Empty !`` command found"))
        elif re.search(r'2>/dev/null', cmd) and '||' in cmd:
            # Safe fallback pattern: command 2>/dev/null ... || echo "default"
            results.append(("PASS", "Dynamic injection", f"Valid (with fallback): !`{cmd[:50]}`"))
        elif "|" in cmd and (">" in cmd or ";" in cmd):
            results.append(("WARN", "Dynamic injection", f"Complex command in injection: {cmd[:60]}"))
        else:
            results.append(("PASS", "Dynamic injection", f"Valid: !`{cmd[:50]}`"))

    return results


# ---------------------------------------------------------------------------
# CHECK: Hardcoded OS paths (new)
# ---------------------------------------------------------------------------
def check_os_paths(content):
    """Detect hardcoded OS-specific paths in SKILL.md."""
    results = []
    found = []

    in_code_block = False
    for i, line in enumerate(content.split("\n"), 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        for pattern, label in OS_PATH_PATTERNS:
            if re.search(pattern, line):
                found.append((i, label, line.strip()[:70]))

    if found:
        results.append(("WARN", "Hardcoded OS paths", f"{len(found)} OS-specific path(s) found"))
        for lineno, label, text in found[:3]:
            results.append(("", "", f"  Line {lineno} ({label}): {text}"))
    else:
        results.append(("PASS", "Hardcoded OS paths", "No OS-specific paths found"))

    return results


# ---------------------------------------------------------------------------
# CHECK: Credential/PII detection (new)
# ---------------------------------------------------------------------------
def check_credentials(content):
    """Scan SKILL.md for hardcoded credentials or PII."""
    results = []
    found = []

    in_code_block = False
    for i, line in enumerate(content.split("\n"), 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        # Check all lines including code blocks (credentials in examples are still risky)
        for pattern, label in CREDENTIAL_PATTERNS:
            # Skip email pattern in description-like contexts (attribution, docs)
            if label == "Email address" and ("@example" in line or "noreply@" in line):
                continue
            if re.search(pattern, line):
                found.append((i, label, line.strip()[:70]))

    if found:
        results.append(("WARN", "Credentials/PII", f"{len(found)} potential credential(s) or PII found"))
        for lineno, label, text in found[:3]:
            results.append(("", "", f"  Line {lineno} ({label}): {text}"))
    else:
        results.append(("PASS", "Credentials/PII", "No hardcoded credentials or PII detected"))

    return results


# ---------------------------------------------------------------------------
# CHECK: Anti-slop detection (new)
# ---------------------------------------------------------------------------
def check_anti_slop(body):
    """Detect AI-generated filler phrases in skill instructions."""
    results = []
    found = []

    for i, line in enumerate(body.split("\n"), 1):
        line_lower = line.lower()
        # Skip lines that list banned/blocked words (the phrase is being prohibited, not used)
        if re.search(r'(?:banned|blocked|never use|avoid|prohibit)', line_lower):
            continue
        for pattern in SLOP_PHRASES:
            if re.search(pattern, line_lower):
                found.append((i, re.search(pattern, line_lower).group(), line.strip()[:70]))

    if found:
        results.append(("WARN", "Anti-slop", f"{len(found)} filler phrase(s) found -- weakens skill instructions"))
        for lineno, phrase, text in found[:3]:
            results.append(("", "", f"  Line {lineno}: \"{phrase}\""))
    else:
        results.append(("PASS", "Anti-slop", "No AI filler phrases detected"))

    return results


# ---------------------------------------------------------------------------
# CHECK: Examples present (new)
# ---------------------------------------------------------------------------
def check_examples(body):
    """Check if skill includes input/output examples (best practice)."""
    results = []

    has_example = bool(re.search(
        r'(?i)(?:##?\s*example|input.*output|before.*after|```\s*(?:json|bash|python|sh))',
        body
    ))

    if has_example:
        results.append(("PASS", "Examples", "Input/output examples found"))
    else:
        results.append(("WARN", "Examples", "No examples found. Skills with examples perform better (add ## Example section)"))

    return results


# ---------------------------------------------------------------------------
# CHECK: Negative triggers (new)
# ---------------------------------------------------------------------------
def check_negative_triggers(body):
    """Check if skill defines what it should NOT be used for."""
    results = []

    has_negative = bool(re.search(
        r'(?i)(?:do\s+not\s+use|don\'?t\s+use|not\s+(?:for|intended|designed)|instead.*use\s+/|should\s+not|never\s+use\s+this)',
        body
    ))

    if has_negative:
        results.append(("PASS", "Negative triggers", "Defines when NOT to use this skill"))
    else:
        results.append(("WARN", "Negative triggers", "No negative triggers found. Add 'Do NOT use for...' to prevent false activation"))

    return results


# ---------------------------------------------------------------------------
# CHECK: Contradiction detection (new)
# ---------------------------------------------------------------------------
def check_contradictions(body):
    """Basic contradiction detection: ALWAYS X vs NEVER X on same topic."""
    results = []
    always_rules = set()
    never_rules = set()

    for line in body.split("\n"):
        # Extract ALWAYS/NEVER + next 3 words as topic fingerprint
        for m in re.finditer(r'\bALWAYS\s+(\w+(?:\s+\w+){0,2})', line):
            always_rules.add(m.group(1).lower())
        for m in re.finditer(r'\bNEVER\s+(\w+(?:\s+\w+){0,2})', line):
            never_rules.add(m.group(1).lower())

    conflicts = always_rules & never_rules
    if conflicts:
        results.append(("WARN", "Contradictions", f"ALWAYS vs NEVER conflict on: {', '.join(sorted(conflicts)[:3])}"))
    else:
        results.append(("PASS", "Contradictions", "No ALWAYS/NEVER conflicts detected"))

    return results


# ---------------------------------------------------------------------------
# CHECK: Script quality (new -- scans scripts/ directory)
# ---------------------------------------------------------------------------
def check_scripts(skill_dir):
    """Check scripts for interactive prompts and --help support."""
    results = []
    scripts_dir = os.path.join(skill_dir, "scripts")

    if not os.path.isdir(scripts_dir):
        return []

    script_files = []
    for ext in ("*.py", "*.sh", "*.bash"):
        script_files.extend(glob.glob(os.path.join(scripts_dir, ext)))

    if not script_files:
        return []

    interactive_found = []
    help_count = 0
    total_scripts = len(script_files)

    # Self-exclude: skip qa_lint.py itself (regex patterns create false positives)
    self_path = os.path.abspath(__file__)

    for sf in script_files:
        if os.path.abspath(sf) == self_path:
            continue
        basename = os.path.basename(sf)
        try:
            with open(sf, "r") as f:
                content = f.read()
        except Exception:
            continue

        # Interactive prompts (hard fail in agent context)
        if sf.endswith(".py"):
            # Match input( but not # input( or "input(" in comments/strings
            for i, line in enumerate(content.split("\n"), 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if re.search(r'\binput\s*\(', stripped):
                    interactive_found.append((basename, i, "input()"))
        elif sf.endswith((".sh", ".bash")):
            for i, line in enumerate(content.split("\n"), 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if re.search(r'\bread\s+-[ep]', stripped):
                    interactive_found.append((basename, i, "read -p/-e"))
                if re.search(r'\bselect\s+\w+\s+in\b', stripped):
                    interactive_found.append((basename, i, "select menu"))

        # --help handler
        if re.search(r'--help|usage\(\)|print_usage|show_help|argparse', content):
            help_count += 1

    # Adjust total for self-exclusion
    actual_total = sum(1 for sf in script_files if os.path.abspath(sf) != self_path)

    if interactive_found:
        results.append(("FAIL", "Interactive prompts", f"{len(interactive_found)} interactive prompt(s) found (agents run non-interactive)"))
        for basename, lineno, kind in interactive_found[:3]:
            results.append(("", "", f"  {basename}:{lineno} -- {kind}"))
    elif actual_total > 0:
        results.append(("PASS", "Interactive prompts", f"All {actual_total} script(s) are non-interactive"))

    if help_count == 0 and actual_total > 0:
        results.append(("WARN", "Script --help", f"0/{total_scripts} scripts have --help. Agents learn interfaces via --help"))
    else:
        results.append(("PASS", "Script --help", f"{help_count}/{total_scripts} script(s) have --help"))

    return results


# ---------------------------------------------------------------------------
# CHECK: Shared scripts quality (runs once for --all)
# ---------------------------------------------------------------------------
def check_shared_scripts():
    """Check shared scripts for interactive prompts and --help support."""
    results = []

    if not os.path.isdir(SHARED_SCRIPTS):
        return []

    script_files = []
    for ext in ("*.py", "*.sh", "*.bash"):
        script_files.extend(glob.glob(os.path.join(SHARED_SCRIPTS, ext)))

    if not script_files:
        return []

    interactive_found = []
    help_count = 0

    for sf in script_files:
        basename = os.path.basename(sf)
        try:
            with open(sf, "r") as f:
                content = f.read()
        except Exception:
            continue

        if sf.endswith(".py"):
            for i, line in enumerate(content.split("\n"), 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if re.search(r'\binput\s*\(', stripped):
                    interactive_found.append((basename, i, "input()"))
        elif sf.endswith((".sh", ".bash")):
            for i, line in enumerate(content.split("\n"), 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if re.search(r'\bread\s+-[ep]', stripped):
                    interactive_found.append((basename, i, "read -p/-e"))

        if re.search(r'--help|usage\(\)|print_usage|show_help|argparse', content):
            help_count += 1

    total = len(script_files)
    if interactive_found:
        results.append(("FAIL", "Shared: interactive", f"{len(interactive_found)} interactive prompt(s) in shared scripts"))
        for basename, lineno, kind in interactive_found[:3]:
            results.append(("", "", f"  {basename}:{lineno} -- {kind}"))
    else:
        results.append(("PASS", "Shared: interactive", f"All {total} shared script(s) are non-interactive"))

    if help_count == 0:
        results.append(("WARN", "Shared: --help", f"0/{total} shared scripts have --help"))
    else:
        results.append(("PASS", "Shared: --help", f"{help_count}/{total} shared script(s) have --help"))

    return results


# ===========================================================================
# MAIN ORCHESTRATION
# ===========================================================================

def lint_skill(skill_name):
    """Run all checks on a single skill."""
    skill_dir = os.path.join(SKILLS_ROOT, skill_name)
    skill_file = os.path.join(skill_dir, "SKILL.md")

    if not os.path.exists(skill_file):
        print(f"{RED}[ERROR]{RESET} Skill '{skill_name}' not found at {skill_file}")
        return None

    with open(skill_file, "r") as f:
        content = f.read()

    fm, body = parse_frontmatter(content)

    all_results = []
    # Core checks (original)
    all_results.extend(check_frontmatter(fm, skill_name))
    all_results.extend(check_paths(content, skill_dir))
    all_results.extend(check_file_references(content, skill_dir))
    all_results.extend(check_line_count(content))
    all_results.extend(check_dynamic_injection(content))
    # New checks (Anthropic spec + SkillCheck)
    all_results.extend(check_os_paths(content))
    all_results.extend(check_credentials(content))
    all_results.extend(check_anti_slop(body))
    all_results.extend(check_examples(body))
    all_results.extend(check_negative_triggers(body))
    all_results.extend(check_contradictions(body))
    all_results.extend(check_scripts(skill_dir))

    return all_results


def print_results(skill_name, results):
    """Pretty-print lint results for a skill."""
    if results is None:
        return 0, 0, 0

    print(f"\n{BOLD}=== Skill: {skill_name} ==={RESET}")

    passes = 0
    warnings = 0
    failures = 0

    for status, label, message in results:
        if status == "PASS":
            print(f"  {GREEN}[PASS]{RESET} {label}: {message}")
            passes += 1
        elif status == "WARN":
            print(f"  {YELLOW}[WARN]{RESET} {label}: {message}")
            warnings += 1
        elif status == "FAIL":
            print(f"  {RED}[FAIL]{RESET} {label}: {message}")
            failures += 1
        elif status == "INFO":
            print(f"  {CYAN}[INFO]{RESET} {label}: {message}")
        elif status == "":
            print(f"         {message}")

    print(f"\n  Score: {passes} passed, {warnings} warning(s), {failures} failure(s)")
    return passes, warnings, failures


def generate_template(name):
    """Generate a new skill scaffold (updated for v3.0 checks)."""
    skill_dir = os.path.join(SKILLS_ROOT, name)

    if os.path.exists(skill_dir):
        print(f"{RED}[ERROR]{RESET} Skill directory already exists: {skill_dir}")
        return

    # Validate name before creating
    if not NAME_PATTERN.match(name):
        print(f"{RED}[ERROR]{RESET} '{name}' is not valid kebab-case. Use lowercase + hyphens (e.g., 'my-skill')")
        return
    if len(name) > MAX_NAME_LEN:
        print(f"{RED}[ERROR]{RESET} Name exceeds {MAX_NAME_LEN} chars")
        return

    os.makedirs(os.path.join(skill_dir, "references"), exist_ok=True)
    os.makedirs(os.path.join(skill_dir, "scripts"), exist_ok=True)

    skill_md = f"""---
name: {name}
description: "[What this skill does]. Use when user says /{name}, [other triggers], or similar."
allowed-tools: "Read Write Edit Glob Grep"
---

# /{name} -- [Skill Title]

> **Trigger:** User says `/{name}`, "[other trigger phrases]", or similar.
> **Do NOT use for:** [What this skill should NOT handle -- prevents false activation]

## Workflow

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Example

**Input:** [Example user request]
**Output:** [What the skill produces]

## References

- `${{CLAUDE_SKILL_DIR}}/references/` -- Detailed documentation (loaded on demand)
- `${{CLAUDE_SKILL_DIR}}/scripts/` -- Automation scripts

## Error Handling

- [Common error]: [How to handle]
"""

    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(skill_md)

    print(f"{GREEN}[OK]{RESET} Scaffold created at {skill_dir}/")
    print(f"     SKILL.md -- Pre-filled frontmatter (edit description and workflow)")
    print(f"     references/ -- Add detailed docs here (progressive disclosure Level 3)")
    print(f"     scripts/ -- Add automation scripts here")
    print(f"\n  Next: Edit SKILL.md, then run: python3 qa_lint.py {name}")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 qa_lint.py <skill_name|--all|--template name>")
        print(f"\nAvailable skills:")
        for d in sorted(os.listdir(SKILLS_ROOT)):
            if os.path.isfile(os.path.join(SKILLS_ROOT, d, "SKILL.md")):
                print(f"  - {d}")
        sys.exit(1)

    if sys.argv[1] == "--template":
        if len(sys.argv) < 3:
            print(f"{RED}[ERROR]{RESET} Provide a name: python3 qa_lint.py --template <name>")
            sys.exit(1)
        generate_template(sys.argv[2])
        return

    if sys.argv[1] == "--all":
        skills = sorted([
            d for d in os.listdir(SKILLS_ROOT)
            if os.path.isfile(os.path.join(SKILLS_ROOT, d, "SKILL.md"))
        ])
    else:
        skills = [sys.argv[1]]

    total_p, total_w, total_f = 0, 0, 0

    for skill in skills:
        results = lint_skill(skill)
        p, w, f_ = print_results(skill, results)
        total_p += p
        total_w += w
        total_f += f_

    # Run shared scripts check once (only in --all mode)
    if len(skills) > 1:
        shared_results = check_shared_scripts()
        if shared_results:
            print(f"\n{BOLD}=== Shared Scripts ==={RESET}")
            for status, label, message in shared_results:
                if status == "PASS":
                    print(f"  {GREEN}[PASS]{RESET} {label}: {message}")
                    total_p += 1
                elif status == "WARN":
                    print(f"  {YELLOW}[WARN]{RESET} {label}: {message}")
                    total_w += 1
                elif status == "FAIL":
                    print(f"  {RED}[FAIL]{RESET} {label}: {message}")
                    total_f += 1
                elif status == "":
                    print(f"         {message}")

    if len(skills) > 1:
        print(f"\n{BOLD}=== Summary ({len(skills)} skills) ==={RESET}")
        print(f"  {GREEN}{total_p} passed{RESET}, {YELLOW}{total_w} warning(s){RESET}, {RED}{total_f} failure(s){RESET}")

        if total_f == 0 and total_w == 0:
            print(f"\n  {GREEN}All skills fully compliant with Agent Skills 2.0{RESET}")
        elif total_f == 0:
            print(f"\n  {YELLOW}All skills pass, but {total_w} warning(s) to review{RESET}")
        else:
            print(f"\n  {RED}{total_f} failure(s) must be fixed{RESET}")

    sys.exit(1 if total_f > 0 else 0)


if __name__ == "__main__":
    main()
