---
type: playbook
date: 2026-03-21
status: active
topics: [claude-code, obsidian, workspace-setup, onboarding, team, windows]
summary: "Step-by-step guide to set up a Claude Code-powered Obsidian workspace on Windows"
---

# Playbook: Claude Code Workspace Setup for Windows

> **Purpose:** Replicate the full Claude Code + Obsidian + Supabase + GHL stack on a Windows machine, connecting to a shared database.
> **Time:** ~2–3 hours for complete setup
> **Prerequisites:** Windows 10/11, Node.js 18+, Python 3.12+, Obsidian installed, Supabase project access

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Phase 1: Install Claude Code + VS Code Extension](#2-phase-1-install-claude-code--vs-code-extension)
3. [Phase 2: Create the Obsidian Vault](#3-phase-2-create-the-obsidian-vault)
4. [Phase 3: Implement the Three-Layer Architecture](#4-phase-3-implement-the-three-layer-architecture)
5. [Phase 4: Configure Claude Code Settings](#5-phase-4-configure-claude-code-settings)
6. [Phase 5: Connect to the Shared Supabase Database](#6-phase-5-connect-to-the-shared-supabase-database)
7. [Phase 6: Set Up Real-Time Vault Watcher + Backup](#7-phase-6-set-up-real-time-vault-watcher--backup)
8. [Phase 7: Enable MCP Servers](#8-phase-7-enable-mcp-servers)
9. [Phase 8: Install Plugins](#9-phase-8-install-plugins)
10. [Phase 9: Set Up GWS CLI + YouTube Search](#10-phase-9-set-up-gws-cli--youtube-search)
11. [Phase 10: NotebookLM Integration](#11-phase-10-notebooklm-integration)
12. [Phase 11: GHL Social Media Manager](#12-phase-11-ghl-social-media-manager)
13. [Phase 12: Clief Notes Structure + Best Practices](#13-phase-12-clief-notes-structure--best-practices)
14. [Phase 13: Task Scheduler Automation](#14-phase-13-task-scheduler-automation)
15. [Phase 14: Hooks, Skills & Memory System](#15-phase-14-hooks-skills--memory-system)
16. [Phase 15: Verification Checklist](#16-phase-15-verification-checklist)
17. [Appendix A: Full Capabilities Reference](#appendix-a-full-capabilities-reference)
18. [Appendix B: Troubleshooting](#appendix-b-troubleshooting)

---

## 1. Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                        COLLEAGUE'S WINDOWS PC                      │
│                                                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐ │
│  │  VS Code +   │◄──►│  Claude Code  │◄──►│  Obsidian Vault(s)  │ │
│  │  Extension   │    │  CLI (Opus)   │    │  (Personal + Shared)│ │
│  └──────────────┘    └──────┬───────┘    └──────────┬───────────┘ │
│                             │                       │              │
│        ┌────────────────────┼───────────────────────┤              │
│        │                    │                       │              │
│  ┌─────▼──────┐  ┌─────────▼────────┐  ┌──────────▼───────────┐ │
│  │ MCP Servers │  │ Plugins          │  │ Task Scheduler Jobs  │ │
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

### 2.1 Install Prerequisites

```powershell
# Install Node.js 18+ from https://nodejs.org (LTS recommended)
# Or via winget:
winget install OpenJS.NodeJS.LTS

# Install Python 3.12+ from https://python.org
# Or via winget:
winget install Python.Python.3.12

# Verify installations
node --version
python --version
```

### 2.2 Install Claude Code CLI

```powershell
# Install via npm (requires Node.js 18+)
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version

# First-time authentication — opens browser for Anthropic login
claude
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

### 3.1 Choose Vault Location

```powershell
# Create the root directory for all vaults
mkdir C:\Users\%USERNAME%\Obsidian
```

### 3.2 Create Vault Structure

Each colleague needs at minimum ONE vault. For a full team setup, create domain-specific vaults:

```powershell
# Example: Create a project vault + AI brain vault
# PowerShell supports creating nested directories:

$vaults = @(
    "C:\Users\$env:USERNAME\Obsidian\ProjectName\product",
    "C:\Users\$env:USERNAME\Obsidian\ProjectName\research",
    "C:\Users\$env:USERNAME\Obsidian\ProjectName\build",
    "C:\Users\$env:USERNAME\Obsidian\ProjectName\competitive",
    "C:\Users\$env:USERNAME\Obsidian\ProjectName\decisions",
    "C:\Users\$env:USERNAME\Obsidian\ProjectName\journal",
    "C:\Users\$env:USERNAME\Obsidian\ProjectName\playbooks",
    "C:\Users\$env:USERNAME\Obsidian\ProjectName\assets",
    "C:\Users\$env:USERNAME\Obsidian\ProjectName\audit-trail",
    "C:\Users\$env:USERNAME\Obsidian\Claude-Brain\00-Inbox",
    "C:\Users\$env:USERNAME\Obsidian\Claude-Brain\01-Projects",
    "C:\Users\$env:USERNAME\Obsidian\Claude-Brain\02-AI-Conversations\claude-code",
    "C:\Users\$env:USERNAME\Obsidian\Claude-Brain\02-AI-Conversations\claude-web",
    "C:\Users\$env:USERNAME\Obsidian\Claude-Brain\03-Skills-and-Tools\skills",
    "C:\Users\$env:USERNAME\Obsidian\Claude-Brain\03-Skills-and-Tools\plugins",
    "C:\Users\$env:USERNAME\Obsidian\Claude-Brain\04-Resources\concepts",
    "C:\Users\$env:USERNAME\Obsidian\Claude-Brain\04-Resources\references",
    "C:\Users\$env:USERNAME\Obsidian\Claude-Brain\04-Resources\snippets",
    "C:\Users\$env:USERNAME\Obsidian\Claude-Brain\05-Templates",
    "C:\Users\$env:USERNAME\Obsidian\Claude-Brain\06-Archive",
    "C:\Users\$env:USERNAME\Obsidian\Claude-Brain\06-Scripts"
)

foreach ($dir in $vaults) {
    New-Item -ItemType Directory -Force -Path $dir
}
```

### 3.3 Open as Obsidian Vault

1. Open Obsidian
2. Click "Open folder as vault"
3. Select `C:\Users\{username}\Obsidian\Claude-Brain` (or your primary vault)
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

Create `C:\Users\{username}\Obsidian\CLAUDE.md` at the root:

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

```powershell
# Location: %USERPROFILE%\.claude\settings.json
# (typically C:\Users\{username}\.claude\settings.json)
```

Create or edit `%USERPROFILE%\.claude\settings.json`:

```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch",
      "Bash(curl *)",
      "Bash(node *)",
      "Bash(npm *)",
      "Bash(npx *)",
      "Bash(git status*)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(dir *)",
      "Bash(mkdir *)",
      "Bash(type *)",
      "Bash(where *)",
      "Bash(python *)",
      "Bash(python3 *)",
      "Bash(pip *)",
      "Bash(pip3 *)",
      "Bash(echo *)",
      "Bash(cat *)",
      "Bash(ls *)",
      "Bash(head *)",
      "Bash(tail *)",
      "Bash(sort *)",
      "Bash(diff *)",
      "Bash(pwd)",
      "Bash(wc *)",
      "Bash(file *)",
      "Bash(tree *)",
      "Bash(find *)"
    ]
  }
}
```

> **Note:** Claude Code on Windows uses Git Bash or WSL as the shell. The `Bash(...)` permission patterns work the same way — they match commands run inside that shell. Commands like `ls`, `cat`, `head`, `tail` work via Git Bash. If you need native PowerShell commands, use `Bash(powershell *)` or `Bash(pwsh *)`.

### 5.2 Project-Specific Settings

For each project directory, create `.claude\settings.json`:

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
      "Bash(rm -rf *)",
      "Bash(del /f /s *)"
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
            "command": "python C:\\Users\\%USERNAME%\\Obsidian\\.secrets\\block-destructive.py"
          }
        ]
      }
    ]
  }
}
```

Example `block-destructive.py` (cross-platform alternative to bash script):

```python
import sys
import json

input_data = json.loads(sys.stdin.read())
command = input_data.get("tool_input", {}).get("command", "")

dangerous_patterns = ["rm -rf", "del /f /s", "drop table", "truncate", "--force",
                      "rmdir /s", "Remove-Item -Recurse -Force"]

for pattern in dangerous_patterns:
    if pattern.lower() in command.lower():
        print(json.dumps({"decision": "block", "reason": f"Destructive command blocked: contains '{pattern}'"}))
        sys.exit(0)

print(json.dumps({"decision": "allow"}))
```

---

## 6. Phase 5: Connect to the Shared Supabase Database

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

```powershell
# Create secrets directory
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Obsidian\.secrets"

# Create the env file
@"
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_BUCKET=vault-files
USER_ID=colleague-name
"@ | Out-File -FilePath "$env:USERPROFILE\Obsidian\.secrets\supabase-backup.env" -Encoding UTF8

# Restrict file permissions (Windows equivalent of chmod 600)
$acl = Get-Acl "$env:USERPROFILE\Obsidian\.secrets\supabase-backup.env"
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $env:USERNAME, "FullControl", "Allow")
$acl.SetAccessRule($rule)
Set-Acl "$env:USERPROFILE\Obsidian\.secrets\supabase-backup.env" $acl
```

### 6.3 Install the Backup Script

Copy the `backup-to-supabase.py` script to the colleague's machine. The script:

- Uses **SHA-256 content hashing** to skip unchanged files (incremental sync)
- **Batch upserts** 20 records per request
- **Retries** up to 3 times per operation
- **Extracts YAML frontmatter** and stores it in the `metadata` JSONB column
- **Excludes:** `.git`, `.obsidian`, `.secrets`, `.trash`, `.claude`, `node_modules`, `__pycache__`, `.DS_Store`, `Thumbs.db`, `desktop.ini`
- **Text extensions:** `.md`, `.txt`, `.json`, `.yaml`, `.yml`, `.csv`, `.tsv`, `.html`, `.css`, `.js`, `.ts`, `.py`, `.sh`, `.toml`, `.xml`, `.svg`, `.excalidraw`, `.mermaid`, `.bib`
- **Max file size:** 10 MB
- **Binary handling:** base64 if < 256 KB, Storage bucket if larger

```powershell
# Install Python dependencies
pip install supabase python-dotenv

# Test with dry-run
python "$env:USERPROFILE\Obsidian\.secrets\backup-to-supabase.py" --dry-run

# Run full initial backup
python "$env:USERPROFILE\Obsidian\.secrets\backup-to-supabase.py" --full
```

---

## 7. Phase 6: Set Up Real-Time Vault Watcher + Backup

### 7.1 Install a File Watcher

Windows doesn't have `fswatch`. Use one of these alternatives:

**Option A: Python watchdog (recommended — cross-platform)**

```powershell
pip install watchdog
```

**Option B: If using WSL, install fswatch inside WSL**

```bash
sudo apt install fswatch
```

### 7.2 Create the Watcher Script (Python watchdog)

Save as `C:\Users\{username}\Obsidian\.secrets\watch-and-backup.py`:

```python
"""
Watch Obsidian vaults for changes and trigger incremental backup.
Debounces: waits 30 seconds after last change before syncing.
"""
import os
import sys
import time
import subprocess
import logging
from datetime import datetime, timezone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OBSIDIAN_ROOT = os.path.dirname(SCRIPT_DIR)
BACKUP_SCRIPT = os.path.join(SCRIPT_DIR, "backup-to-supabase.py")
LOG_FILE = os.path.join(SCRIPT_DIR, "backup.log")
DEBOUNCE_SECONDS = 30

# Directories to exclude
EXCLUDE_DIRS = {".git", ".obsidian", ".secrets", ".trash", ".claude",
                "node_modules", "__pycache__"}

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s UTC] %(message)s",
    datefmt="%Y-%m-%d %H:%M"
)


class DebouncedHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_change = 0
        self.pending = False

    def _should_ignore(self, path):
        parts = path.replace("\\", "/").split("/")
        return any(p in EXCLUDE_DIRS for p in parts)

    def on_any_event(self, event):
        if self._should_ignore(event.src_path):
            return
        self.last_change = time.time()
        self.pending = True


def main():
    # Determine which vault directories to watch
    vaults = []
    for item in os.listdir(OBSIDIAN_ROOT):
        full_path = os.path.join(OBSIDIAN_ROOT, item)
        if os.path.isdir(full_path) and not item.startswith("."):
            vaults.append(full_path)

    if not vaults:
        logging.error("No vault directories found in %s", OBSIDIAN_ROOT)
        sys.exit(1)

    handler = DebouncedHandler()
    observer = Observer()

    for vault in vaults:
        observer.schedule(handler, vault, recursive=True)
        logging.info("Watching: %s", vault)

    observer.start()
    logging.info("Watcher started")

    try:
        while True:
            time.sleep(5)
            if handler.pending:
                elapsed = time.time() - handler.last_change
                if elapsed >= DEBOUNCE_SECONDS:
                    handler.pending = False
                    logging.info("Change detected — syncing...")
                    try:
                        subprocess.run(
                            [sys.executable, BACKUP_SCRIPT],
                            capture_output=True, text=True, timeout=300
                        )
                        logging.info("Sync complete")
                    except subprocess.TimeoutExpired:
                        logging.error("Backup timed out after 300s")
                    except Exception as e:
                        logging.error("Backup failed: %s", e)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
```

### 7.3 Create a Windows Task (Runs on Login, Stays Alive)

Use Task Scheduler to run the watcher on login:

**Option A: PowerShell (automated setup)**

```powershell
# Register the watcher as a scheduled task that starts at logon
$action = New-ScheduledTaskAction `
    -Execute "pythonw" `
    -Argument "$env:USERPROFILE\Obsidian\.secrets\watch-and-backup.py" `
    -WorkingDirectory "$env:USERPROFILE\Obsidian\.secrets"

$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Days 365)

Register-ScheduledTask `
    -TaskName "Obsidian-Vault-Watcher" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Watch Obsidian vaults for changes and sync to Supabase"
```

> **Note:** `pythonw` runs Python without a console window. If `pythonw` is not in your PATH, use the full path (e.g., `C:\Python312\pythonw.exe`).

**Option B: Task Scheduler GUI**

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Task** (not "Create Basic Task")
3. General tab: Name = `Obsidian-Vault-Watcher`, check "Run whether user is logged on or not"
4. Triggers tab: New → "At log on", Specific user = your account
5. Actions tab: New → Program = `pythonw`, Arguments = path to `watch-and-backup.py`
6. Settings tab: Uncheck "Stop the task if it runs longer than"

### 7.4 Create Hourly Backup Scheduled Task

```powershell
$action = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "$env:USERPROFILE\Obsidian\.secrets\backup-to-supabase.py" `
    -WorkingDirectory "$env:USERPROFILE\Obsidian\.secrets"

$trigger = New-ScheduledTaskTrigger `
    -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Hours 1) `
    -RepetitionDuration (New-TimeSpan -Days 365)

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName "Obsidian-Hourly-Backup" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Hourly incremental backup of Obsidian vaults to Supabase"
```

### 7.5 Verify Scheduled Tasks

```powershell
# List your Obsidian tasks
Get-ScheduledTask | Where-Object { $_.TaskName -like "*Obsidian*" } | Format-Table TaskName, State

# Start a task manually to test
Start-ScheduledTask -TaskName "Obsidian-Vault-Watcher"

# Check task history
Get-ScheduledTask -TaskName "Obsidian-Hourly-Backup" | Get-ScheduledTaskInfo
```

---

## 8. Phase 7: Enable MCP Servers

MCP (Model Context Protocol) servers extend Claude's capabilities. Configure in `%USERPROFILE%\.claude\settings.json`:

### 8.1 Obsidian MCP Server

Allows Claude to search, read, and manage vault notes via semantic search.

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "node",
      "args": ["C:\\Users\\{username}\\Obsidian\\{vault}\\.obsidian\\plugins\\mcp-tools\\bin\\mcp-server"],
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
4. Add the server config to `%USERPROFILE%\.claude\settings.json`

> **Note:** Use double backslashes (`\\`) in JSON paths on Windows, or forward slashes (`/`) which also work.

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

## 9. Phase 8: Install Plugins

Plugins extend Claude Code's capabilities beyond the base tools.

### 9.1 Enable in Claude Code

```bash
# Inside a Claude Code session:
/plugins

# Or configure in %USERPROFILE%\.claude\settings.json:
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

## 10. Phase 9: Set Up GWS CLI + YouTube Search

### 10.1 Google Cloud CLI (gcloud)

```powershell
# Install gcloud via the official installer
# Download from: https://cloud.google.com/sdk/docs/install#windows
# Or via winget:
winget install Google.CloudSDK

# Initialize and authenticate (run in a new terminal after install)
gcloud init
gcloud auth login
gcloud auth application-default login

# Enable required APIs
gcloud services enable youtube.googleapis.com
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

## 11. Phase 10: NotebookLM Integration

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

To replicate, create a script and Scheduled Task (see Phase 13).

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

## 12. Phase 11: GHL Social Media Manager

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

## 13. Phase 12: Clief Notes Structure + Best Practices

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

## 14. Phase 13: Task Scheduler Automation

MC's macOS system runs 5 LaunchAgents. Here are the **Windows Task Scheduler equivalents**:

### 14.1 Summary of Scheduled Tasks

| Task Name | Purpose | Schedule |
|-----------|---------|----------|
| `Obsidian-Vault-Watcher` | Real-time vault → Supabase sync | At logon (persistent) |
| `Obsidian-Hourly-Backup` | Hourly incremental backup | Every 3600s |
| `Obsidian-Canvas-Monitor` | Canvas LMS → Obsidian notes | Every 1800s |
| `Obsidian-Intelligence-Brief` | Daily news synthesis | Daily at 9:00 AM |
| `Obsidian-Project-Sync` | Project vault → Supabase | Every 4 hours |

### 14.2 Intelligence Brief Task (Optional)

For daily automated research briefs:

```powershell
$action = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "C:\Users\$env:USERNAME\Obsidian\.secrets\run_intelligence_brief.py" `
    -WorkingDirectory "C:\Users\$env:USERNAME\Obsidian\.secrets"

$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName "Obsidian-Intelligence-Brief" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Daily intelligence brief: web search + NotebookLM + Discord"
```

### 14.3 Managing Scheduled Tasks

```powershell
# List all Obsidian tasks
Get-ScheduledTask | Where-Object { $_.TaskName -like "*Obsidian*" } | Format-Table TaskName, State

# Start a task manually
Start-ScheduledTask -TaskName "Obsidian-Hourly-Backup"

# Stop a running task
Stop-ScheduledTask -TaskName "Obsidian-Vault-Watcher"

# Disable a task (without deleting)
Disable-ScheduledTask -TaskName "Obsidian-Canvas-Monitor"

# Enable a disabled task
Enable-ScheduledTask -TaskName "Obsidian-Canvas-Monitor"

# Remove a task entirely
Unregister-ScheduledTask -TaskName "Obsidian-Canvas-Monitor" -Confirm:$false

# View task run history
Get-ScheduledTask -TaskName "Obsidian-Hourly-Backup" | Get-ScheduledTaskInfo

# View logs (check the script's log output location)
Get-Content "$env:USERPROFILE\Obsidian\.secrets\backup.log" -Tail 20
```

---

## 15. Phase 14: Hooks, Skills & Memory System

### 15.0 Install the Skills Bundle

The skills bundle is included in this repository (you already have it if you cloned).

**Option A: Clone from GitHub and install (PowerShell):**

```powershell
# Clone the bundle
git clone https://github.com/mcmespinaa/claude-skills-bundle.git "$env:USERPROFILE\Downloads\claude-skills-bundle"

# Run the Windows installer
cd "$env:USERPROFILE\Downloads\claude-skills-bundle"
.\install.ps1 -Global                              # Global skills + commands only
.\install.ps1 -All                                 # Everything (prompts for each project path)
.\install.ps1 -Project ai-social-media-manager     # Specific project
.\install.ps1 -DryRun -All                         # Preview without copying
```

**Option B: If you already have the bundle directory:**

```powershell
cd path\to\claude-skills-bundle
.\install.ps1 -Global
```

**What the installer does:**
1. `-Global`: Copies 4 slash commands to `%USERPROFILE%\.claude\commands\` and 2 global skills (`notebooklm`, `ui-ux-pro-max`) to `%USERPROFILE%\.claude\skills\`
2. `-Project <name>`: Copies project-specific skills + commands to `<project-root>\.claude\skills\` and `<project-root>\.claude\commands\`
3. `-All`: Installs global + all 11 project skill sets (prompts for each project's local path)
4. Safe to re-run — overwrites existing files with latest versions

**Post-install — update paths:**

The vault skill files reference macOS paths (`$HOME/...`). Update the `## Location` section in each skill to match your Windows paths:

```powershell
# Bulk find-replace (PowerShell)
$skillsDir = "$env:USERPROFILE\Obsidian\Claude-Brain\03-Skills-and-Tools\skills"
Get-ChildItem "$skillsDir\*.md" | ForEach-Object {
    (Get-Content $_.FullName) -replace '$HOME/', "C:\Users\$env:USERNAME\" |
    Set-Content $_.FullName
}
```

**Post-install — dependencies:**

```powershell
# NotebookLM skill
pip install notebooklm-py
notebooklm login

# Render skill (Playwright for branded image generation)
pip install playwright Pillow
playwright install chromium

# YouTube search fallback
pip install yt-dlp
```

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
            "command": "python C:\\Users\\{username}\\Obsidian\\.secrets\\sync_sessions.py --last 3 2>NUL || echo ok && python C:\\Users\\{username}\\Obsidian\\.secrets\\sync_skills.py 2>NUL || echo ok"
          }
        ]
      }
    ]
  }
}
```

This ensures every Claude Code conversation is automatically saved to the `02-AI-Conversations/` folder.

> **Note:** Windows uses `2>NUL` instead of `2>/dev/null` for stderr suppression. The `|| echo ok` ensures the chain continues if a script fails.

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
| 8 | `/ui-ux-pro-max` | Design intelligence: 67 styles, 96 palettes, 57 font pairings, 25 charts, 13 stacks |
| 9 | `/frontend-design` | Create distinctive, production-grade frontend interfaces with high design quality |
| 10 | `/playground` | Create interactive HTML playgrounds — self-contained single-file explorers |
| 11 | `/notebooklm` | Complete API for Google NotebookLM — notebooks, sources, all artifact types, downloads |
| 12 | `/update-config` | Configure Claude Code settings.json — hooks, permissions, env vars, automated behaviors |

#### B. Vault-Based Skills — Content Creation (11 skills)

| # | Command | File | Description |
|---|---------|------|-------------|
| 1 | `/blog` | `blog.md` | SEO-optimized blog posts published to GoHighLevel Blog API |
| 2 | `/blog` | `blog-claude-ai-social-media-manager.md` | Extended blog skill with cross-posting to social media |
| 3 | `/plan-blog` | `plan-blog.md` | Content strategist mode — plan and batch-publish blog posts |
| 4 | `/newsletter` | `newsletter.md` | Draft and send email newsletters via GHL |
| 5 | `/newsletter` | `newsletter-claude-ai-social-media-manager.md` | Styled HTML newsletters via GHL Conversations API |
| 6 | `/newsletter` | `newsletter-claude-notebooklm.md` | Send NotebookLM content as newsletters |
| 7 | `/plan-newsletter` | `plan-newsletter.md` | Plan newsletter calendars, batch schedule |
| 8 | `/post` | `post.md` | Platform-optimized social media posts via GHL API |
| 9 | `/linkedin` | `linkedin.md` | LinkedIn-specific posts optimized for 2026 algorithm |
| 10 | `/presentation` | `presentation.md` | Professional decks via Canva or python-pptx |
| 11 | `/web-design` | `web-design.md` | Design specs for sales pages, landing pages, funnels |

#### C. Vault-Based Skills — Social Media Management (6 skills)

| # | Command | File | Description |
|---|---------|------|-------------|
| 12 | `/edit-post` | `edit-post.md` | Edit previously scheduled GHL posts |
| 13 | `/delete-post` | `delete-post.md` | Delete a scheduled GHL post |
| 14 | `/plan-week` | `plan-week.md` | Full 7-day content plan with batch scheduling |
| 15 | `/distribute` | `distribute.md` | Distribute NotebookLM content to GHL social media, Drive, YouTube |
| 16 | `/render` | `render.md` | Playwright rendering engine — HTML → production images |
| 17 | `/render` | `render-claude-ai-social-media-manager.md` | Extended render with email previews, thumbnails |

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
| 23 | `/vault-save` | `vault-save.md` | Save Claude Code outputs to Obsidian vault |
| 24 | `/google-docs-export` | `google-docs-export.md` | Upload markdown/docx to Google Drive as Google Docs |

#### F. Vault-Based Skills — Quality Assurance & DevOps (5 skills)

| # | Command | File | Description |
|---|---------|------|-------------|
| 25 | `/skill-checker` | `skill-checker.md` | Validate skills against Anthropic best practices |
| 26 | `/qa` | `qa.md` | Validate skills against Agent Skills 2.0 standard |
| 27 | `/qa-test` | `qa-test.md` | Live functional testing of MCP server |
| 28 | `/resilience` | `resilience.md` | Static analysis resilience auditor for scripts |
| 29 | `/eval` | `eval.md` | Evaluate LLM content quality against brand voice rules |

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
%USERPROFILE%\.claude\projects\{project-path}\memory\
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

## 16. Phase 15: Verification Checklist

Run through this after setup is complete:

### Infrastructure
- [ ] Claude Code CLI installed and authenticated (`claude --version`)
- [ ] VS Code extension installed and functional
- [ ] Obsidian installed with vault(s) created
- [ ] Essential plugins installed (Linter, Git, Dataview, Smart Connections, MCP Tools)

### Three-Layer Architecture
- [ ] Root `CLAUDE.md` exists with routing table
- [ ] Each vault has `CONTEXT.md` with all required sections
- [ ] Naming conventions documented per vault
- [ ] Folder purpose table has Read/Write designations

### Supabase Connection
- [ ] `.secrets\supabase-backup.env` configured with credentials
- [ ] `backup-to-supabase.py` runs successfully (`--dry-run` first)
- [ ] Initial `--full` backup completed
- [ ] Verify data in Supabase dashboard

### Automation
- [ ] Python `watchdog` installed (`pip install watchdog`)
- [ ] Watcher script created and tested
- [ ] `Obsidian-Vault-Watcher` task registered and running
- [ ] `Obsidian-Hourly-Backup` task registered and running
- [ ] Logs generating correctly in `.secrets\`

### MCP Servers
- [ ] Obsidian MCP server configured with API key
- [ ] Test: Claude can search vault notes

### Plugins
- [ ] GitHub plugin enabled
- [ ] Playwright plugin enabled
- [ ] Context7 plugin enabled
- [ ] Frontend Design plugin enabled

### Skills
- [ ] `/context-load` works in Claude Code session
- [ ] `/notebooklm` responds correctly
- [ ] YouTube search functional

### Safety
- [ ] `.env` files excluded from Read/Edit/Write permissions
- [ ] Destructive commands blocked (both Unix and Windows variants)
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
| **Background Jobs** | Scheduled tasks | Windows Task Scheduler |

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

### Scheduled Task Not Running

```powershell
# Check if the task exists and its state
Get-ScheduledTask -TaskName "Obsidian-Vault-Watcher" | Format-List TaskName, State, LastRunTime, LastTaskResult

# If LastTaskResult is non-zero, check the logs
Get-Content "$env:USERPROFILE\Obsidian\.secrets\backup.log" -Tail 50

# Common fix: ensure Python is in PATH
# Check with:
where.exe python
where.exe pythonw

# If not in PATH, use full path in task action:
# C:\Users\{username}\AppData\Local\Programs\Python\Python312\python.exe
```

### watchdog Not Working

```powershell
# Reinstall
pip install --upgrade watchdog

# Test manually
python "$env:USERPROFILE\Obsidian\.secrets\watch-and-backup.py"

# If "pythonw" not found, use full path or install Python with "Add to PATH" checked
```

### Supabase Backup Fails

```powershell
# Test connection
python -c "from supabase import create_client; print('OK')"

# Check env file
Get-Content "$env:USERPROFILE\Obsidian\.secrets\supabase-backup.env"

# Run with verbose output
python "$env:USERPROFILE\Obsidian\.secrets\backup-to-supabase.py" --dry-run 2>&1
```

### MCP Server Connection Issues

```powershell
# Test Obsidian MCP server
node "C:\Users\{username}\Obsidian\{vault}\.obsidian\plugins\mcp-tools\bin\mcp-server"

# Verify API key matches between Obsidian plugin settings and %USERPROFILE%\.claude\settings.json
```

### Claude Code Can't Find Files

```json
// In %USERPROFILE%\.claude\settings.json:
{
  "permissions": {
    "additionalDirectories": [
      "C:\\Users\\{username}\\Obsidian"
    ]
  }
}
```

### Skills Not Loading

```powershell
# Verify skill files exist in Claude-Brain\03-Skills-and-Tools\skills\
dir "$env:USERPROFILE\Obsidian\Claude-Brain\03-Skills-and-Tools\skills\"

# Skills are loaded via CLAUDE.md routing — ensure the root CLAUDE.md
# points to the Skills folder correctly
```

### Path Separator Issues

Windows uses backslashes (`\`) but many tools accept forward slashes (`/`). In JSON config files, always escape backslashes as `\\` or use forward slashes instead:

```json
// Both work in JSON:
"C:\\Users\\me\\Obsidian"
"C:/Users/me/Obsidian"
```

### Git Bash vs PowerShell

Claude Code on Windows typically uses Git Bash as its shell. If you need PowerShell-specific commands:
- Prefix with `powershell -Command "..."` or `pwsh -Command "..."`
- Or configure Claude Code to use PowerShell as the default shell

---

> **Last Updated:** 2026-03-21
> **Author:** Generated from MC's production workspace configuration (adapted for Windows)
> **Source of Truth:** Adapted from macOS playbook — paths use `%USERPROFILE%` (env var) or `C:\Users\{username}\`
