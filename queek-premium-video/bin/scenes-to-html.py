#!/usr/bin/env python3
"""scenes-to-html.py — render a queek-premium-video scene-design layer
(`scenes-design.md`) as a single-file interactive design-review page.

This is the Design gate surface (Flow step 4): the reviewer approves how each
scene LOOKS and MOVES before any composition HTML exists. Each scene renders as
a wireframe (boxes on a grid, generated from a text layout spec — NOT built
HTML), its archetype + motion + type spec, a 6-dimension scorecard with fixes,
the reference it derives from, and a comment thread with APPROVE / REVISE +
markdown export the reviewer pastes back to resolve the gate.

Self-contained (inline CSS/JS, no external requests) so it works from file://
and offline. Stdlib only. Mirrors the review shell of plan-to-html.py
intentionally; if a third consumer appears, factor the shell into a module.

Usage:
  scenes-to-html.py works/<slug>/scenes-design.md          -> .../SCENES.html
  scenes-to-html.py scenes-design.md -o review.html --title "Refunds — design"
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- inline md

RE_CODE = re.compile(r"`([^`]+)`")
RE_BOLD = re.compile(r"\*\*([^*]+)\*\*")
RE_HEX = re.compile(r"(?<![\w&;])#([0-9A-Fa-f]{6})\b")


def esc(text: str) -> str:
    return html.escape(str(text), quote=False)


def attr(text: str) -> str:
    return html.escape(str(text), quote=True)


def inline(text: str) -> str:
    out = esc(text)
    out = RE_CODE.sub(r"<code>\1</code>", out)
    out = RE_BOLD.sub(r"<strong>\1</strong>", out)
    out = RE_HEX.sub(r'<span class="sw" style="background:#\1"></span>#\1', out)
    return out


def slugify(text: str, seen: set) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    s = re.sub(r"[\s_]+", "-", s) or "scene"
    base, n = s, 2
    while s in seen:
        s = f"{base}-{n}"
        n += 1
    seen.add(s)
    return s


# ---------------------------------------------------------------- parse

DIM_NAMES = [
    "Focal idea",
    "Motion meaning",
    "Color discipline",
    "Type hierarchy",
    "Composition",
    "Timing & energy",
]
FIELD_KEYS = ["archetype", "derives", "focal", "motion", "type"]
HEADER_KEYS = [
    ("signature", r"\*\*Signature(?:\s*device)?:?\*\*"),
    ("arc", r"\*\*Arc:?\*\*"),
    ("concept", r"\*\*Concept:?\*\*"),
]
SCENE_H = re.compile(r"^##\s+(S\d+)\b\s*[·.:-]?\s*(.*?)\s*(\(([^)]*)\))?\s*$")
REGION_RE = re.compile(
    r'^(hero|pill|label|text|media|box)\s+"([^"]*)"\s*:\s*(.+?)\s*$', re.I
)


def parse_layout(block_lines):
    cols, rows, aspect = 12, 8, "16/9"
    regions, unplaced = [], []
    for raw in block_lines:
        line = raw.strip()
        if not line:
            continue
        h = re.match(
            r"^cols:\s*(\d+)?.*?(?:rows:\s*(\d+))?.*?(?:aspect:\s*([\d]+\s*/\s*[\d]+))?",
            line,
            re.I,
        )
        if line.lower().startswith("cols:") and h:
            if h.group(1):
                cols = max(1, min(48, int(h.group(1))))
            if h.group(2):
                rows = max(1, min(48, int(h.group(2))))
            if h.group(3):
                aspect = h.group(3).replace(" ", "")
            continue
        m = REGION_RE.match(line)
        if not m:
            unplaced.append(line)
            continue
        kind, label, place = m.group(1).lower(), m.group(2), m.group(3)
        focal = bool(re.search(r"\bfocal\b", place, re.I))
        muted = bool(re.search(r"\bmuted\b", place, re.I))
        cm = re.search(r"c(\d+)(?:\s*-\s*(\d+))?", place, re.I)
        rm = re.search(r"r(\d+)(?:\s*-\s*(\d+))?", place, re.I)
        if not cm and not rm:
            unplaced.append(line)
            continue
        ca = int(cm.group(1)) if cm else 1
        cb = int(cm.group(2)) if (cm and cm.group(2)) else ca
        ra = int(rm.group(1)) if rm else 1
        rb = int(rm.group(2)) if (rm and rm.group(2)) else ra
        ca, cb = sorted((max(1, min(cols, ca)), max(1, min(cols, cb))))
        ra, rb = sorted((max(1, min(rows, ra)), max(1, min(rows, rb))))
        regions.append(
            {
                "kind": kind,
                "label": label,
                "ca": ca,
                "cb": cb,
                "ra": ra,
                "rb": rb,
                "focal": focal,
                "muted": muted,
            }
        )
    return {"cols": cols, "rows": rows, "aspect": aspect,
            "regions": regions, "unplaced": unplaced}


def parse_score(line):
    dims = {}
    for d, v in re.findall(r"(\d)\s*:\s*([0-2])", line):
        dims[int(d)] = int(v)
    if not dims:
        return None
    total = sum(dims.get(i, 0) for i in range(1, 7))
    has_zero = any(dims.get(i, 0) == 0 for i in range(1, 7))
    verdict = "premium" if (total >= 10 and not has_zero) else "rework"
    return {"dims": dims, "total": total, "verdict": verdict, "fixes": {}}


def parse_scenes(text: str):
    lines = text.splitlines()
    title = "Scene design"
    header = {}
    scenes, current = [], None
    in_fence = False
    fence_buf, fence_owner = None, None

    def flush_fence():
        nonlocal fence_buf, fence_owner
        if fence_buf is not None and fence_owner is not None:
            fence_owner["layout"] = parse_layout(fence_buf)
        fence_buf, fence_owner = None, None

    for raw in lines:
        s = raw.strip()
        if s.startswith("```"):
            if in_fence:
                in_fence = False
                flush_fence()
            else:
                in_fence = True
                # a layout fence belongs to the open scene
                if "layout" in s.lower() or current is not None:
                    fence_buf, fence_owner = [], current
                else:
                    fence_buf, fence_owner = [], None
            continue
        if in_fence:
            if fence_buf is not None:
                fence_buf.append(raw)
            continue

        m = re.match(r"^#\s+(.*)$", s)
        if m and title == "Scene design":
            title = m.group(1).strip()
            continue
        m = SCENE_H.match(s)
        if m:
            flush_fence()
            current = {
                "num": m.group(1),
                "name": (m.group(2) or "").strip(),
                "span": (m.group(4) or "").strip(),
                "fields": {},
                "layout": None,
                "score": None,
            }
            scenes.append(current)
            continue
        if current is None:
            for key, pat in HEADER_KEYS:
                hm = re.match(rf"^(?:[-*]\s+)?{pat}\s*(.+)$", s)
                if hm and key not in header:
                    header[key] = hm.group(1).strip(" ·")
            continue
        # within a scene: fields / score / fix
        fm = re.match(r"^[-*]\s*([A-Za-z][\w &/]*?)\s*:\s*(.+)$", s)
        if fm and fm.group(1).strip().lower() in FIELD_KEYS:
            current["fields"][fm.group(1).strip().lower()] = fm.group(2).strip()
            continue
        sm = re.match(r"^Score\s*:\s*(.+)$", s, re.I)
        if sm:
            current["score"] = parse_score(sm.group(1))
            continue
        xm = re.match(r"^Fix\s*(\d)\s*:\s*(.+)$", s, re.I)
        if xm and current["score"]:
            current["score"]["fixes"][int(xm.group(1))] = xm.group(2).strip()
            continue

    flush_fence()
    return title, header, scenes


# ---------------------------------------------------------------- derives

IMG_EXT = {"png", "jpg", "jpeg", "webp", "gif", "svg"}


def derives_widget(value, plan_dir, out_dir):
    """Render the Derives field: a screenshot path -> preview chip; an
    archetype:/ref: token -> labelled tag; anything else -> inline text."""
    v = value.strip()
    low = v.lower()
    if low.startswith("archetype:"):
        return f'<span class="der der-arch">archetype · {esc(v.split(":",1)[1].strip())}</span>'
    if low.startswith("ref:"):
        return f'<span class="der der-ref">reference · {esc(v.split(":",1)[1].strip())}</span>'
    pm = re.match(r'([\w~][\w.\-/]*\.(?:png|jpe?g|webp|gif|svg))\b', v, re.I)
    if pm:
        token = pm.group(1)
        roots = [plan_dir, *list(plan_dir.parents)[:3], Path.cwd()]
        found = None
        if token.startswith("~"):
            cand = Path(token).expanduser().resolve()
            found = cand if cand.is_file() else None
        else:
            for r in roots:
                cand = (r / token).resolve()
                if cand.is_file():
                    found = cand
                    break
        name = esc(Path(token).name)
        if found:
            rel = attr(os.path.relpath(found, out_dir))
            return (f'<a class="der der-img" href="{rel}" data-view="img">'
                    f'▣ {name}</a>')
        return f'<span class="der der-miss">{name}</span>'
    return f'<span class="der">{inline(v)}</span>'


# ---------------------------------------------------------------- render

def render_wireframe(layout):
    if not layout or (not layout["regions"] and not layout["unplaced"]):
        return '<div class="wf-empty">No layout spec for this scene.</div>'
    cols, rows = layout["cols"], layout["rows"]
    cells = []
    for reg in layout["regions"]:
        cls = f'wf-r wf-{reg["kind"]}'
        if reg["focal"]:
            cls += " wf-focal"
        if reg["muted"]:
            cls += " wf-muted"
        style = (
            f'grid-column:{reg["ca"]}/{reg["cb"]+1};'
            f'grid-row:{reg["ra"]}/{reg["rb"]+1}'
        )
        badge = '<i class="wf-foc" title="focal point"></i>' if reg["focal"] else ""
        cells.append(
            f'<div class="{cls}" style="{style}">{badge}'
            f'<span>{esc(reg["label"])}</span></div>'
        )
    grid = (
        f'<div class="wf" style="aspect-ratio:{attr(layout["aspect"])};'
        f'grid-template-columns:repeat({cols},1fr);'
        f'grid-template-rows:repeat({rows},1fr)">{"".join(cells)}</div>'
    )
    if layout["unplaced"]:
        items = "".join(f"<li>{esc(u)}</li>" for u in layout["unplaced"])
        grid += (
            f'<div class="wf-unplaced"><b>Unplaced</b> — fix placement before '
            f'the gate:<ul>{items}</ul></div>'
        )
    return grid


def render_scorecard(score):
    if not score:
        return '<div class="sc-none">No score yet.</div>'
    rows = []
    for i in range(1, 7):
        v = score["dims"].get(i, 0)
        dots = "".join(
            f'<span class="dot {"on" if j < v else ""}"></span>' for j in range(2)
        )
        fix = score["fixes"].get(i)
        fixhtml = f'<div class="sc-fix">{inline(fix)}</div>' if fix else ""
        cls = "sc-row" + (" sc-low" if v < 2 else "")
        rows.append(
            f'<div class="{cls}"><span class="sc-n">{i}</span>'
            f'<span class="sc-name">{DIM_NAMES[i-1]}</span>'
            f'<span class="sc-dots">{dots}</span>'
            f'<span class="sc-v">{v}</span></div>{fixhtml}'
        )
    vcls = "ok" if score["verdict"] == "premium" else "warn"
    badge = (
        f'<div class="sc-total"><span class="sc-sum">{score["total"]}/12</span>'
        f'<span class="sc-badge {vcls}">{score["verdict"]}</span></div>'
    )
    return f'<div class="scorecard">{"".join(rows)}{badge}</div>'


# ---------------------------------------------------------------- page

CSS = r"""
:root{
  --paper:#F7F5F0;--surface:#FFFEFB;--ink:#1C1A15;--muted:#6F6A5E;
  --line:#E5E0D4;--line2:#D8D2C2;--accent:#0E6B43;--accent-ink:#0A4D31;
  --accent-soft:#EAF3ED;--gold:#8A6D1F;--gold-soft:#F6EFDB;--danger:#A33A2A;
  --danger-soft:#F7E9E4;
  --mono:ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace;
  --serif:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;
  --sans:-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:24px}
body{margin:0;background:var(--paper);color:var(--ink);font:13.5px/1.6 var(--sans);
  -webkit-font-smoothing:antialiased}
a{color:var(--accent-ink)}
:is(a,button,summary,[tabindex]):focus-visible{outline:2px solid var(--accent);
  outline-offset:2px;border-radius:4px}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}*,*::before,*::after{transition:none!important;animation:none!important}
}
.layout{display:grid;grid-template-columns:236px minmax(0,1fr);max-width:1240px;
  margin:0 auto;gap:0 44px;padding:0 32px}
.toc{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;
  padding:34px 0 120px;border-right:1px solid var(--line);scrollbar-width:thin}
.toc .brand{font:600 10px/1 var(--sans);letter-spacing:.2em;text-transform:uppercase;
  color:var(--muted);margin:0 0 6px}
.toc .nm{font:700 13.5px/1.35 var(--sans);margin:0 16px 16px 0;overflow-wrap:break-word}
.toc nav{display:flex;flex-direction:column;gap:1px;padding-right:14px}
.toc nav a{display:flex;gap:9px;align-items:baseline;padding:6px 9px;border-radius:7px;
  text-decoration:none;color:var(--muted);font-size:12.5px;line-height:1.3}
.toc nav a .n{font:600 10px/1.4 var(--mono);color:var(--accent);min-width:22px}
.toc nav a:hover{color:var(--ink);background:rgba(0,0,0,.035)}
.toc nav a.active{color:var(--accent-ink);background:var(--accent-soft);font-weight:600}
.toc nav a .vb{margin-left:auto;width:7px;height:7px;border-radius:50%;flex:none;
  align-self:center}
.toc nav a .vb.premium{background:var(--accent)}
.toc nav a .vb.rework{background:var(--gold)}
.toc nav a .cb{margin-left:6px;font:600 10px/1.5 var(--mono);background:var(--gold-soft);
  color:var(--gold);border-radius:9px;padding:0 6px;display:none}
.toc nav a .cb.show{display:inline-block}
main{padding:42px 0 170px;min-width:0}
.eyebrow{font:600 10px/1 var(--sans);letter-spacing:.22em;text-transform:uppercase;
  color:var(--accent);margin:0 0 12px}
h1.title{font:600 29px/1.15 var(--serif);letter-spacing:-.01em;margin:0 0 16px;text-wrap:balance}
.recap{display:flex;flex-wrap:wrap;gap:18px;margin:0 0 14px;padding:14px 18px;
  background:var(--surface);border:1px solid var(--line);border-radius:12px}
.recap div{font-size:13px}
.recap b{display:block;font:600 9.5px/1.5 var(--sans);letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted)}
.chips{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 30px}
.chip{font:600 10.5px/1 var(--sans);letter-spacing:.04em;padding:6px 11px;
  border:1px solid var(--line2);border-radius:999px;background:var(--surface);color:var(--muted)}
.chip.ok{border-color:var(--accent);color:var(--accent-ink);background:var(--accent-soft)}
.chip.warn{border-color:#E3D2A6;color:var(--gold);background:var(--gold-soft)}

/* scene card */
.scene{background:var(--surface);border:1px solid var(--line);border-radius:14px;
  margin:0 0 18px;overflow:hidden;
  box-shadow:0 1px 2px rgba(28,26,21,.04),0 14px 36px -28px rgba(28,26,21,.3)}
.sc-head{display:flex;align-items:center;gap:12px;padding:15px 20px;border-bottom:1px solid var(--line);
  background:linear-gradient(#FDFCFA,#F9F7F1)}
.sc-head .id{font:600 11px/1 var(--mono);color:var(--accent);background:var(--accent-soft);
  border-radius:7px;padding:6px 8px}
.sc-head .ttl{font:600 15px/1.3 var(--sans);letter-spacing:-.01em;flex:1}
.sc-head .span{font:500 11px/1 var(--mono);color:var(--muted)}
.sc-body{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:22px;padding:20px}
.sc-meta dl{margin:0;display:grid;grid-template-columns:74px 1fr;gap:7px 12px}
.sc-meta dt{font:600 9.5px/1.7 var(--sans);letter-spacing:.1em;text-transform:uppercase;
  color:var(--muted)}
.sc-meta dd{margin:0;font-size:13px}
.der{display:inline-flex;align-items:center;gap:5px;font:600 11px/1 var(--sans);
  padding:4px 9px;border:1px solid var(--line2);border-radius:7px;background:var(--paper);
  color:var(--ink)}
.der-arch{color:var(--accent-ink);border-color:#CDE3D6;background:var(--accent-soft)}
.der-ref{color:var(--gold);border-color:#E8DDBC;background:var(--gold-soft)}
.der-img{color:var(--accent-ink);text-decoration:none;cursor:pointer}
.der-img:hover{border-color:var(--accent);background:var(--accent-soft)}
.der-miss{border-style:dashed;color:var(--muted)}

/* wireframe */
.wf-wrap{margin:0}
.wf-cap{font:600 9.5px/1.5 var(--sans);letter-spacing:.12em;text-transform:uppercase;
  color:var(--muted);margin:0 0 8px;display:flex;justify-content:space-between}
.wf{display:grid;gap:3px;width:100%;background:
  repeating-linear-gradient(0deg,transparent,transparent calc(12.5% - 1px),rgba(28,26,21,.04) 12.5%),
  repeating-linear-gradient(90deg,transparent,transparent calc(8.33% - 1px),rgba(28,26,21,.04) 8.33%),
  var(--paper);
  border:1px solid var(--line2);border-radius:10px;padding:3px}
.wf-r{position:relative;display:flex;align-items:center;justify-content:center;
  text-align:center;padding:4px 6px;border:1px solid var(--line2);border-radius:6px;
  background:#fff;overflow:hidden;min-height:0}
.wf-r span{font:500 11px/1.25 var(--sans);color:var(--ink);
  overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:3;
  -webkit-box-orient:vertical}
.wf-hero span{font-weight:700;font-size:13px}
.wf-pill{border-radius:999px;background:var(--accent-soft);border-color:#CDE3D6}
.wf-pill span{font-weight:600;font-size:10px;color:var(--accent-ink)}
.wf-label span{font:600 9px/1.3 var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.wf-media{border-style:dashed;background:repeating-linear-gradient(45deg,#fff,#fff 6px,#FAF8F2 6px,#FAF8F2 12px)}
.wf-media span{color:var(--muted)}
.wf-muted{opacity:.5}
.wf-focal{border:2px solid var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}
.wf-foc{position:absolute;top:4px;right:4px;width:7px;height:7px;border-radius:50%;
  background:var(--accent)}
.wf-empty,.wf-unplaced{font-size:12px;color:var(--muted);padding:10px 0}
.wf-unplaced{margin-top:10px;background:var(--danger-soft);border:1px solid #E8CABF;
  border-radius:9px;padding:9px 12px;color:#7a2c1e}
.wf-unplaced b{color:var(--danger)}
.wf-unplaced ul{margin:5px 0 0;padding-left:18px}

/* scorecard */
.scorecard{margin-top:14px}
.sc-row{display:flex;align-items:center;gap:10px;padding:5px 0}
.sc-low .sc-name{color:var(--danger)}
.sc-n{font:600 10px/1 var(--mono);color:var(--muted);min-width:12px}
.sc-name{flex:1;font-size:12.5px}
.sc-dots{display:flex;gap:3px}
.dot{width:8px;height:8px;border-radius:50%;background:var(--line2)}
.dot.on{background:var(--accent)}
.sc-low .dot.on{background:var(--gold)}
.sc-v{font:600 11px/1 var(--mono);color:var(--muted);min-width:12px;text-align:right}
.sc-fix{font-size:11.5px;color:#7a2c1e;background:var(--danger-soft);border:1px solid #EAD3CB;
  border-radius:7px;padding:6px 10px;margin:2px 0 6px 22px}
.sc-total{display:flex;align-items:center;gap:10px;margin-top:10px;padding-top:11px;
  border-top:1px solid var(--line)}
.sc-sum{font:600 15px/1 var(--serif);color:var(--ink)}
.sc-badge{font:600 10px/1 var(--sans);letter-spacing:.08em;text-transform:uppercase;
  padding:5px 9px;border-radius:999px}
.sc-badge.ok{background:var(--accent);color:#F8F6F0}
.sc-badge.warn{background:var(--gold-soft);color:var(--gold);border:1px solid #E3D2A6}
.sc-none{font-size:12px;color:var(--muted)}
.sc-meta h4{font:600 9.5px/1.5 var(--sans);letter-spacing:.12em;text-transform:uppercase;
  color:var(--muted);margin:0 0 10px}

/* comments (mirrors plan review shell) */
.cwrap{padding:14px 20px 16px;background:#FAF8F2;border-top:1px dashed var(--line2)}
.clabel{font:600 9.5px/1 var(--sans);letter-spacing:.16em;text-transform:uppercase;
  color:var(--muted);margin:0 0 10px;display:flex;align-items:center;gap:8px}
.clabel::before{content:'';width:7px;height:7px;border-radius:50%;background:var(--gold)}
.cmt{background:var(--surface);border:1px solid var(--line);border-radius:10px;
  padding:9px 13px;margin:0 0 8px;font-size:13px;position:relative}
.cmt .q{border:1px solid #E8DDBC;background:var(--gold-soft);border-radius:7px;
  padding:5px 10px;margin:0 0 7px;color:#6b5618;font-size:11.5px;font-style:italic}
.cmt .meta{font:500 10px/1 var(--sans);color:var(--muted);margin-top:7px}
.cmt .del{position:absolute;top:7px;right:10px;border:0;background:none;color:var(--line2);
  font:600 14px/1 var(--sans);cursor:pointer}
.cmt .del:hover{color:var(--danger)}
.cform{display:flex;flex-direction:column;gap:8px}
.cform textarea{resize:vertical;min-height:54px;border:1px solid var(--line2);border-radius:10px;
  padding:9px 12px;font:13px/1.5 var(--sans);background:var(--surface);color:var(--ink)}
.cform textarea:focus{outline:2px solid var(--accent);outline-offset:-1px;border-color:transparent}
.cform .row{display:flex;justify-content:flex-end}
.cform button{font:600 11.5px/1 var(--sans);padding:8px 15px;border:0;border-radius:8px;
  background:var(--ink);color:#F8F6F0;cursor:pointer}
.cform button:hover{background:var(--accent-ink)}

#qpill{position:absolute;z-index:60;display:none;font:600 12px/1 var(--sans);
  background:var(--ink);color:#F8F6F0;border-radius:999px;padding:8px 13px;cursor:pointer;
  box-shadow:0 8px 24px -8px rgba(0,0,0,.45)}
#lb{position:fixed;inset:0;z-index:80;background:rgba(24,22,17,.86);display:flex;
  flex-direction:column;align-items:center;justify-content:center;gap:12px;padding:40px}
#lb[hidden]{display:none}
#lbfig{margin:0;max-width:min(1100px,92vw);max-height:84vh}
#lbfig img{max-width:100%;max-height:84vh;border-radius:10px;
  box-shadow:0 32px 80px -24px rgba(0,0,0,.6)}
#lbcap{font:600 12px/1 var(--sans);color:#D9D4C7}
#lbclose{position:absolute;top:18px;right:22px;border:0;background:rgba(248,246,240,.12);
  color:#F8F6F0;font:300 22px/1 var(--sans);width:40px;height:40px;border-radius:50%;cursor:pointer}

#bar{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);z-index:50;display:flex;
  align-items:center;gap:13px;background:var(--surface);border:1px solid var(--line2);
  border-radius:999px;padding:9px 11px 9px 19px;
  box-shadow:0 6px 18px -4px rgba(28,26,21,.18),0 24px 60px -24px rgba(28,26,21,.35)}
#bar .cnt{font:600 12px/1 var(--sans);color:var(--muted);white-space:nowrap}
#bar .cnt b{color:var(--ink);font-size:13.5px}
#bar .verdict{display:flex;background:#F1EEE5;border-radius:999px;padding:3px}
#bar .verdict button{font:700 10.5px/1 var(--sans);letter-spacing:.06em;border:0;cursor:pointer;
  border-radius:999px;padding:8px 12px;background:none;color:var(--muted)}
#bar .verdict button.on-approve{background:var(--accent);color:#F8F6F0}
#bar .verdict button.on-revise{background:var(--danger);color:#F8F6F0}
#bar .act{font:600 11.5px/1 var(--sans);border:0;border-radius:999px;padding:10px 15px;
  cursor:pointer;background:var(--ink);color:#F8F6F0;white-space:nowrap}
#bar .act.ghost{background:none;border:1px solid var(--line2);color:var(--muted);padding:9px 12px}
#toast{position:fixed;bottom:84px;left:50%;transform:translateX(-50%);z-index:55;
  background:var(--accent-ink);color:#F8F6F0;font:600 12px/1 var(--sans);border-radius:9px;
  padding:11px 16px;opacity:0;pointer-events:none;transition:.25s}
#toast.show{opacity:1}
.sw{display:inline-block;width:11px;height:11px;border-radius:50%;
  border:1px solid rgba(0,0,0,.18);margin:0 4px 0 1px;transform:translateY(1px)}

@media (max-width:980px){
  body{font-size:14px}
  .layout{grid-template-columns:1fr;padding:0 18px}
  .toc{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line);padding:22px 0 12px}
  .toc nav{flex-direction:row;flex-wrap:wrap}
  .sc-body{grid-template-columns:1fr}
  h1.title{font-size:24px}
  #bar{width:calc(100% - 24px);justify-content:space-between;gap:8px;padding-left:14px}
}
"""

JS = r"""
(function () {
  'use strict';
  var KEY = 'scenesreview:' + (document.body.getAttribute('data-plan') || 'scenes');
  function load(){try{return JSON.parse(localStorage.getItem(KEY))||{comments:[],verdict:''};}
    catch(e){return{comments:[],verdict:''};}}
  function save(s){try{localStorage.setItem(KEY,JSON.stringify(s));}catch(e){}}
  var state = load();
  function toast(m){var t=document.getElementById('toast');t.textContent=m;t.classList.add('show');
    clearTimeout(t._h);t._h=setTimeout(function(){t.classList.remove('show');},1800);}

  function goTo(id,instant){var el=document.getElementById(id);
    if(el)el.scrollIntoView({behavior:instant?'instant':'smooth',block:'start'});}
  document.addEventListener('click',function(e){
    var a=e.target.closest('a[href^="#"]');if(!a)return;
    var id=decodeURIComponent(a.getAttribute('href').slice(1));
    if(!document.getElementById(id))return;e.preventDefault();
    history.replaceState(null,'','#'+id);goTo(id);});
  if(location.hash)goTo(decodeURIComponent(location.hash.slice(1)),true);

  var tocLinks={};
  document.querySelectorAll('.toc nav a[data-sec]').forEach(function(a){
    tocLinks[a.getAttribute('data-sec')]=a;});
  var spy=new IntersectionObserver(function(es){es.forEach(function(en){if(!en.isIntersecting)return;
    var id=en.target.id;Object.keys(tocLinks).forEach(function(k){
      tocLinks[k].classList.toggle('active',k===id);});});},
    {rootMargin:'-10% 0px -70% 0px'});
  document.querySelectorAll('.scene[id]').forEach(function(s){spy.observe(s);});

  function fmt(ts){var d=new Date(ts);
    return d.toLocaleDateString(undefined,{month:'short',day:'numeric'})+' '+
      d.toLocaleTimeString(undefined,{hour:'2-digit',minute:'2-digit'});}
  function esc(s){return s.replace(/[&<>"]/g,function(c){
    return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function render(){
    document.querySelectorAll('.cwrap').forEach(function(w){
      var sec=w.getAttribute('data-sec');var list=w.querySelector('.clist');
      var mine=state.comments.filter(function(c){return c.sec===sec;});
      list.innerHTML=mine.map(function(c){return '<div class="cmt">'+
        (c.quote?'<div class="q">'+esc(c.quote)+'</div>':'')+
        '<div>'+esc(c.text)+'</div><div class="meta">'+fmt(c.ts)+'</div>'+
        '<button class="del" data-id="'+c.id+'" aria-label="Delete comment">×</button></div>';
      }).join('');
      document.querySelectorAll('[data-cfor="'+sec+'"]').forEach(function(b){
        b.textContent=mine.length;b.classList.toggle('show',mine.length>0);});});
    var t=state.comments.length;
    document.getElementById('ccount').innerHTML='<b>'+t+'</b> comment'+(t===1?'':'s');
    document.getElementById('v-approve').className=state.verdict==='APPROVE'?'on-approve':'';
    document.getElementById('v-revise').className=state.verdict==='REVISE'?'on-revise':'';
  }
  document.addEventListener('click',function(e){
    var del=e.target.closest('.cmt .del');
    if(del){state.comments=state.comments.filter(function(c){
      return String(c.id)!==del.getAttribute('data-id');});save(state);render();return;}
    var add=e.target.closest('.cform button');
    if(add){var f=add.closest('.cform');var ta=f.querySelector('textarea');
      var raw=ta.value.trim();if(!raw)return;var quote='';var text=raw;
      var qm=raw.match(/^>\s?([\s\S]*?)\n{2}([\s\S]*)$/);
      if(qm){quote=qm[1].replace(/\n>\s?/g,' ').trim();text=qm[2].trim();}
      state.comments.push({id:Date.now()+Math.floor(Math.random()*1000),
        sec:f.closest('.cwrap').getAttribute('data-sec'),quote:quote,text:text,ts:Date.now()});
      ta.value='';save(state);render();}});

  var pill=document.getElementById('qpill');
  document.addEventListener('mouseup',function(e){
    if(e.target.closest('#qpill')||e.target.closest('.cform'))return;
    setTimeout(function(){var sel=window.getSelection();var txt=sel?String(sel).trim():'';
      if(!txt||txt.length<3||sel.rangeCount===0){pill.style.display='none';return;}
      var node=sel.anchorNode&&sel.anchorNode.parentElement;
      var sc=node&&node.closest('.scene');
      if(!sc){pill.style.display='none';return;}
      var r=sel.getRangeAt(0).getBoundingClientRect();
      pill.style.display='block';
      pill.style.left=Math.max(12,r.left+r.width/2-55+window.scrollX)+'px';
      pill.style.top=(r.top+window.scrollY-44)+'px';
      pill._quote=txt.replace(/\s+/g,' ').slice(0,400);pill._sec=sc.id;},0);});
  pill.addEventListener('click',function(){
    var sc=document.getElementById(pill._sec);if(!sc)return;
    var ta=sc.querySelector('.cform textarea');ta.value='> '+pill._quote+'\n\n';
    pill.style.display='none';if(window.getSelection)window.getSelection().removeAllRanges();
    ta.scrollIntoView({behavior:'smooth',block:'center'});setTimeout(function(){ta.focus();},350);});
  document.addEventListener('scroll',function(){pill.style.display='none';});

  var lb=document.getElementById('lb'),lbfig=document.getElementById('lbfig'),
      lbcap=document.getElementById('lbcap');
  function lbClose(){lb.hidden=true;lbfig.innerHTML='';document.body.style.overflow='';}
  document.addEventListener('click',function(e){
    var m=e.target.closest('.der[data-view]');
    if(m){e.preventDefault();lbfig.innerHTML='<img src="'+m.getAttribute('href')+'" alt="">';
      lbcap.textContent=m.textContent.trim();lb.hidden=false;document.body.style.overflow='hidden';return;}
    if(!lb.hidden&&(e.target===lb||e.target.id==='lbclose'))lbClose();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!lb.hidden)lbClose();});

  document.getElementById('v-approve').addEventListener('click',function(){
    state.verdict=state.verdict==='APPROVE'?'':'APPROVE';save(state);render();});
  document.getElementById('v-revise').addEventListener('click',function(){
    state.verdict=state.verdict==='REVISE'?'':'REVISE';save(state);render();});
  function exportMd(){
    var title=document.body.getAttribute('data-title')||'Scene design';
    var lines=['# Scene-design review — '+title,'',
      '**Verdict:** '+(state.verdict||'(none set)')+' · **Comments:** '+state.comments.length+
      ' · '+new Date().toISOString().slice(0,16).replace('T',' '),''];
    document.querySelectorAll('.scene').forEach(function(sc){
      var mine=state.comments.filter(function(c){return c.sec===sc.id;});if(!mine.length)return;
      lines.push('## '+sc.getAttribute('data-name'));
      mine.forEach(function(c){lines.push(c.quote?'- (re: "'+c.quote+'") '+c.text:'- '+c.text);});
      lines.push('');});
    if(!state.comments.length)lines.push('_No scene comments._');
    return lines.join('\n');}
  function copyText(t,m){function fb(){var ta=document.createElement('textarea');ta.value=t;
    document.body.appendChild(ta);ta.select();try{document.execCommand('copy');toast(m);}
    catch(e){toast('Copy failed');}document.body.removeChild(ta);}
    if(navigator.clipboard&&navigator.clipboard.writeText)
      navigator.clipboard.writeText(t).then(function(){toast(m);},fb);else fb();}
  document.getElementById('copyreview').addEventListener('click',function(){
    copyText(exportMd(),'Review copied as markdown');});
  document.getElementById('dlreview').addEventListener('click',function(){
    var b=new Blob([exportMd()],{type:'text/markdown'});var a=document.createElement('a');
    a.href=URL.createObjectURL(b);a.download='scenes-review.md';a.click();
    setTimeout(function(){URL.revokeObjectURL(a.href);},500);});
  render();
  document.body.setAttribute('data-jsready','1');
})();
"""

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ · scene design</title><style>__CSS__</style></head>
<body data-plan="__KEY__" data-title="__TITLEATTR__">
<div class="layout">
  <aside class="toc"><p class="brand">Scene design · gate</p><p class="nm">__TITLE__</p>
    <nav>__TOC__</nav></aside>
  <main>
    <p class="eyebrow">Scene design · second human gate</p>
    <h1 class="title">__TITLE__</h1>
    __RECAP__
    <div class="chips">__CHIPS__</div>
    __SCENES__
  </main>
</div>
<div id="qpill">💬 Comment</div>
<div id="lb" role="dialog" aria-modal="true" aria-label="Reference preview" hidden>
  <button id="lbclose" type="button" aria-label="Close preview">×</button>
  <figure id="lbfig"></figure><figcaption id="lbcap"></figcaption></div>
<div id="bar">
  <span class="cnt" id="ccount"><b>0</b> comments</span>
  <span class="verdict"><button id="v-approve" type="button">APPROVE</button>
    <button id="v-revise" type="button">REVISE</button></span>
  <button class="act ghost" id="dlreview" type="button">Download .md</button>
  <button class="act" id="copyreview" type="button">Copy review</button>
</div>
<div id="toast" role="status"></div>
<script>__JS__</script></body></html>
"""


def build(src_path: Path, out_path: Path, title_override):
    text = src_path.read_text(encoding="utf-8")
    title, header, scenes = parse_scenes(text)
    if title_override:
        title = title_override
    plan_dir = src_path.resolve().parent
    out_dir = out_path.resolve().parent
    ids: set = set()

    toc, cards = [], []
    n_premium = 0
    for sc in scenes:
        label = f'{sc["num"]} · {sc["name"]}'.strip(" ·")
        sid = slugify(label, ids)
        sc["_id"] = sid
        verdict = sc["score"]["verdict"] if sc["score"] else None
        if verdict == "premium":
            n_premium += 1
        vb = f'<span class="vb {verdict}"></span>' if verdict else ""
        toc.append(
            f'<a href="#{sid}" data-sec="{sid}"><span class="n">{esc(sc["num"])}</span>'
            f'{esc(sc["name"])}<span class="cb" data-cfor="{sid}"></span>{vb}</a>'
        )

        f = sc["fields"]
        meta_rows = []
        if f.get("archetype"):
            meta_rows.append(f'<dt>Archetype</dt><dd>{inline(f["archetype"])}</dd>')
        if f.get("derives"):
            meta_rows.append(
                f'<dt>Derives</dt><dd>{derives_widget(f["derives"], plan_dir, out_dir)}</dd>'
            )
        if f.get("focal"):
            meta_rows.append(f'<dt>Focal</dt><dd>{inline(f["focal"])}</dd>')
        if f.get("motion"):
            meta_rows.append(f'<dt>Motion</dt><dd>{inline(f["motion"])}</dd>')
        if f.get("type"):
            meta_rows.append(f'<dt>Type</dt><dd>{inline(f["type"])}</dd>')
        meta = (
            f'<div class="sc-meta"><dl>{"".join(meta_rows)}</dl>'
            f'<h4 style="margin-top:18px">Scorecard</h4>{render_scorecard(sc["score"])}</div>'
        )

        span = f' <span class="span">{esc(sc["span"])}</span>' if sc["span"] else ""
        cards.append(
            f'<section class="scene" id="{sid}" data-name="{attr(label)}">'
            f'<div class="sc-head"><span class="id">{esc(sc["num"])}</span>'
            f'<span class="ttl">{inline(sc["name"])}</span>{span}</div>'
            f'<div class="sc-body">'
            f'<div class="wf-wrap"><p class="wf-cap"><span>Layout wireframe</span>'
            f'<span>{esc(sc["layout"]["cols"]) if sc["layout"] else ""}'
            f'{"×" + str(sc["layout"]["rows"]) if sc["layout"] else ""}</span></p>'
            f'{render_wireframe(sc["layout"])}</div>'
            f'{meta}</div>'
            f'<div class="cwrap" data-sec="{sid}"><p class="clabel">Review comments</p>'
            f'<div class="clist"></div><div class="cform">'
            f'<textarea placeholder="Comment on this scene… (or select any text / the layout to quote it)"></textarea>'
            f'<div class="row"><button type="button">Add comment</button></div></div></div>'
            f"</section>"
        )

    recap_bits = []
    for k, lbl in (("concept", "Concept"), ("signature", "Signature device"), ("arc", "Arc")):
        if header.get(k):
            recap_bits.append(f"<div><b>{lbl}</b>{inline(header[k])}</div>")
    recap = f'<div class="recap">{"".join(recap_bits)}</div>' if recap_bits else ""

    chips = [f'<span class="chip">{len(scenes)} scenes</span>']
    scored = [s for s in scenes if s["score"]]
    if scored:
        allp = n_premium == len(scored)
        chips.append(
            f'<span class="chip {"ok" if allp else "warn"}">'
            f'{n_premium}/{len(scored)} premium</span>'
        )

    key = "-".join(
        p for p in (
            re.sub(r"[^\w-]+", "-", title.lower()).strip("-"),
            re.sub(r"[^\w-]+", "-", plan_dir.name.lower()).strip("-"),
        ) if p
    ) or "scenes"

    page = (
        PAGE.replace("__TITLE__", esc(title))
        .replace("__TITLEATTR__", attr(title))
        .replace("__KEY__", attr(key))
        .replace("__TOC__", "".join(toc) or '<a href="#">no scenes parsed</a>')
        .replace("__RECAP__", recap)
        .replace("__CHIPS__", "".join(chips))
        .replace("__SCENES__", "".join(cards) or
                 '<p style="color:#6F6A5E">No scenes found in this file.</p>')
        .replace("__CSS__", CSS)
        .replace("__JS__", JS)
    )
    out_path.write_text(page, encoding="utf-8")
    return len(scenes), n_premium


def main():
    ap = argparse.ArgumentParser(description="Render scenes-design.md as an interactive design-review page")
    ap.add_argument("src", help="path to scenes-design.md")
    ap.add_argument("-o", "--out", help="output html (default: SCENES.html beside the source)")
    ap.add_argument("--title", help="override document title")
    args = ap.parse_args()
    src = Path(args.src)
    if not src.is_file():
        sys.exit(f"scenes-to-html: no such file: {src}")
    out = Path(args.out) if args.out else src.with_name("SCENES.html")
    n, p = build(src, out, args.title)
    print(f"scenes-to-html: wrote {out} ({n} scenes, {p} premium)")


if __name__ == "__main__":
    main()
