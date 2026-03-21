Surface relevant decisions from the decision registry. Optionally filter by status or topic.

## Steps

1. Read `/Users/MC/Projects/Ces ai-portfolio/Ces Portfolio/decisions/decision-registry.md`

2. Parse the user's request:
   - If they asked about a specific topic → filter decisions by keyword
   - If they asked about a status → filter by status (active, proposed, deferred, rejected)
   - If no filter → show all decisions

3. Output matching decisions in a readable format:

```
## Decisions — [filter or "all"]

| ID | Status | Title | Date |
|----|--------|-------|------|
| DEC-NNN | [status] | [title] | [date] |

### Details
[For each matching decision, show the rationale]
```

4. If the user wants to **add** a decision:
   - Assign the next DEC number
   - Append to the registry table
   - Confirm what was added

## Rules
- Read the actual file — do not guess from memory
- Keep the output scannable
- If no decisions exist yet, say so and offer to create the first one
