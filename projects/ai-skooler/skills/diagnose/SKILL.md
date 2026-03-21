---
name: diagnose
description: Diagnose where a community creator sits in the Kourse 7-OS progression, identify their binding constraint, and show the revenue math. Use when user asks to assess their community, figure out what to focus on, or wants a diagnostic.
---

# Community Scaling Diagnostic

Maps a community creator to their position in the Kourse 7-OS progression, identifies the binding constraint blocking growth, and runs the revenue math.

## Prerequisites

- Kourse vault must exist at `/Users/MC/Obsidian/ai-skooler/Kourse/`
- Read [references/os-phases.md](references/os-phases.md) for the full phase map before starting

## Input

The user describes their community situation. They may provide details upfront or need to be asked.

If the user provides a community URL or name, that's context — but the diagnostic is about their _current state_, not their content.

## Instructions

### Step 1: Gather the situation

Read [references/os-phases.md](references/os-phases.md) for the diagnostic questions.

If the user hasn't provided enough information, ask the 13 diagnostic questions. Group them naturally — don't fire all 13 as a numbered list. Ask in 2-3 conversational rounds:

**Round 1 (Identity):** Niche, Skool group status, current revenue, revenue target
**Round 2 (Infrastructure):** Funnel, course content, traffic sources, weekly new members
**Round 3 (Conversion):** Calls booked/week, show-up rate, close rate, offer price, team

If the user gives partial info, work with what you have. Use the default assumptions from the reference file for missing numbers. Flag what you assumed.

### Step 2: Determine their OS phase

Using the phase definitions in [references/os-phases.md](references/os-phases.md), determine which OS they're currently _in_ (not which they've completed). The phases are sequential — you can't be in Sales OS if Traffic OS isn't producing leads.

**Phase detection logic:**

1. No infrastructure (domain, funnel, Skool, calendar) → **Launch OS**
2. Infrastructure exists, no course content → **Course OS**
3. Content exists, under ~100 free members or no traffic system → **Traffic OS**
4. Traffic coming but low conversion to calls (under 2% of members booking) → **Promo OS**
5. Calls happening but close rate under 20% or no sales system → **Sales OS**
6. Closing deals but revenue plateaued, no team, no backend → **Ascension OS**
7. $30K+/month, needs team scaling and advanced strategies → **Scale OS**

People often _think_ they're in a later phase. Check the prerequisites of their claimed phase. If prerequisites aren't met, they're actually in an earlier phase.

### Step 3: Identify the binding constraint

The binding constraint is the single bottleneck that, if resolved, moves everything forward. It's always in their current OS phase.

Common binding constraints by phase:

- **Launch OS:** No funnel / no payment system / no niche selected
- **Course OS:** Perfectionism (won't publish until "ready") / no content structure
- **Traffic OS:** Zero traffic sources active / only one channel / not publishing consistently
- **Promo OS:** No conversion mechanism (no Auto DM, no workshops, no email sequence) / bad offer structure
- **Sales OS:** No script / fear of selling / bad discovery (not building the gap) / no objection handling
- **Ascension OS:** Founder is the bottleneck / no team / no backend offer / burnout

State the binding constraint directly. One sentence. No hedging.

### Step 4: Run the math

Using the revenue math formula from [references/os-phases.md](references/os-phases.md), calculate:

1. Clients needed per month
2. Sales calls needed (adjusted for close rate)
3. Calls that need to be booked (adjusted for show-up rate)
4. Daily call target

Show the math explicitly. If numbers are assumed, say so.

### Step 5: Read relevant vault content

Based on the diagnosed phase, read 2-3 key lesson files from the Kourse vault at `/Users/MC/Obsidian/ai-skooler/Kourse/` that directly address their binding constraint. Don't summarize the entire OS — pull the specific insight that applies to their situation.

### Step 6: Write the diagnostic

Output a single, concise diagnostic. No fluff. Use this structure exactly:

```markdown
## Diagnostic: [User's niche/community name]

### Position: [OS Phase Name] (Phase [N] of 7)

[1-2 sentences on why they're in this phase, not the one they think they're in if applicable]

### Binding Constraint

**[One sentence stating the constraint]**

[2-3 sentences explaining why this is the bottleneck, referencing the Kourse framework]

### The Math

| Metric            | Value               |
| ----------------- | ------------------- |
| Revenue target    | $X/month            |
| Offer price       | $X                  |
| Clients needed    | X/month             |
| Close rate        | X% [assumed/actual] |
| Calls needed      | X/month             |
| Show-up rate      | X% [assumed/actual] |
| Calls to book     | X/month             |
| Daily call target | X/day               |

### What to Do Next

1. [Specific action 1] → uses [[Resource Name]]
2. [Specific action 2] → uses [[Resource Name]]
3. [Specific action 3]

### What NOT to Do

[1-2 things they should explicitly stop or avoid — common mistakes for their phase]

### When You're Ready to Move On

[Exit criteria — specific, measurable conditions that signal they can advance to the next OS]
```

## Output Rules

- No motivational language. No "you've got this." No "great question."
- Direct, specific, actionable.
- Reference actual Kourse resources by wiki-link name.
- If the user is in Launch OS or Course OS, do NOT talk about sales tactics. They're not there yet.
- If the user claims they need "more traffic" but their offer sucks, call it. The binding constraint is the offer, not the traffic.
- Show the math even if it's uncomfortable. If they need 15 calls/day on a 5% close rate with a $200 offer, the math says the offer price is the problem.
- Suggest `/blueprint` for the identified phase as the natural next step.
