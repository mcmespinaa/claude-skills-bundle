Surface relevant decisions from the decision registry. Optionally filter by workstream, status, or cost-of-delay.

## Steps

1. **Read the decision registry**
   - Read `~/Obsidian/OrganicForward/decisions/decision-registry.md` in full

2. **Determine filter** from user's message or context:
   - If user specified a workstream (e.g., "marketplace", "community", "security"), filter decisions relevant to that area
   - If user said "blocking" or "critical", show only proposed decisions with critical cost-of-delay
   - If user said "deferred", show only deferred decisions
   - If no filter specified, show a summary of all decisions grouped by status

3. **Output format**:

### If filtered by workstream:
```
## Decisions — [workstream]

| id | title | status | summary |
|----|-------|--------|---------|
| DEC-XXX | ... | ... | ... |

### Implications for Current Work
[how these decisions affect what the user is about to build]
```

### If showing blocking decisions:
```
## Blocking Decisions (proposed + critical)

| id | title | summary | what it blocks |
|----|-------|---------|----------------|
| DEC-XXX | ... | ... | ... |

### Recommendation
[which decisions should be resolved first and why]
```

### If no filter (summary):
```
## Decision Registry Summary

- Total: [N]
- Accepted: [N]
- Proposed: [N] (of which [N] critical)
- Deferred: [N]

### Critical Proposed (need resolution)
- DEC-XXX: [title]
- ...

### Recently Accepted
- DEC-XXX: [title]
- ...

### Deferred (parking lot)
- DEC-XXX: [title]
- ...
```

## Rules
- Always read the actual registry file — do not answer from memory
- When filtering by workstream, use judgment to match decisions to areas (e.g., DEC-013 through DEC-019 are community, DEC-020 through DEC-025 are phase 1a)
- If the user asks "what have we decided about X?", search the registry AND the relevant research/product docs for additional context
- Never contradict a decision marked as accepted — flag it if you think it should be revisited
