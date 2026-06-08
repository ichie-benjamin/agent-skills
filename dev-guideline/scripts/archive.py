#!/usr/bin/env python3
"""
archive.py — move completed tasks into .agent/TASKS/archived/.

Interactive default:
  - count completed tasks
  - tell the user
  - offer choices: archive all / archive older than N days / cancel
  - default selection: ALL (because completed is meant to be temporary)

Non-interactive flags:
  --all              archive every completed task
  --older=30d        archive completed older than N days (units: d, w, m)
  --yes              skip confirmation prompts
  --dry-run          show plan, don't move anything
  --root=.           project root (default: cwd)
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
from pathlib import Path

TODAY = dt.date.today()


def parse_age(s: str) -> dt.timedelta:
    m = re.match(r"^(\d+)\s*([dwm])?$", s.strip().lower())
    if not m:
        raise ValueError(f"bad age '{s}' — use forms like 30d, 4w, 2m")
    n = int(m.group(1))
    unit = m.group(2) or "d"
    if unit == "d": return dt.timedelta(days=n)
    if unit == "w": return dt.timedelta(weeks=n)
    if unit == "m": return dt.timedelta(days=n * 30)
    raise ValueError(f"bad unit '{unit}'")


def task_date(path: Path) -> dt.date:
    """Best-effort date from frontmatter 'updated' (then 'completed', 'created') else file mtime."""
    try:
        text = path.read_text()
    except OSError:
        return dt.date.fromtimestamp(path.stat().st_mtime)
    if text.startswith("---"):
        end = text.find("\n---", 4)
        if end != -1:
            for line in text[4:end].splitlines():
                m = re.match(r"^(updated|completed|created)\s*:\s*(\S+)", line)
                if m:
                    try:
                        return dt.date.fromisoformat(m.group(2).strip().strip('"'))
                    except ValueError:
                        continue
    return dt.date.fromtimestamp(path.stat().st_mtime)


def confirm(msg: str, yes: bool) -> bool:
    if yes:
        return True
    try:
        return input(f"{msg} [Y/n] ").strip().lower() in ("", "y", "yes")
    except EOFError:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="archive completed tasks")
    ap.add_argument("--root", default=".")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--older")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    completed_dir = root / ".agent" / "TASKS" / "completed"
    archived_dir  = root / ".agent" / "TASKS" / "archived"

    if not completed_dir.exists():
        print(f"no completed dir at {completed_dir}")
        return 0

    files = sorted(completed_dir.glob("*.md"))
    count = len(files)

    if count == 0:
        print("nothing to archive — 0 completed tasks.")
        return 0

    # decide which to archive
    if args.all:
        chosen = files
        reason = f"all {count}"
    elif args.older:
        delta = parse_age(args.older)
        cutoff = TODAY - delta
        chosen = [f for f in files if task_date(f) <= cutoff]
        reason = f"older than {args.older} (≤ {cutoff})"
    else:
        # interactive
        print(f"you have {count} completed task{'s' if count != 1 else ''} in .agent/TASKS/completed/")
        print()
        print("  [1] archive all                 (default)")
        print("  [2] archive older than 30 days")
        print("  [3] archive older than 7 days")
        print("  [4] cancel")
        try:
            choice = input("> ").strip() or "1"
        except EOFError:
            choice = "1"
        if choice == "1":
            chosen = files
            reason = f"all {count}"
        elif choice == "2":
            cutoff = TODAY - dt.timedelta(days=30)
            chosen = [f for f in files if task_date(f) <= cutoff]
            reason = f"older than 30d (≤ {cutoff})"
        elif choice == "3":
            cutoff = TODAY - dt.timedelta(days=7)
            chosen = [f for f in files if task_date(f) <= cutoff]
            reason = f"older than 7d (≤ {cutoff})"
        else:
            print("cancelled.")
            return 0

    if not chosen:
        print(f"no tasks match ({reason}).")
        return 0

    print()
    print(f"will archive {len(chosen)} task{'s' if len(chosen) != 1 else ''} ({reason}):")
    for f in chosen[:20]:
        print(f"  {f.name}  (date: {task_date(f)})")
    if len(chosen) > 20:
        print(f"  ... and {len(chosen) - 20} more")
    print()

    if args.dry_run:
        print("(dry-run — no changes.)")
        return 0

    if not confirm(f"proceed?", args.yes):
        print("cancelled.")
        return 0

    archived_dir.mkdir(parents=True, exist_ok=True)
    moved = 0
    for f in chosen:
        dst = archived_dir / f.name
        if dst.exists():
            print(f"skip {f.name} (already exists in archived/)")
            continue
        shutil.move(str(f), str(dst))
        moved += 1

    print(f"archived {moved} task{'s' if moved != 1 else ''}.")
    remaining = len(list(completed_dir.glob("*.md")))
    print(f"completed/ now has {remaining} task{'s' if remaining != 1 else ''}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
