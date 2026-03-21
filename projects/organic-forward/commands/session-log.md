Review this entire conversation and extract information into the correct Obsidian vault categories. Do NOT create one monolithic document — route each piece to where it belongs.

## Vault Location
`~/Obsidian/OrganicForward/`

## Vault Structure & Routing Rules

| Category | Folder | What goes here | Action |
|----------|--------|----------------|--------|
| journal | journal/ | Process narrative, methodology, lessons learned, session story | Create new file |
| decisions | decisions/ | New decisions made during session | Append to decision-registry.md (continue from last DEC-NNN) |
| playbooks | playbooks/ | Reusable procedures, new operational rules | Create or append |
| build | build/ | System state changes, what was built/modified | Create or append |
| product | product/ | Specs, requirements, feature plans | Create or append |
| research | research/ | Findings, evidence, analysis | Create or append |

## File Naming Convention
Lowercase kebab-case with category prefix:
- `journal/journal-[topic]-[YYYY-MM-DD].md`
- `playbooks/playbook-[topic].md`
- `build/build-[phase-or-topic].md`

## Output Process

1. **Read `_index.md`** first to understand current vault state
2. **Read `decisions/decision-registry.md`** to get the last decision number
3. **Scan the full conversation** for extractable content
4. **For each category that has content**:
   - Create or append to the appropriate file
   - Add YAML frontmatter with aliases if creating new files
   - Use wikilinks to cross-reference other vault files
5. **Update `_index.md`** if new files were created
6. **Report what was written** — list each file and a one-line summary

## Routing Rules
- One piece of information goes in ONE place (no duplication)
- Journal gets the narrative ("what we did and why this session")
- Decisions get numbered entries (DEC-NNN format, sequential)
- Playbooks get reusable procedures ("how to do this again")
- Build gets system state changes ("what changed")
- If something doesn't fit any category, flag it — don't force it
- Add YAML `aliases` with human-readable names on new files
- When appending to existing files, preserve existing content and formatting

## Quality Checks
- [ ] No information lost from the session
- [ ] No duplicate content across files
- [ ] All wikilinks resolve to existing files
- [ ] Decision numbering is sequential with no gaps
- [ ] _index.md updated if new files added
