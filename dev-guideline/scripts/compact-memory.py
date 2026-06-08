#!/usr/bin/env python3
"""
compact-memory.py — analyze .agent/MEMORY.md and prepare for compaction.

This script does the MECHANICAL parts only:
  - counts entries and lines
  - groups entries by month
  - identifies likely duplicates (same date or near-identical titles)
  - rewrites frontmatter with current counts and last_updated

The MERGE/DROP judgment is done by the agent after reading this script's
report. The agent then applies edits and re-runs this script to verify.

Usage:
  compact-memory.py            # report only
  compact-memory.py --refresh  # rewrite frontmatter (entries/last_updated) only
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections import defaultdict
from pathlib import Path

TODAY = dt.date.today().isoformat()
ENTRY_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*[—-]?\s*(.*)$", re.MULTILINE)


def parse(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    fm: dict = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^([a-zA-Z_]+)\s*:\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm, text[end + 4 :].lstrip("\n")


def render_fm(fm: dict) -> str:
    return "---\n" + "\n".join(f"{k}: {v}" for k, v in fm.items()) + "\n---\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--refresh", action="store_true",
                    help="rewrite frontmatter with current entries/last_updated only")
    args = ap.parse_args()

    path = Path(args.root) / ".agent" / "MEMORY.md"
    if not path.exists():
        print(f"error: {path} not found", file=sys.stderr)
        return 1

    text = path.read_text()
    fm, body = parse(text)
    entries = ENTRY_RE.findall(body)
    line_count = len(text.splitlines())

    print(f"MEMORY: {path}")
    print(f"  lines:   {line_count}")
    print(f"  entries: {len(entries)}")
    print(f"  thresholds: 150 lines / 40 entries")
    over = line_count > 150 or len(entries) > 40
    print(f"  status:  {'OVER THRESHOLD — compact recommended' if over else 'ok'}")
    print()

    # group by month
    by_month: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for date, title in entries:
        month = date[:7]
        by_month[month].append((date, title.strip()))
    print("entries by month:")
    for month in sorted(by_month):
        items = by_month[month]
        print(f"  {month}: {len(items)}")
        for date, title in items:
            print(f"    {date}  {title[:60]}")
    print()

    # likely duplicates (same title or substring overlap)
    titles_seen: dict[str, list[str]] = defaultdict(list)
    for date, title in entries:
        key = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
        titles_seen[key].append(date)
    dupes = {k: v for k, v in titles_seen.items() if len(v) > 1}
    if dupes:
        print("possible duplicates (same/near-identical title):")
        for title, dates in dupes.items():
            print(f"  '{title}' — {', '.join(dates)}")
        print()
    else:
        print("no obvious duplicates detected.")
        print()

    if args.refresh:
        new_fm = {"last_updated": TODAY, "entries": str(len(entries))}
        # preserve any extra keys
        for k, v in fm.items():
            if k not in new_fm:
                new_fm[k] = v
        new_text = render_fm(new_fm) + "\n" + body.lstrip()
        path.write_text(new_text)
        print(f"refreshed frontmatter: last_updated={TODAY}, entries={len(entries)}")

    if over and not args.refresh:
        print("NEXT STEP (for the agent):")
        print("  1. Read MEMORY.md")
        print("  2. Group entries by topic; merge near-duplicates; drop obsolete entries")
        print("  3. Drop entries now codified in CLAUDE.md or the code itself")
        print("  4. Show the user a diff and ask for approval")
        print("  5. On approval, re-run with --refresh to update the frontmatter")
    return 0


if __name__ == "__main__":
    sys.exit(main())
