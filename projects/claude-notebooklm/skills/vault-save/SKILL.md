---
name: vault-save
description: Save Claude Code outputs to the Obsidian vault with proper frontmatter, wikilinks, and folder routing. Use when user says "save this to Obsidian", "vault save", "log this session", "save to vault", or invokes /vault-save. Supports conversations, skills, snippets, resources, and project notes. Do NOT use for reading or querying the vault — use direct file tools instead.
argument-hint: '"<content or file>" [--type conversation|skill|snippet|resource|note] [--project name]'
disable-model-invocation: true
---

# /vault-save — Save to Obsidian Vault

> **Trigger:** User says `/vault-save`, "save this to Obsidian", "save to vault", "log this session", "vault save this", or similar.

## Purpose

Save Claude Code outputs — session summaries, skills, code snippets, resources, or notes — into the Obsidian Claude-Brain vault with correct frontmatter, folder placement, and wikilinks.

---

## Constants

```
VAULT_ROOT: $HOME/Obsidian/Claude-Brain
CONVERSATIONS_DIR: ${VAULT_ROOT}/02-AI-Conversations/claude-code
SKILLS_DIR: ${VAULT_ROOT}/03-Skills-and-Tools/skills
SNIPPETS_DIR: ${VAULT_ROOT}/04-Resources/snippets
RESOURCES_DIR: ${VAULT_ROOT}/04-Resources/concepts
INBOX_DIR: ${VAULT_ROOT}/00-Inbox
PROJECTS_DIR: ${VAULT_ROOT}/01-Projects
TEMPLATES_DIR: ${VAULT_ROOT}/05-Templates
```

---

## Workflow

### Step 1 — Determine Note Type

Infer the type from context or `--type` flag:

| Type | When | Target Folder |
|------|------|---------------|
| `conversation` | Session summaries, session docs | `02-AI-Conversations/claude-code/` |
| `skill` | New or updated skill documentation | `03-Skills-and-Tools/skills/` |
| `snippet` | Reusable code patterns | `04-Resources/snippets/` |
| `resource` | Concepts, references, learnings | `04-Resources/concepts/` |
| `note` | Anything else, quick captures | `00-Inbox/` |

If unclear, default to `note` (Inbox).

### Step 2 — Build Frontmatter

Every note needs YAML frontmatter following the vault's conventions. Use flat YAML only (no nesting).

#### For Conversations

```yaml
---
type: ai-conversation
date: YYYY-MM-DDTHH:mm
model: claude-code
source: claude-code
project: "[[project-name]]"
topics:
  - topic1
  - topic2
status: raw
summary: "One-line summary"
---
```

#### For Skills

```yaml
---
type: skill
date: YYYY-MM-DD
skill_name: "/skill-name"
associated_project: "[[project-name]]"
topics:
  - topic1
status: reviewed
summary: "What does this skill do?"
---
```

#### For Snippets

```yaml
---
type: snippet
date: YYYY-MM-DD
language: python
project: "[[project-name]]"
topics:
  - topic1
status: reviewed
summary: "What this snippet does"
---
```

#### For Resources

```yaml
---
type: resource
date: YYYY-MM-DD
project: "[[project-name]]"
topics:
  - topic1
status: raw
summary: "One-line description"
---
```

### Step 3 — Generate File Name

Follow the vault's naming convention:

- **Conversations:** `YYYY-MM-DD Title of Session.md`
- **Skills:** `Skill - skill-name.md`
- **Snippets:** `Snippet - descriptive-name.md`
- **Resources:** `descriptive-title.md`
- **Notes:** `YYYY-MM-DD descriptive-title.md`

Rules:
- No special characters except hyphens and spaces
- Title case for conversations, sentence case for others
- Keep titles concise (under 60 characters)

### Step 4 — Write the Content

Structure the note body based on type:

**Conversations:**
```markdown
# {Title}

## Context
{What prompted this session}

## Key Outputs
{Main results, decisions, artifacts produced}

## Changes Made
{List of files created/modified with brief descriptions}

## Action Items
- [ ] {Any follow-up tasks}
```

**Skills:**
```markdown
# Skill: {name}

## Purpose
{What problem does this skill solve}

## Usage
`/{skill-name} [args]`

## Workflow Steps
1. ...

## Dependencies
{What tools, APIs, files needed}
```

**Snippets:**
````markdown
# {Title}

## Usage
```{language}
{code}
```

## Notes
{When to use, edge cases}
````

**Resources:**
```markdown
# {Title}

{Content — one topic per note, atomic}

## Related
- [[wikilink to related notes]]
```

### Step 5 — Write the File

Use the Write tool to save the file to the target folder. Use the full absolute path.

```
Write file to: {VAULT_ROOT}/{target_folder}/{filename}.md
```

### Step 6 — Verify and Link

After writing:

1. Read the file back to confirm it saved correctly
2. Check if a related project note exists in `01-Projects/` — if so, mention it in output
3. Report the file path to the user

---

## Quick Examples

### Save current session
```
User: /vault-save
-> Generates a conversation note from the current session context
-> Saves to 02-AI-Conversations/claude-code/2026-03-07 Session Title.md
```

### Save a code snippet
```
User: /vault-save --type snippet "the resolve_location pattern"
-> Creates a snippet note with the code and usage notes
-> Saves to 04-Resources/snippets/Snippet - resolve-location-pattern.md
```

### Save a learning
```
User: /vault-save --type resource "MCP servers need Obsidian running for the bridge"
-> Creates a resource note with the concept
-> Saves to 04-Resources/concepts/mcp-servers-obsidian-bridge.md
```

---

## Autonomy Rules

**Run automatically (no confirmation):**
- Determining note type from context
- Building frontmatter
- Generating file name
- Reading existing project notes for linking

**Ask before running:**
- Writing the file (show preview first with frontmatter + body)
- Overwriting an existing file with the same name
---

## Error Handling

| Error | Action |
|-------|--------|
| Vault directory doesn't exist | "Obsidian vault not found at `~/Obsidian/Claude-Brain/`. Check the path." |
| File already exists | "A note with this name already exists. Overwrite, rename, or skip?" |
| No project context | Use `"[[claude-notebooklm]]"` as default project |
| Content too long for single note | Split into multiple atomic notes, link them with wikilinks |
