#!/usr/bin/env python3
"""
check_skill.py — Validate a Claude skill against Anthropic's best practices.

Usage:
    python3 check_skill.py <skill-directory>
    python3 check_skill.py <skill-directory> --json     # machine-readable output
    python3 check_skill.py <skill-directory> --fix      # auto-fix simple issues

Outputs a report with errors, warnings, and info items.
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip3 install pyyaml", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
MAX_NAME_LENGTH = 64
RECOMMENDED_MAX_BODY_LINES = 500
RECOMMENDED_FOLDER_NAME = "references"
DEPRECATED_FOLDER_NAME = "docs"
KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Patterns that suggest a script should be bundled
UNBUNDLED_SCRIPT_PATTERNS = [
    r"write a (?:python|bash|shell) script",
    r"create a (?:python|bash|shell) script",
    r"write the following (?:python|bash|shell)",
    r"run this (?:python|bash) (?:script|code)",
]

# Trigger phrase indicators
NEGATIVE_TRIGGER_PATTERNS = [
    r"do not use",
    r"don't use",
    r"not for",
    r"instead.use",
    r"do NOT",
]


# ---------------------------------------------------------------------------
# Result helpers
# ---------------------------------------------------------------------------

class CheckResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.passed = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.info.append(msg)

    def ok(self, msg):
        self.passed.append(msg)

    def to_dict(self):
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "passed": self.passed,
            "summary": {
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "info": len(self.info),
                "passed": len(self.passed),
                "total_checks": len(self.errors) + len(self.warnings) + len(self.info) + len(self.passed),
            },
        }


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_skill_md_exists(skill_path: Path, result: CheckResult):
    """SKILL.md must exist."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        result.error("SKILL.md not found")
        return None
    result.ok("SKILL.md exists")
    return skill_md


def parse_frontmatter(content: str, result: CheckResult):
    """Extract and parse YAML frontmatter."""
    if not content.startswith("---"):
        result.error("No YAML frontmatter found (must start with ---)")
        return None, None

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        result.error("Invalid frontmatter format (missing closing ---)")
        return None, None

    frontmatter_text = match.group(1)
    body = content[match.end():].strip()

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            result.error("Frontmatter must be a YAML dictionary")
            return None, body
    except yaml.YAMLError as e:
        result.error(f"Invalid YAML in frontmatter: {e}")
        return None, body

    result.ok("Valid YAML frontmatter")
    return frontmatter, body


def check_frontmatter_keys(frontmatter: dict, result: CheckResult):
    """Only allowed keys at top level."""
    unexpected = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        result.error(
            f"Unexpected frontmatter key(s): {', '.join(sorted(unexpected))}. "
            f"Move custom fields under `metadata:`. "
            f"Allowed top-level keys: {', '.join(sorted(ALLOWED_FRONTMATTER_KEYS))}"
        )
    else:
        result.ok("All frontmatter keys are valid")


def check_name(frontmatter: dict, skill_path: Path, result: CheckResult):
    """Name field: required, kebab-case, matches directory name."""
    if "name" not in frontmatter:
        result.error("Missing required `name` field in frontmatter")
        return

    name = frontmatter["name"]
    if not isinstance(name, str) or not name.strip():
        result.error("`name` must be a non-empty string")
        return

    name = name.strip()

    # Kebab-case
    if not KEBAB_CASE_RE.match(name):
        result.error(f"Name '{name}' is not kebab-case (lowercase letters, digits, hyphens only)")
    else:
        result.ok("Name is kebab-case")

    # Length
    if len(name) > MAX_NAME_LENGTH:
        result.error(f"Name is {len(name)} chars (max {MAX_NAME_LENGTH})")
    else:
        result.ok(f"Name length OK ({len(name)} chars)")

    # Match directory
    dir_name = skill_path.name
    if name != dir_name:
        result.warn(f"Name '{name}' doesn't match directory name '{dir_name}'")
    else:
        result.ok("Name matches directory name")


def check_description(frontmatter: dict, result: CheckResult):
    """Description field: required, length, trigger phrases, negative triggers."""
    if "description" not in frontmatter:
        result.error("Missing required `description` field in frontmatter")
        return

    desc = frontmatter["description"]
    if not isinstance(desc, str) or not desc.strip():
        result.error("`description` must be a non-empty string")
        return

    desc = desc.strip()

    # Angle brackets
    if "<" in desc or ">" in desc:
        result.error("Description contains angle brackets (< or >) which are not allowed")
    else:
        result.ok("No angle brackets in description")

    # Length
    if len(desc) > MAX_DESCRIPTION_LENGTH:
        result.error(f"Description is {len(desc)} chars (max {MAX_DESCRIPTION_LENGTH})")
    else:
        result.ok(f"Description length OK ({len(desc)} chars)")

    # Minimum useful length
    if len(desc) < 50:
        result.warn(f"Description is very short ({len(desc)} chars). Include trigger phrases and what the skill does.")
    elif len(desc) < 100:
        result.warn(f"Description may be too short ({len(desc)} chars). Consider adding trigger phrases.")

    # Trigger phrases (should mention "use when" or similar)
    trigger_indicators = ["use when", "use if", "trigger", "invoke", "says", "asks"]
    has_trigger = any(t in desc.lower() for t in trigger_indicators)
    if has_trigger:
        result.ok("Description includes trigger context")
    else:
        result.warn("Description lacks trigger phrases (e.g., 'Use when user says...')")

    # Negative triggers
    has_negative = any(re.search(p, desc, re.IGNORECASE) for p in NEGATIVE_TRIGGER_PATTERNS)
    if has_negative:
        result.ok("Description includes negative triggers")
    else:
        result.warn("No negative triggers in description (e.g., 'Do NOT use for...')")


def check_compatibility(frontmatter: dict, result: CheckResult):
    """Compatibility field: optional but recommended."""
    if "compatibility" not in frontmatter:
        result.note("No `compatibility` field (optional but recommended for skills with dependencies)")
        return

    compat = frontmatter["compatibility"]
    if not isinstance(compat, str):
        result.error(f"`compatibility` must be a string, got {type(compat).__name__}")
        return

    if len(compat) > MAX_COMPATIBILITY_LENGTH:
        result.error(f"Compatibility is {len(compat)} chars (max {MAX_COMPATIBILITY_LENGTH})")
    else:
        result.ok(f"Compatibility field OK ({len(compat)} chars)")


def check_metadata(frontmatter: dict, result: CheckResult):
    """Metadata field: if present, should be a dict."""
    if "metadata" not in frontmatter:
        result.note("No `metadata` field (use for custom fields like author, version)")
        return

    meta = frontmatter["metadata"]
    if not isinstance(meta, dict):
        result.error(f"`metadata` must be a dictionary, got {type(meta).__name__}")
    else:
        result.ok("Metadata is a valid dictionary")


def check_body_length(body: str, result: CheckResult):
    """SKILL.md body should be under 500 lines for progressive disclosure."""
    lines = body.split("\n")
    line_count = len(lines)

    if line_count > RECOMMENDED_MAX_BODY_LINES:
        result.warn(
            f"SKILL.md body is {line_count} lines (recommended: under {RECOMMENDED_MAX_BODY_LINES}). "
            f"Consider moving detailed content to references/ files."
        )
    else:
        result.ok(f"SKILL.md body length OK ({line_count} lines)")


def check_folder_structure(skill_path: Path, result: CheckResult):
    """Check for correct folder naming and structure."""
    # Check for deprecated docs/ folder
    docs_dir = skill_path / DEPRECATED_FOLDER_NAME
    refs_dir = skill_path / RECOMMENDED_FOLDER_NAME

    if docs_dir.exists() and docs_dir.is_dir():
        result.warn(
            f"`docs/` directory found — rename to `references/` per Anthropic convention"
        )
    elif refs_dir.exists() and refs_dir.is_dir():
        result.ok("Uses `references/` directory (correct convention)")
    else:
        result.note("No `references/` directory (OK if skill has no reference docs)")

    # Check for scripts/
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists() and scripts_dir.is_dir():
        result.ok("Has `scripts/` directory")
    else:
        result.note("No `scripts/` directory (OK if skill has no scripts)")

    # Check for assets/
    assets_dir = skill_path / "assets"
    if assets_dir.exists() and assets_dir.is_dir():
        result.ok("Has `assets/` directory")

    # Check for unexpected top-level files (other than SKILL.md, LICENSE)
    expected_files = {"SKILL.md", "LICENSE", "LICENSE.txt", "LICENSE.md", "README.md"}
    expected_dirs = {"scripts", "references", "assets", "agents", "evals", "docs"}
    for item in skill_path.iterdir():
        if item.is_file() and item.name not in expected_files:
            result.warn(f"Unexpected top-level file: `{item.name}`. Move to scripts/, references/, or assets/.")
        elif item.is_dir() and item.name not in expected_dirs:
            result.warn(f"Unexpected directory: `{item.name}/`. Standard dirs are scripts/, references/, assets/.")


def check_unbundled_scripts(body: str, result: CheckResult):
    """Detect instructions that tell Claude to write scripts that should be bundled."""
    found = []
    for pattern in UNBUNDLED_SCRIPT_PATTERNS:
        matches = re.findall(pattern, body, re.IGNORECASE)
        if matches:
            found.extend(matches)

    if found:
        result.warn(
            f"Body contains {len(found)} instruction(s) to write scripts inline. "
            f"Consider bundling these in scripts/ instead. "
            f"Found: {', '.join(repr(f) for f in found[:3])}"
        )
    else:
        result.ok("No unbundled script instructions detected")


def check_em_dashes_and_formatting(body: str, result: CheckResult):
    """Check for common formatting issues in the body."""
    # Em dashes (common issue if brand voice bans them)
    em_dash_count = body.count("\u2014")  # —
    if em_dash_count > 0:
        result.note(f"Body contains {em_dash_count} em dash(es) — check if brand voice allows them")

    # Check for very long lines (readability)
    long_lines = [i + 1 for i, line in enumerate(body.split("\n")) if len(line) > 200 and not line.startswith("|")]
    if len(long_lines) > 5:
        result.note(f"{len(long_lines)} lines exceed 200 chars — consider line breaks for readability")


def check_reference_links(body: str, skill_path: Path, result: CheckResult):
    """Check that files referenced in the body actually exist."""
    # Find references to files in references/, scripts/, assets/
    # But skip paths prefixed with variables like ${CLAUDE_PLUGIN_ROOT}/ or $SCRIPTS_DIR/
    # which point outside the skill directory
    all_refs = re.findall(r"(?:references|scripts|assets|docs)/[^\s)\"'`]+", body)

    # Filter out refs that appear after a variable expansion on the same line
    ref_patterns = []
    for ref in all_refs:
        # Check if this ref is part of a variable-prefixed path in the body
        # e.g., ${CLAUDE_PLUGIN_ROOT}/skills/distribute/scripts/foo.py
        escaped = re.escape(ref)
        if re.search(r"\$\{?\w+\}?/(?:\S+/)?" + escaped, body):
            continue  # Skip — this points outside the skill
        ref_patterns.append(ref)

    missing = []
    for ref in ref_patterns:
        # Strip trailing punctuation
        ref = ref.rstrip(".,;:)")
        ref_path = skill_path / ref
        if not ref_path.exists():
            # Also check with common extensions
            if not any((skill_path / f"{ref}{ext}").exists() for ext in [".md", ".py", ".sh", ".json"]):
                missing.append(ref)

    if missing:
        result.warn(f"Referenced files not found: {', '.join(missing[:5])}")
    elif ref_patterns:
        result.ok(f"All {len(ref_patterns)} file references resolve correctly")


# ---------------------------------------------------------------------------
# Auto-fix
# ---------------------------------------------------------------------------

def apply_fixes(skill_path: Path, frontmatter: dict, content: str):
    """Apply auto-fixable changes. Returns (modified_content, fix_log)."""
    fixes = []

    # Fix 1: Rename docs/ to references/
    docs_dir = skill_path / DEPRECATED_FOLDER_NAME
    refs_dir = skill_path / RECOMMENDED_FOLDER_NAME
    if docs_dir.exists() and docs_dir.is_dir() and not refs_dir.exists():
        docs_dir.rename(refs_dir)
        content = content.replace("/docs/", "/references/").replace("docs/", "references/")
        fixes.append("Renamed docs/ to references/")

    # Fix 2: Move non-standard frontmatter keys under metadata
    if frontmatter:
        unexpected = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
        if unexpected:
            meta = frontmatter.get("metadata", {}) or {}
            for key in unexpected:
                meta[key] = frontmatter.pop(key)
            frontmatter["metadata"] = meta

            # Rebuild frontmatter YAML
            fm_yaml = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip()
            body_start = content.index("---", 3) + 3
            content = f"---\n{fm_yaml}\n---{content[body_start:]}"
            fixes.append(f"Moved {', '.join(sorted(unexpected))} under metadata:")

    # Fix 3: Trim trailing whitespace
    lines = content.split("\n")
    trimmed = [line.rstrip() for line in lines]
    if lines != trimmed:
        content = "\n".join(trimmed)
        fixes.append("Trimmed trailing whitespace")

    return content, fixes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def check_skill(skill_path: Path, fix: bool = False) -> dict:
    """Run all checks on a skill directory. Returns result dict."""
    result = CheckResult()
    skill_name = skill_path.name

    # 1. SKILL.md exists
    skill_md = check_skill_md_exists(skill_path, result)
    if skill_md is None:
        return {"skill": skill_name, "path": str(skill_path), **result.to_dict()}

    content = skill_md.read_text()

    # 2. Parse frontmatter
    frontmatter, body = parse_frontmatter(content, result)
    if frontmatter is None:
        return {"skill": skill_name, "path": str(skill_path), **result.to_dict()}

    # 3. Frontmatter checks
    check_frontmatter_keys(frontmatter, result)
    check_name(frontmatter, skill_path, result)
    check_description(frontmatter, result)
    check_compatibility(frontmatter, result)
    check_metadata(frontmatter, result)

    # 4. Body checks
    if body:
        check_body_length(body, result)
        check_unbundled_scripts(body, result)
        check_em_dashes_and_formatting(body, result)
        check_reference_links(body, skill_path, result)

    # 5. Folder structure
    check_folder_structure(skill_path, result)

    # 6. Auto-fix
    fix_log = []
    if fix:
        new_content, fix_log = apply_fixes(skill_path, frontmatter, content)
        if new_content != content:
            skill_md.write_text(new_content)

    report = {"skill": skill_name, "path": str(skill_path), **result.to_dict()}
    if fix_log:
        report["fixes_applied"] = fix_log

    return report


def print_report(report: dict):
    """Print a human-readable report."""
    name = report["skill"]
    summary = report["summary"]

    print(f"\n{'='*60}")
    print(f"  Skill Check: {name}")
    print(f"{'='*60}\n")

    if report["errors"]:
        print("ERRORS (must fix):")
        for e in report["errors"]:
            print(f"  \u2717 {e}")
        print()

    if report["warnings"]:
        print("WARNINGS (should fix):")
        for w in report["warnings"]:
            print(f"  \u26a0 {w}")
        print()

    if report["info"]:
        print("INFO (nice to have):")
        for i in report["info"]:
            print(f"  \u2139 {i}")
        print()

    if report.get("fixes_applied"):
        print("FIXES APPLIED:")
        for f in report["fixes_applied"]:
            print(f"  \u2713 {f}")
        print()

    total = summary["total_checks"]
    passed = summary["passed"]
    print(f"PASSED: {passed}/{total} checks")
    if report["passed"]:
        for p in report["passed"]:
            print(f"  \u2713 {p}")

    print()

    # Overall verdict
    if summary["errors"] > 0:
        print(f"RESULT: FAIL ({summary['errors']} error(s) found)")
    elif summary["warnings"] > 0:
        print(f"RESULT: PASS with {summary['warnings']} warning(s)")
    else:
        print("RESULT: PASS")

    print()


def main():
    parser = argparse.ArgumentParser(description="Validate a Claude skill against best practices")
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--fix", action="store_true", help="Auto-fix simple issues")
    args = parser.parse_args()

    skill_path = Path(args.skill_path).resolve()

    if not skill_path.exists():
        print(f"Error: Path does not exist: {skill_path}", file=sys.stderr)
        sys.exit(1)

    if not skill_path.is_dir():
        # Maybe they passed the SKILL.md file directly
        if skill_path.name == "SKILL.md":
            skill_path = skill_path.parent
        else:
            print(f"Error: Not a directory: {skill_path}", file=sys.stderr)
            sys.exit(1)

    report = check_skill(skill_path, fix=args.fix)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    sys.exit(1 if report["summary"]["errors"] > 0 else 0)


if __name__ == "__main__":
    main()
