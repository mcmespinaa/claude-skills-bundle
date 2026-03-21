# Claude Code Skills Bundle Installer — Windows (PowerShell)
# Usage:
#   .\install.ps1 -All                              Install everything
#   .\install.ps1 -Global                            Install global commands + skills only
#   .\install.ps1 -Project ai-social-media-manager   Install specific project
#   .\install.ps1 -List                              List available projects
#   .\install.ps1 -DryRun -All                       Preview without copying

param(
    [switch]$All,
    [switch]$Global,
    [string[]]$Project,
    [string]$TargetDir,
    [string]$ClaudeHome,
    [switch]$List,
    [switch]$DryRun,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

$BundleDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ClaudeHome) { $ClaudeHome = Join-Path $env:USERPROFILE ".claude" }

# --- Colors ---
function Log($msg)  { Write-Host "[OK]  $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "[!!]  $msg" -ForegroundColor Yellow }
function Info($msg) { Write-Host "[..]  $msg" -ForegroundColor Cyan }
function Err($msg)  { Write-Host "[ERR] $msg" -ForegroundColor Red }

function Show-Usage {
    @"
Claude Code Skills Bundle Installer (Windows)

Usage:
  .\install.ps1 -All                                Install global + all projects
  .\install.ps1 -Global                             Install global commands + skills only
  .\install.ps1 -Project <name> [-Project <n2>]     Install specific project(s)
  .\install.ps1 -List                               List available projects
  .\install.ps1 -DryRun <any of above>              Preview without copying

Options:
  -TargetDir <path>     Override project root for -Project installs
  -ClaudeHome <path>    Override ~/.claude location (default: %USERPROFILE%\.claude)
  -Help                 Show this help

Examples:
  .\install.ps1 -Global
  .\install.ps1 -Project ai-social-media-manager -TargetDir C:\Projects\my-project
  .\install.ps1 -DryRun -All
"@
    exit 0
}

function Copy-SkillDir {
    param([string]$Src, [string]$Dst)
    if ($DryRun) {
        Info "[dry-run] Would copy: $Src -> $Dst"
        return
    }
    if (-not (Test-Path $Dst)) {
        New-Item -ItemType Directory -Force -Path $Dst | Out-Null
    }
    Copy-Item -Path "$Src\*" -Destination $Dst -Recurse -Force
}

function Copy-SkillFile {
    param([string]$Src, [string]$Dst)
    if ($DryRun) {
        Info "[dry-run] Would copy: $Src -> $Dst"
        return
    }
    $parent = Split-Path -Parent $Dst
    if (-not (Test-Path $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    Copy-Item -Path $Src -Destination $Dst -Force
}

function Install-Global {
    # Commands
    $commandsDir = Join-Path $BundleDir "global\commands"
    if (Test-Path $commandsDir) {
        Info "Installing global commands -> $ClaudeHome\commands\"
        Get-ChildItem -Path $commandsDir -Filter "*.md" | ForEach-Object {
            $dst = Join-Path $ClaudeHome "commands\$($_.Name)"
            Copy-SkillFile -Src $_.FullName -Dst $dst
            Log "  $($_.Name)"
        }
    }

    # Skills
    $skillsDir = Join-Path $BundleDir "global\skills"
    if (Test-Path $skillsDir) {
        Info "Installing global skills -> $ClaudeHome\skills\"
        Get-ChildItem -Path $skillsDir -Directory | ForEach-Object {
            $dst = Join-Path $ClaudeHome "skills\$($_.Name)"
            Copy-SkillDir -Src $_.FullName -Dst $dst
            $count = (Get-ChildItem -Path $_.FullName -Recurse -File).Count
            Log "  $($_.Name)/ ($count files)"
        }
    }
}

function Install-SingleProject {
    param([string]$ProjectName)

    $projectSrc = Join-Path $BundleDir "projects\$ProjectName"
    if (-not (Test-Path $projectSrc)) {
        Err "Project '$ProjectName' not found in bundle"
        $available = (Get-ChildItem -Path (Join-Path $BundleDir "projects") -Directory).Name -join ", "
        Err "Available: $available"
        return
    }

    # Determine target directory
    $target = $TargetDir
    if (-not $target) {
        Write-Host ""
        Write-Host "Project: $ProjectName"
        $target = Read-Host "Where is this project on disk? (the root directory with .claude\)"
    }

    if (-not (Test-Path $target) -and -not $DryRun) {
        Warn "Directory $target does not exist"
        $confirm = Read-Host "Create it? [y/N]"
        if ($confirm -match "^[Yy]") {
            New-Item -ItemType Directory -Force -Path $target | Out-Null
        } else {
            Err "Skipping $ProjectName"
            return
        }
    }

    Info "Installing $ProjectName -> $target\.claude\"

    # Install skills
    $skillsSrc = Join-Path $projectSrc "skills"
    if (Test-Path $skillsSrc) {
        Get-ChildItem -Path $skillsSrc -Directory | ForEach-Object {
            $dst = Join-Path $target ".claude\skills\$($_.Name)"
            Copy-SkillDir -Src $_.FullName -Dst $dst
            $count = (Get-ChildItem -Path $_.FullName -Recurse -File).Count
            Log "  skill: $($_.Name)/ ($count files)"
        }
    }

    # Install commands
    $commandsSrc = Join-Path $projectSrc "commands"
    if (Test-Path $commandsSrc) {
        Get-ChildItem -Path $commandsSrc -Filter "*.md" | ForEach-Object {
            $dst = Join-Path $target ".claude\commands\$($_.Name)"
            Copy-SkillFile -Src $_.FullName -Dst $dst
            Log "  command: $($_.Name)"
        }
    }
}

function Show-Projects {
    Write-Host "Available projects in bundle:" -ForegroundColor Cyan
    Write-Host ""
    $projectsDir = Join-Path $BundleDir "projects"
    Get-ChildItem -Path $projectsDir -Directory | ForEach-Object {
        $skills = 0; $commands = 0
        $sDir = Join-Path $_.FullName "skills"
        $cDir = Join-Path $_.FullName "commands"
        if (Test-Path $sDir) { $skills = (Get-ChildItem -Path $sDir -Directory).Count }
        if (Test-Path $cDir) { $commands = (Get-ChildItem -Path $cDir -Filter "*.md").Count }
        $name = $_.Name.PadRight(35)
        Write-Host "  $name $skills skills, $commands commands"
    }
}

# --- Main ---

if ($Help) { Show-Usage }
if ($List) { Show-Projects; exit 0 }

$installGlobal = $Global -or $All
$hasProjects = $Project.Count -gt 0

if (-not $installGlobal -and -not $hasProjects) {
    Err "No install target specified. Use -All, -Global, or -Project <name>"
    Write-Host ""
    Show-Usage
}

# Header
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Claude Code Skills Bundle Installer"    -ForegroundColor Cyan
Write-Host "  (Windows)"                              -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Bundle:      $BundleDir"
Write-Host "  Claude home: $ClaudeHome"
if ($DryRun) { Write-Host "  Mode:        DRY RUN (no files will be copied)" -ForegroundColor Yellow }
Write-Host ""

# Install global
if ($installGlobal) {
    Install-Global
    Write-Host ""
}

# Install projects
if ($All) {
    Warn "Installing ALL projects requires specifying each project's target directory."
    Warn "Use -TargetDir to set a single target, or you'll be prompted for each."
    Write-Host ""
    $projectsDir = Join-Path $BundleDir "projects"
    Get-ChildItem -Path $projectsDir -Directory | ForEach-Object {
        Install-SingleProject -ProjectName $_.Name
    }
} elseif ($hasProjects) {
    foreach ($p in $Project) {
        Install-SingleProject -ProjectName $p
    }
}

# Done
Write-Host ""
if ($DryRun) {
    Info "Dry run complete. No files were modified."
} else {
    Log "Installation complete!"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Restart Claude Code to pick up new skills"
    Write-Host "  2. Check README.md for prerequisites (NotebookLM, Playwright, etc.)"
    Write-Host "  3. Run '/skill-name' in Claude Code to test a slash command"
    Write-Host ""
    Write-Host "  For full workspace setup, see SETUP-WINDOWS.md" -ForegroundColor Cyan
}
