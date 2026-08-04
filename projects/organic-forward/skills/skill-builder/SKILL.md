---
name: skill-builder
description: >-
  Create new skills, modify and improve existing skills, and measure skill
  performance. Use when users want to create a skill from scratch, edit or
  optimize an existing skill, run evals to test a skill, benchmark skill
  performance, or optimize a skill's description for better triggering accuracy.
  Also use when someone says "build a skill", "make a skill", "turn this into a
  skill", or "improve this skill".
---

# Skill Builder

A skill for creating, testing, and iteratively improving Claude Code skills.

## Core Loop

The skill-building process follows this cycle:

1. **Capture intent** — understand what the skill should do
2. **Draft the skill** — write SKILL.md with frontmatter and instructions
3. **Create test cases** — 2-3 realistic prompts a real user would say
4. **Run tests** — execute with-skill and baseline runs in parallel
5. **Evaluate** — quantitative evals + human review via the eval viewer
6. **Improve** — revise skill based on feedback
7. **Repeat** until satisfied
8. **Optimize description** — tune triggering accuracy

Your job is to figure out where the user is in this process and help them progress. Maybe they want to create something from scratch, or maybe they already have a draft that needs testing. Be flexible.

## Communication Style

Pay attention to context cues about the user's technical level. In the default case:
- "evaluation" and "benchmark" are fine
- For "JSON" and "assertion", check for cues the user knows these before using without explanation
- It's OK to briefly explain terms if you're unsure

---

## Phase 1: Capture Intent

Start by understanding what the user wants. The current conversation might already contain a workflow to capture (e.g., "turn this into a skill"). If so, extract answers from the conversation history first.

Key questions:
1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases? (suggest the appropriate default based on skill type — objectively verifiable outputs benefit from tests, subjective outputs often don't)

### Interview and Research

Proactively ask about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've ironed this out.

Check available MCPs and project context. Research in parallel via subagents if available.

---

## Phase 2: Write the SKILL.md

### Skill Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

### Frontmatter Fields

```yaml
---
name: skill-name
description: What it does AND when to trigger. Be slightly "pushy" — include contexts where the skill should activate even if the user doesn't explicitly name it.
disable-model-invocation: true  # Optional: manual-only invocation
user-invocable: false           # Optional: hide from / menu
allowed-tools: Read, Grep       # Optional: restrict tool access
context: fork                   # Optional: run in subagent
agent: Explore                  # Optional: subagent type
model: sonnet                   # Optional: model override
---
```

### Writing Guidelines

- **Explain the why** behind instructions. Today's LLMs are smart — reasoning > rigid rules.
- **Use imperative form** for instructions.
- **Keep SKILL.md under 500 lines**. Move detailed reference material to separate files.
- **Progressive disclosure**: Metadata (~100 tokens) always loaded. SKILL.md body loaded when triggered. Bundled resources loaded as needed.
- **Include examples** to show expected format.
- **Think general, not narrow** — don't overfit to specific examples.

### Description Writing

The description is the primary triggering mechanism. Include:
- What the skill does
- Specific contexts when to use it
- Related phrases users might say

Make it slightly "pushy" to combat under-triggering. Example:
- Bad: "Creates API endpoints"
- Good: "Creates API endpoints following project conventions. Use when building new routes, REST endpoints, API handlers, or when the user mentions adding backend functionality."

### Dynamic Context

Use `!`command`` to inject live data before Claude sees the prompt:

```yaml
## Current branch info
- Branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -5`
```

### Supporting Files

Reference them from SKILL.md so Claude knows when to load them:

```markdown
## Additional resources
- For JSON schemas, see [references/schemas.md](references/schemas.md)
- For grading instructions, see [agents/grader.md](agents/grader.md)
```

---

## Phase 3: Test Cases

After writing the skill draft, create 2-3 realistic test prompts. Share with the user for review before running.

Save test cases to `evals/evals.json`:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": [],
      "expectations": [
        "The output includes X",
        "The skill used script Y"
      ]
    }
  ]
}
```

See [references/schemas.md](references/schemas.md) for the full schema including the assertions field.

---

## Phase 4: Run and Evaluate

This is one continuous sequence — don't stop partway through.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Organize by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, each test case gets a directory.

### Step 1: Spawn all runs in the same turn

For each test case, spawn two subagents simultaneously:

**With-skill run:**
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any>
- Save outputs to: <workspace>/iteration-N/eval-ID/with_skill/outputs/
```

**Baseline run** (same prompt, no skill):
- Creating new skill → no skill at all, save to `without_skill/outputs/`
- Improving existing skill → snapshot old version, save to `old_skill/outputs/`

Write `eval_metadata.json` for each test case with a descriptive name.

### Step 2: While runs are in progress, draft assertions

Don't wait — draft quantitative assertions and explain them to the user. Good assertions are objectively verifiable with descriptive names.

Update `eval_metadata.json` and `evals/evals.json` with assertions.

### Step 3: Capture timing data

When subagent tasks complete, save `total_tokens` and `duration_ms` to `timing.json` immediately — this data isn't persisted elsewhere.

### Step 4: Grade, aggregate, and launch viewer

1. **Grade each run** — use [agents/grader.md](agents/grader.md) instructions. Save to `grading.json`. Use fields `text`, `passed`, and `evidence`.

2. **Aggregate into benchmark** — run:
   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/aggregate_benchmark.py <workspace>/iteration-N --skill-name <name>
   ```

3. **Analyst pass** — read benchmark data, surface patterns per [agents/analyzer.md](agents/analyzer.md).

4. **Launch the viewer**:
   ```bash
   python ${CLAUDE_SKILL_DIR}/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json
   ```
   For iteration 2+, add `--previous-workspace <workspace>/iteration-<N-1>`.

   If no browser available, use `--static <output_path>` for standalone HTML.

5. **Tell the user**: "I've opened the results in your browser. 'Outputs' tab lets you review each test case. 'Benchmark' tab shows the numbers. Come back when you're done."

### Step 5: Read feedback

Read `feedback.json` when the user is done. Empty feedback = user thought it was fine. Focus improvements on test cases with specific complaints.

---

## Phase 5: Improve the Skill

### How to Think About Improvements

1. **Generalize from feedback.** You're iterating on a few examples, but the skill will be used many times across many prompts. Don't overfit — if there's a stubborn issue, try different metaphors or patterns rather than fiddly constraints.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Read transcripts, not just outputs — if the skill makes the model waste time on unproductive steps, cut those parts.

3. **Explain the why.** If you're writing ALWAYS or NEVER in all caps, reframe with reasoning instead. Explain why something matters so the model understands, rather than just following rigid rules.

4. **Look for repeated work.** If all test runs independently wrote similar helper scripts, that's a signal to bundle the script in `scripts/` and reference it from the skill.

### Iteration Loop

1. Apply improvements
2. Rerun all test cases into `iteration-<N+1>/`
3. Launch reviewer with `--previous-workspace` pointing at previous iteration
4. Wait for user review
5. Read feedback, improve, repeat

Keep going until the user is happy, feedback is empty, or you're not making progress.

---

## Phase 6: Description Optimization

After the skill is solid, optimize the description for triggering accuracy.

### Step 1: Generate trigger eval queries

Create 20 queries — mix of should-trigger (8-10) and should-not-trigger (8-10). Save as JSON.

**For should-trigger**: Different phrasings, casual/formal mix, cases where user doesn't explicitly name the skill but clearly needs it.

**For should-not-trigger**: Near-misses that share keywords but actually need something different. Avoid obviously irrelevant queries — test the tricky cases.

Make queries realistic: include file paths, personal context, column names, casual speech, typos, abbreviations.

### Step 2: Review with user

Present eval set using the HTML template:
1. Read `${CLAUDE_SKILL_DIR}/assets/eval_review.html`
2. Replace `__EVAL_DATA_PLACEHOLDER__`, `__SKILL_NAME_PLACEHOLDER__`, `__SKILL_DESCRIPTION_PLACEHOLDER__`
3. Write to temp file and open it
4. User edits and exports to `~/Downloads/eval_set.json`

### Step 3: Run optimization loop

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id> \
  --max-iterations 5 \
  --verbose
```

### Step 4: Apply result

Take `best_description` from the JSON output and update SKILL.md frontmatter.

---

## Advanced: Blind Comparison

For rigorous A/B testing between skill versions, use blind comparison:
- See [agents/comparator.md](agents/comparator.md) for blind judging
- See [agents/analyzer.md](agents/analyzer.md) for post-hoc analysis

This is optional — the human review loop is usually sufficient.

---

## Project-Specific Notes

Skills in this project should be placed in `.claude/skills/<skill-name>/SKILL.md`. They'll be available to anyone working on the Organic Forward project.

Consider the project's existing command structure when creating skills:
- `/context-load` — session orientation
- `/status` — project state report
- `/session-log` — conversation extraction to Obsidian
- `/decisions` — decision registry queries

New skills should complement these without overlap.

---

## Reference Files

- [agents/grader.md](agents/grader.md) — Evaluate assertions against outputs
- [agents/comparator.md](agents/comparator.md) — Blind A/B comparison
- [agents/analyzer.md](agents/analyzer.md) — Post-hoc analysis and benchmark analysis
- [references/schemas.md](references/schemas.md) — JSON schemas for evals, grading, benchmarks
