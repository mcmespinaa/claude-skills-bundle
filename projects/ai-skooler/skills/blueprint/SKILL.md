---
name: blueprint
description: Generate a step-by-step execution blueprint for a specific OS phase or community scaling goal. Use when user says /blueprint, asks for a plan, playbook, or step-by-step guide for their community, or after a /diagnose reveals what phase they're in.
---

# Community Scaling Blueprint

Generates a no-fluff, step-by-step execution blueprint for a specific Kourse OS phase or community scaling goal. Every step maps to real Kourse resources and frameworks.

## Prerequisites

- Kourse vault must exist at `/Users/MC/Obsidian/ai-skooler/Kourse/`
- Read the OS phases reference at `/Users/MC/ai-skooler/.claude/skills/diagnose/references/os-phases.md` for phase context
- Read the relevant lesson files from the vault before writing the blueprint

## Input

The user provides one of:

1. An OS phase name (e.g., "blueprint for Traffic OS", "blueprint for Sales OS")
2. A specific goal (e.g., "blueprint to get my first 10 sales calls", "blueprint to launch my Skool community")
3. Output from a `/diagnose` — build the blueprint for the diagnosed phase automatically

If the input is a goal, map it to the correct OS phase first. If it spans multiple phases, build the blueprint for the earliest incomplete phase only — sequential execution, not parallel.

## Instructions

### Step 1: Identify the phase and scope

Determine which single OS phase this blueprint covers. Read the phase definition from the diagnose skill's [references/os-phases.md](../diagnose/references/os-phases.md).

If the user came from `/diagnose`, use the diagnosed phase. If they specified a phase directly, use that. If they described a goal, map it:

| Goal pattern                                           | Phase        |
| ------------------------------------------------------ | ------------ |
| "set up my community", "launch", "get started"         | Launch OS    |
| "create my course", "build content", "record lessons"  | Course OS    |
| "get members", "grow", "traffic", "get eyeballs"       | Traffic OS   |
| "convert members", "get people on calls", "engagement" | Promo OS     |
| "close deals", "sell", "sales calls", "revenue"        | Sales OS     |
| "scale", "hire", "team", "mastermind", "backend"       | Ascension OS |

### Step 2: Read the vault lessons

Read the actual lesson files from `/Users/MC/Obsidian/ai-skooler/Kourse/` for the relevant OS module. Every blueprint step must trace back to a real lesson or resource — no invented advice.

Read at minimum:

- The "Welcome to [X] OS" lesson for that phase
- 2-3 key tactical lessons within that module
- Relevant resource files from `/Users/MC/Obsidian/ai-skooler/Kourse/Resources/` (if they exist)

### Step 3: Build the blueprint

Structure the blueprint as a **linear execution sequence**. Each step is one concrete action with a clear done-state. No branching. No "it depends." Pick the path.

Use this format exactly:

```markdown
## Blueprint: [Phase Name] — [User's specific goal or context]

**Time horizon:** [X weeks] (assuming [hours/week] dedicated)
**Entry condition:** [What must be true before starting this blueprint]
**Exit condition:** [Measurable outcome that signals this phase is complete]

---

### Week 1: [Theme]

**Step 1: [Action verb] [specific thing]**

- What: [1-2 sentences, exactly what to do]
- Resource: [[Resource Name]] or [[Lesson Name]]
- Done when: [Observable completion criteria]
- Time: ~[X hours]

**Step 2: [Action verb] [specific thing]**

- What: [1-2 sentences]
- Resource: [[Resource Name]]
- Done when: [Criteria]
- Time: ~[X hours]

### Week 2: [Theme]

...

---

### Tradeoffs & Decisions

| Decision         | Option A | Option B | Recommendation | Why                            |
| ---------------- | -------- | -------- | -------------- | ------------------------------ |
| [Decision point] | [Option] | [Option] | [Pick one]     | [Reason from Kourse framework] |

### Common Failure Modes

1. **[Failure pattern]** — [How it shows up] → [What to do instead]
2. **[Failure pattern]** — [How it shows up] → [What to do instead]

### Metrics to Track

| Metric   | Target   | Tool                   |
| -------- | -------- | ---------------------- |
| [Metric] | [Number] | [[Resource]] or manual |
```

### Step 4: Validate against the vault

Before outputting, verify:

- Every `[[Resource Name]]` and `[[Lesson Name]]` reference exists in the vault
- Steps follow the actual Kourse teaching order (don't skip ahead)
- Time estimates are realistic (not aspirational)
- The blueprint is completable — no steps that require things outside the user's control

### Step 5: Suggest decision logging

If the blueprint surfaces tradeoffs (it should), suggest the user run `/decision-log` on any decision they want to document with full rationale.

## Output Rules

- Maximum 4 weeks per blueprint. If the phase takes longer, split into Part 1 / Part 2.
- Every step starts with an action verb: Create, Write, Record, Set up, Configure, Test, Launch, Send, Call, Track.
- No motivational filler. No "remember, consistency is key." No "this is where the magic happens."
- If a step requires a tool/platform decision, put it in the Tradeoffs table with a clear recommendation.
- Time estimates are per-step, not per-day. A "~2 hours" step might take someone 4 hours if they're learning.
- Include 2-4 decision points in the Tradeoffs table. Community scaling always involves choices — surface them.
- Include 2-3 failure modes. These should be real patterns from the Kourse content, not generic advice.
- If the user hasn't done `/diagnose` first, suggest it — but still build the blueprint if they specified a phase.
