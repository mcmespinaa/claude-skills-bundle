---
name: skill-checker
description: Validate and QA Claude skills against Anthropic's official best practices. Use when user says "check this skill", "validate my skill", "QA the distribute skill", "audit skills", "run skill checker", or invokes /skill-checker. Checks frontmatter, description quality, folder structure, progressive disclosure, writing patterns, and triggering accuracy. Do NOT use for creating new skills — use skill-creator instead.
compatibility: Requires python3 and PyYAML. macOS or Linux.
metadata:
  author: content-engine
  version: 1.0.0
  argument-hint: '"<skill-path>" [--fix] [--all]'
  user-invokable: true
---

# /skill-checker — Skill QA Validator

> **Trigger:** User says `/skill-checker`, "check this skill", "validate my skill", "QA the skills", "audit skills", or similar.

## Purpose

Validate one or more skills against Anthropic's official "Complete Guide to Building Skills for Claude" and surface issues ranked by severity. Optionally auto-fix simple problems.

---

## Workflow

### Step 1 — Determine Scope

Figure out what to check:

| Input | Action |
|-------|--------|
| `/skill-checker <path>` | Check the skill at that path |
| `/skill-checker --all` | Check all skills in `content-engine/skills/` |
| "check my skills" (no path) | List available skills, ask which to check or offer `--all` |

### Step 2 — Run Automated Checks

Run the validation script on each skill:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/skill-checker/scripts/check_skill.py" "<skill-path>"
```

The script runs all machine-checkable rules and outputs a JSON report with pass/fail/warn for each check.

If checking multiple skills, run the script once per skill and collect all reports.

### Step 3 — Run Manual Checks

Some checks require reading comprehension that a script can't do well. After the automated checks, read the SKILL.md body and evaluate these manually:

1. **Description trigger coverage** — Does the description include enough trigger phrases? Would a user's natural phrasing match? Are there negative triggers ("Do NOT use for...")?

2. **Progressive disclosure** — Is the SKILL.md body under 500 lines? Are large reference files linked rather than inlined? Is there guidance on *when* to read each reference file?

3. **Writing quality** — Does the skill explain *why* behind instructions, or rely on heavy-handed MUSTs? Are examples provided for output formats? Is the tone imperative but not robotic?

4. **Workflow completeness** — Does the skill have a clear step-by-step workflow? Are edge cases and errors handled? Is there an approval gate before destructive actions?

5. **Script bundling** — If the skill instructs Claude to write helper scripts, those scripts should be bundled in `scripts/` instead. Look for patterns telling Claude to create scripts inline rather than bundling them.

Read `references/checklist.md` for the full list of manual checks with examples of good and bad patterns.

### Step 4 — Present Results

Present a summary report organized by severity:

```
## Skill Check: <skill-name>

### Errors (must fix)
- [ ] Missing `name` in frontmatter
- [ ] Description exceeds 1024 characters (1,247 chars)

### Warnings (should fix)
- [ ] No negative triggers in description
- [ ] SKILL.md body is 612 lines (recommended: under 500)
- [ ] `docs/` directory found — rename to `references/`

### Info (nice to have)
- [ ] No `compatibility` field (optional but recommended)
- [ ] Consider adding examples for output format

### Passed (23/28 checks)
- [x] Valid YAML frontmatter
- [x] Name is kebab-case
- [x] Description under 1024 chars
...
```

### Step 5 — Offer Fixes

If `--fix` was passed or the user asks to fix issues:

**Auto-fixable issues:**
- Rename `docs/` to `references/`
- Move non-standard frontmatter keys under `metadata:`
- Trim trailing whitespace in SKILL.md
- Add missing `metadata:` wrapper around custom fields

**Manual-fix guidance:**
For issues that need human judgment (description rewording, content restructuring), explain what to change and why, but don't auto-apply.

---

## Quick Reference: Severity Levels

| Level | Meaning | Examples |
|-------|---------|----------|
| **Error** | Skill will malfunction or fail to load | Missing name/description, invalid YAML, name not kebab-case |
| **Warning** | Skill works but doesn't follow best practices | No negative triggers, body too long, wrong folder names |
| **Info** | Optional improvements | Missing compatibility field, no examples in body |

---

## Error Handling

| Error | Action |
|-------|--------|
| Path doesn't exist | "Skill not found at `<path>`. Check the path and try again." |
| No SKILL.md in directory | "No SKILL.md found in `<path>`. Is this a skill directory?" |
| PyYAML not installed | "PyYAML is required. Install with: `pip3 install pyyaml`" |
