#!/usr/bin/env bash
set -euo pipefail

# Claude Code Skills Bundle Installer
# Usage:
#   ./install.sh --all                              Install everything
#   ./install.sh --global                           Install global commands + skills only
#   ./install.sh --project <name> [--project <n2>]  Install specific project(s)
#   ./install.sh --list                             List available projects
#   ./install.sh --dry-run --all                    Preview without copying

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
DRY_RUN=false
INSTALL_GLOBAL=false
INSTALL_ALL=false
PROJECTS=()

# Colors (if terminal supports it)
if [ -t 1 ]; then
  GREEN='\033[0;32m'
  YELLOW='\033[0;33m'
  BLUE='\033[0;34m'
  RED='\033[0;31m'
  NC='\033[0m'
else
  GREEN='' YELLOW='' BLUE='' RED='' NC=''
fi

log()  { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[!!]${NC} $1"; }
info() { echo -e "${BLUE}[..]${NC} $1"; }
err()  { echo -e "${RED}[ERR]${NC} $1" >&2; }

usage() {
  cat <<'EOF'
Claude Code Skills Bundle Installer

Usage:
  ./install.sh --all                              Install global + all projects
  ./install.sh --global                           Install global commands + skills only
  ./install.sh --project <name> [--project <n2>]  Install specific project(s)
  ./install.sh --list                             List available projects
  ./install.sh --dry-run <any of above>           Preview without copying

Options:
  --target-dir <path>   Override project root for --project installs
                        (default: prompts interactively)
  --claude-home <path>  Override ~/.claude location (default: ~/.claude)
  --help                Show this help

Examples:
  ./install.sh --global
  ./install.sh --project ai-social-media-manager --target-dir ~/my-project
  ./install.sh --dry-run --all
EOF
  exit 0
}

copy_dir() {
  local src="$1" dst="$2"
  if [ "$DRY_RUN" = true ]; then
    info "[dry-run] Would copy: $src → $dst"
    return
  fi
  mkdir -p "$dst"
  cp -R "$src"/* "$dst"/ 2>/dev/null || true
}

copy_file() {
  local src="$1" dst="$2"
  if [ "$DRY_RUN" = true ]; then
    info "[dry-run] Would copy: $src → $dst"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
}

install_global() {
  info "Installing global commands → $CLAUDE_HOME/commands/"
  if [ -d "$BUNDLE_DIR/global/commands" ]; then
    for f in "$BUNDLE_DIR"/global/commands/*.md; do
      [ -f "$f" ] || continue
      copy_file "$f" "$CLAUDE_HOME/commands/$(basename "$f")"
      log "  $(basename "$f")"
    done
  fi

  info "Installing global skills → $CLAUDE_HOME/skills/"
  if [ -d "$BUNDLE_DIR/global/skills" ]; then
    for skill_dir in "$BUNDLE_DIR"/global/skills/*/; do
      [ -d "$skill_dir" ] || continue
      local skill_name
      skill_name="$(basename "$skill_dir")"
      copy_dir "$skill_dir" "$CLAUDE_HOME/skills/$skill_name"
      local file_count
      file_count=$(find "$skill_dir" -type f | wc -l | tr -d ' ')
      log "  $skill_name/ ($file_count files)"
    done
  fi
}

install_project() {
  local project_name="$1"
  local project_src="$BUNDLE_DIR/projects/$project_name"

  if [ ! -d "$project_src" ]; then
    err "Project '$project_name' not found in bundle"
    err "Available: $(ls "$BUNDLE_DIR/projects/" | tr '\n' ', ')"
    return 1
  fi

  # Determine target directory
  local target_dir="${TARGET_DIR:-}"
  if [ -z "$target_dir" ]; then
    echo ""
    echo "Project: $project_name"
    echo "Where is this project on disk? (the root directory with .claude/)"
    read -r -p "Path: " target_dir
    target_dir="${target_dir/#\~/$HOME}"
  fi

  if [ ! -d "$target_dir" ] && [ "$DRY_RUN" = false ]; then
    warn "Directory $target_dir does not exist"
    read -r -p "Create it? [y/N] " confirm
    if [[ "$confirm" =~ ^[Yy] ]]; then
      mkdir -p "$target_dir"
    else
      err "Skipping $project_name"
      return 1
    fi
  fi

  info "Installing $project_name → $target_dir/.claude/"

  # Install skills
  if [ -d "$project_src/skills" ]; then
    for skill_dir in "$project_src"/skills/*/; do
      [ -d "$skill_dir" ] || continue
      local skill_name
      skill_name="$(basename "$skill_dir")"
      copy_dir "$skill_dir" "$target_dir/.claude/skills/$skill_name"
      local file_count
      file_count=$(find "$skill_dir" -type f | wc -l | tr -d ' ')
      log "  skill: $skill_name/ ($file_count files)"
    done
  fi

  # Install commands
  if [ -d "$project_src/commands" ]; then
    for f in "$project_src"/commands/*.md; do
      [ -f "$f" ] || continue
      copy_file "$f" "$target_dir/.claude/commands/$(basename "$f")"
      log "  command: $(basename "$f")"
    done
  fi
}

list_projects() {
  echo "Available projects in bundle:"
  echo ""
  for project_dir in "$BUNDLE_DIR"/projects/*/; do
    [ -d "$project_dir" ] || continue
    local name
    name="$(basename "$project_dir")"
    local skills=0 commands=0
    [ -d "$project_dir/skills" ] && skills=$(find "$project_dir/skills" -maxdepth 1 -type d | tail -n+2 | wc -l | tr -d ' ')
    [ -d "$project_dir/commands" ] && commands=$(find "$project_dir/commands" -name '*.md' | wc -l | tr -d ' ')
    printf "  %-35s %2d skills, %2d commands\n" "$name" "$skills" "$commands"
  done
}

# Parse arguments
TARGET_DIR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --all)        INSTALL_ALL=true; INSTALL_GLOBAL=true; shift ;;
    --global)     INSTALL_GLOBAL=true; shift ;;
    --project)    PROJECTS+=("$2"); shift 2 ;;
    --target-dir) TARGET_DIR="$2"; shift 2 ;;
    --claude-home) CLAUDE_HOME="$2"; shift 2 ;;
    --dry-run)    DRY_RUN=true; shift ;;
    --list)       list_projects; exit 0 ;;
    --help|-h)    usage ;;
    *)            err "Unknown option: $1"; usage ;;
  esac
done

# Validate
if [ "$INSTALL_GLOBAL" = false ] && [ ${#PROJECTS[@]} -eq 0 ]; then
  err "No install target specified. Use --all, --global, or --project <name>"
  echo ""
  usage
fi

# Header
echo ""
echo "========================================="
echo "  Claude Code Skills Bundle Installer"
echo "========================================="
echo ""
echo "  Bundle:     $BUNDLE_DIR"
echo "  Claude home: $CLAUDE_HOME"
[ "$DRY_RUN" = true ] && echo "  Mode:       DRY RUN (no files will be copied)"
echo ""

# Install global
if [ "$INSTALL_GLOBAL" = true ]; then
  install_global
  echo ""
fi

# Install projects
if [ "$INSTALL_ALL" = true ]; then
  warn "Installing ALL projects requires specifying each project's target directory."
  warn "Use --target-dir to set a single target, or you'll be prompted for each."
  echo ""
  for project_dir in "$BUNDLE_DIR"/projects/*/; do
    [ -d "$project_dir" ] || continue
    install_project "$(basename "$project_dir")" || true
  done
else
  for project in "${PROJECTS[@]}"; do
    install_project "$project" || true
  done
fi

echo ""
if [ "$DRY_RUN" = true ]; then
  info "Dry run complete. No files were modified."
else
  log "Installation complete!"
  echo ""
  echo "Next steps:"
  echo "  1. Restart Claude Code to pick up new skills"
  echo "  2. Check prerequisites in README.md for specific skills"
  echo "  3. Run '/skill-name' to test a slash command"
fi
