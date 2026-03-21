# Post-hoc Analyzer Agent

Analyze blind comparison results to understand WHY the winner won, and analyze benchmark data for patterns.

---

## Part 1: Comparison Analysis

### Role

After the blind comparator determines a winner, examine skills and transcripts to extract actionable insights.

### Inputs

- **winner**: "A" or "B"
- **winner_skill_path**: Path to winning skill
- **winner_transcript_path**: Winner's transcript
- **loser_skill_path**: Path to losing skill
- **loser_transcript_path**: Loser's transcript
- **comparison_result_path**: Comparator's output JSON
- **output_path**: Where to save analysis

### Process

1. **Read comparison result** — note winner, reasoning, scores
2. **Read both skills** — identify structural differences in instructions, scripts, examples, edge cases
3. **Read both transcripts** — compare execution patterns, tool usage, divergences
4. **Analyze instruction following** — score 1-10 for each, note specific issues
5. **Identify winner strengths** — clearer instructions? better scripts? more examples?
6. **Identify loser weaknesses** — ambiguous instructions? missing tools? gaps?
7. **Generate improvement suggestions** — prioritized by impact

### Output Format

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path",
    "loser_skill": "path",
    "comparator_reasoning": "Brief summary"
  },
  "winner_strengths": ["..."],
  "loser_weaknesses": ["..."],
  "instruction_following": {
    "winner": { "score": 9, "issues": [] },
    "loser": { "score": 6, "issues": [] }
  },
  "improvement_suggestions": [
    {
      "priority": "high|medium|low",
      "category": "instructions|tools|examples|error_handling|structure|references",
      "suggestion": "Specific change to make",
      "expected_impact": "What this would improve"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "...",
    "loser_execution_pattern": "..."
  }
}
```

### Priority Levels

- **high**: Would likely change the comparison outcome
- **medium**: Would improve quality but may not change win/loss
- **low**: Nice to have, marginal improvement

---

## Part 2: Benchmark Analysis

### Role

Review benchmark run results and surface patterns the aggregate stats might hide.

### Inputs

- **benchmark_data_path**: Path to benchmark.json
- **skill_path**: Path to the skill
- **output_path**: Where to save notes

### Process

1. **Read benchmark data** — configurations, run_summary
2. **Per-assertion patterns**:
   - Always pass in both configs? (may not differentiate value)
   - Always fail in both? (broken or beyond capability)
   - Pass with skill, fail without? (skill adds clear value)
   - Fail with skill, pass without? (skill may be hurting)
   - Highly variable? (flaky or non-deterministic)
3. **Cross-eval patterns** — some evals consistently harder? high variance?
4. **Metrics patterns** — time, tokens, tool calls, outliers
5. **Generate notes** as JSON array of strings

### Output

```json
[
  "Assertion 'X' passes 100% in both configs - may not differentiate skill value",
  "Eval 3 shows high variance (50% +/- 40%) - possibly flaky",
  "Skill adds 13s average but improves pass rate by 50%"
]
```

### Guidelines

**DO:** Report observations grounded in data. Be specific about which evals/assertions/runs.
**DO NOT:** Suggest skill improvements (that's for the improvement step). Speculate without evidence. Repeat run_summary aggregates.
