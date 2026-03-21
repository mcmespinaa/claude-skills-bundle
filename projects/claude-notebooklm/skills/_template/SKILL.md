---
name: SKILL_NAME
description: >
  One-paragraph description. Include: what the skill does, when to use it,
  trigger phrases, and what NOT to use it for (direct to correct skill instead).
compatibility: Requires jq, curl, python3. macOS or Linux. GHL API key in .env.
metadata:
  author: content-engine
  version: 1.0.0
  argument-hint: '"required_arg" [--optional-flag value]'
  user-invokable: true
---

# /SKILL_NAME — Short Title

> **Trigger:** User says `/SKILL_NAME`, "TRIGGER_PHRASE_1", "TRIGGER_PHRASE_2", or similar.

## Role

You are a [ROLE]. You [WHAT_YOU_DO]. You follow brand voice rules and [KEY_CONSTRAINT].

---

## Constants

```
SCRIPTS_DIR: ${CLAUDE_PLUGIN_ROOT}/skills/SKILL_NAME/scripts
REFS_DIR:    ${CLAUDE_PLUGIN_ROOT}/skills/SKILL_NAME/references
BRAND_DOCS_DIR: Resolved in Step 0 — $PWD/brands/<LOCATION>/ if it exists,
                else ${CLAUDE_PLUGIN_ROOT}/skills/SKILL_NAME/references (fallback)
```

---

## Workflow

### Step 0: Resolve Location & Brand

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve_location.sh" \
  --export --location <LOCATION>
```

Read `<BRAND_DOCS_DIR>/brand-voice.md` before writing any outward-facing content.

### Step 1: [GATHER_INPUT]

Collect from the user:

| Input | Required | Default |
|-------|----------|---------|
| [input_1] | Yes | — |
| [input_2] | No | [default_value] |

### Step 2: [PROCESS]

[Core logic. What the skill does with the inputs.]

### Step 3: [PRESENT_FOR_APPROVAL]

Show the draft to the user:

> Here's your [OUTPUT_TYPE]:
>
> [output preview]
>
> Approve, edit, or regenerate?

**Do NOT proceed until the user approves.**

### Step 4: [EXECUTE]

[API calls, file operations, or external actions.]

### Step 5: Log & Confirm

[Log to the appropriate audit trail file.]

Confirm to user: **"[Action] complete. [Details]."**

---

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| 401 Unauthorized | API token expired | Notify user to refresh key |
| [ERROR_2] | [CAUSE] | [ACTION] |

---

## Autonomy Rules

**Run automatically (no confirmation):**
- Reading config files (locations.json, brand-voice.md)
- [OTHER_SAFE_ACTIONS]

**Ask before running:**
- [ACTIONS_WITH_SIDE_EFFECTS]
- Writing to log files
