#!/usr/bin/env python3
"""
dev-guideline setup — detect project state and init / migrate / repair.

Modes (auto-detected, can be forced):
  bootstrap  — neither .ai/ nor .agent/ exists. Scaffold .agent/.
  migrate    — .ai/TASKS/ exists, no .agent/. Move and normalize.
  repair     — .agent/ exists. Verify structure, lint, report drift.

The script does mechanical work only (file moves, frontmatter normalization,
.gitignore updates, template scaffolding). The agent does the judgment work
(seeding MEMORY/PROGRESS from project knowledge, reviewing stale entries).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"

TODAY = dt.date.today().isoformat()

GITIGNORE_ENTRIES = [
    ".agent/.tmp/",
    ".agent/credentials.json",
    ".agent/data/",
]

REQUIRED_TASK_KEYS = ["title", "slug", "created", "updated", "status", "owner"]


# ---------- detection ----------

def detect_mode(root: Path) -> str:
    has_legacy = (root / ".ai" / "TASKS").exists() or (root / ".ai" / "memory.md").exists()
    has_new = (root / ".agent").exists()
    if has_legacy and not has_new:
        return "migrate"
    if has_legacy and has_new:
        return "migrate-merge"
    if has_new:
        return "repair"
    return "bootstrap"


def project_looks_active(root: Path) -> bool:
    signals = [
        "CLAUDE.md", "AGENTS.md", "AGENT.md",
        "package.json", "pyproject.toml", "go.mod", "Cargo.toml",
        "composer.json", "Gemfile",
        "src", "app", "lib",
    ]
    return any((root / s).exists() for s in signals)


# ---------- helpers ----------

def confirm(prompt: str, yes: bool) -> bool:
    if yes:
        return True
    try:
        ans = input(f"{prompt} [y/N] ").strip().lower()
    except EOFError:
        return False
    return ans in ("y", "yes")


def log(msg: str, dry: bool = False) -> None:
    prefix = "[dry-run] " if dry else ""
    print(f"{prefix}{msg}")


def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9-]+", "-", name).strip("-").lower()
    return s or "task"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Minimal YAML — flat key: value only."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    fm_text = text[4:end].strip()
    body = text[end + 4 :].lstrip("\n")
    fm: dict = {}
    for line in fm_text.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        fm[key] = val
    return fm, body


def render_frontmatter(fm: dict) -> str:
    lines = ["---"]
    for k, v in fm.items():
        if v is None or v == "":
            lines.append(f"{k}:")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def write_file(path: Path, content: str, dry: bool) -> None:
    if dry:
        log(f"WRITE {path} ({len(content)} bytes)", dry=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    log(f"WRITE {path}")


def move_file(src: Path, dst: Path, dry: bool) -> None:
    if dry:
        log(f"MOVE  {src} -> {dst}", dry=True)
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    log(f"MOVE  {src} -> {dst}")


def remove_path(path: Path, dry: bool) -> None:
    if dry:
        log(f"RM    {path}", dry=True)
        return
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()
    log(f"RM    {path}")


# ---------- gitignore ----------

def update_gitignore(root: Path, dry: bool, yes: bool) -> None:
    gi = root / ".gitignore"
    existing = gi.read_text() if gi.exists() else ""
    needed = [e for e in GITIGNORE_ENTRIES if e not in existing.splitlines()]
    if not needed:
        return
    if not gi.exists():
        log(f"create .gitignore with {len(needed)} entries")
    else:
        log(f"append {len(needed)} entries to .gitignore: {needed}")
    if not confirm("Update .gitignore?", yes):
        log("skipped .gitignore update")
        return
    new_text = existing.rstrip() + "\n\n# dev-guideline\n" + "\n".join(needed) + "\n"
    if not existing:
        new_text = "# dev-guideline\n" + "\n".join(needed) + "\n"
    if dry:
        log(f"WRITE {gi} (+{len(needed)} entries)", dry=True)
    else:
        gi.write_text(new_text)
        log(f"updated {gi}")


# ---------- template scaffolding ----------

def load_template(name: str) -> str:
    return (ASSETS / name).read_text().replace("__DATE__", TODAY)


def scaffold_tree(root: Path, dry: bool) -> None:
    agent = root / ".agent"
    for sub in ["TASKS/active", "TASKS/completed", "TASKS/archived", ".tmp", "data"]:
        d = agent / sub
        if dry:
            log(f"MKDIR {d}", dry=True)
        else:
            d.mkdir(parents=True, exist_ok=True)
            log(f"MKDIR {d}")

    memory = agent / "MEMORY.md"
    if not memory.exists():
        write_file(memory, load_template("memory-template.md"), dry)

    progress = agent / "PROGRESS.md"
    if not progress.exists():
        write_file(progress, load_template("progress-template.md"), dry)


# ---------- task normalization ----------

def normalize_task(path: Path, default_status: str, dry: bool) -> dict:
    """Return a report dict describing fixes applied."""
    text = path.read_text()
    fm, body = parse_frontmatter(text)
    fixes: list[str] = []

    slug = path.stem
    mtime = dt.date.fromtimestamp(path.stat().st_mtime).isoformat()

    # extract title from first H1 if missing
    title = fm.get("title")
    if not title:
        for line in body.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
    if not title:
        title = slug.replace("-", " ").title()

    normalized = {
        "title": title,
        "slug": slug,
        "created": fm.get("created", mtime),
        "updated": fm.get("updated", TODAY),
        "status": fm.get("status", default_status),
        "owner": fm.get("owner", "unknown"),
    }
    if fm.get("external_ref"):
        normalized["external_ref"] = fm["external_ref"]
    else:
        normalized["external_ref"] = ""

    for key in REQUIRED_TASK_KEYS:
        if key not in fm:
            fixes.append(f"added {key}")

    # ensure a Resume block exists
    has_resume = re.search(r"^##\s+Resume\b", body, re.MULTILINE) is not None
    if not has_resume:
        body = body.rstrip() + "\n\n## Resume\n**Last touched:** " + TODAY + \
            "\n**Next step:** <fill in on next session>\n**Context:**\n**Files in flight:**\n"
        fixes.append("added Resume block")

    new_text = render_frontmatter(normalized) + body
    if new_text != text:
        if dry:
            log(f"NORMALIZE {path} ({', '.join(fixes) or 'frontmatter rewrite'})", dry=True)
        else:
            path.write_text(new_text)
            log(f"NORMALIZE {path} ({', '.join(fixes) or 'frontmatter rewrite'})")
    return {"path": str(path), "fixes": fixes}


# ---------- migrate ----------

def migrate(root: Path, dry: bool, yes: bool) -> dict:
    ai = root / ".ai"
    agent = root / ".agent"
    report = {"moved": [], "normalized": [], "deleted_legacy": False}

    log("=== migrate: .ai/ -> .agent/ ===")
    scaffold_tree(root, dry)

    # move TASKS
    for sub in ["active", "completed"]:
        src_dir = ai / "TASKS" / sub
        dst_dir = agent / "TASKS" / sub
        if src_dir.exists():
            for f in sorted(src_dir.glob("*.md")):
                dst = dst_dir / f.name
                if dst.exists():
                    if not confirm(f"{dst} exists. Overwrite?", yes):
                        log(f"skip  {f}")
                        continue
                move_file(f, dst, dry)
                report["moved"].append(str(dst))
                if not dry:
                    normalize_task(dst, default_status=("completed" if sub == "completed" else "in_progress"), dry=dry)

    # memory.md -> MEMORY.md (rewrite header)
    legacy_mem = ai / "memory.md"
    new_mem = agent / "MEMORY.md"
    if legacy_mem.exists():
        old_text = legacy_mem.read_text()
        _fm, body = parse_frontmatter(old_text)
        # strip a leading single-# heading (legacy "# Memory" etc.) to avoid double headings
        body = re.sub(r"^\s*#\s+[^\n]+\n+", "", body, count=1)
        entry_count = len(re.findall(r"^##\s+\d{4}-\d{2}-\d{2}", body, re.MULTILINE))
        merged = render_frontmatter({"last_updated": TODAY, "entries": entry_count}) + \
            "\n# Project Memory\n\n" + body.strip() + "\n"
        if dry:
            log(f"WRITE {new_mem} (merged from legacy memory.md, {entry_count} entries)", dry=True)
            log(f"RM    {legacy_mem}", dry=True)
        else:
            new_mem.write_text(merged)
            legacy_mem.unlink()
            log(f"merged {legacy_mem} -> {new_mem} ({entry_count} entries)")
        report["moved"].append(str(new_mem))

    # credentials, data, .tmp pass-through
    for name in ["credentials.json", "data", ".tmp"]:
        src = ai / name
        dst = agent / name
        if src.exists() and not dst.exists():
            move_file(src, dst, dry)

    update_gitignore(root, dry, yes)

    # delete .ai/ if empty
    if ai.exists() and not dry:
        remaining = [p for p in ai.rglob("*") if p.is_file()]
        if not remaining:
            if confirm(f"Delete now-empty {ai}?", yes):
                remove_path(ai, dry)
                report["deleted_legacy"] = True
        else:
            log(f"{ai} still contains: {[str(p.relative_to(ai)) for p in remaining[:5]]}")

    return report


# ---------- bootstrap ----------

def bootstrap(root: Path, dry: bool, yes: bool) -> dict:
    log("=== bootstrap: scaffolding .agent/ ===")
    scaffold_tree(root, dry)
    update_gitignore(root, dry, yes)
    log("")
    log("NEXT STEP (for the agent):")
    log("  Seed .agent/MEMORY.md and .agent/PROGRESS.md from project knowledge.")
    log("  Read CLAUDE.md / AGENTS.md / README.md / package.json / git log,")
    log("  then draft entries. Show the user before finalizing.")
    return {"scaffolded": True}


# ---------- repair ----------

def repair(root: Path, dry: bool, yes: bool) -> dict:
    log("=== repair: verifying .agent/ ===")
    agent = root / ".agent"
    issues: list[str] = []

    scaffold_tree(root, dry)  # creates any missing dirs/files

    # lint every task
    task_reports = []
    for sub in ["active", "completed", "archived"]:
        for f in sorted((agent / "TASKS" / sub).glob("*.md")):
            r = normalize_task(f, default_status=("completed" if sub != "active" else "in_progress"), dry=dry)
            if r["fixes"]:
                task_reports.append(r)

    # memory thresholds
    memory = agent / "MEMORY.md"
    if memory.exists():
        text = memory.read_text()
        _fm, body = parse_frontmatter(text)
        line_count = len(text.splitlines())
        entry_count = len(re.findall(r"^##\s+\d{4}-\d{2}-\d{2}", body, re.MULTILINE))
        if line_count > 150 or entry_count > 40:
            issues.append(f"MEMORY exceeds compaction threshold ({line_count} lines, {entry_count} entries). Run /dev-guideline compact.")

    update_gitignore(root, dry, yes)

    log("")
    log(f"repair complete. {len(task_reports)} tasks normalized, {len(issues)} issues.")
    for i in issues:
        log(f"  ! {i}")
    return {"task_reports": task_reports, "issues": issues}


# ---------- main ----------

def main() -> int:
    ap = argparse.ArgumentParser(description="dev-guideline setup")
    ap.add_argument("--root", default=".", help="project root (default: cwd)")
    ap.add_argument("--dry-run", action="store_true", help="show plan without changes")
    ap.add_argument("--yes", action="store_true", help="skip confirmations")
    mode_group = ap.add_mutually_exclusive_group()
    mode_group.add_argument("--migrate", action="store_true")
    mode_group.add_argument("--bootstrap", action="store_true")
    mode_group.add_argument("--repair", action="store_true")
    ap.add_argument("--json", action="store_true", help="emit JSON report at end")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    if args.migrate:
        mode = "migrate"
    elif args.bootstrap:
        mode = "bootstrap"
    elif args.repair:
        mode = "repair"
    else:
        mode = detect_mode(root)

    log(f"project: {root}")
    log(f"mode:    {mode}")
    if args.dry_run:
        log("(dry-run — no files will be changed)")
    log("")

    if mode == "bootstrap" and not project_looks_active(root):
        log("note: this directory has no obvious project signals (CLAUDE.md / package.json / etc).")
        if not confirm("Bootstrap anyway?", args.yes):
            log("aborted.")
            return 1

    if mode in ("migrate", "migrate-merge"):
        report = migrate(root, args.dry_run, args.yes)
    elif mode == "bootstrap":
        report = bootstrap(root, args.dry_run, args.yes)
    elif mode == "repair":
        report = repair(root, args.dry_run, args.yes)
    else:
        log(f"unknown mode: {mode}")
        return 2

    if args.json:
        print(json.dumps({"mode": mode, "root": str(root), "report": report}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
