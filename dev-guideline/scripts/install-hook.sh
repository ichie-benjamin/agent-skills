#!/usr/bin/env bash
# install-hook.sh — install dev-guideline SessionStart hook into ~/.claude/settings.json
# Adds a SessionStart hook that prints a marker so the model is prompted to
# run the dev-guideline session-start protocol on every new session.
#
# Idempotent: re-running does not duplicate the hook.

set -euo pipefail

SETTINGS_DIR="${HOME}/.claude"
SETTINGS_FILE="${SETTINGS_DIR}/settings.json"
HOOK_CMD='echo "[dev-guideline] new session — run the session-start protocol: list .agent/TASKS/active/ and report before any new work."'

mkdir -p "${SETTINGS_DIR}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 required" >&2
  exit 1
fi

if [[ ! -f "${SETTINGS_FILE}" ]]; then
  echo "{}" > "${SETTINGS_FILE}"
fi

python3 - "$SETTINGS_FILE" "$HOOK_CMD" <<'PY'
import json, sys
path, cmd = sys.argv[1], sys.argv[2]
with open(path) as f:
    cfg = json.load(f)

cfg.setdefault("hooks", {})
ss = cfg["hooks"].setdefault("SessionStart", [])

# Look for existing dev-guideline hook
exists = False
for group in ss:
    for hook in group.get("hooks", []):
        if hook.get("type") == "command" and "dev-guideline" in hook.get("command", ""):
            exists = True
            break

if exists:
    print("dev-guideline SessionStart hook already installed — no changes.")
    sys.exit(0)

ss.append({
    "hooks": [
        {"type": "command", "command": cmd}
    ]
})

with open(path, "w") as f:
    json.dump(cfg, f, indent=2)
print(f"installed SessionStart hook in {path}")
PY
