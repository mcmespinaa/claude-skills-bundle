# Claude Code Skills Bundle

Complete collection of Claude Code skills and commands extracted from the Ces AI workspace (Mac, March 2026).

## Contents

| Category | Count | Description |
|----------|-------|-------------|
| **Global commands** | 4 | Slash commands available in all projects (`~/.claude/commands/`) |
| **Global skills** | 2 | Skills available in all projects (`~/.claude/skills/`) |
| **Project skills** | 49 | Project-specific skills (`.claude/skills/` per project) |
| **Project commands** | 19 | Project-specific commands (`.claude/commands/` per project) |
| **Total files** | 268 | Including SKILL.md, scripts, references, data files |

## Bundle Structure

```
claude-skills-bundle/
├── README.md                 ← You are here
├── MANIFEST.md               ← Full inventory of every skill
├── install.sh                ← Cross-platform installer (macOS/Linux/WSL)
├── global/
│   ├── commands/             ← 4 global slash commands
│   │   ├── context-load.md
│   │   ├── decisions.md
│   │   ├── session-log.md
│   │   └── status.md
│   └── skills/               ← 2 global skills
│       ├── notebooklm/       ← NotebookLM automation (SKILL.md)
│       └── ui-ux-pro-max/    ← UI/UX design intelligence (SKILL.md + scripts + 24 CSV data files)
└── projects/                 ← Project-specific skills
    ├── ai-blog-builder/          ← 2 skills: blog, plan-blog
    ├── ai-newsletter-manager/    ← 2 skills: newsletter, plan-newsletter
    ├── ai-skatteverket/          ← 1 command: seos-context-load
    ├── ai-skooler/               ← 5 skills: blueprint, classroom, community, decision-log, diagnose
    ├── ai-social-media-manager/  ← 16 skills: post, blog, newsletter, research, eval, qa, render, etc.
    ├── ai-socialagent/           ← 3 skills: senior-engineer, seo-aio, socialdesigner
    ├── ces-ai-portfolio/         ← 3 skills + 4 commands
    ├── claude-notebooklm/        ← 15 skills: distribute, blog, newsletter, render, web-build, etc.
    ├── claude-shopwired/         ← 2 skills: sync, plan-sync
    ├── ghl-social-mcp-server/    ← 9 commands: post, research, newsletter, plan-week, etc.
    └── organic-forward/          ← 2 skills + 5 commands: frontend-design, skill-builder, etc.
```

## Quick Install

### Option A: Install everything (global + all projects)
```bash
chmod +x install.sh
./install.sh --all
```

### Option B: Install global only
```bash
./install.sh --global
```

### Option C: Install specific project(s)
```bash
./install.sh --project ai-social-media-manager
./install.sh --project organic-forward --project ai-skooler
```

### Option D: Manual install
```bash
# Global commands → ~/.claude/commands/
cp -R global/commands/*.md ~/.claude/commands/

# Global skills → ~/.claude/skills/
cp -R global/skills/* ~/.claude/skills/

# Project skills → <project-root>/.claude/skills/
cp -R projects/ai-social-media-manager/skills/* /path/to/project/.claude/skills/
```

## How Claude Code Discovers Skills

| Type | Location | Scope |
|------|----------|-------|
| **Global commands** | `~/.claude/commands/*.md` | Available in every project via `/command-name` |
| **Global skills** | `~/.claude/skills/<name>/SKILL.md` | Auto-activated by description matching |
| **Project commands** | `<project>/.claude/commands/*.md` | Available only in that project |
| **Project skills** | `<project>/.claude/skills/<name>/SKILL.md` | Available only in that project |

## Platform Notes

- **macOS/Linux**: Scripts use `bash` and standard Unix tools. Works as-is.
- **Windows (WSL)**: Run inside WSL. The installer detects WSL and adjusts `~/.claude` paths.
- **Windows (native)**: Use `%USERPROFILE%\.claude\` instead of `~/.claude/`. Manual copy recommended.

## Prerequisites for Specific Skills

| Skill | Requires |
|-------|----------|
| `ui-ux-pro-max` | Python 3.x |
| `notebooklm` | `pip install notebooklm-py` + `notebooklm login` |
| `post`, `blog`, `newsletter` (GHL) | GoHighLevel API credentials |
| `sync` (Shopwired) | ShopWired API credentials |
| `distribute` | Google Drive API + GHL credentials |
| `render` | Playwright (`pip install playwright && playwright install`) |

## Updating

Re-run the installer to overwrite with newer versions. The installer does not delete skills that were removed from the bundle.

## Origin

Extracted from Ces AI Mac workspace on 2026-03-21 using automated bundler.
