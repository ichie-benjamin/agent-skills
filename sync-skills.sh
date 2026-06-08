#!/usr/bin/env bash
# sync-skills.sh — symlink every custom skill in this folder into each AI tool's
# skills directory. Idempotent: re-running fixes drift without duplicating links.
#
# Canonical home: this directory (the script lives next to the skills it manages).
# Targets: ~/.claude/skills, ~/.codex/skills, ~/.cursor/skills (created if missing).
#
# Usage:
#   ./sync-skills.sh            # sync all skills to all targets
#   ./sync-skills.sh --dry-run  # show what would change, no writes
#   ./sync-skills.sh --prune    # also remove dangling symlinks in targets
#                               # (only links pointing into this canonical dir)

set -euo pipefail

CANON="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGETS=(
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.cursor/skills"
)

DRY=0
PRUNE=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    --prune)   PRUNE=1 ;;
    *) echo "usage: $0 [--dry-run] [--prune]"; exit 2 ;;
  esac
done

log() { printf '%s\n' "$*"; }
run() { if [[ $DRY -eq 1 ]]; then log "[dry] $*"; else eval "$@"; fi }

# collect skill dirs (anything in CANON that is a directory and has SKILL.md)
SKILLS=()
while IFS= read -r d; do
  if [[ -f "$d/SKILL.md" ]]; then SKILLS+=("$(basename "$d")"); fi
done < <(find "$CANON" -mindepth 1 -maxdepth 1 -type d -not -name ".*")

if [[ ${#SKILLS[@]} -eq 0 ]]; then
  echo "no skills with SKILL.md found in $CANON"
  exit 1
fi

log "canonical: $CANON"
log "skills:    ${SKILLS[*]}"
log ""

for target in "${TARGETS[@]}"; do
  log "=== $target ==="
  if [[ ! -d "$target" ]]; then
    run "mkdir -p '$target'"
  fi

  for skill in "${SKILLS[@]}"; do
    src="$CANON/$skill"
    dst="$target/$skill"
    if [[ -L "$dst" ]]; then
      cur="$(readlink "$dst")"
      if [[ "$cur" == "$src" ]]; then
        log "  ok   $skill"
      else
        log "  fix  $skill (was -> $cur)"
        run "rm '$dst'"
        run "ln -s '$src' '$dst'"
      fi
    elif [[ -e "$dst" ]]; then
      log "  SKIP $skill (target exists and is NOT a symlink — manual review)"
    else
      log "  link $skill"
      run "ln -s '$src' '$dst'"
    fi
  done

  if [[ $PRUNE -eq 1 ]]; then
    while IFS= read -r link; do
      tgt="$(readlink "$link")"
      if [[ "$tgt" == "$CANON/"* && ! -e "$tgt" ]]; then
        log "  prune $(basename "$link") (dangling -> $tgt)"
        run "rm '$link'"
      fi
    done < <(find "$target" -mindepth 1 -maxdepth 1 -type l)
  fi
  log ""
done

log "done. $(if [[ $DRY -eq 1 ]]; then echo 'dry-run — no changes made.'; fi)"
