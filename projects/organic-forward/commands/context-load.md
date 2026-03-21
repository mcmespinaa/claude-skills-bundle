You are starting a fresh session. Perform a full context load to orient yourself before any work begins.

## Steps

1. **Read project instructions**
   - Read `$HOME/organic-forward/CLAUDE.md`
   - Read the sub-project CLAUDE.md for whichever directory the user wants to work in (if specified)

2. **Read vault index**
   - Read `~/Obsidian/OrganicForward/_index.md` for full vault overview

3. **Read decision registry**
   - Read `~/Obsidian/OrganicForward/decisions/decision-registry.md`
   - Note the last decision number and any proposed/deferred decisions

4. **Read agent operations playbook**
   - Read `~/Obsidian/OrganicForward/playbooks/playbook-agent-operations.md`
   - Internalize the do's/don'ts for this session

5. **Check current system state**
   - Run `git status` and `git log --oneline -10` in $HOME/organic-forward/
   - Note current branch, uncommitted changes, recent work

6. **Output a session briefing** in this format:

```
## Session Briefing — [date]

### Current Phase
[phase and status from vault index]

### Recent Activity
[last 3-5 commits, any uncommitted changes]

### Open Decisions
[any proposed/deferred decisions relevant to likely work]

### Key Constraints
- Tech stack: [from vault index]
- Agent rules: [top 3 most relevant from playbook]

### Ready For
[what workstreams are available based on current state]
```

7. **Ask the user**: "What workstream are you focusing on today?"

## Rules
- Do NOT start any implementation work — this is orientation only
- Do NOT summarize files you haven't actually read
- If the user specified a workstream in their message, tailor the briefing to that workstream and read relevant files from the vault
