#!/usr/bin/env python3
"""
preview.py — local browser dashboard for .agent/ project state.

Three-column layout:
  - Left: TASKS list (active, blocked, recent completed)
  - Center: selected task rendered as markdown
  - Right: PROGRESS + MEMORY summaries

Live-reload via SSE that watches .agent/ mtime.
Read-only. Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import threading
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets" / "preview"


def _read(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError:
        return ""


def parse_fm(text: str) -> tuple[dict, str]:
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


def extract_next_step(body: str) -> str:
    m = re.search(r"\*\*Next step:\*\*\s*(.+)", body)
    return m.group(1).strip() if m else ""


def list_tasks(root: Path) -> dict:
    out: dict = {"active": [], "completed": [], "archived": []}
    base = root / ".agent" / "TASKS"
    for bucket in ("active", "completed", "archived"):
        d = base / bucket
        if not d.exists():
            continue
        # alphabetical by title (fallback to slug)
        entries = []
        for f in d.glob("*.md"):
            fm, body = parse_fm(_read(f))
            entries.append({
                "slug": fm.get("slug", f.stem),
                "title": fm.get("title", f.stem),
                "status": fm.get("status", bucket),
                "updated": fm.get("updated", ""),
                "next_step": extract_next_step(body),
                "bucket": bucket,
            })
        entries.sort(key=lambda e: (e["title"] or e["slug"]).lower())
        out[bucket] = entries
    return out


def get_task(root: Path, bucket: str, slug: str) -> dict | None:
    safe = re.sub(r"[^a-zA-Z0-9_-]", "", slug)
    if bucket not in ("active", "completed", "archived"):
        return None
    f = root / ".agent" / "TASKS" / bucket / f"{safe}.md"
    if not f.exists():
        return None
    fm, body = parse_fm(_read(f))
    return {
        "slug": safe,
        "bucket": bucket,
        "frontmatter": fm,
        "body": body,
        "raw": _read(f),
    }


_PROGRESS_KEYWORDS = {
    "shipped":     ["shipped", "done", "complete", "released", "delivered", "launched", "deployed"],
    "in_progress": ["progress", "wip", "active", "doing", "current", "ongoing"],
    "pending":     ["pending", "planned", "plan", "backlog", "todo", "to do", "to-do", "future", "next", "upcoming"],
}


def _classify_progress_heading(h: str) -> str | None:
    s = h.lower()
    # check most specific first (in_progress before "progress" alone would be ambiguous,
    # but "in progress" / "wip" land in in_progress; "planned"/"pending" in pending)
    for bucket, kws in _PROGRESS_KEYWORDS.items():
        if any(kw in s for kw in kws):
            return bucket
    return None


def progress_summary(root: Path) -> dict:
    f = root / ".agent" / "PROGRESS.md"
    if not f.exists():
        return {"raw": "", "shipped": 0, "in_progress": 0, "pending": 0,
                "last_updated": "", "lines": 0, "chars": 0}
    text = _read(f)
    fm, body = parse_fm(text)

    counts = {"shipped": 0, "in_progress": 0, "pending": 0}

    # find every ## section and classify
    section_re = re.compile(r"^##\s+(.+?)\s*\n(.*?)(?=^##\s|\Z)", re.MULTILINE | re.DOTALL)
    for m in section_re.finditer(body):
        heading, content = m.group(1), m.group(2)
        bucket = _classify_progress_heading(heading)
        if bucket is None:
            continue
        checked = len(re.findall(r"^\s*-\s+\[[xX]\]", content, re.MULTILINE))
        unchecked = len(re.findall(r"^\s*-\s+\[ \]", content, re.MULTILINE))
        if bucket == "shipped":
            # Shipped section: count everything (treat unchecked as still counted toward bucket)
            counts["shipped"] += checked + unchecked
        elif bucket == "in_progress":
            # In-progress section: only unchecked are still in progress; checked → shipped
            counts["in_progress"] += unchecked
            counts["shipped"] += checked
        elif bucket == "pending":
            counts["pending"] += unchecked
            counts["shipped"] += checked  # a [x] in pending = done out of order

    return {
        "raw": text,
        "shipped":     counts["shipped"],
        "in_progress": counts["in_progress"],
        "pending":     counts["pending"],
        "last_updated": fm.get("last_updated", ""),
        "lines": len(text.splitlines()),
        "chars": len(text),
    }


def memory_summary(root: Path) -> dict:
    f = root / ".agent" / "MEMORY.md"
    if not f.exists():
        return {"raw": "", "entries": 0, "lines": 0, "chars": 0,
                "last_updated": "", "over_threshold": False}
    text = _read(f)
    fm, body = parse_fm(text)
    # Any ## heading counts as an entry — be permissive so users aren't forced into
    # a YYYY-MM-DD heading format.
    entries = len(re.findall(r"^##\s+\S", body, re.MULTILINE))
    lines = len(text.splitlines())
    return {
        "raw": text,
        "entries": entries,
        "lines": lines,
        "chars": len(text),
        "last_updated": fm.get("last_updated", ""),
        "over_threshold": entries > 40 or lines > 150,
    }


_KNOWN_AGENT_PATHS = {
    "TASKS", "MEMORY.md", "PROGRESS.md",
    ".tmp", "data", "credentials.json",
}


def other_items(root: Path) -> list[dict]:
    agent = root / ".agent"
    if not agent.exists():
        return []
    items: list[dict] = []
    for entry in sorted(agent.iterdir()):
        if entry.name in _KNOWN_AGENT_PATHS or entry.name.startswith("."):
            continue
        if entry.is_file():
            items.append({
                "name": entry.name,
                "kind": "file",
                "size": entry.stat().st_size,
                "ext": entry.suffix,
            })
        elif entry.is_dir():
            files = [p for p in entry.iterdir() if p.is_file()]
            items.append({
                "name": entry.name,
                "kind": "dir",
                "count": len(files),
                "files": sorted([p.name for p in files])[:50],
            })
    return items


def get_other_file(root: Path, name: str) -> dict | None:
    safe = re.sub(r"[^a-zA-Z0-9._/-]", "", name)
    parts = safe.split("/")
    if any(p in _KNOWN_AGENT_PATHS or p.startswith(".") or p == "" for p in parts):
        return None
    f = root / ".agent" / Path(*parts)
    if not f.exists() or not f.is_file():
        return None
    try:
        text = f.read_text()
    except UnicodeDecodeError:
        return {"name": safe, "raw": "(binary file)", "chars": f.stat().st_size, "lines": 0}
    return {"name": safe, "raw": text, "chars": len(text), "lines": len(text.splitlines())}


def latest_mtime(root: Path) -> float:
    agent = root / ".agent"
    if not agent.exists():
        return 0.0
    latest = 0.0
    for f in agent.rglob("*.md"):
        try:
            latest = max(latest, f.stat().st_mtime)
        except OSError:
            pass
    return latest


# ---------- HTTP handler ----------

class Handler(BaseHTTPRequestHandler):
    project_root: Path = Path(".")

    def log_message(self, format: str, *args) -> None:  # quiet
        return

    def _send_json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_text(self, text: str, content_type: str = "text/plain", status: int = 200) -> None:
        data = text.encode()
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: Path) -> None:
        if not path.exists():
            self.send_error(404)
            return
        ctype, _ = mimetypes.guess_type(str(path))
        ctype = ctype or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/" or path == "/index.html":
            self._send_file(ASSETS / "index.html")
            return
        if path == "/styles.css":
            self._send_file(ASSETS / "styles.css")
            return
        if path == "/app.js":
            self._send_file(ASSETS / "app.js")
            return
        if path == "/marked.min.js":
            self._send_file(ASSETS / "marked.min.js")
            return
        if path == "/api/state":
            root = Handler.project_root
            self._send_json({
                "project": str(root),
                "project_name": root.name,
                "has_agent": (root / ".agent").exists(),
                "tasks": list_tasks(root),
                "progress": progress_summary(root),
                "memory": memory_summary(root),
                "other": other_items(root),
                "mtime": latest_mtime(root),
            })
            return
        if path.startswith("/api/other/"):
            name = path[len("/api/other/"):]
            item = get_other_file(Handler.project_root, name)
            if item is None:
                self.send_error(404)
                return
            self._send_json(item)
            return
        if path.startswith("/api/task/"):
            parts = path[len("/api/task/"):].split("/", 1)
            if len(parts) != 2:
                self.send_error(400)
                return
            bucket, slug = parts
            task = get_task(Handler.project_root, bucket, slug)
            if task is None:
                self.send_error(404)
                return
            self._send_json(task)
            return
        if path == "/api/events":
            # SSE — push mtime updates
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            last = 0.0
            try:
                while True:
                    cur = latest_mtime(Handler.project_root)
                    if cur != last:
                        last = cur
                        payload = json.dumps({"mtime": cur})
                        self.wfile.write(f"data: {payload}\n\n".encode())
                        self.wfile.flush()
                    time.sleep(1.0)
            except (BrokenPipeError, ConnectionResetError):
                return
        self.send_error(404)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="project root (default: cwd)")
    ap.add_argument("--port", type=int, default=7878)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--no-open", action="store_true", help="don't auto-open browser")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    Handler.project_root = root

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}/"
    print(f"dev-guideline preview — {url}")
    print(f"project: {root}")
    if not (root / ".agent").exists():
        print("note: no .agent/ dir in this project. Run /dev-guideline setup first.")
    print("ctrl-c to stop.")

    if not args.no_open:
        threading.Thread(target=lambda: (time.sleep(0.5), webbrowser.open(url)), daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
