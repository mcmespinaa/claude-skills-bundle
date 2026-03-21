# Skill QA Checklist

Complete reference for manual checks that supplement the automated `check_skill.py` script. Read this when doing a thorough skill audit.

---

## Table of Contents

1. [Frontmatter Quality](#1-frontmatter-quality)
2. [Description & Triggering](#2-description--triggering)
3. [Progressive Disclosure](#3-progressive-disclosure)
4. [Writing Patterns](#4-writing-patterns)
5. [Workflow Design](#5-workflow-design)
6. [Scripts & Resources](#6-scripts--resources)
7. [Folder Structure](#7-folder-structure)

---

## 1. Frontmatter Quality

**Automated checks handle:** YAML validity, required fields, kebab-case name, key whitelist, description length, angle brackets.

**Manual checks:**

- **Name matches purpose.** The name should clearly communicate what the skill does. `distribute` is better than `content-sender`. `skill-checker` is better than `qa-tool`.

- **Metadata is meaningful.** If `metadata:` exists, check that `version` follows semver, `author` is set, and any custom fields serve a purpose.

---

## 2. Description & Triggering

This is the most impactful area. The description determines whether Claude invokes the skill.

**Good description pattern:**
```
[What it does]. Use when [trigger phrases]. [Negative triggers].
```

**Example (good):**
```
Distribute content to GHL social media, Google Drive, and YouTube.
Use when user says "distribute this", "post to Instagram", "schedule on all platforms".
Do NOT use for writing content from scratch — use /linkedin instead.
```

**Example (bad):**
```
Handles content distribution across platforms.
```

**Manual checks:**

- **Trigger phrase coverage.** List 5 things a real user would say. Do they match the description? Common gap: the description uses formal language but users say things casually.

- **Negative triggers.** If the skill overlaps with other skills, the description must say when NOT to use it. Example: linkedin skill says "Do NOT use for other social platforms — use /distribute."

- **Pushiness.** Per Anthropic's guidance, descriptions should be slightly "pushy" — Claude tends to under-trigger. The description should make it clear that even loosely related requests should trigger the skill.

- **No angle brackets or special chars.** Automated check covers this, but also watch for backticks, markdown formatting, or HTML in descriptions.

---

## 3. Progressive Disclosure

Skills use a three-level loading system:

| Level | What loads | Size target |
|-------|-----------|-------------|
| 1. Frontmatter | name + description | ~100 words |
| 2. SKILL.md body | Full instructions | Under 500 lines |
| 3. Reference files | Read on demand | Unlimited |

**Manual checks:**

- **Body under 500 lines.** If over, identify what can move to `references/`. Good candidates: detailed API docs, style guides, schema definitions, long examples.

- **Reference file pointers.** The body should tell Claude *when* to read each reference file, not just that it exists. Bad: "See references/api.md". Good: "Before making API calls, read references/api.md for endpoint details and rate limits."

- **Large reference files have TOC.** Any reference file over 300 lines should start with a table of contents so Claude can navigate efficiently.

- **Scripts don't need loading.** Scripts in `scripts/` can be executed without reading them into context. The SKILL.md should give the command to run, not explain the script's internals.

---

## 4. Writing Patterns

**Explain the why, not just the what.** Per Anthropic's guide: "Try hard to explain the why behind everything. Today's LLMs are smart. If you find yourself writing ALWAYS or NEVER in all caps, reframe and explain the reasoning."

**Bad:**
```
ALWAYS use 4:5 aspect ratio. NEVER use landscape.
```

**Good:**
```
Use 4:5 portrait (1080x1350) — this takes up more screen real estate
in mobile feeds, which is where 85% of LinkedIn browsing happens.
```

**Manual checks:**

- **Imperative voice.** Instructions should be direct: "Read the file", not "You should read the file" or "The file should be read."

- **Examples for output formats.** If the skill specifies an output format, include at least one example. A template is better than a description.

- **No excessive MUSTs.** Count instances of MUST, ALWAYS, NEVER (case-insensitive). More than 5 per 100 lines suggests the instructions are too rigid. Reframe with reasoning.

- **Consistent terminology.** Pick one term and stick with it. Don't switch between "post", "content", "asset", and "media" for the same concept.

---

## 5. Workflow Design

**Manual checks:**

- **Clear step numbering.** Steps should be numbered and sequential. If steps can happen in parallel, say so explicitly.

- **Approval gates.** Before any destructive or externally visible action (posting to social media, sending emails, deleting files), the skill should require user confirmation.

- **Error handling.** The skill should have a table or section covering what to do when things go wrong. At minimum: missing credentials, API errors, invalid input.

- **Input gathering.** Step 1 should collect all needed inputs. Don't ask the user for information mid-workflow that could have been gathered upfront.

- **Autonomy rules.** If the skill has both autonomous and confirmation-required actions, list them explicitly. This prevents Claude from asking permission for every trivial step.

---

## 6. Scripts & Resources

**Manual checks:**

- **Scripts are executable.** Check that `.sh` files have `#!/usr/bin/env bash` and `.py` files have `#!/usr/bin/env python3`.

- **No inline script instructions.** If the SKILL.md tells Claude to "write a Python script that does X", that script should be in `scripts/` instead. Every future invocation would otherwise reinvent it.

- **Dependencies documented.** If scripts need pip packages or system tools, the `compatibility` frontmatter field should list them.

- **Reference files are referenced.** Every file in `references/` should be mentioned in SKILL.md with guidance on when to read it. Orphaned reference files add confusion.

- **Assets are used.** Every file in `assets/` should be referenced somewhere. Templates, icons, fonts that aren't used should be removed.

---

## 7. Folder Structure

**Expected structure:**
```
skill-name/
├── SKILL.md          (required)
├── scripts/          (executable code)
├── references/       (documentation, NOT "docs/")
└── assets/           (templates, icons, fonts)
```

**Manual checks:**

- **No `docs/` directory.** Anthropic convention is `references/`. If `docs/` exists, rename it.

- **No loose files.** Files at the skill root (other than SKILL.md and LICENSE) should be in a subdirectory.

- **Directory naming.** All directories should be lowercase. No spaces, no camelCase.

- **Name matches directory.** The `name` in frontmatter must match the skill's directory name.

---

## Severity Guide

When reporting issues, use these severity levels:

| Level | Criteria | Action |
|-------|----------|--------|
| **Error** | Skill will fail to load or malfunction | Must fix before use |
| **Warning** | Works but doesn't follow best practices | Should fix for quality |
| **Info** | Optional improvement | Fix when convenient |
