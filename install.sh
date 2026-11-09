#!/usr/bin/env bash
# Installs the skills of one or more plugins into a tool's skills folder.
# It is the route for Windsurf (which has no plugin system) and the alternative for
# any tool compatible with the Agent Skills standard.
#
# Usage:
#   ./install.sh --tool <claude|codex|copilot|cursor|windsurf> [--scope user|project]
#                [--plugins qa,engineering,...] [--project-dir DIR] [--link] [--force] [--dry-run]
#   ./install.sh --dest <skills-folder> [--plugins ...] [--link] [--force] [--dry-run]
#
# By default it installs every plugin, copies (does not link) and, in the "project" scope,
# uses the current directory. It never overwrites a skill it did not install without --force.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL="" SCOPE="project" PLUGINS="" DEST="" PROJECT_DIR="$PWD" LINK=0 FORCE=0 DRY=0

usage() { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }
error() { echo "error: $*" >&2; exit 2; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool) TOOL="${2:-}"; shift 2 ;;
    --scope) SCOPE="${2:-}"; shift 2 ;;
    --plugins) PLUGINS="${2:-}"; shift 2 ;;
    --dest) DEST="${2:-}"; shift 2 ;;
    --project-dir) PROJECT_DIR="${2:-}"; shift 2 ;;
    --link) LINK=1; shift ;;
    --force) FORCE=1; shift ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) usage 0 ;;
    *) echo "unknown option: $1" >&2; usage 2 ;;
  esac
done

if [[ -z "$DEST" ]]; then
  [[ -n "$TOOL" ]] || error "give --tool or --dest"
  [[ "$SCOPE" == "user" || "$SCOPE" == "project" ]] || error "--scope must be user or project"
  case "$TOOL:$SCOPE" in
    claude:project)   DEST="$PROJECT_DIR/.claude/skills" ;;
    claude:user)      DEST="$HOME/.claude/skills" ;;
    codex:project)    DEST="$PROJECT_DIR/.agents/skills" ;;
    codex:user)       DEST="$HOME/.agents/skills" ;;
    copilot:project)  DEST="$PROJECT_DIR/.github/skills" ;;
    copilot:user)     error "for Copilot at user level install the plugin instead: copilot plugin install <plugin>@sv-agent-plugins" ;;
    cursor:project)   DEST="$PROJECT_DIR/.cursor/skills" ;;
    cursor:user)      DEST="$HOME/.cursor/skills" ;;
    windsurf:project) DEST="$PROJECT_DIR/.windsurf/skills" ;;
    windsurf:user)    DEST="$HOME/.codeium/windsurf/skills" ;;
    *) error "unsupported tool: $TOOL (use --dest for another skills folder)" ;;
  esac
fi

AVAILABLE=$(cd "$ROOT/plugins" && ls -d */ | tr -d '/')
if [[ -z "$PLUGINS" ]]; then PLUGINS=$(echo "$AVAILABLE" | tr '\n' ','); fi

IFS=',' read -r -a LIST <<< "$PLUGINS"
SKILLS=()
for p in "${LIST[@]}"; do
  [[ -z "$p" ]] && continue
  [[ -d "$ROOT/plugins/$p/skills" ]] || error "unknown plugin: $p (available: $(echo $AVAILABLE))"
  for s in "$ROOT/plugins/$p/skills"/*/; do
    [[ -f "$s/SKILL.md" ]] && SKILLS+=("${s%/}")
  done
done
[[ ${#SKILLS[@]} -gt 0 ]] || error "no skills to install"

# Pre-check: do not overwrite skills installed by someone else
for s in "${SKILLS[@]}"; do
  name=$(basename "$s"); target="$DEST/$name"
  if [[ -e "$target" && $FORCE -eq 0 ]]; then
    if [[ ! -f "$target/.sv-agent-plugins" && ! -L "$target" ]]; then
      error "$target already exists and was not installed by this repository; use --force to replace it"
    fi
  fi
done

echo "Installing ${#SKILLS[@]} skills into $DEST ($([[ $LINK -eq 1 ]] && echo links || echo copies))"
[[ $DRY -eq 1 ]] && { for s in "${SKILLS[@]}"; do echo "  $(basename "$s")"; done; echo "(dry-run: nothing was written)"; exit 0; }

mkdir -p "$DEST"
for s in "${SKILLS[@]}"; do
  name=$(basename "$s"); target="$DEST/$name"
  rm -rf "$target"
  if [[ $LINK -eq 1 ]]; then
    ln -s "$s" "$target"
  else
    cp -R "$s" "$target"
    find "$target" -name '__pycache__' -prune -exec rm -rf {} +
    echo "installed from $ROOT" > "$target/.sv-agent-plugins"
  fi
  echo "  $name"
done
echo "Done. Restart the tool or open a new session so it picks up the skills."
