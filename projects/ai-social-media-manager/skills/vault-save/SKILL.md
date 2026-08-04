---
name: vault-save
description: >-
  Save Claude Code outputs to the Obsidian vault with proper frontmatter,
  wikilinks, and folder routing. Use when user says "save this to Obsidian",
  "vault save", "log this session", "save to vault", or invokes /vault-save.
  Supports conversations, skills, snippets, resources, and project notes.
allowed-tools: "Read Write Glob Grep"
---

# /vault-save -- Save to Obsidian Vault

Save Claude Code outputs -- session summaries, skills, code snippets, resources, or notes -- into the Obsidian Claude-Brain vault with correct frontmatter, folder placement, and wikilinks.

> **Do NOT use for:** Storing credentials or API keys, binary files, or large media assets. Not for publishing content -- use /post or /blog instead.

---

## Constants

```
VAULT_ROOT: ~/Obsidian/Claude-Brain
CONVERSATIONS_DIR: ${VAULT_ROOT}/02-AI-Conversations/claude-code
SKILLS_DIR: ${VAULT_ROOT}/03-Skills-and-Tools/skills
SNIPPETS_DIR: ${VAULT_ROOT}/04-Resources/snippets
RESOURCES_DIR: ${VAULT_ROOT}/04-Resources/concepts
INBOX_DIR: ${VAULT_ROOT}/00-Inbox
PROJECTS_DIR: ${VAULT_ROOT}/01-Projects
DEFAULT_PROJECT: "[[AI Social Media Manager]]"
```

---

## Workflow

### Step 1 -- Determine Note Type

Infer the type from context or `--type` flag:

| Type | When | Target Folder |
|------|------|---------------|
| `conversation` | Session summaries, session docs, work logs | `02-AI-Conversations/claude-code/` |
| `skill` | New or updated skill documentation | `03-Skills-and-Tools/skills/` |
| `snippet` | Reusable code patterns, script docs | `04-Resources/snippets/` |
| `resource` | Concepts, references, learnings, research briefs | `04-Resources/concepts/` |
| `note` | Anything else, quick captures | `00-Inbox/` |

If unclear, default to `note` (Inbox).

### Step 2 -- Build Frontmatter

Every note needs flat YAML frontmatter following the vault's conventions. No nesting.

**Conversations:**
```yaml
---
type: ai-conversation
date: YYYY-MM-DDTHH:mm
model: claude-code
source: claude-code
project: "[[AI Social Media Manager]]"
topics:
  - topic1
  - topic2
status: raw
summary: "One-line summary of what was accomplished"
---
```

**Skills:**
```yaml
---
type: skill
date: YYYY-MM-DD
skill_name: "/skill-name"
associated_project: "[[AI Social Media Manager]]"
topics:
  - topic1
status: reviewed
summary: "What does this skill do?"
---
```

**Snippets:**
```yaml
---
type: snippet
date: YYYY-MM-DD
language: python
project: "[[AI Social Media Manager]]"
topics:
  - topic1
status: reviewed
summary: "What this snippet does"
---
```

**Resources:**
```yaml
---
type: resource
date: YYYY-MM-DD
project: "[[AI Social Media Manager]]"
topics:
  - topic1
status: raw
summary: "One-line description"
---
```

### Step 3 -- Generate File Name

Follow the vault's naming convention:

| Type | Pattern | Example |
|------|---------|---------|
| Conversation | `YYYY-MM-DD Title of Session.md` | `2026-03-07 Research Skill Implementation.md` |
| Skill | `Skill - skill-name.md` | `Skill - research.md` |
| Snippet | `Snippet - descriptive-name.md` | `Snippet - resolve-location-pattern.md` |
| Resource | `descriptive-title.md` | `notebooklm-integration-patterns.md` |
| Note | `YYYY-MM-DD descriptive-title.md` | `2026-03-07 carousel-engagement-data.md` |

Rules:
- No special characters except hyphens and spaces
- Title case for conversations, sentence case for others
- Keep titles concise (under 60 characters)

### Step 4 -- Write the Content

Structure the note body based on type:

**Conversations (default -- reflective retrospective):**

This is the standard format for all conversation notes. Use this unless explicitly instructed otherwise.

```markdown
# {Title}

## Context
{What prompted this session -- 1-2 sentences}

## Reflective Retrospective

### What went well
{3-5 bullet points. Be specific about decisions, execution, and outcomes.}

### What could improve
{2-4 bullet points. Honest assessment of friction, mistakes, or missed opportunities.}

## Key Decisions and Rationale
{For each significant decision made during the session:}

### Decision N: {Short title}
**Chose:** {What was selected}
**Rejected:** {What alternatives were considered}
**Rationale:** {Why this choice won. Include the tradeoff accepted.}

## Tradeoffs Accepted

| Tradeoff | Accepted | Gained |
|----------|----------|--------|
| {What was given up} | Yes/Partially | {What was gained in return} |

## Learnings
{3-5 numbered insights. Concrete, reusable knowledge -- not session-specific.}

## Changes Made

| File | Action | Description |
|------|--------|-------------|
| `{path}` | Created/Modified/Deleted | {Brief description} |

## Action Items
- [ ] {Follow-up tasks discovered during the session}

## Related
- [[wikilink to related vault notes]]

---

## Conversation Log

{Full transcript of the session. Include every user prompt and assistant response
in chronological order. Use the following format:}

**User:**
> {Exact user message, quoted}

**Claude:**
{Summary of assistant response and actions taken. Include tool calls and key outputs.
For long code outputs, summarize what was generated rather than pasting full source.}

{Repeat for each exchange in the session.}
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

{Content -- one topic per note, atomic}

## Related
- [[wikilink to related notes]]
```

### Step 5 -- Save Artifacts

Copy all non-markdown artifacts generated during the session to the vault attachments folder. This preserves the full output alongside the conversation note.

**Target folder:** `${VAULT_ROOT}/04-Resources/attachments/`

**Rules:**
- **Auto-save (no confirmation):** HTML files, JSON files, Python scripts, shell scripts, text files, PDFs, PPTX
- **Ask before saving:** Images (PNG, JPG, GIF, SVG), videos (MP4, MOV), audio files, any file over 10MB
- **Never save:** Credentials, `.env` files, API keys, `node_modules`, `.git` directories

**How:**
1. Identify all files created or modified during the session (from Changes Made)
2. Copy each artifact to `${VAULT_ROOT}/04-Resources/attachments/`
3. In the conversation note, link artifacts using `[[filename.ext]]` wikilinks
4. Add a tip: `> Open in browser: right-click the link in Obsidian and choose "Open in default app"`

### Step 6 -- Preview and Write

1. Show the full note (frontmatter + body) to the user.
2. Ask: **"Save to [target path]? Approve or edit."**
3. On approval, write the file using the Write tool with the full absolute path.

### Step 7 -- Sync to Firestore

After writing the file locally, sync it to Firestore for cloud access:

```bash
python3 ${CLAUDE_SKILL_DIR}/../../shared/scripts/vault_firestore_sync.py --file "<absolute_path_to_saved_file>"
```

This mirrors the note to the corresponding Firestore collection (e.g., `conversations`, `resources`, `skills`). If Firestore is unavailable, log a warning but do not block the save.

### Step 8 -- Verify

1. Read the file back to confirm it saved correctly.
2. Report: **"Saved to [path]. [N] words, [type] note. Synced to Firestore: [collection]. [N] artifacts attached."**

---

## Examples

### Save current session
```
User: /vault-save
-> Summarizes the current session context
-> Saves to 02-AI-Conversations/claude-code/2026-03-07 Research Skill Implementation.md
```

### Save a skill doc
```
User: /vault-save --type skill the /research skill
-> Creates a skill note documenting /research
-> Saves to 03-Skills-and-Tools/skills/Skill - research.md
```

### Save a learning
```
User: /vault-save --type resource "Veo 3.1 cannot render text reliably"
-> Creates an atomic resource note
-> Saves to 04-Resources/concepts/veo-text-rendering-limitation.md
```

---

## Autonomy Rules

**Run automatically (no confirmation):**
- Determining note type from context
- Building frontmatter
- Generating file name
- Reading existing vault notes for linking

**Ask before running:**
- Writing the file (show preview first)
- Overwriting an existing file

---

## Error Handling

| Error | Action |
|-------|--------|
| Vault directory doesn't exist | "Obsidian vault not found at `~/Obsidian/Claude-Brain/`. Check the path or create the directory structure." |
| File already exists | "A note with this name already exists. Overwrite, rename, or skip?" |
| Content too long for single note | Split into multiple atomic notes, link them with wikilinks |
