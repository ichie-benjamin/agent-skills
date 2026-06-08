#!/usr/bin/env bash
# new-task.sh — scaffold a new task file in .agent/TASKS/active/
# Usage: new-task.sh <slug> [title]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="${SCRIPT_DIR}/../assets/task-template.md"

if [[ $# -lt 1 ]]; then
  echo "usage: new-task.sh <slug> [title]" >&2
  exit 2
fi

SLUG="$1"
TITLE="${2:-$(echo "$SLUG" | tr '-' ' ' | awk '{for(i=1;i<=NF;i++)$i=toupper(substr($i,1,1))substr($i,2)}1')}"
DATE="$(date +%Y-%m-%d)"
OWNER="${DEV_GUIDELINE_OWNER:-$(whoami)}"

if [[ ! -d .agent/TASKS/active ]]; then
  echo "error: .agent/TASKS/active not found. Run /dev-guideline setup first." >&2
  exit 1
fi

DEST=".agent/TASKS/active/${SLUG}.md"
if [[ -f "$DEST" ]]; then
  echo "error: $DEST already exists" >&2
  exit 1
fi

if [[ ! -f "$TEMPLATE" ]]; then
  echo "error: template not found at $TEMPLATE" >&2
  exit 1
fi

sed \
  -e "s|__TITLE__|${TITLE}|g" \
  -e "s|__SLUG__|${SLUG}|g" \
  -e "s|__DATE__|${DATE}|g" \
  -e "s|__OWNER__|${OWNER}|g" \
  "$TEMPLATE" > "$DEST"

echo "created $DEST"
