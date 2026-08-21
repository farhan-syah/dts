#!/usr/bin/env bash
# Install DTS into every agent harness found on this machine.
#
# DTS ships in three parts. Not every harness takes all three.
#   skill        skills/dts/       the full spec, loaded on demand
#   rules        rules/dts.md      the always-on block, appended to the memory file
#   output style output-styles/       Claude Code only
#
# The rules block is written between markers and replaced in place on reinstall.
# Nothing outside the markers is touched, and no memory file is ever overwritten.
#
# Usage:
#   ./install.sh                 install into every harness detected
#   ./install.sh --dry-run       print what would change, touch nothing
#   ./install.sh --only claude   restrict to one harness
#   ./install.sh --uninstall     remove the skill and the marked block
#   ./install.sh --list          show detected harnesses and their paths
#   ./install.sh --print         print the rules block to paste into any other agent
set -euo pipefail
cd "$(dirname "$0")"
SRC="$PWD"

BEGIN="<!-- dts:start -->"
END="<!-- dts:end -->"
DRY=0; UNINSTALL=0; ONLY=""; LIST=0; PRINT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --uninstall) UNINSTALL=1 ;;
    --list) LIST=1 ;;
    --print) PRINT=1 ;;
    --only) ONLY="${2:-}"; shift ;;
    -h|--help) sed -n '2,/^set -/p' "$0" | grep '^#' | sed 's|^# \{0,1\}||'; exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
  shift
done

# name | binary | skills dir | memory file | wants output style
HARNESSES=(
  "claude|claude|$HOME/.claude/skills|$HOME/.claude/CLAUDE.md|yes"
  "codex|codex|$HOME/.codex/skills|$HOME/.codex/AGENTS.md|no"
  "opencode|opencode|$HOME/.config/opencode/skills|$HOME/.config/opencode/AGENTS.md|no"
  "pi|pi|$HOME/.pi/agent/skills|$HOME/.pi/agent/AGENTS.md|no"
  "gemini|gemini||$HOME/.gemini/GEMINI.md|no"
)

say() { printf '%s\n' "$*"; }
act() { [[ $DRY -eq 1 ]] && say "    would: $*" || eval "$@"; }

if [[ $PRINT -eq 1 ]]; then
  # Paste target for any agent this script does not know. The markers matter:
  # keep them and a later ./install.sh will update the block in place instead of
  # adding a second copy.
  printf '%s\n' "$BEGIN"
  cat "$SRC/rules/dts.md"
  printf '%s\n' "$END"
  exit 0
fi

detected=0
for row in "${HARNESSES[@]}"; do
  IFS='|' read -r name bin skills mem style <<<"$row"
  [[ -n "$ONLY" && "$ONLY" != "$name" ]] && continue

  if ! command -v "$bin" >/dev/null 2>&1; then
    [[ $LIST -eq 1 ]] && say "  $name: not installed"
    continue
  fi
  detected=$((detected+1))

  if [[ $LIST -eq 1 ]]; then
    say "  $name"
    say "    skills: ${skills:-none (rules only)}"
    say "    memory: $mem"
    [[ "$style" == yes ]] && say "    output style: $HOME/.claude/output-styles/"
    continue
  fi

  say "$name"

  # 1. skill
  if [[ -n "$skills" ]]; then
    if [[ $UNINSTALL -eq 1 ]]; then
      [[ -d "$skills/dts" ]] && act "rm -rf '$skills/dts'" || say "    skill: absent"
    else
      act "mkdir -p '$skills'"
      act "rm -rf '$skills/dts'"
      act "cp -r '$SRC/skills/dts' '$skills/dts'"
      say "    skill -> $skills/dts"
    fi
  else
    say "    skill: not supported by $name, rules only"
  fi

  # 2. rules block, between markers, never clobbering the file
  if [[ $UNINSTALL -eq 1 ]]; then
    if [[ -f "$mem" ]] && grep -qF "$BEGIN" "$mem"; then
      act "python3 '$SRC/install.py' remove '$mem'"
      say "    rules removed from $mem"
    else
      say "    rules: not present"
    fi
  else
    act "mkdir -p \"\$(dirname '$mem')\""
    act "python3 '$SRC/install.py' write '$mem' '$SRC/rules/dts.md'"
    say "    rules -> $mem"
  fi

  # 3. output style, Claude Code only
  if [[ "$style" == yes ]]; then
    dest="$HOME/.claude/output-styles"
    if [[ $UNINSTALL -eq 1 ]]; then
      [[ -f "$dest/dts.md" ]] && act "rm -f '$dest/dts.md'" || true
      say "    output style removed"
    else
      act "mkdir -p '$dest'"
      act "cp '$SRC/output-styles/dts.md' '$dest/dts.md'"
      say "    output style -> $dest/dts.md"
      say "    activate it with /config -> Output style -> DTS"
    fi
  fi
done

if [[ $detected -eq 0 ]]; then
  say "No supported harness found on PATH."
  say "Supported: claude, codex, opencode, pi, gemini."
  exit 1
fi
[[ $LIST -eq 1 ]] && exit 0
[[ $DRY -eq 1 ]] && say "" && say "Dry run. Nothing changed."
exit 0
