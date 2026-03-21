# Claude Code Skills Bundle

Complete collection of Claude Code skills and commands extracted from the Ces AI workspace (March 2026). Includes installers for **macOS/Linux** and **Windows**.

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
├── SETUP-WINDOWS.md          ← Full workspace setup guide for Windows
├── install.sh                ← Installer (macOS/Linux/WSL)
├── install.ps1               ← Installer (Windows PowerShell)
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

### macOS / Linux

```bash
git clone https://github.com/mcmespinaa/claude-skills-bundle.git
cd claude-skills-bundle

# Install global skills + commands only
chmod +x install.sh
./install.sh --global

# Install everything (prompts for each project path)
./install.sh --all

# Install specific project(s)
./install.sh --project ai-social-media-manager
./install.sh --project organic-forward --project ai-skooler

# Preview without copying
./install.sh --dry-run --all
```

### Windows (PowerShell)

```powershell
git clone https://github.com/mcmespinaa/claude-skills-bundle.git
cd claude-skills-bundle

# Install global skills + commands only
.\install.ps1 -Global

# Install everything (prompts for each project path)
.\install.ps1 -All

# Install specific project(s)
.\install.ps1 -Project ai-social-media-manager
.\install.ps1 -Project organic-forward -Project ai-skooler

# Preview without copying
.\install.ps1 -DryRun -All

# Override default paths
.\install.ps1 -Project ai-social-media-manager -TargetDir "C:\Projects\my-project"
.\install.ps1 -Global -ClaudeHome "D:\custom\.claude"
```

### Manual Install

```bash
# macOS/Linux
cp -R global/commands/*.md ~/.claude/commands/
cp -R global/skills/* ~/.claude/skills/
cp -R projects/ai-social-media-manager/skills/* /path/to/project/.claude/skills/
```

```powershell
# Windows
Copy-Item global\commands\*.md "$env:USERPROFILE\.claude\commands\" -Force
Copy-Item global\skills\* "$env:USERPROFILE\.claude\skills\" -Recurse -Force
Copy-Item projects\ai-social-media-manager\skills\* "C:\path\to\project\.claude\skills\" -Recurse -Force
```

## Full Workspace Setup (Windows)

For a complete workspace setup including Claude Code, Obsidian, Supabase, MCP servers, GHL, NotebookLM, YouTube search, and scheduled automation — see **[SETUP-WINDOWS.md](SETUP-WINDOWS.md)**.

This is a 15-phase guide that covers:
1. Claude Code CLI + VS Code extension
2. Obsidian vault creation
3. Three-layer architecture (CLAUDE.md → CONTEXT.md → Playbooks)
4. Claude Code settings + safety hooks
5. Shared Supabase database
6. Real-time vault watcher + backup
7. MCP servers (Obsidian, Stitch, Excalidraw, Playwright)
8. Plugins (GitHub, Frontend Design, Context7, Playwright, GHL)
9. Google Workspace CLI + YouTube search
10. NotebookLM integration
11. GHL social media manager
12. Clief Notes best practices
13. Task Scheduler automation
14. Skills bundle installation + hooks + memory system
15. Verification checklist

## How Claude Code Discovers Skills

| Type | Location (macOS/Linux) | Location (Windows) | Scope |
|------|------------------------|---------------------|-------|
| **Global commands** | `~/.claude/commands/*.md` | `%USERPROFILE%\.claude\commands\*.md` | Available in every project via `/command-name` |
| **Global skills** | `~/.claude/skills/<name>/SKILL.md` | `%USERPROFILE%\.claude\skills\<name>\SKILL.md` | Auto-activated by description matching |
| **Project commands** | `<project>/.claude/commands/*.md` | `<project>\.claude\commands\*.md` | Available only in that project |
| **Project skills** | `<project>/.claude/skills/<name>/SKILL.md` | `<project>\.claude\skills\<name>\SKILL.md` | Available only in that project |

## Prerequisites for Specific Skills

| Skill | Requires |
|-------|----------|
| `ui-ux-pro-max` | Python 3.x |
| `notebooklm` | `pip install notebooklm-py` + `notebooklm login` |
| `post`, `blog`, `newsletter` (GHL) | GoHighLevel API credentials |
| `sync` (Shopwired) | ShopWired API credentials |
| `distribute` | Google Drive API + GHL credentials |
| `render` | Playwright (`pip install playwright && playwright install`) |
| `youtube-search` | YouTube Data API key (falls back to `yt-dlp`) |

## Updating

```bash
# Pull latest and re-run installer
cd claude-skills-bundle
git pull
./install.sh --global          # macOS/Linux
.\install.ps1 -Global          # Windows
```

Re-running the installer overwrites existing files with the latest versions. It does not delete skills that were removed from the bundle.

## Origin

Extracted from Ces AI Mac workspace on 2026-03-21. Maintained at [github.com/mcmespinaa/claude-skills-bundle](https://github.com/mcmespinaa/claude-skills-bundle).
