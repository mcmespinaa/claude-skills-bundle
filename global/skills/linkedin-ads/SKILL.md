---
name: linkedin-ads
description: Run the LinkedIn Ad Engine — a client-agnostic, research-to-launch pipeline for winning LinkedIn B2B ads. Use when the user wants to create, plan, research, or launch LinkedIn ads / LinkedIn B2B campaigns, build a LinkedIn ad workflow, mine competitor LinkedIn ads, pick ad angles, or run any stage of the 6-stage LinkedIn ad pipeline (intelligence, angle, swipe, build, launch-matrix, read-iterate). Triggered by /linkedin-ads, "LinkedIn ads", "B2B LinkedIn campaign", "research LinkedIn competitors", "winning LinkedIn ad". NOT for Meta/Facebook/Instagram ads — use /ads. NOT for organic LinkedIn posting — use /post.
---

# LinkedIn Ad Engine

A client-agnostic, research-to-launch pipeline for winning LinkedIn B2B ads. Usable by any
agency for any client. This skill is a thin launcher — the methodology and stage contracts
live in the engine repo; this file routes the user into them.

## Where the engine lives

- **Pipeline (run it):** `~/Workspaces/Projects/linkedin-ad-engine/`
  - `CLAUDE.md` — entry point, "factory vs. product" model
  - `pipeline/**/CONTEXT.md` — the 6 stage contracts (chained output→input)
  - `templates/client-brief.template.md` — the one required input
  - `runs/<client-slug>/` — live artifacts per engagement
- **Knowledge (browse it):** `~/Obsidian-Project-Docs/linkedin-ad-engine-docs/`
  - `methodology/` — workflow, 5-part B2B skeleton, tools landscape
  - `swipe-file/` — proven structures + own confirmed winners
  - `client-runs/` — durable ICP insight per client

If those paths don't exist on this machine, tell the user the engine repo isn't installed
here and point them at `~/Workspaces/Projects/linkedin-ad-engine/` as the canonical home.

## Boundaries (route elsewhere)

- **Meta / Facebook / Instagram ads** → `/ads` (this skill is LinkedIn-only)
- **Organic LinkedIn posting** → `/post` (this skill is paid ads only)
- **General research** → `/think` (this skill calls it from stage 01/02, but standalone research is /think)

## The 6 stages

```
01-intelligence → 02-angle → 03-swipe → 04-build → 05-launch-matrix → 06-read-iterate
   mine sources     pick bets   borrow      write+      test 1 var        kill / scale
                                structure    design      in isolation      → feeds 03
```

Default posture: **balanced — 3 angles × 1 hook**, audience constant. Judge on
cost-per-qualified-lead and ad longevity, never CTR.

## How to run

1. **Start a run.** Ask the user which client this is for. Copy
   `templates/client-brief.template.md` → `runs/<client-slug>/client-brief.md` and help
   them fill it in (ICP, named competitors, offer, proof, voice, compliance, budget,
   qualified-lead definition). The brief is the *only* client-specific input — everything
   downstream reads from it. Do not proceed past stage 01 with placeholders unfilled.

2. **Seed stage 01.** Copy the filled brief into `pipeline/01-intelligence/reference/`.

3. **Run stages in order** using the ICM skills (the contracts are written for them):
   - `/run-stage` — execute the next stage from its `CONTEXT.md`.
   - `/stage-review` — verify outputs against the stage's Review Checkpoint before advancing.
   - `/validate-pipeline` — check the output→input chain across all six stages.

4. **Human gates.** Two stages need explicit user sign-off, not just agent output:
   - **Stage 02 (angle):** confirm which angles go live — cheapest place to kill a bad bet.
   - **Stage 05 (launch matrix):** set kill/scale thresholds *before* launch.

5. **Close the loop.** Stage 06 writes confirmed winners back to
   `~/Obsidian-Project-Docs/linkedin-ad-engine-docs/swipe-file/` and spawns hook variants by
   re-entering stage 03. Each run leaves the swipe file stronger for the next client.

## Sub-skills this calls

`/think` (stage 01–02) · `/ads` hook-library mode (stage 03) · `/slop-proof` + `/nordic-style`
(stage 04 register gate) · `/frontend-design` (stage 04 visuals) · `/analytics` (stage 06).
