---
name: decision-log
description: Document a community scaling decision with full rationale, tradeoffs, and reversibility analysis. Use when user says /decision-log, asks to log a decision, or wants to document why they chose a specific approach for their community.
---

# Decision Log

Documents community scaling decisions with structured rationale, tradeoffs, and reversibility analysis. Writes to the Obsidian decisions vault for future reference.

## Prerequisites

- Decisions vault at `$HOME/Obsidian/OrganicForward/decisions/` must be accessible
- Kourse vault at `$HOME/Obsidian/ai-skooler/Kourse/` for framework references

## Input

The user describes a decision they've made or need to make. This can be:

1. A completed decision: "I decided to use GoHighLevel instead of Calendly"
2. A pending decision: "Should I do free or paid community first?"
3. A decision surfaced by `/blueprint`: a tradeoff from the Tradeoffs table
4. A strategic direction: "I'm going to focus on YouTube instead of Meta ads"

## Instructions

### Step 1: Understand the decision context

If the user hasn't provided enough context, ask (one round only):

- What are you deciding between?
- What's driving this decision? (deadline, cost, capability, preference)
- What have you already tried or ruled out?
- What phase are you in? (or reference their last `/diagnose`)

### Step 2: Research from the vault

Read relevant Kourse lessons that address this decision area. The vault has real frameworks for most community scaling decisions. Pull the actual Kourse perspective — don't invent generic pros/cons.

Check if similar decisions have been logged before:

```
$HOME/Obsidian/OrganicForward/decisions/
```

### Step 3: Write the decision record

Use this format exactly:

```markdown
---
type: decision
status: [decided | pending | revisit]
date: [YYYY-MM-DD]
phase:
  [
    Launch OS | Course OS | Traffic OS | Promo OS | Sales OS | Ascension OS | Scale OS,
  ]
tags: [relevant tags]
---

# [Decision Title — short, specific]

## Context

[2-3 sentences: What situation created this decision point? What phase are you in? What constraint or goal is driving it?]

## Decision

**[One sentence: what was decided, or what the options are if pending]**

## Options Evaluated

### Option A: [Name]

- **Pros:** [bullet list]
- **Cons:** [bullet list]
- **Cost:** [money, time, or effort]
- **Kourse alignment:** [Does this match what the Kourse framework recommends? Reference specific lesson if applicable]

### Option B: [Name]

- **Pros:** [bullet list]
- **Cons:** [bullet list]
- **Cost:** [money, time, or effort]
- **Kourse alignment:** [Reference]

### Option C: [Name] (if applicable)

...

## Rationale

[3-5 sentences: Why this option over the others. What was the deciding factor? Reference the Kourse framework if it informed the choice. Be honest about what's a guess vs. what's data-driven.]

## Tradeoffs Accepted

- [What you're giving up by choosing this path]
- [What risk you're accepting]
- [What assumption must hold true for this to work]

## Reversibility

| Factor          | Assessment                            |
| --------------- | ------------------------------------- |
| Reversibility   | [Easy / Medium / Hard / Irreversible] |
| Cost to reverse | [What it would take to undo this]     |
| Time locked in  | [How long before you can re-evaluate] |
| Blast radius    | [What else this decision affects]     |

## Review Trigger

[Specific condition that should cause you to revisit this decision. Not a date — a signal.]

Example: "Revisit if close rate stays below 15% after 20 calls" or "Revisit if Meta CPL exceeds $15 for 2 consecutive weeks"

## Related

- [[Relevant Lesson or Resource]]
- [[Previous Decision if applicable]]
```

### Step 4: Save the decision

Write the decision record to `$HOME/Obsidian/OrganicForward/decisions/` with the filename format:
`[YYYY-MM-DD] [Decision Title].md`

If the decision is about the ai-skooler project specifically (not OrganicForward), save to `$HOME/Obsidian/ai-skooler/` in an appropriate location instead.

### Step 5: Cross-reference

If the decision relates to a specific blueprint step, mention which blueprint and step it connects to. If it invalidates or modifies a previous decision, note that and update the previous decision's status to `superseded`.

## Output Rules

- No judgment on the user's choice. Document it faithfully even if the Kourse framework would recommend differently — but note the divergence.
- If the user asks "what should I do?" — give a recommendation with rationale, but frame it as a recommendation, not a directive. Reference the Kourse framework.
- For pending decisions: present the analysis and make a recommendation, but let the user decide. Then log whatever they choose.
- Reversibility analysis is mandatory. Most community decisions feel permanent but aren't — help the user see which ones actually are.
- Keep the record concise. A decision log that nobody reads is worthless. Target under 400 words for the whole record.
- If this decision was surfaced by `/blueprint`, link back to the specific blueprint step.
