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
#   ./install.sh --project [dir] write project rule files for editor agents
#   ./install.sh --project --all force every project target, not only detected ones
#   ./install.sh --print         print the rules block to paste into any other agent
set -euo pipefail
cd "$(dirname "$0")"
SRC="$PWD"

BEGIN="<!-- dts:start -->"
END="<!-- dts:end -->"
DRY=0; UNINSTALL=0; ONLY=""; LIST=0; PRINT=0; PROJECT=""; ALL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --uninstall) UNINSTALL=1 ;;
    --list) LIST=1 ;;
    --print) PRINT=1 ;;
    --only) ONLY="${2:-}"; shift ;;
    --project) PROJECT="${2:-$PWD}"; [[ -n "${2:-}" && "${2:-}" != -* ]] && shift ;;
    --all) ALL=1 ;;
    -h|--help) sed -n '2,/^set -/p' "$0" | grep '^#' | sed 's|^# \{0,1\}||'; exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
  shift
done

# Agents with a global instructions file, detected by their binary on PATH.
#
# name | binary | skills dir | memory file | wants output style
HARNESSES=(
  "claude|claude|$HOME/.claude/skills|$HOME/.claude/CLAUDE.md|yes"
  "codex|codex|$HOME/.codex/skills|$HOME/.codex/AGENTS.md|no"
  "opencode|opencode|$HOME/.config/opencode/skills|$HOME/.config/opencode/AGENTS.md|no"
  "pi|pi|$HOME/.pi/agent/skills|$HOME/.pi/agent/AGENTS.md|no"
  "gemini|gemini||$HOME/.gemini/GEMINI.md|no"
  "copilot|copilot||$HOME/.copilot/copilot-instructions.md|no"
  "amp|amp||$HOME/.config/amp/AGENTS.md|no"
  "kiro|kiro||$HOME/.kiro/steering/dts.md|no"
)

# Agents that read a rule file from inside the project instead of $HOME. Written
# by --project. DTS is plain text with no runtime, so each of these needs a copy
# of the same block and nothing else.
#
# name | marker directory | file to write
PROJECT_TARGETS=(
  "cursor|.cursor|.cursor/rules/dts.mdc"
  "windsurf|.windsurf|.windsurf/rules/dts.md"
  "cline|.clinerules|.clinerules/dts.md"
  "qoder|.qoder|.qoder/rules/dts.md"
  "kiro|.kiro|.kiro/steering/dts.md"
  "copilot|.github|.github/copilot-instructions.md"
)

say() { printf '%s\n' "$*"; }

# Runs a command, or prints it under --dry-run. Arguments stay a real argv, so a
# path holding a space or a quote is passed through untouched. An earlier version
# built a string and called eval, which broke on both.
run() {
  if [[ $DRY -eq 1 ]]; then
    printf '    would:'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

if [[ $PRINT -eq 1 ]]; then
  # Paste target for any agent this script does not know. The markers matter:
  # keep them and a later ./install.sh will update the block in place instead of
  # adding a second copy.
  printf '%s\n' "$BEGIN"
  cat "$SRC/rules/dts.md"
  printf '%s\n' "$END"
  exit 0
fi

# Cursor reads .mdc and needs this front matter to apply the rule unprompted.
# Every other project target takes the block as-is.
cursor_frontmatter() {
  printf -- '---\ndescription: DTS output standard\nalwaysApply: true\n---\n\n'
}

if [[ -n "$PROJECT" ]]; then
  [[ -d "$PROJECT" ]] || { echo "no such directory: $PROJECT" >&2; exit 2; }
  say "project: $PROJECT"
  wrote=0
  for row in "${PROJECT_TARGETS[@]}"; do
    IFS='|' read -r name marker file <<<"$row"
    [[ -n "$ONLY" && "$ONLY" != "$name" ]] && continue
    dest="$PROJECT/$file"

    if [[ $UNINSTALL -eq 1 ]]; then
      if [[ -f "$dest" ]]; then
        run python3 "$SRC/install.py" remove "$dest"
        say "    $name: rules removed from $file"
        wrote=$((wrote+1))
      fi
      continue
    fi

    # Without --all only the agents this project already uses get a file, so a
    # repo does not collect rule files for editors nobody here runs.
    if [[ $ALL -eq 0 && ! -d "$PROJECT/$marker" ]]; then
      say "    $name: skipped, no $marker/ (use --all to force)"
      continue
    fi

    run mkdir -p "$(dirname "$dest")"
    if [[ "$file" == *.mdc && ! -f "$dest" ]]; then
      if [[ $DRY -eq 1 ]]; then
        say "    would: write Cursor front matter to $file"
      else
        cursor_frontmatter > "$dest"
      fi
    fi
    run python3 "$SRC/install.py" write "$dest" "$SRC/rules/dts.md"
    say "    $name -> $file"
    wrote=$((wrote+1))
  done

  # Every remaining instruction-tier agent reads AGENTS.md: Zed, Amp, Jules,
  # Junie, Antigravity, CodeWhale, Swival, and the VS Code Codex extension.
  if [[ -z "$ONLY" || "$ONLY" == agents ]]; then
    if [[ $UNINSTALL -eq 1 ]]; then
      if [[ -f "$PROJECT/AGENTS.md" ]]; then
        run python3 "$SRC/install.py" remove "$PROJECT/AGENTS.md"
        say "    AGENTS.md: rules removed"
        wrote=$((wrote+1))
      fi
    else
      run python3 "$SRC/install.py" write "$PROJECT/AGENTS.md" "$SRC/rules/dts.md"
      say "    AGENTS.md -> read by Zed, Amp, Jules, Junie, Antigravity, CodeWhale"
      wrote=$((wrote+1))
    fi
  fi

  [[ $wrote -eq 0 ]] && say "  nothing to do"
  if [[ $DRY -eq 1 ]]; then
    say ""
    say "Dry run. Nothing changed."
  fi
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
      if [[ -d "$skills/dts" ]]; then
        run rm -rf "$skills/dts"
        say "    skill removed"
      else
        say "    skill: absent"
      fi
    else
      run mkdir -p "$skills"
      run rm -rf "$skills/dts"
      run cp -r "$SRC/skills/dts" "$skills/dts"
      say "    skill -> $skills/dts"
    fi
  else
    say "    skill: not supported by $name, rules only"
  fi

  # 2. rules block, between markers, never clobbering the file
  if [[ $UNINSTALL -eq 1 ]]; then
    if [[ -f "$mem" ]] && grep -qF "$BEGIN" "$mem"; then
      run python3 "$SRC/install.py" remove "$mem"
      say "    rules removed from $mem"
    else
      say "    rules: not present"
    fi
  else
    run mkdir -p "$(dirname "$mem")"
    run python3 "$SRC/install.py" write "$mem" "$SRC/rules/dts.md"
    say "    rules -> $mem"
  fi

  # 3. output style, Claude Code only
  if [[ "$style" == yes ]]; then
    dest="$HOME/.claude/output-styles"
    if [[ $UNINSTALL -eq 1 ]]; then
      if [[ -f "$dest/dts.md" ]]; then
        run rm -f "$dest/dts.md"
        say "    output style removed"
      else
        say "    output style: absent"
      fi
    else
      run mkdir -p "$dest"
      run cp "$SRC/output-styles/dts.md" "$dest/dts.md"
      say "    output style -> $dest/dts.md"
      say "    activate it with /config -> Output style -> DTS"
    fi
  fi
done

if [[ $LIST -eq 1 ]]; then
  say ""
  say "  project targets (./install.sh --project [dir]):"
  for row in "${PROJECT_TARGETS[@]}"; do
    IFS='|' read -r name marker file <<<"$row"
    say "    $name: $file  (written when $marker/ exists, or with --all)"
  done
  say "    every other agent: AGENTS.md"
fi

if [[ $detected -eq 0 ]]; then
  say "No supported harness found on PATH."
  say "Supported: claude, codex, opencode, pi, gemini."
  exit 1
fi
[[ $LIST -eq 1 ]] && exit 0
[[ $DRY -eq 1 ]] && say "" && say "Dry run. Nothing changed."
exit 0
