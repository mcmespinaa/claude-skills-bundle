---
type: playbook
date: 2026-03-21
status: active
topics: [claude-code, obsidian, workspace-setup, onboarding, team, linux, ubuntu]
summary: "Step-by-step guide to set up a Claude Code-powered Obsidian workspace on Ubuntu Desktop"
---

# Playbook: Claude Code Workspace Setup — Ubuntu Desktop

> **Purpose:** Replicate the full Claude Code + Obsidian + Supabase + GHL stack on Ubuntu Desktop, connecting to a shared database.
> **Time:** ~2–3 hours for complete setup
> **Prerequisites:** Ubuntu 22.04+ (or latest LTS), Node.js 18+, Python 3.12+, Obsidian installed, Supabase project access

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Phase 1: Install Claude Code + VS Code Extension](#2-phase-1-install-claude-code--vs-code-extension)
3. [Phase 2: Create the Obsidian Vault](#3-phase-2-create-the-obsidian-vault)
4. [Phase 3: Implement the Three-Layer Architecture](#4-phase-3-implement-the-three-layer-architecture)
5. [Phase 4: Configure Claude Code Settings](#5-phase-4-configure-claude-code-settings)
6. [Phase 4B: Install Skills Bundle](#6-phase-4b-install-skills-bundle)
7. [Phase 5: Connect to the Shared Supabase Database](#7-phase-5-connect-to-the-shared-supabase-database)
8. [Phase 6: Set Up Real-Time Vault Watcher + Backup](#8-phase-6-set-up-real-time-vault-watcher--backup)
9. [Phase 7: Enable MCP Servers](#9-phase-7-enable-mcp-servers)
10. [Phase 8: Install Plugins](#10-phase-8-install-plugins)
11. [Phase 9: Set Up GWS CLI + YouTube Search](#11-phase-9-set-up-gws-cli--youtube-search)
12. [Phase 10: NotebookLM Integration](#12-phase-10-notebooklm-integration)
13. [Phase 11: GHL Social Media Manager](#13-phase-11-ghl-social-media-manager)
14. [Phase 12: Clief Notes Structure + Best Practices](#14-phase-12-clief-notes-structure--best-practices)
15. [Phase 13: systemd Automation](#15-phase-13-systemd-automation)
16. [Phase 14: Hooks, Skills & Memory System](#16-phase-14-hooks-skills--memory-system)
17. [Phase 15: Verification Checklist](#17-phase-15-verification-checklist)
18. [Appendix A: Full Capabilities Reference](#appendix-a-full-capabilities-reference)
19. [Appendix B: Troubleshooting](#appendix-b-troubleshooting)

---

## 1. Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                     COLLEAGUE'S UBUNTU DESKTOP                     │
│                                                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐ │
│  │  VS Code +   │◄──►│  Claude Code  │◄──►│  Obsidian Vault(s)  │ │
│  │  Extension   │    │  CLI (Opus)   │    │  (Personal + Shared)│ │
│  └──────────────┘    └──────┬───────┘    └──────────┬───────────┘ │
│                             │                       │              │
│        ┌────────────────────┼───────────────────────┤              │
│        │                    │                       │              │
│  ┌─────▼──────┐  ┌─────────▼────────┐  ┌──────────▼───────────┐ │
│  │ MCP Servers │  │ Plugins          │  │ systemd User Units   │ │
│  │ • Obsidian  │  │ • GitHub         │  │ • Vault Watcher      │ │
│  │ • Stitch    │  │ • Playwright     │  │ • Hourly Backup      │ │
│  │ • Excalidraw│  │ • Context7       │  │ • Canvas Monitor     │ │
│  │ • Playwright│  │ • Frontend Design│  │ • Intelligence Brief │ │
│  │             │  │ • GHL Social     │  │                      │ │
│  └─────────────┘  │ • Playground     │  └──────────┬───────────┘ │
│                    └─────────────────┘              │              │
└────────────────────────────────────────────────────-┼──────────────┘
                                                      │
                              ┌────────────────────────▼──────────────┐
                              │         SHARED SUPABASE               │
                              │  ┌────────────┐  ┌────────────────┐  │
                              │  │ vault_files │  │ Storage Bucket │  │
                              │  │ (all users) │  │ (binaries)     │  │
                              │  └────────────┘  └────────────────┘  │
                              │  ┌────────────┐  ┌────────────────┐  │
                              │  │ Discord Bot │  │ Shared Queries │  │
                              │  │ (retrieval) │  │ (cross-vault)  │  │
                              │  └────────────┘  └────────────────┘  │
                              └───────────────────────────────────────┘
```

**What each colleague gets:**
- Their own Obsidian vault(s) with the Clief Notes three-layer architecture
- Claude Code CLI + VS Code integration with Opus model
- Automated backup to a shared Supabase database (each user's data is namespaced by vault name)
- YouTube search, NotebookLM, GHL social posting, Google Workspace CLI
- Real-time file watching with incremental sync
- Skills, playbooks, and persistent memory across sessions

---

## 2. Phase 1: Install Claude Code + VS Code Extension

### 2.0 Install System Prerequisites

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install essential build tools
sudo apt install -y build-essential curl git jq

# Install Node.js 18+ via NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify Node.js and npm
node --version   # Should be v20.x+
npm --version

# Install Python 3.12+
sudo apt install -y python3 python3-pip python3-venv

# Verify Python
python3 --version
```

### 2.1 Install Claude Code CLI

```bash
# Install via npm (requires Node.js 18+)
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version

# First-time authentication — opens browser for Anthropic login
claude
```

### 2.2 Install VS Code

```bash
# Install VS Code via apt (Microsoft repo)
sudo apt install -y wget gpg
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
rm -f packages.microsoft.gpg
sudo apt update
sudo apt install -y code

# Or install via Snap (simpler)
# sudo snap install code --classic
```

### 2.3 Install VS Code Extension

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Claude Code"
4. Install the official Anthropic extension
5. Restart VS Code

### 2.4 Configure VS Code Integration

The extension integrates Claude Code directly into the VS Code terminal panel. Key features:
- **Claude panel** appears in the sidebar
- **Ctrl+Shift+P → "Claude Code"** opens the command palette
- Files open in the IDE are automatically visible to Claude as context
- Claude can read, edit, and create files directly in the workspace

### 2.5 Set Default Model

```bash
# Inside a Claude Code session, set the model
/model opus

# Or configure in settings for persistence
```

---

## 3. Phase 2: Create the Obsidian Vault

### 3.0 Install Obsidian

```bash
# Option 1: Snap (recommended — auto-updates)
sudo snap install obsidian --classic

# Option 2: AppImage
# Download the latest .AppImage from https://obsidian.md/download
# Then:
# chmod +x Obsidian-*.AppImage
# sudo mv Obsidian-*.AppImage /usr/local/bin/obsidian
```

### 3.1 Choose Vault Location

```bash
# Create the root directory for all vaults
mkdir -p ~/Obsidian
```

### 3.2 Create Vault Structure

Each colleague needs at minimum ONE vault. For a full team setup, create domain-specific vaults:

```bash
# Example: Create a project vault + AI brain vault
mkdir -p ~/Obsidian/{ProjectName}/{product,research,build,competitive,decisions,journal,playbooks,assets,audit-trail}
mkdir -p ~/Obsidian/Claude-Brain/{00-Inbox,01-Projects,02-AI-Conversations,03-Skills-and-Tools,04-Resources,05-Templates,06-Archive,06-Scripts}
mkdir -p ~/Obsidian/Claude-Brain/02-AI-Conversations/{claude-code,claude-web}
mkdir -p ~/Obsidian/Claude-Brain/03-Skills-and-Tools/{skills,plugins}
mkdir -p ~/Obsidian/Claude-Brain/04-Resources/{concepts,references,snippets}
```

### 3.3 Open as Obsidian Vault

1. Open Obsidian
2. Click "Open folder as vault"
3. Select `~/Obsidian/Claude-Brain` (or your primary vault)
4. Repeat for each vault folder

### 3.4 Install Essential Obsidian Plugins

Go to **Settings → Community Plugins → Browse** and install:

| Plugin | Purpose |
|--------|---------|
| **Linter** | Enforce YAML frontmatter formatting |
| **Git** | Automatic version control backup |
| **Dataview** | Query notes as a database |
| **Dataview Serializer** | Serialize Dataview queries to markdown |
| **Smart Connections** | AI-powered related notes + chat |
| **MCP Tools** | Connect Claude Desktop to your vault |

---

## 4. Phase 3: Implement the Three-Layer Architecture

This is the **core methodology from the Clief Notes curriculum**. Every workspace needs three layers:

### Layer 1: The Map (CLAUDE.md)

Create `~/Obsidian/CLAUDE.md` at the root:

```markdown
# Obsidian Workspace — Root Map

This directory contains {N} Obsidian vaults. Each vault is a bounded context —
read its CONTEXT.md before doing any work inside it.

## Folder Tree

{ASCII tree of all vaults}

## Routing Table

| Task | Vault | Entry Point | Notes |
|------|-------|-------------|-------|
| {task description} | {vault name} | {folder/file} | {context} |

## Rules

- Never modify vault contents without explicit instruction.
- Always read the vault's CONTEXT.md before working inside it.
- Naming conventions vary per vault — follow each vault's own rules.
- Cross-vault links use file paths, not wikilinks.
```

### Layer 2: The Rooms (CONTEXT.md per vault)

Every vault folder gets a `CONTEXT.md` with these **required sections**:

```markdown
# {Vault Name} — Workspace Context

{One paragraph: what this vault is and what it's for.}

## Folder Purpose

| Folder | Purpose | Read/Write |
|--------|---------|------------|
| `folder-name/` | What it contains | Read-only or Read-write |

## Naming Conventions

- **{file type}**: `{pattern}` (e.g., `research-{slug}.md`)

## Structure

{ASCII tree, 2 levels deep}

## Workflow

{How folders relate: research/ → product/ → build/ → decisions/}

## Key Files

- `path/to/file.md` — what it is and why it matters
```

### Layer 3: The Tools (Playbooks + Skills)

Only add when you hit **friction you can name**. Don't create preemptively.

```markdown
# playbooks/ folder structure
playbook-{procedure}.md

# Each playbook contains:
## When to Use
## Prerequisites
## Steps (numbered, no ambiguity)
## Expected Output
```

### Design Principles (from Clief Notes)

1. **Less description, more routing** — Agents need to know which file to read, not your life story
2. **Constraints over instructions** — Say what NOT to do
3. **Read/Write designations matter** — Mark folders read-only if they shouldn't change
4. **Naming conventions are mandatory** — Without explicit patterns, agents invent bad names
5. **60/30/10 Rule** — 60% traditional code, 30% routing/rules, 10% actual AI
6. **Constraints = Creativity** — Tight boundaries, loose interior produces best work

---

## 5. Phase 4: Configure Claude Code Settings

### 5.1 Global Settings

```bash
# Location: ~/.claude/settings.json
mkdir -p ~/.claude
```

Create or edit `~/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch",
      "Bash(source *)",
      "Bash(export *)",
      "Bash(curl *)",
      "Bash(jq *)",
      "Bash(ls *)",
      "Bash(grep *)",
      "Bash(which *)",
      "Bash(node *)",
      "Bash(npm *)",
      "Bash(npx *)",
      "Bash(git status*)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(tree *)",
      "Bash(find *)",
      "Bash(mkdir *)",
      "Bash(touch *)",
      "Bash(head *)",
      "Bash(tail *)",
      "Bash(sort *)",
      "Bash(diff *)",
      "Bash(pwd)",
      "Bash(echo *)",
      "Bash(cat *)",
      "Bash(wc *)",
      "Bash(file *)"
    ]
  }
}
```

### 5.2 Project-Specific Settings

For each project directory, create `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch"
    ],
    "deny": [
      "Read(.env*)",
      "Edit(.env*)",
      "Write(.env*)",
      "Bash(rm -rf *)"
    ]
  }
}
```

### 5.3 Safety Hooks (Recommended)

Add pre-tool-use hooks to prevent destructive actions:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/block-destructive.sh"
          }
        ]
      }
    ]
  }
}
```

Example `block-destructive.sh`:
```bash
#!/bin/bash
# Block dangerous commands: rm -rf, drop table, etc.
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
if echo "$COMMAND" | grep -qE '(rm -rf|drop table|truncate|--force)'; then
  echo '{"decision":"block","reason":"Destructive command blocked by safety hook"}'
else
  echo '{"decision":"allow"}'
fi
```

```bash
chmod +x /path/to/block-destructive.sh
```

---

## 6. Phase 4B: Install Skills Bundle

This phase installs all 32 vault-based skills, 4 system commands, and 2 system skills (ui-ux-pro-max + notebooklm) that power the slash commands. **Without this step, the skills folders will be empty and slash commands won't work.**

### 6.1 Get the Bundle

The skills bundle is distributed as a folder containing an installer script and a tar.gz archive:

```
skill-bundle-ubuntu/
├── README.md                      ← Documentation
├── install-skills.sh              ← Installer (run this)
└── claude-skills-bundle.tar.gz    ← 65 files, ~190 KB
```

**Option A — Copy from shared drive / USB:**
```bash
# Copy the skill-bundle-ubuntu/ folder to your machine
cp -r /path/to/shared/skill-bundle-ubuntu ~/
```

**Option B — SCP from the source machine:**
```bash
scp -r mc@source-mac:~/Obsidian/Ces\ OS/playbooks/skill-bundle-ubuntu ~/
```

**Option C — Download from team file share:**
```bash
# If hosted on Google Drive, Supabase Storage, or a Git repo:
# wget or curl the tar.gz + install script
```

### 6.2 Run the Installer

```bash
cd ~/skill-bundle-ubuntu
chmod +x install-skills.sh
./install-skills.sh
```

The installer will:
1. Extract 32 vault-based skills to `~/Obsidian/Claude-Brain/03-Skills-and-Tools/skills/`
2. Extract 4 system commands to `~/.claude/commands/` (enables `/status`, `/context-load`, `/session-log`, `/decisions`)
3. Extract 2 system skills to `~/.claude/skills/` (notebooklm + ui-ux-pro-max with all data files)
4. Patch all macOS-specific paths (`$HOME/`) to your Linux home directory
5. Replace `launchctl` → `systemctl`, `brew install` → `apt install`
6. Create a Skills MOC.md with Dataview queries

**Custom vault location:**
```bash
./install-skills.sh --vault-root ~/MyObsidian --brain-vault My-AI-Brain
```

### 6.3 Verify Installation

```bash
# Check vault skills (should show 32 .md files)
ls ~/Obsidian/Claude-Brain/03-Skills-and-Tools/skills/*.md | wc -l

# Check system commands (should show 4 files)
ls ~/.claude/commands/

# Check system skills
ls ~/.claude/skills/notebooklm/SKILL.md
ls ~/.claude/skills/ui-ux-pro-max/SKILL.md

# Test in a Claude Code session
claude
# Then type: /status
```

### 6.4 What's Included vs. What's Not

**Included (in the bundle):**
- All 32 vault-based skill markdown files (workflow docs, trigger phrases, metadata)
- 4 system command definitions (`/status`, `/context-load`, `/session-log`, `/decisions`)
- NotebookLM skill (SKILL.md — CLI reference + workflows)
- UI/UX Pro Max skill (SKILL.md + 3 Python scripts + 23 CSV data files)

**NOT included (set up separately per later phases):**
- Project-specific shell scripts (GHL API, Supabase backup, Google integrations)
- Brand asset directories (`brands/ces/`, templates, logos)
- API keys and credentials (`.env` files, `locations.json`)
- The actual GHL Social Manager MCP plugin (installed via Claude Code plugins)

The vault-based skills document the **workflows and rules** for each slash command. The scripts they reference are the **execution layer** that gets set up in Phases 5-11 when you configure each integration.

### 6.5 Updating Skills Later

When skills are updated on the source machine, re-run the installer with a fresh bundle:

```bash
# Get updated bundle
scp -r mc@source-mac:~/Obsidian/Ces\ OS/playbooks/skill-bundle-ubuntu ~/

# Re-run (overwrites existing files)
cd ~/skill-bundle-ubuntu
./install-skills.sh
```

---

## 7. Phase 5: Connect to the Shared Supabase Database

### 6.1 Supabase Schema

The shared database uses this schema for all team members:

```sql
CREATE TABLE vault_files (
  id BIGSERIAL PRIMARY KEY,
  vault TEXT NOT NULL,           -- e.g., 'Claude-Brain', 'OrganicForward'
  path TEXT NOT NULL,            -- relative path within vault
  content TEXT,                  -- full text content (for .md, .json, etc.)
  file_size BIGINT,
  mime_type TEXT,
  is_binary BOOLEAN DEFAULT FALSE,
  content_hash TEXT,             -- SHA-256 for change detection
  metadata JSONB,               -- extracted YAML frontmatter
  user_id TEXT,                  -- identifies which colleague owns this
  backed_up_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(vault, path, user_id)
);

-- Storage bucket for binary files (images, PDFs, etc.)
-- Bucket name: vault-files
```

**Key:** Each colleague's data is namespaced by `user_id` so everyone writes to the same table but owns their own rows.

### 6.2 Create Environment File

```bash
mkdir -p ~/Obsidian/.secrets

cat > ~/Obsidian/.secrets/supabase-backup.env << 'EOF'
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_BUCKET=vault-files
USER_ID=colleague-name
EOF

chmod 600 ~/Obsidian/.secrets/supabase-backup.env
```

### 6.3 Install the Backup Script

Copy the `backup-to-supabase.py` script to the colleague's machine. The script:

- Uses **SHA-256 content hashing** to skip unchanged files (incremental sync)
- **Batch upserts** 20 records per request
- **Retries** up to 3 times per operation
- **Extracts YAML frontmatter** and stores it in the `metadata` JSONB column
- **Excludes:** `.git`, `.obsidian`, `.secrets`, `.trash`, `.claude`, `node_modules`, `__pycache__`, `.DS_Store`
- **Text extensions:** `.md`, `.txt`, `.json`, `.yaml`, `.yml`, `.csv`, `.tsv`, `.html`, `.css`, `.js`, `.ts`, `.py`, `.sh`, `.toml`, `.xml`, `.svg`, `.excalidraw`, `.mermaid`, `.bib`
- **Max file size:** 10 MB
- **Binary handling:** base64 if < 256 KB, Storage bucket if larger

```bash
# Install Python dependencies
pip3 install supabase python-dotenv

# Test with dry-run
python3 ~/Obsidian/.secrets/backup-to-supabase.py --dry-run

# Run full initial backup
python3 ~/Obsidian/.secrets/backup-to-supabase.py --full
```

---

## 8. Phase 6: Set Up Real-Time Vault Watcher + Backup

### 7.1 Install inotify-tools

```bash
# inotify-tools is the Linux equivalent of macOS fswatch
sudo apt install -y inotify-tools
```

### 7.2 Create the Watcher Script

Save as `~/Obsidian/.secrets/watch-and-backup.sh`:

```bash
#!/bin/bash
# Watch Obsidian vaults for changes and trigger incremental backup
# Debounces: waits 30 seconds after last change before syncing

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OBSIDIAN_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_SCRIPT="$SCRIPT_DIR/backup-to-supabase.py"
PYTHON="$(which python3)"
LOG="$SCRIPT_DIR/backup.log"
DEBOUNCE=30
LAST_RUN=0

echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Watcher started" >> "$LOG"

# Watch directories — edit these to match your vaults
WATCH_DIRS=(
  "$OBSIDIAN_ROOT/Claude-Brain"
  "$OBSIDIAN_ROOT/YourVault1"
  "$OBSIDIAN_ROOT/YourVault2"
)

inotifywait -m -r \
  --exclude '(\.git|\.obsidian|\.secrets|\.trash|\.claude|node_modules|\.DS_Store)' \
  -e modify,create,delete,move \
  "${WATCH_DIRS[@]}" \
  | while read -r directory event filename; do
    NOW=$(date +%s)
    ELAPSED=$((NOW - LAST_RUN))

    if [ "$ELAPSED" -ge "$DEBOUNCE" ]; then
      LAST_RUN=$NOW
      echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Change detected: ${directory}${filename} ($event) — syncing..." >> "$LOG"
      "$PYTHON" "$BACKUP_SCRIPT" >> "$LOG" 2>&1
      echo "[$(date -u '+%Y-%m-%d %H:%M UTC')] Sync complete" >> "$LOG"
    fi
  done
```

```bash
chmod +x ~/Obsidian/.secrets/watch-and-backup.sh
```

### 7.3 Create systemd User Service (Watcher — Runs on Login, Stays Alive)

Save as `~/.config/systemd/user/obsidian-watcher.service`:

```bash
# Create the directory first
mkdir -p ~/.config/systemd/user
```

```ini
[Unit]
Description=Obsidian Vault Watcher — real-time sync to Supabase
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=%h/Obsidian/.secrets/watch-and-backup.sh
Restart=always
RestartSec=10
StandardOutput=append:%h/Obsidian/.secrets/watcher.log
StandardError=append:%h/Obsidian/.secrets/watcher-error.log
Environment=PATH=/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=default.target
```

### 7.4 Create systemd Timer (Hourly Backup)

Save as `~/.config/systemd/user/obsidian-backup.service`:

```ini
[Unit]
Description=Obsidian Vault Hourly Backup to Supabase

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 %h/Obsidian/.secrets/backup-to-supabase.py
StandardOutput=append:%h/Obsidian/.secrets/backup.log
StandardError=append:%h/Obsidian/.secrets/backup-error.log
Environment=PATH=/usr/local/bin:/usr/bin:/bin
```

Save as `~/.config/systemd/user/obsidian-backup.timer`:

```ini
[Unit]
Description=Run Obsidian backup every hour

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h
Persistent=true

[Install]
WantedBy=timers.target
```

### 7.5 Enable and Start Services

```bash
# Reload systemd user daemon
systemctl --user daemon-reload

# Enable and start the watcher (runs on login, auto-restarts)
systemctl --user enable --now obsidian-watcher.service

# Enable and start the hourly backup timer
systemctl --user enable --now obsidian-backup.timer

# Allow user services to run without active login session (optional but recommended)
sudo loginctl enable-linger "$USER"

# Verify they're running
systemctl --user status obsidian-watcher.service
systemctl --user status obsidian-backup.timer
systemctl --user list-timers
```

---

## 9. Phase 7: Enable MCP Servers

MCP (Model Context Protocol) servers extend Claude's capabilities. Configure in `~/.claude/settings.json`:

### 8.1 Obsidian MCP Server

Allows Claude to search, read, and manage vault notes via semantic search.

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "/path/to/obsidian-vault/.obsidian/plugins/mcp-tools/bin/mcp-server",
      "env": {
        "OBSIDIAN_API_KEY": "generate-a-unique-api-key-here"
      }
    }
  }
}
```

**Setup:**
1. In Obsidian, install the **MCP Tools** community plugin
2. Enable it in Settings → Community Plugins
3. Copy the API key from the plugin settings
4. Add the server config to `~/.claude/settings.json`

### 8.2 Stitch MCP Server (Firebase/Firestore)

```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["@_davideast/stitch-mcp", "proxy"]
    }
  }
}
```

### 8.3 Excalidraw MCP Server (Diagrams)

```json
{
  "mcpServers": {
    "excalidraw": {
      "command": "npx",
      "args": ["excalidraw-mcp"]
    }
  }
}
```

### 8.4 Playwright MCP Server (Browser Automation)

Installed via the Playwright plugin. Enables Claude to:
- Navigate websites
- Click elements, fill forms
- Take screenshots
- Scrape content (used for Skool community scraping)

---

## 10. Phase 8: Install Plugins

Plugins extend Claude Code's capabilities beyond the base tools.

### 9.1 Enable in Claude Code

```bash
# Inside a Claude Code session:
/plugins

# Or configure in ~/.claude/settings.json:
```

```json
{
  "enabledPlugins": {
    "github@claude-plugins-official": true,
    "frontend-design@claude-plugins-official": true,
    "context7@claude-plugins-official": true,
    "playwright@claude-plugins-official": true,
    "playground@claude-plugins-official": true,
    "ghl-social-manager@local-desktop-app-uploads": true
  }
}
```

### Plugin Capabilities

| Plugin | What It Does |
|--------|-------------|
| **GitHub** | PR reviews, issue management, code search across repos |
| **Frontend Design** | Generate production-grade UI components (React, Vue, Svelte, etc.) |
| **Context7** | Fetch up-to-date library docs and code examples |
| **Playwright** | Browser automation — navigate, click, scrape, screenshot |
| **Playground** | Create interactive HTML playgrounds for any topic |
| **GHL Social Manager** | Schedule posts, manage social accounts, send emails |

---

## 11. Phase 9: Set Up GWS CLI + YouTube Search

### 10.1 Google Cloud CLI (gcloud)

```bash
# Install gcloud via apt
sudo apt install -y apt-transport-https ca-certificates gnupg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.asc] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo tee /usr/share/keyrings/cloud.google.asc
sudo apt update && sudo apt install -y google-cloud-cli

# Initialize and authenticate
gcloud init
gcloud auth login
gcloud auth application-default login

# Enable required APIs
gcloud services enable youtube.googleapis.com
gcloud services enable drive.googleapis.com
gcloud services enable calendar-json.googleapis.com
gcloud services enable gmail.googleapis.com
```

### 10.2 YouTube Search via Claude Code

Claude Code has a built-in YouTube search skill. Usage:

```
/youtube-search "organic farming innovations 2026"
```

**Capabilities:**
- Search videos, channels, and playlists
- Filter by: date, duration, region, language, captions, HD quality
- Extract video metadata (title, description, view count, publish date)
- Falls back to `yt-dlp` if YouTube Data API quota is exhausted

**YouTube Transcript Extraction:**

```
/yt-transcript https://youtube.com/watch?v=VIDEO_ID
```

- Extracts full transcripts with timestamps
- Supports multiple languages
- Output formatted for Obsidian notes

### 10.3 YouTube Channel Analysis

Via the GHL Social Manager plugin:

```
# Analyze a channel's content strategy
youtube_channel_analysis(channel_url="https://youtube.com/@channelname")

# Search YouTube programmatically
youtube_search(query="topic", max_results=10)

# Get transcript of any video
youtube_transcript(video_url="https://youtube.com/watch?v=ID")
```

---

## 12. Phase 10: NotebookLM Integration

### 11.1 Overview

NotebookLM provides full programmatic API access for:
- Creating notebooks with sources (URLs, PDFs, text)
- Generating artifacts: **podcasts**, FAQs, briefing documents, study guides, timelines, summaries
- Downloading in multiple formats
- Querying notebook content

### 11.2 Using the Skill

```
/notebooklm
```

Or express intent naturally:
- "Create a podcast about organic farming trends"
- "Make a study guide from these research papers"
- "Generate a FAQ from this documentation"

### 11.3 Artifact Types

| Type | Description | Output Format |
|------|-------------|---------------|
| `podcast` | Two-host audio discussion | MP3/WAV |
| `faq` | Question-answer pairs | Markdown |
| `briefing` | Executive summary | Markdown |
| `study_guide` | Structured learning material | Markdown |
| `timeline` | Chronological event summary | Markdown |
| `summary` | Concise content digest | Markdown |

### 11.4 Automated Intelligence Briefs

MC's system runs a daily intelligence brief at 9:00 AM:

1. Web search for relevant topics via Claude CLI
2. Add sources to a NotebookLM notebook
3. Generate briefing artifact
4. Post to Discord + save to vault

To replicate, create a script and systemd timer (see Phase 13).

### 11.5 Example Workflow

```
User: Create a podcast about the latest EU Digital Product Passport regulations

Claude:
1. Searches web for latest DPP news
2. Creates NotebookLM notebook
3. Adds top 5 sources
4. Generates podcast artifact
5. Returns download link + transcript
```

---

## 13. Phase 11: GHL Social Media Manager

### 12.1 Overview

GoHighLevel (GHL) integration provides:
- Multi-platform social media scheduling (Facebook, Instagram, LinkedIn, TikTok, YouTube, X/Twitter, Google Business)
- Contact search and email campaigns
- Media library management (single files + carousels)
- Caption validation and next-slot scheduling

### 12.2 Setup

1. Install the GHL Social Manager plugin (local plugin upload)
2. Register credentials:

```
register_credentials(
  ghl_api_key="your-ghl-api-key",
  ghl_location_id="your-location-id",
  youtube_api_key="optional",
  gemini_api_key="optional"
)
```

3. Map accounts:

```
get_accounts()  # Lists all connected social accounts with IDs
```

### 12.3 Key Operations

```
# Create a post
create_post(
  account_ids=["acc_123"],
  caption="Your post text",
  media_urls=["https://..."],
  schedule_time="2026-03-22T10:00:00Z"
)

# Upload carousel (validates platform limits automatically)
upload_carousel(files=["slide1.png", "slide2.png", "slide3.png"])

# Send email to contact
send_email(contact_id="...", subject="...", body="<html>...")

# Get next available 24h posting slot
get_next_slot(account_id="acc_123")

# Validate caption before posting
validate_caption(caption="...", platform="instagram")
```

### 12.4 Post Logging

All posts are logged to `ghl_post_log.md` for audit trail.

---

## 14. Phase 12: Clief Notes Structure + Best Practices

### 13.1 The Clief Notes Curriculum Structure

This is the teaching methodology from the Clief Notes community (7,400+ members) that MC's system is built on:

```
Clief Notes/
├── The Foundation/                  ← Core course (19 lessons, 5 modules)
│   ├── Module 1 - Quick Start/     ← Setup + five-part prompting
│   ├── Module 2 - Abstraction/     ← Computing layers, memory, orchestration
│   ├── Module 3 - Folder Arch/     ← Three-layer routing (THIS IS KEY)
│   ├── Module 4 - Claude Code/     ← CLI mastery, project understanding
│   └── Module 5 - Next Steps/      ← Scaling roadmap
├── Implementation Playbooks/        ← Applied courses (8 lessons)
│   ├── Module 1 - Build Tools/     ← Skills, MCP servers, automation
│   └── Module 2 - Advanced/        ← Multi-agent, production systems
├── Building Your Stack/             ← Advanced course (8 lessons)
│   ├── Module 1 - Architecture/    ← System design patterns
│   └── Module 2 - Integration/     ← External services, APIs
├── The Vault/                       ← Premium assets + advanced courses
├── Community Posts/                 ← Member implementations
├── Video Transcripts/               ← Raw lesson transcripts
├── Course Index.md                  ← Master routing file
└── Journal of Learnings.md          ← Cross-course synthesis
```

### 13.2 Five Core Frameworks

**1. Three-Layer Routing (Most Important)**
```
Layer 1: CLAUDE.md (The Map)     → Routes to the right vault
Layer 2: CONTEXT.md (The Room)   → Routes to the right folder
Layer 3: Playbooks (The Tools)   → Solves specific friction
```

**2. Five-Part Prompting Framework**
```
1. Identity   → Who is Claude in this context?
2. Task       → What specific thing should it do?
3. Context    → What background does it need?
4. Constraints → What should it NOT do?
5. Output     → What format should the result be in?
```

**3. 60/30/10 Rule**
```
60% — Traditional code (functions, APIs, data structures)
30% — Routing and rules (CLAUDE.md, CONTEXT.md, naming conventions)
10% — Actual AI (the Claude calls, the "magic")
```

**4. Abstraction Ladder**
```
Layer 1: Raw AI output (basic prompting)
Layer 2: Custom flows (skills, playbooks, automation)
Layer 3: Self-improving systems (hooks, memory, auto-sync)
```

**5. Constraints = Creativity**
```
Tight boundaries + loose interior = best AI output
More constraints → more reliable behavior
"Don't do X" is more useful than "Do Y"
```

### 13.3 Best Practices for Vault Organization

**Naming Conventions (CRITICAL — enforce these strictly):**

| File Type | Pattern | Example |
|-----------|---------|---------|
| Conversations | `YYYY-MM-DD-descriptive-slug.md` | `2026-03-21-workspace-setup.md` |
| Projects | `Project - Name.md` | `Project - SocialAgent.md` |
| Skills | `skill-name.md` (kebab-case) | `skill-youtube-search.md` |
| Playbooks | `playbook-{procedure}.md` | `playbook-vault-backup.md` |
| Resources | `Concept Name.md` (title case) | `Digital Product Passport.md` |
| Decisions | `DEC-NNN` or `{PREFIX}-NNN` | `DEC-001`, `SKL-003` |
| Journal | `YYYY-MM-DD {Title}.md` | `2026-03-21 Workspace Review.md` |

**Metadata Convention (flat YAML only):**

```yaml
---
type: ai-conversation | skill | plugin | script | doc | resource | project | snippet
date: 2026-03-21
status: raw | reviewed | distilled | archived
model: claude-code | claude-web
project: "[[Project Name]]"
topics: [topic1, topic2]
summary: "One-line description"
---
```

**Operational Rules:**
1. Raw captures go to `00-Inbox/` first — always
2. Link every note to its parent project via the `project` field
3. Update MOC (Map of Content) indexes when adding significant content
4. Never delete — archive instead (move to `06-Archive/`)
5. One idea per note — split multi-topic sessions into atomic notes
6. Tag with `#status/raw` on capture, promote to `#status/reviewed` after reading

### 13.4 Anti-Patterns to Avoid

1. **Oversized CONTEXT.md** — Keep under 80 lines. Move details into the files themselves.
2. **No routing table** — Context without navigation is useless
3. **Personality over context** — Don't describe who the agent should be; describe where things are
4. **Missing naming conventions** — "Follow existing patterns" is NOT a convention
5. **Everything is read-write** — Mark read-only content explicitly
6. **Premature Layer 3** — Don't create playbooks until you've used the vault enough to know what's repetitive
7. **Nested YAML** — Always keep frontmatter flat

---

## 15. Phase 13: systemd Automation

macOS uses LaunchAgents; Ubuntu uses **systemd user services**. Here's how to replicate all 5 background daemons.

### 14.1 Summary of Services

| systemd Unit | Purpose | Schedule |
|-------------|---------|----------|
| `obsidian-watcher.service` | Real-time vault → Supabase sync | Always on (Restart=always) |
| `obsidian-backup.timer` | Hourly incremental backup | Every 1h |
| `canvas-monitor.timer` | Canvas LMS → Obsidian notes | Every 30min |
| `intelligence-brief.timer` | Daily news synthesis | Daily at 9:00 AM |
| `vault-sync.timer` | Project vault → Supabase | Every 4h |

### 14.2 Intelligence Brief Timer (Optional)

For daily automated research briefs:

Save as `~/.config/systemd/user/intelligence-brief.service`:

```ini
[Unit]
Description=Daily Intelligence Brief via Claude + NotebookLM

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 %h/path/to/run_intelligence_brief.py
StandardOutput=append:%h/Obsidian/.secrets/intelligence-brief.log
StandardError=append:%h/Obsidian/.secrets/intelligence-brief-error.log
Environment=PATH=/usr/local/bin:/usr/bin:/bin
```

Save as `~/.config/systemd/user/intelligence-brief.timer`:

```ini
[Unit]
Description=Run intelligence brief daily at 9:00 AM

[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### 14.3 Canvas Monitor Timer (Optional)

Save as `~/.config/systemd/user/canvas-monitor.service`:

```ini
[Unit]
Description=Canvas LMS monitor — sync course content to Obsidian

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 %h/path/to/canvas_monitor.py
StandardOutput=append:%h/Obsidian/.secrets/canvas-monitor.log
StandardError=append:%h/Obsidian/.secrets/canvas-monitor-error.log
Environment=PATH=/usr/local/bin:/usr/bin:/bin
```

Save as `~/.config/systemd/user/canvas-monitor.timer`:

```ini
[Unit]
Description=Run Canvas monitor every 30 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=30min
Persistent=true

[Install]
WantedBy=timers.target
```

### 14.4 Vault Sync Timer (Optional)

Save as `~/.config/systemd/user/vault-sync.service`:

```ini
[Unit]
Description=Project vault sync to Supabase (4-hour cycle)

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 %h/Obsidian/.secrets/backup-to-supabase.py --full
StandardOutput=append:%h/Obsidian/.secrets/vault-sync.log
StandardError=append:%h/Obsidian/.secrets/vault-sync-error.log
Environment=PATH=/usr/local/bin:/usr/bin:/bin
```

Save as `~/.config/systemd/user/vault-sync.timer`:

```ini
[Unit]
Description=Run vault sync every 4 hours

[Timer]
OnBootSec=10min
OnUnitActiveSec=4h
Persistent=true

[Install]
WantedBy=timers.target
```

### 14.5 Managing systemd User Services

```bash
# Reload after editing unit files
systemctl --user daemon-reload

# Enable and start a service + timer
systemctl --user enable --now intelligence-brief.timer
systemctl --user enable --now canvas-monitor.timer
systemctl --user enable --now vault-sync.timer

# Check status
systemctl --user status obsidian-watcher.service
systemctl --user list-timers

# View logs (journalctl)
journalctl --user -u obsidian-watcher.service -f
journalctl --user -u obsidian-backup.service --since "1 hour ago"

# Stop a service
systemctl --user stop obsidian-watcher.service

# Disable a timer
systemctl --user disable --now intelligence-brief.timer

# Manually trigger a one-shot service
systemctl --user start obsidian-backup.service

# Allow services to run without active login session
sudo loginctl enable-linger "$USER"
```

---

## 16. Phase 14: Hooks, Skills & Memory System

### 15.1 Stop Hooks (Auto-Sync on Session End)

MC's system auto-syncs conversations and skills when a Claude Code session ends:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/sync_sessions.py --last 3 2>/dev/null || true; python3 /path/to/sync_skills.py 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

This ensures every Claude Code conversation is automatically saved to the `02-AI-Conversations/` folder.

### 15.2 Complete Skills Catalog

MC's system includes **32 vault-based skills** (stored in `Claude-Brain/03-Skills-and-Tools/skills/`) plus **12 system-level skills** (registered in Claude Code itself). Here is every skill available:

#### A. System-Level Skills (Built into Claude Code)

These are registered in the Claude Code harness and available in every session regardless of project:

| # | Command | Purpose |
|---|---------|---------|
| 1 | `/context-load` | Full orientation scan at session start — reads vault structure, active projects, recent changes |
| 2 | `/session-log` | Extract information from the current conversation into the correct Obsidian vault categories |
| 3 | `/status` | Report the current state of the Organic Forward project from actual sources |
| 4 | `/decisions` | Surface relevant decisions from the decision registry, filterable by workstream/status |
| 5 | `/simplify` | Review changed code for reuse, quality, and efficiency, then fix any issues found |
| 6 | `/loop` | Run a prompt or slash command on a recurring interval (e.g., `/loop 5m /foo`, defaults to 10m) |
| 7 | `/claude-api` | Build apps with the Claude API or Anthropic SDK — triggers when code imports `anthropic` or `@anthropic-ai/sdk` |
| 8 | `/ui-ux-pro-max` | Design intelligence: 67 styles, 96 palettes, 57 font pairings, 25 charts, 13 stacks (React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui) |
| 9 | `/frontend-design` | Create distinctive, production-grade frontend interfaces with high design quality |
| 10 | `/playground` | Create interactive HTML playgrounds — self-contained single-file explorers with controls, live preview, and prompt copy |
| 11 | `/notebooklm` | Complete API for Google NotebookLM — notebooks, sources, all artifact types, downloads. Activates on `/notebooklm` or "create a podcast about X" |
| 12 | `/update-config` | Configure Claude Code settings.json — hooks, permissions, env vars, automated behaviors |

#### B. Vault-Based Skills — Content Creation (11 skills)

| # | Command | File | Description |
|---|---------|------|-------------|
| 1 | `/blog` | `blog.md` | SEO-optimized blog posts published to GoHighLevel Blog API |
| 2 | `/blog` | `blog-claude-ai-social-media-manager.md` | Extended blog skill with cross-posting to social media |
| 3 | `/plan-blog` | `plan-blog.md` | Content strategist mode — plan a series of blog posts, batch-publish |
| 4 | `/newsletter` | `newsletter.md` | Draft and send email newsletters via GHL |
| 5 | `/newsletter` | `newsletter-claude-ai-social-media-manager.md` | Styled HTML newsletters via GHL Conversations API |
| 6 | `/newsletter` | `newsletter-claude-notebooklm.md` | Send NotebookLM-generated content as styled HTML newsletters |
| 7 | `/plan-newsletter` | `plan-newsletter.md` | Plan newsletter calendars, batch schedule |
| 8 | `/post` | `post.md` | Platform-optimized social media posts via GHL API |
| 9 | `/linkedin` | `linkedin.md` | LinkedIn-specific posts optimized for 2026 algorithm |
| 10 | `/presentation` | `presentation.md` | Professional decks via Canva or python-pptx |
| 11 | `/web-design` | `web-design.md` | Design specs using PAS, AIDA, StoryBrand, Hook-Story-Offer frameworks |

#### C. Vault-Based Skills — Social Media Management (6 skills)

| # | Command | File | Description |
|---|---------|------|-------------|
| 12 | `/edit-post` | `edit-post.md` | Edit previously scheduled GHL posts |
| 13 | `/delete-post` | `delete-post.md` | Delete a scheduled GHL post (irreversible) |
| 14 | `/plan-week` | `plan-week.md` | Full 7-day content plan with per-platform captions |
| 15 | `/distribute` | `distribute.md` | Distribute NotebookLM content to GHL social media, Google Drive, YouTube |
| 16 | `/render` | `render.md` | Playwright rendering engine — HTML templates → production images |
| 17 | `/render` | `render-claude-ai-social-media-manager.md` | Extended render with email previews, YouTube thumbnails |

#### D. Vault-Based Skills — Research & YouTube (5 skills)

| # | Command | File | Description |
|---|---------|------|-------------|
| 18 | `/youtube-search` | `youtube-search.md` | Search YouTube for videos, channels, playlists |
| 19 | `/yt-search` | `yt-search.md` | Full YouTube pipeline: search → transcripts → analyze → repurpose |
| 20 | `/research` | `research.md` | Deep research via NotebookLM |
| 21 | `/notebooklm` | `notebooklm.md` | Complete NotebookLM API |
| 22 | `/save-to-drive` | `save-to-drive.md` | Upload files to Google Drive |

#### E. Vault-Based Skills — Vault & Session Management (2 skills)

| # | Command | File | Description |
|---|---------|------|-------------|
| 23 | `/vault-save` | `vault-save.md` | Save outputs to Obsidian vault with proper frontmatter |
| 24 | `/google-docs-export` | `google-docs-export.md` | Upload to Google Drive as native Google Docs |

#### F. Vault-Based Skills — Quality Assurance & DevOps (5 skills)

| # | Command | File | Description |
|---|---------|------|-------------|
| 25 | `/skill-checker` | `skill-checker.md` | Validate skills against Anthropic best practices |
| 26 | `/qa` | `qa.md` | Validate skills against Agent Skills 2.0 standard |
| 27 | `/qa-test` | `qa-test.md` | Live functional testing of MCP server |
| 28 | `/resilience` | `resilience.md` | Static analysis resilience auditor for bash/Python scripts |
| 29 | `/eval` | `eval.md` | Evaluate LLM-generated content quality |

#### G. Vault-Based Skills — Integration & Sync (3 skills)

| # | Command | File | Description |
|---|---------|------|-------------|
| 30 | `/sync` | `sync.md` | Sync products/customers between ShopWired and GHL |
| 31 | `/plan-sync` | `plan-sync.md` | Configure ShopWired ↔ GHL integration |
| 32 | Web Build | `Web Build - Product Documentation.md` | Product documentation generation |

#### H. Skills Map of Content (Dataview-Powered)

The `Skills MOC.md` file uses Dataview queries to dynamically index all skills:

```dataview
TABLE skill_name AS "Command", summary AS "Description", project AS "Project"
FROM "03-Skills-and-Tools/skills"
WHERE type = "claude-skill"
SORT project ASC, skill_name ASC
```

#### I. Skill Metadata Standard

Every vault-based skill follows this YAML frontmatter schema:

```yaml
---
type: claude-skill
date: YYYY-MM-DD
skill_name: "/command-name"
project: "[[Parent Project]]"
topics:
  - "topic1"
  - "topic2"
status: raw | reviewed | distilled | archived
summary: "What the skill does and when to use it"
---
```

#### J. How Skills Are Triggered

Skills activate through multiple trigger patterns:
1. **Explicit slash command**: `/post`, `/blog`, `/newsletter`
2. **Natural language intent**: "write a blog about...", "create a podcast about..."
3. **Called by other skills**: `/render` is called by `/post`, `/blog`, `/newsletter` for visual generation
4. **Skill chains**: `/research` → `/notebooklm` → `/distribute` → `/newsletter`

#### K. Adding New Skills

To create a new skill for a colleague:

1. Create `skill-name.md` in `Claude-Brain/03-Skills-and-Tools/skills/`
2. Include full YAML frontmatter (type, date, skill_name, project, topics, status, summary)
3. Structure the skill body with: Identity → Task → Context → Constraints → Output Format
4. Run `/skill-checker` to validate against best practices
5. Run `/qa` to verify compliance with the Agent Skills 2.0 standard
6. The Skills MOC.md Dataview query will automatically index it

### 15.3 Persistent Memory System

Claude Code maintains auto-memory across sessions:

```
~/.claude/projects/{project-path}/memory/
├── MEMORY.md          ← Index file (always loaded into context)
├── user_*.md          ← Who the user is, preferences
├── feedback_*.md      ← Corrections and validated approaches
├── project_*.md       ← Active work, goals, deadlines
└── reference_*.md     ← Pointers to external systems
```

**Memory Types:**
- **user** — Role, goals, knowledge level, preferences
- **feedback** — What to avoid or repeat (corrections + validations)
- **project** — Active work, initiatives, deadlines
- **reference** — Pointers to external systems (Linear, Slack, Grafana)

Memory is automatically loaded at session start and persists across conversations.

---

## 17. Phase 15: Verification Checklist

Run through this after setup is complete:

### Infrastructure
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.12+ installed (`python3 --version`)
- [ ] Claude Code CLI installed and authenticated (`claude --version`)
- [ ] VS Code installed with Claude Code extension
- [ ] Obsidian installed with vault(s) created
- [ ] Essential plugins installed (Linter, Git, Dataview, Smart Connections, MCP Tools)

### Three-Layer Architecture
- [ ] Root `CLAUDE.md` exists with routing table
- [ ] Each vault has `CONTEXT.md` with all required sections
- [ ] Naming conventions documented per vault
- [ ] Folder purpose table has Read/Write designations

### Supabase Connection
- [ ] `.secrets/supabase-backup.env` configured with credentials
- [ ] `backup-to-supabase.py` runs successfully (`--dry-run` first)
- [ ] Initial `--full` backup completed
- [ ] Verify data in Supabase dashboard

### Automation
- [ ] `inotify-tools` installed (`which inotifywait`)
- [ ] Watcher script created and executable
- [ ] Watcher systemd service enabled and running (`systemctl --user status obsidian-watcher`)
- [ ] Backup timer enabled and running (`systemctl --user list-timers`)
- [ ] Linger enabled (`loginctl show-user "$USER" | grep Linger`)
- [ ] Logs generating correctly in `.secrets/`

### MCP Servers
- [ ] Obsidian MCP server configured with API key
- [ ] Test: Claude can search vault notes

### Plugins
- [ ] GitHub plugin enabled
- [ ] Playwright plugin enabled
- [ ] Context7 plugin enabled
- [ ] Frontend Design plugin enabled

### Skills Bundle
- [ ] Skills installer ran successfully (`install-skills.sh`)
- [ ] 32 vault skill files in `~/Obsidian/Claude-Brain/03-Skills-and-Tools/skills/`
- [ ] 4 command files in `~/.claude/commands/`
- [ ] `~/.claude/skills/notebooklm/SKILL.md` exists
- [ ] `~/.claude/skills/ui-ux-pro-max/SKILL.md` exists with data/ and scripts/
- [ ] Skills MOC.md created in `03-Skills-and-Tools/`
- [ ] macOS paths patched to Linux (`grep -r "/Users/" ~/.claude/commands/` returns nothing)

### Skills (Functional Test)
- [ ] `/status` works in Claude Code session
- [ ] `/context-load` works in Claude Code session
- [ ] `/decisions` works in Claude Code session
- [ ] `/notebooklm` responds correctly
- [ ] YouTube search functional

### Safety
- [ ] `.env` files excluded from Read/Edit/Write permissions
- [ ] Destructive bash commands blocked
- [ ] Pre-tool-use hooks installed (if applicable)

---

## Appendix A: Full Capabilities Reference

### Everything Claude Code Can Do in This Stack

| Category | Capability | How |
|----------|-----------|-----|
| **File Management** | Read/write/edit any file | Built-in tools |
| **Code Generation** | Write code in any language | Built-in |
| **Web Search** | Search the internet | WebSearch tool |
| **Web Fetch** | Fetch any URL content | WebFetch tool |
| **Git** | Status, diff, log, commit, PR | Bash + GitHub plugin |
| **Browser Automation** | Navigate, click, scrape, screenshot | Playwright MCP |
| **Vault Search** | Semantic search across notes | Obsidian MCP |
| **Library Docs** | Up-to-date documentation lookup | Context7 plugin |
| **YouTube** | Search, transcripts, channel analysis | GHL plugin + skills |
| **NotebookLM** | Notebooks, sources, podcasts, FAQs | NotebookLM skill |
| **Social Media** | Schedule posts, carousels, emails | GHL plugin |
| **Diagrams** | Excalidraw diagrams | Excalidraw MCP |
| **UI Design** | Production-grade components | Frontend Design plugin |
| **Playgrounds** | Interactive HTML tools | Playground plugin |
| **Calendar** | View/create/manage events | Google Calendar MCP |
| **Figma** | Read designs, generate code | Figma MCP |
| **Notion** | Search, create, update pages | Notion MCP |
| **Canva** | Design creation and management | Canva MCP |
| **Supabase** | SQL, migrations, edge functions | Supabase MCP |
| **Memory** | Persistent context across sessions | Auto-memory system |
| **Hooks** | Pre/post tool automation | Settings hooks |
| **Background Jobs** | systemd user services + timers | Linux systemd |

### Cloud MCP Servers Available (via claude.ai)

These are available through the Claude desktop app and can be connected:
- **Supermetrics** — Marketing data from 50+ sources (Google Ads, Facebook Ads, etc.)
- **Figma** — Design-to-code workflow
- **Notion** — Knowledge base management
- **Google Calendar** — Scheduling
- **Canva** — Design management
- **Supabase** — Database operations
- **Clay** — CRM data enrichment
- **Indeed** — Job search data

---

## Appendix B: Troubleshooting

### systemd Service Not Running

```bash
# Check if the service is active
systemctl --user status obsidian-watcher.service

# Check for errors
journalctl --user -u obsidian-watcher.service --no-pager -n 50

# Common fix: reload daemon after editing unit files
systemctl --user daemon-reload

# Restart the service
systemctl --user restart obsidian-watcher.service

# If services stop when you log out:
sudo loginctl enable-linger "$USER"
```

### inotifywait Not Found

```bash
sudo apt install -y inotify-tools

# If watching many files, increase the inotify limit:
echo "fs.inotify.max_user_watches=524288" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Supabase Backup Fails

```bash
# Test connection
python3 -c "from supabase import create_client; print('OK')"

# Check env file
cat ~/Obsidian/.secrets/supabase-backup.env

# Run with verbose output
python3 ~/Obsidian/.secrets/backup-to-supabase.py --dry-run 2>&1
```

### MCP Server Connection Issues

```bash
# Test Obsidian MCP server
node /path/to/.obsidian/plugins/mcp-tools/bin/mcp-server

# Verify API key matches between Obsidian plugin settings and ~/.claude/settings.json
```

### Claude Code Can't Find Files

```bash
# Ensure the vault directory is in additionalDirectories
# In ~/.claude/settings.json:
{
  "permissions": {
    "additionalDirectories": [
      "/home/{username}/Obsidian"
    ]
  }
}
```

### Skills Not Loading

```bash
# Verify skill files exist in Claude-Brain/03-Skills-and-Tools/skills/
ls ~/Obsidian/Claude-Brain/03-Skills-and-Tools/skills/

# Skills are loaded via CLAUDE.md routing — ensure the root CLAUDE.md
# points to the Skills folder correctly
```

### Obsidian AppImage Won't Launch

```bash
# Ensure FUSE is installed (required for AppImage)
sudo apt install -y libfuse2

# Or use the Snap version instead
sudo snap install obsidian --classic
```

### Node.js Permission Errors with npm -g

```bash
# Fix npm global install permissions (avoids needing sudo)
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Then reinstall Claude Code
npm install -g @anthropic-ai/claude-code
```

---

> **Last Updated:** 2026-03-21
> **Author:** Adapted from MC's macOS production workspace for Ubuntu Desktop
> **Source of Truth:** `/home/{username}/Obsidian/` + `~/.claude/` + `~/.config/systemd/user/`
