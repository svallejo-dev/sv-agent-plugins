#!/usr/bin/env bash
# Connects a single personal rules file (~/.agents/AGENTS.md by default) to each tool's
# global instructions file, so every tool loads the same rules in any project.
#
#   Claude Code  ~/.claude/CLAUDE.md                          (adds the line @<source>)
#   Codex        ~/.codex/AGENTS.md                            (symbolic link)
#   Copilot CLI  ~/.copilot/copilot-instructions.md            (symbolic link)
#   Windsurf     ~/.codeium/windsurf/memories/global_rules.md  (symbolic link; 6,000 characters max)
#   Cursor       no file: paste it into Settings → Rules → User Rules (the script says so)
#
# Usage:
#   tools/install-global-rules.sh [--source PATH] [--tools claude,codex,copilot,windsurf]
#                                 [--force] [--dry-run]
#
# If the source does not exist, it is created from templates/global-rules.md for you to edit.
# It never replaces an existing instructions file without --force; with --force it leaves a .bak copy.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$HOME/.agents/AGENTS.md"
TOOLS="claude,codex,copilot,windsurf"
FORCE=0 DRY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source) SOURCE="${2:-}"; shift 2 ;;
    --tools) TOOLS="${2:-}"; shift 2 ;;
    --force) FORCE=1; shift ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

run() { if [[ $DRY -eq 1 ]]; then echo "  (dry-run) $*"; else "$@"; fi; }

if [[ ! -f "$SOURCE" ]]; then
  echo "Creating $SOURCE from the template: edit it with your rules."
  run mkdir -p "$(dirname "$SOURCE")"
  run cp "$ROOT/templates/global-rules.md" "$SOURCE"
fi

link() {  # $1 = target
  local target="$1"
  if [[ -L "$target" && "$(readlink "$target")" == "$SOURCE" ]]; then
    echo "  already linked: $target"; return
  fi
  if [[ -e "$target" || -L "$target" ]]; then
    if [[ $FORCE -eq 0 ]]; then
      echo "  SKIPPED: $target already exists and is not a link to the source. Merge its content into $SOURCE and run again with --force."
      return
    fi
    run mv "$target" "$target.bak"
    echo "  backup: $target.bak"
  fi
  run mkdir -p "$(dirname "$target")"
  run ln -s "$SOURCE" "$target"
  echo "  linked: $target → $SOURCE"
}

IFS=',' read -r -a LIST <<< "$TOOLS"
for t in "${LIST[@]}"; do
  case "$t" in
    claude)
      echo "Claude Code"
      target="$HOME/.claude/CLAUDE.md"; line="@$SOURCE"
      if [[ -f "$target" ]] && grep -qxF "$line" "$target"; then
        echo "  already imports the source: $target"
      else
        run mkdir -p "$(dirname "$target")"
        if [[ $DRY -eq 1 ]]; then echo "  (dry-run) append '$line' to $target"; else printf '%s\n' "$line" >> "$target"; fi
        echo "  imported in: $target"
      fi ;;
    codex)    echo "Codex";       link "$HOME/.codex/AGENTS.md" ;;
    copilot)  echo "Copilot CLI"; link "$HOME/.copilot/copilot-instructions.md" ;;
    windsurf)
      echo "Windsurf"
      if [[ -f "$SOURCE" ]] && [[ $(wc -m < "$SOURCE") -gt 6000 ]]; then
        echo "  WARNING: the source exceeds the 6,000 characters Windsurf accepts for global rules; trim it or Windsurf will truncate it."
      fi
      link "$HOME/.codeium/windsurf/memories/global_rules.md" ;;
    cursor) ;;  # no global file: reported at the end
    *) echo "unknown tool: $t (claude, codex, copilot, windsurf, cursor)" >&2; exit 2 ;;
  esac
done

echo "Cursor: it does not use a global file; copy the content of $SOURCE into Settings → Rules → User Rules."
echo "Open a new session in each tool so it loads the rules."
