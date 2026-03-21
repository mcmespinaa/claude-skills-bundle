---
name: qa
description: "Validates skills against the Agent Skills 2.0 standard. Checks YAML frontmatter, path variables, file references, line counts, description quality, and cross-skill links. Use when user says /qa, check skill quality, validate skills, lint skills, or wants to audit skill compliance. Run with a skill name (/qa post) or --all to check everything."
allowed-tools: "Bash(python3:*) Read Glob Grep"
---

# /qa -- Skill Quality Checker

> **Trigger:** `/qa`, `/qa <skill-name>`, `/qa --all`, "check skill quality", "validate skills", "lint skills"
> **Do NOT use for:** Script resilience auditing (use /resilience), live API testing (use /qa-test), or unit testing (use pytest).

## Usage

- `/qa post` -- Validate a single skill
- `/qa --all` -- Validate all skills
- `/qa --template` -- Generate a new skill scaffold

## Validation Script

Run the linter:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/qa_lint.py [skill_name|--all]
```

The script checks:

1. **Frontmatter (required):** `name` and `description` must exist
2. **Frontmatter (valid YAML):** No syntax errors in the `---` block
3. **Path variables:** No hardcoded `.claude/skills/` paths -- must use `${CLAUDE_SKILL_DIR}`
4. **File references:** All referenced scripts and reference files must exist on disk
5. **Line count:** Warns if SKILL.md exceeds 500 lines (progressive disclosure guideline)
6. **Description quality:** Must include trigger conditions ("Use when...")
7. **Cross-skill references:** `${CLAUDE_SKILL_DIR}/../<sibling>/` paths must resolve
8. **Allowed-tools:** Field must be present (skills without tools are likely misconfigured)
9. **Non-standard fields:** Warns about fields not in the Agent Skills spec (name, description, allowed-tools, license, compatibility, metadata)
10. **Dynamic injection:** Validates `!`command`` syntax is well-formed

## Output Format

```
=== Skill: post ===
[PASS] Frontmatter: name and description present
[PASS] Path variables: no hardcoded paths
[PASS] File references: 12/12 files found
[WARN] Line count: 561 lines (recommended: <500)
[PASS] Description: trigger conditions found
[PASS] Cross-skill refs: 3/3 resolved
[PASS] Allowed-tools: present

Score: 6/7 passed, 1 warning
```

## Scaffold Template

Run `/qa --template` to generate a new skill scaffold. This creates:

```
.claude/skills/<name>/
  SKILL.md          # Pre-filled frontmatter
  references/       # Progressive disclosure (Level 3)
  scripts/          # Automation scripts
```

The scaffold enforces the standard from line one -- quality is foundational, not a retrofit.

## When to Run

- Before committing a new or modified skill
- After syncing skills to the plugin directory
- As part of any skill refactoring
- When onboarding a new skill to the project
