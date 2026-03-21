You are starting a fresh session. Perform a full context load to orient yourself before any work begins.

## Steps

1. **Read project instructions**
   - Read `/Users/MC/Projects/Ces ai-portfolio/CLAUDE.md`

2. **Read vault index**
   - Read `/Users/MC/Projects/Ces ai-portfolio/Ces Portfolio/_index.md` for full vault overview

3. **Read decision registry**
   - Read `/Users/MC/Projects/Ces ai-portfolio/Ces Portfolio/decisions/decision-registry.md`
   - Note the last decision number and any proposed/deferred decisions

4. **Check current system state**
   - Run `git status` and `git log --oneline -10` in `/Users/MC/Projects/Ces ai-portfolio/`
   - Note current branch, uncommitted changes, recent work

5. **Output a session briefing** in this format:

```
## Session Briefing — [date]

### Current Phase
[phase and status from vault index]

### Recent Activity
[last 3-5 commits, any uncommitted changes]

### Open Decisions
[any proposed/deferred decisions]

### Tech Stack
[from CLAUDE.md]

### Ready For
[what workstreams are available based on current state]
```

6. **Ask the user**: "What are you focusing on today?"

## Rules
- Do NOT start any implementation work — this is orientation only
- Do NOT summarize files you haven't actually read
- If the user specified a workstream in their message, tailor the briefing to that workstream
