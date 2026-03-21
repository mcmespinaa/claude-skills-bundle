Report the current state of the Organic Forward project. Read actual sources — do not answer from memory.

## Steps

1. **Git state**
   - Run `git status` in $HOME/organic-forward/
   - Run `git log --oneline -15` for recent commits
   - Note current branch and any uncommitted/untracked changes

2. **Build progress**
   - Read `~/Obsidian/OrganicForward/_index.md` for phase status
   - Read the latest build doc (highest phase number in `~/Obsidian/OrganicForward/build/`)

3. **Decision state**
   - Read `~/Obsidian/OrganicForward/decisions/decision-registry.md`
   - Count: accepted, proposed, deferred
   - List any proposed decisions that are blocking (cost-of-delay = critical)

4. **Output a status report** in this format:

```
## Status Report — [date]

### Phase
[current phase] — [status]

### Git
- Branch: [branch]
- Last commit: [hash] [message] ([date])
- Uncommitted changes: [yes/no, brief summary]

### Build Progress
| Phase | Status |
|-------|--------|
| Phase 0 | [status] |
| Phase 1A | [status] |
| Phase 1B | [status] |
| Phase 2 | [status] |

### Decisions
- Total: [N] (accepted: [N], proposed: [N], deferred: [N])
- Blocking (proposed + critical):
  - DEC-XXX: [title]
  - ...

### Next Actions
[what logically comes next based on current state]
```

## Rules
- Read actual files — do not guess or use stale information
- Keep the report concise — this is a dashboard, not an essay
- Flag anything that looks inconsistent (e.g., build doc says done but git shows no commits)
