#!/usr/bin/env python3
"""plan-to-html.py — render a queek-premium-video plan.md as a single-file
interactive review page.

The output is self-contained (inline CSS/JS, no external requests) so it
works from file:// and offline. Features:
  - hero card with the creative-bet header (Concept / Audio path / Signature / Arc)
  - accordion per ## section, deep-linkable; TOC sidebar with scrollspy
  - per-section review comments (localStorage) + select-text-to-quote
  - APPROVE / REVISE verdict + one-click "Copy review" markdown export
    that the reviewer pastes back to resolve the Plan gate

Usage:
  plan-to-html.py works/<slug>/plan.md            -> works/<slug>/plan.html
  plan-to-html.py plan.md -o review.html --title "Feature spotlight — refunds"

Stdlib only. Markdown subset: ##/###/#### headings, tables, fenced code,
task lists, ul/ol, blockquote, hr, bold/italic/inline-code/links.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- inline md

RE_CODE = re.compile(r"`([^`]+)`")
RE_BOLD = re.compile(r"\*\*([^*]+)\*\*")
RE_ITAL = re.compile(r"(?<![\w*])\*([^*\s](?:[^*]*[^*\s])?)\*(?![\w*])")
RE_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
RE_HEX = re.compile(r"(?<![\w&;])#([0-9A-Fa-f]{6})\b")


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def inline(text: str) -> str:
    out = esc(text)
    out = RE_CODE.sub(r"<code>\1</code>", out)
    out = RE_BOLD.sub(r"<strong>\1</strong>", out)
    out = RE_ITAL.sub(r"<em>\1</em>", out)
    out = RE_LINK.sub(r'<a href="\2">\1</a>', out)
    out = RE_HEX.sub(r'<span class="sw" style="background:#\1"></span>#\1', out)
    return out


def slugify(text: str, seen: set) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    s = re.sub(r"[\s_]+", "-", s) or "section"
    base, n = s, 2
    while s in seen:
        s = f"{base}-{n}"
        n += 1
    seen.add(s)
    return s


# ---------------------------------------------------------------- block md

CHECK = {
    "x": '<span class="ck ck-on" aria-hidden="true">✓</span>',
    " ": '<span class="ck" aria-hidden="true"></span>',
}


def render_blocks(lines, ids: set, subheads):
    out, i, n = [], 0, len(lines)

    def para_flush(buf):
        if buf:
            out.append("<p>" + "<br>".join(inline(b) for b in buf) + "</p>")
            buf.clear()

    buf = []
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            para_flush(buf)
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + esc("\n".join(code)) + "</code></pre>")
            continue

        if not stripped:
            para_flush(buf)
            i += 1
            continue

        m = re.match(r"^(#{3,4})\s+(.*)$", stripped)
        if m:
            para_flush(buf)
            level = len(m.group(1))
            text = m.group(2).strip()
            hid = slugify(text, ids)
            scene = bool(re.match(r"^S\d+\b", text))
            if level == 3:
                subheads.append({"id": hid, "title": text, "scene": scene})
            cls = ' class="scene-h"' if scene else ""
            out.append(
                f'<h{level} id="{hid}"{cls}>{inline(text)}'
                f'<a class="hlink" href="#{hid}" title="Copy link">¶</a></h{level}>'
            )
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,})$", stripped):
            para_flush(buf)
            out.append("<hr>")
            i += 1
            continue

        if stripped.startswith(">"):
            para_flush(buf)
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            out.append("<blockquote><p>" + inline(" ".join(quote)) + "</p></blockquote>")
            continue

        if stripped.startswith("|") and i + 1 < n and re.match(
            r"^\|[\s:|-]+\|?$", lines[i + 1].strip()
        ):
            para_flush(buf)
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ['<div class="tablewrap"><table><thead><tr>']
            t += [f"<th>{inline(h)}</th>" for h in header]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue

        m = re.match(r"^(\s*)([-*]|\d+[.)])\s+(.*)$", line)
        if m:
            para_flush(buf)
            ordered = m.group(2)[0].isdigit()
            tag = "ol" if ordered else "ul"
            items = []
            while i < n:
                lm = re.match(r"^(\s*)([-*]|\d+[.)])\s+(.*)$", lines[i])
                if not lm:
                    break
                body = lm.group(3)
                cm = re.match(r"^\[( |x|X)\]\s+(.*)$", body)
                if cm:
                    mark = CHECK["x" if cm.group(1).lower() == "x" else " "]
                    items.append(f'<li class="task">{mark}<span>{inline(cm.group(2))}</span></li>')
                else:
                    items.append(f"<li>{inline(body)}</li>")
                i += 1
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue

        buf.append(stripped)
        i += 1

    para_flush(buf)
    return "".join(out)


# ---------------------------------------------------------------- media refs

IMG_EXT = {"png", "jpg", "jpeg", "webp", "gif", "svg"}
AUD_EXT = {"mp3", "wav", "m4a", "aac", "ogg", "flac"}
VID_EXT = {"mp4", "webm", "mov"}
MEDIA_RE = re.compile(
    r"(?<![\w/.\-])([\w~][\w.\-/]*\.(?:png|jpe?g|webp|gif|svg|mp3|wav|m4a|aac|ogg|flac|mp4|webm|mov))\b",
    re.I,
)
ICON_IMG = (
    '<svg viewBox="0 0 16 16" width="11" height="11" fill="none" stroke="currentColor" '
    'stroke-width="1.5"><rect x="1.5" y="2.5" width="13" height="11" rx="2"/>'
    '<circle cx="5.5" cy="6.5" r="1.2"/><path d="M2 12l3.5-3.5 2.5 2.5L11 8l3 3"/></svg>'
)
ICON_VID = (
    '<svg viewBox="0 0 16 16" width="11" height="11" fill="currentColor">'
    '<path d="M3 2.5l10 5.5-10 5.5z"/></svg>'
)


def make_media_resolver(plan_path: Path, out_dir: Path):
    """Return a re.sub callback: media path -> preview widget.

    Paths cited in a plan resolve from the working-project root, which is
    above works/<slug>/ — so try the plan's dir, then up to three parents,
    then cwd. Found files become playable/previewable widgets with hrefs
    relative to the output html; missing ones render as a muted chip
    (status D/R assets get sourced at Make)."""
    import os

    roots = [plan_path.parent, *list(plan_path.parent.parents)[:3], Path.cwd()]

    def resolve(m):
        token = m.group(1)
        name = esc(Path(token).name)
        ext = token.rsplit(".", 1)[-1].lower()
        found = None
        for root in roots:
            cand = (root / token).resolve()
            if cand.is_file():
                found = cand
                break
        if not found:
            if "/" not in token:
                return m.group(1)  # bare name, no path claim — leave as text
            return (
                f'<span class="media m-miss" title="not on disk yet · '
                f'sourced at Make (status D/R)">{name}</span>'
            )
        rel = esc(os.path.relpath(found, out_dir))
        if ext in AUD_EXT:
            return (
                f'<span class="m-audio"><audio controls preload="none" '
                f'src="{rel}"></audio><span class="aname">{name}</span></span>'
            )
        if ext in VID_EXT:
            return (
                f'<a class="media m-vid" href="{rel}" data-view="video">'
                f"{ICON_VID}{name}</a>"
            )
        return (
            f'<a class="media m-img" href="{rel}" data-view="img">'
            f"{ICON_IMG}{name}</a>"
        )

    return resolve


def mediafy(html_str: str, resolve) -> str:
    """Apply the media resolver to text nodes only (never inside tags or
    <pre> blocks, where injected markup would corrupt content)."""
    parts = re.split(r"(<[^>]+>)", html_str)
    in_pre = 0
    for i, part in enumerate(parts):
        if part.startswith("<"):
            if part.startswith("<pre"):
                in_pre += 1
            elif part.startswith("</pre"):
                in_pre = max(0, in_pre - 1)
            continue
        if in_pre or not part.strip():
            continue
        parts[i] = MEDIA_RE.sub(resolve, part)
    return "".join(parts)


# ---------------------------------------------------------------- plan parse

BET_KEYS = [
    ("concept", r"\*\*Concept:?\*\*"),
    ("audio", r"\*\*Audio\s*path:?\*\*"),
    ("signature", r"\*\*Signature(?:\s*device)?:?\*\*"),
    ("arc", r"\*\*Arc:?\*\*"),
]


def parse_plan(text: str):
    lines = text.splitlines()
    title = "Plan"
    bet = {}
    validator = ""
    preamble, sections, current = [], [], None

    for raw in lines:
        s = raw.strip()
        m = re.match(r"^#\s+(.*)$", s)
        if m and title == "Plan":
            title = m.group(1).strip()
            continue
        bet_line = False
        for key, pat in BET_KEYS:
            bm = re.match(rf"^(?:[-*]\s+)?{pat}\s*(.+)$", s)
            if bm:
                bet_line = True
                if key not in bet:
                    bet[key] = bm.group(1).strip(" ·")
        if bet_line and current is None:
            continue  # shown in the hero bet card; don't duplicate in preamble
        if re.match(r"^`?Plan validator:", s):
            validator = s.strip("`")
        m = re.match(r"^##\s+(.*)$", s)
        if m:
            current = {"title": m.group(1).strip(), "lines": []}
            sections.append(current)
            continue
        (current["lines"] if current else preamble).append(raw)

    return title, bet, validator, preamble, sections


# ---------------------------------------------------------------- page shell

CSS = r"""
:root{
  --paper:#F7F5F0; --surface:#FFFEFB; --ink:#1C1A15; --muted:#6F6A5E;
  --line:#E5E0D4; --line2:#D8D2C2; --accent:#0E6B43; --accent-ink:#0A4D31;
  --accent-soft:#EAF3ED; --gold:#8A6D1F; --gold-soft:#F6EFDB; --danger:#A33A2A;
  --mono:ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace;
  --serif:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;
  --sans:-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:24px}
body{margin:0;background:var(--paper);color:var(--ink);font:13.5px/1.62 var(--sans);
  -webkit-font-smoothing:antialiased}
a{color:var(--accent-ink)}
:is(a,button,summary,[tabindex]):focus-visible{outline:2px solid var(--accent);
  outline-offset:2px;border-radius:4px}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{transition:none!important;animation:none!important}
}
.layout{display:grid;grid-template-columns:264px minmax(0,1fr);max-width:1240px;
  margin:0 auto;gap:0 48px;padding:0 32px}

/* ---- toc ---- */
.toc{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;
  padding:36px 0 120px;border-right:1px solid var(--line);scrollbar-width:thin}
.toc .brand{font:600 11px/1 var(--sans);letter-spacing:.18em;text-transform:uppercase;
  color:var(--muted);margin:0 0 6px}
.toc .planname{font:700 13.5px/1.35 var(--sans);margin:0 16px 18px 0;
  overflow-wrap:break-word}
.toc-tools{display:flex;gap:6px;margin:0 16px 18px 0}
.toc-tools button{flex:1;font:600 11px/1 var(--sans);letter-spacing:.04em;
  padding:7px 4px;border:1px solid var(--line2);border-radius:7px;background:var(--surface);
  color:var(--muted);cursor:pointer}
.toc-tools button:hover{color:var(--ink);border-color:var(--ink)}
.toc nav{display:flex;flex-direction:column;gap:1px;padding-right:16px}
.toc nav a{display:flex;gap:9px;align-items:baseline;padding:5px 9px;border-radius:7px;
  text-decoration:none;color:var(--muted);font-size:12px;line-height:1.35}
.toc nav a .n{font:600 10px/1.4 var(--mono);color:var(--line2);min-width:17px}
.toc nav a:hover{color:var(--ink);background:rgba(0,0,0,.035)}
.toc nav a.active{color:var(--accent-ink);background:var(--accent-soft);font-weight:600}
.toc nav a.active .n{color:var(--accent)}
.toc nav a.sub{padding-left:36px;font-size:11px}
.toc nav a.sub.scene .n{display:none}
.toc nav .cb{margin-left:auto;font:600 10px/1.6 var(--mono);background:var(--gold-soft);
  color:var(--gold);border-radius:9px;padding:0 6px;display:none}
.toc nav .cb.show{display:inline-block}

/* ---- main / hero ---- */
main{padding:44px 0 160px;min-width:0}
.eyebrow{font:600 10px/1 var(--sans);letter-spacing:.22em;text-transform:uppercase;
  color:var(--accent);margin:0 0 12px}
h1.title{font:600 30px/1.15 var(--serif);letter-spacing:-.01em;margin:0 0 18px;
  text-wrap:balance}
.chips{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 24px}
.chip{font:600 10.5px/1 var(--sans);letter-spacing:.05em;padding:6px 11px;
  border:1px solid var(--line2);border-radius:999px;background:var(--surface);color:var(--muted)}
.chip.ok{border-color:var(--accent);color:var(--accent-ink);background:var(--accent-soft)}
.bet{background:var(--surface);border:1px solid var(--line);border-radius:14px;
  box-shadow:0 1px 2px rgba(28,26,21,.04),0 12px 32px -24px rgba(28,26,21,.25);
  margin:0 0 40px;overflow:hidden}
.bet .bet-head{display:flex;justify-content:space-between;align-items:center;
  padding:13px 22px;border-bottom:1px solid var(--line);background:linear-gradient(#FDFCFa,#F9F7F1)}
.bet .bet-head b{font:600 11px/1 var(--sans);letter-spacing:.18em;text-transform:uppercase;
  color:var(--muted)}
.bet .bet-head span{font:500 11px/1 var(--sans);color:var(--muted)}
.bet dl{margin:0;display:grid;grid-template-columns:130px 1fr}
.bet dt{font:600 10px/1.5 var(--sans);letter-spacing:.12em;text-transform:uppercase;
  color:var(--accent-ink);padding:14px 0 14px 22px;border-top:1px solid var(--line)}
.bet dd{margin:0;padding:12px 22px 12px 16px;border-top:1px solid var(--line);
  font:400 14.5px/1.5 var(--serif)}
.bet dt:first-of-type,.bet dd:first-of-type{border-top:0}

/* ---- swatches + timeline ---- */
.sw{display:inline-block;width:11px;height:11px;border-radius:50%;
  border:1px solid rgba(0,0,0,.18);margin:0 5px 0 1px;transform:translateY(1px)}
.tl-wrap{margin:0 0 40px}
.tl-head{display:flex;justify-content:space-between;align-items:baseline;margin:0 0 9px}
.tl-head b{font:600 11px/1 var(--sans);letter-spacing:.18em;text-transform:uppercase;
  color:var(--muted)}
.tl-head span{font:500 11px/1 var(--sans);color:var(--muted)}
.timeline{display:flex;gap:4px;height:52px}
.tseg{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;
  background:var(--surface);border:1px solid var(--line2);border-radius:9px;
  text-decoration:none;min-width:34px;overflow:hidden;transition:.15s}
.tseg b{font:700 12px/1 var(--sans);color:var(--ink)}
.tseg span{font:500 10px/1 var(--mono);color:var(--muted)}
.tseg:hover{border-color:var(--accent);background:var(--accent-soft)}
.tseg:hover b{color:var(--accent-ink)}
.tseg.peak{background:var(--accent);border-color:var(--accent)}
.tseg.peak b,.tseg.peak span{color:#F6F4EC}
.tseg.peak:hover{background:var(--accent-ink)}

/* ---- media previews ---- */
.media{display:inline-flex;align-items:center;gap:6px;font:600 11px/1 var(--sans);
  padding:4px 9px;border:1px solid var(--line2);border-radius:7px;background:var(--surface);
  color:var(--accent-ink);text-decoration:none;cursor:pointer;vertical-align:baseline;
  white-space:nowrap;transition:border-color .15s}
.media svg{flex:none;color:var(--accent)}
.media:hover{border-color:var(--accent);background:var(--accent-soft)}
.media.m-miss{border-style:dashed;color:var(--muted);cursor:help}
.media.m-miss::after{content:'pending';font:600 8.5px/1 var(--sans);letter-spacing:.08em;
  text-transform:uppercase;background:#F1EEE5;border-radius:4px;padding:3px 5px;color:var(--muted)}
.m-audio{display:inline-flex;align-items:center;gap:8px;vertical-align:middle;
  background:var(--surface);border:1px solid var(--line2);border-radius:999px;
  padding:3px 12px 3px 3px;margin:2px 0}
.m-audio audio{height:28px;max-width:240px}
.m-audio .aname{font:600 11px/1 var(--sans);color:var(--muted);white-space:nowrap}
#lb{position:fixed;inset:0;z-index:80;background:rgba(24,22,17,.86);
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;
  padding:40px}
#lb[hidden]{display:none}
#lbfig{margin:0;max-width:min(1200px,92vw);max-height:82vh;display:flex}
#lbfig img,#lbfig video{max-width:100%;max-height:82vh;border-radius:10px;
  box-shadow:0 32px 80px -24px rgba(0,0,0,.6)}
#lbcap{font:600 12px/1 var(--sans);color:#D9D4C7}
#lbclose{position:absolute;top:18px;right:22px;border:0;background:rgba(255,254,251,.12);
  color:#F8F6F0;font:300 22px/1 var(--sans);width:40px;height:40px;border-radius:50%;
  cursor:pointer}
#lbclose:hover{background:rgba(255,254,251,.24)}

/* ---- accordion sections ---- */
.sec{margin:0 0 14px}
.sec details{background:var(--surface);border:1px solid var(--line);border-radius:13px;
  overflow:clip;transition:box-shadow .2s}
.sec details[open]{box-shadow:0 1px 2px rgba(28,26,21,.04),0 16px 40px -30px rgba(28,26,21,.3)}
.sec summary{display:flex;align-items:center;gap:13px;padding:14px 18px;cursor:pointer;
  list-style:none;user-select:none}
.sec summary::-webkit-details-marker{display:none}
.sec summary .num{font:600 11px/1 var(--mono);color:var(--accent);background:var(--accent-soft);
  border-radius:7px;padding:6px 7px;min-width:29px;text-align:center}
.sec summary .st{font:600 14.5px/1.3 var(--sans);letter-spacing:-.01em;flex:1}
.sec summary .cb{font:600 10.5px/1.7 var(--mono);background:var(--gold-soft);color:var(--gold);
  border-radius:9px;padding:0 7px;display:none}
.sec summary .cb.show{display:inline-block}
.sec summary .chev{width:9px;height:9px;border-right:1.6px solid var(--muted);
  border-bottom:1.6px solid var(--muted);transform:rotate(-45deg);transition:transform .18s;
  margin-right:4px}
.sec details[open] summary .chev{transform:rotate(45deg)}
.sec summary:hover .st{color:var(--accent-ink)}
.secbody{padding:4px 22px 20px;border-top:1px solid var(--line)}
.secbody>:first-child{margin-top:14px}

/* ---- content ---- */
.secbody h3{font:600 15px/1.3 var(--sans);letter-spacing:-.01em;margin:26px 0 8px;
  padding-top:16px;border-top:1px solid var(--line)}
.secbody h3:first-child{border-top:0;padding-top:0;margin-top:14px}
.secbody h3.scene-h{display:flex;align-items:center;gap:10px}
.secbody h3.scene-h::before{content:'SCENE';font:700 9px/1 var(--sans);letter-spacing:.14em;
  color:var(--accent);background:var(--accent-soft);border:1px solid #CDE3D6;
  border-radius:6px;padding:4px 6px}
.secbody h4{font:600 11px/1.4 var(--sans);letter-spacing:.07em;text-transform:uppercase;
  color:var(--muted);margin:22px 0 7px}
.hlink{opacity:0;margin-left:8px;text-decoration:none;font:400 14px/1 var(--sans);
  color:var(--line2)}
h3:hover .hlink,h4:hover .hlink{opacity:1}
.hlink:hover{color:var(--accent)}
.secbody p{margin:9px 0;max-width:72ch}
.secbody ul,.secbody ol{margin:10px 0;padding-left:24px}
.secbody li{margin:4px 0}
.secbody li.task{list-style:none;margin-left:-24px;display:flex;gap:9px;align-items:baseline}
.ck{display:inline-block;width:15px;height:15px;border:1.5px solid var(--line2);
  border-radius:4.5px;flex:none;transform:translateY(2px);font:700 11px/13px var(--sans);
  text-align:center;color:transparent}
.ck-on{background:var(--accent);border-color:var(--accent);color:#F8F6F0}
.secbody code{font:11.5px/1.5 var(--mono);background:#F1EEE5;border:1px solid var(--line);
  border-radius:5px;padding:1px 5px}
.secbody pre{background:#23211B;color:#EDEAE0;border-radius:10px;padding:14px 16px;
  overflow-x:auto;font:11.5px/1.6 var(--mono);margin:13px 0}
.secbody pre code{background:none;border:0;padding:0;color:inherit;font:inherit}
.secbody blockquote{margin:13px 0;padding:2px 16px;border:1px solid #CDE3D6;
  background:var(--accent-soft);border-radius:9px;color:var(--accent-ink)}
.secbody hr{border:0;border-top:1px solid var(--line);margin:22px 0}
.tablewrap{overflow-x:auto;margin:14px 0;border:1px solid var(--line);border-radius:10px}
.secbody table{border-collapse:collapse;width:100%;font-size:12.5px}
.secbody th{font:600 10px/1.5 var(--sans);letter-spacing:.08em;text-transform:uppercase;
  color:var(--muted);text-align:left;background:#FAF8F2;padding:9px 13px;
  border-bottom:1px solid var(--line);white-space:nowrap}
.secbody td{padding:8px 13px;border-bottom:1px solid var(--line);vertical-align:top}
.secbody tbody tr:last-child td{border-bottom:0}
.secbody tbody tr:hover{background:#FBFAF6}

/* ---- comments ---- */
.cwrap{margin:26px -24px -22px;padding:16px 24px 18px;background:#FAF8F2;
  border-top:1px dashed var(--line2)}
.cwrap .clabel{font:600 10.5px/1 var(--sans);letter-spacing:.16em;text-transform:uppercase;
  color:var(--muted);margin:0 0 10px;display:flex;align-items:center;gap:8px}
.cwrap .clabel::before{content:'';width:7px;height:7px;border-radius:50%;background:var(--gold)}
.cmt{background:var(--surface);border:1px solid var(--line);border-radius:10px;
  padding:10px 13px;margin:0 0 8px;font-size:13.5px;position:relative}
.cmt .q{border:1px solid #E8DDBC;background:var(--gold-soft);border-radius:7px;
  padding:5px 10px;margin:0 0 7px;color:#6b5618;font-size:11.5px;font-style:italic}
.cmt .meta{font:500 10.5px/1 var(--sans);color:var(--muted);margin-top:7px}
.cmt .del{position:absolute;top:8px;right:10px;border:0;background:none;color:var(--line2);
  font:600 14px/1 var(--sans);cursor:pointer;padding:2px}
.cmt .del:hover{color:var(--danger)}
.cform{display:flex;flex-direction:column;gap:8px}
.cform textarea{resize:vertical;min-height:60px;border:1px solid var(--line2);border-radius:10px;
  padding:10px 12px;font:13.5px/1.55 var(--sans);background:var(--surface);color:var(--ink)}
.cform textarea:focus{outline:2px solid var(--accent);outline-offset:-1px;border-color:transparent}
.cform .row{display:flex;justify-content:flex-end}
.cform button{font:600 12px/1 var(--sans);letter-spacing:.03em;padding:9px 16px;border:0;
  border-radius:8px;background:var(--ink);color:#F8F6F0;cursor:pointer}
.cform button:hover{background:var(--accent-ink)}

/* ---- quote pill ---- */
#qpill{position:absolute;z-index:60;display:none;font:600 12px/1 var(--sans);
  background:var(--ink);color:#F8F6F0;border-radius:999px;padding:9px 14px;cursor:pointer;
  box-shadow:0 8px 24px -8px rgba(0,0,0,.45)}
#qpill::after{content:'';position:absolute;left:50%;bottom:-5px;transform:translateX(-50%) rotate(45deg);
  width:9px;height:9px;background:var(--ink)}

/* ---- review bar ---- */
#bar{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);z-index:50;
  display:flex;align-items:center;gap:14px;background:var(--surface);
  border:1px solid var(--line2);border-radius:999px;padding:9px 11px 9px 20px;
  box-shadow:0 6px 18px -4px rgba(28,26,21,.18),0 24px 60px -24px rgba(28,26,21,.35)}
#bar .cnt{font:600 12.5px/1 var(--sans);color:var(--muted);white-space:nowrap}
#bar .cnt b{color:var(--ink);font-size:14px}
#bar .verdict{display:flex;background:#F1EEE5;border-radius:999px;padding:3px}
#bar .verdict button{font:700 11px/1 var(--sans);letter-spacing:.06em;border:0;cursor:pointer;
  border-radius:999px;padding:8px 13px;background:none;color:var(--muted)}
#bar .verdict button.on-approve{background:var(--accent);color:#F8F6F0}
#bar .verdict button.on-revise{background:var(--danger);color:#F8F6F0}
#bar .act{font:600 12px/1 var(--sans);border:0;border-radius:999px;padding:10px 16px;
  cursor:pointer;background:var(--ink);color:#F8F6F0;white-space:nowrap}
#bar .act:hover{background:var(--accent-ink)}
#bar .act.ghost{background:none;border:1px solid var(--line2);color:var(--muted);padding:9px 13px}
#bar .act.ghost:hover{color:var(--ink);border-color:var(--ink)}
#toast{position:fixed;bottom:84px;left:50%;transform:translateX(-50%) translateY(6px);z-index:55;
  background:var(--accent-ink);color:#F8F6F0;font:600 12.5px/1 var(--sans);border-radius:9px;
  padding:11px 16px;opacity:0;pointer-events:none;transition:.25s}
#toast.show{opacity:1;transform:translateX(-50%)}

@media (max-width:980px){
  body{font-size:14px}
  .layout{grid-template-columns:1fr;padding:0 18px}
  .toc{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line);
    padding:24px 0 14px}
  .toc nav{flex-direction:row;flex-wrap:wrap;padding:0}
  .toc nav a.sub{display:none}
  h1.title{font-size:30px}
  .bet dl{grid-template-columns:1fr}
  .bet dt{padding:13px 22px 0}
  .bet dd{border-top:0;padding:3px 22px 13px}
  #bar{width:calc(100% - 24px);justify-content:space-between;gap:8px;padding-left:14px}
}
"""

JS = r"""
(function () {
  'use strict';
  var KEY = 'planreview:' + (document.body.getAttribute('data-plan') || 'plan');

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || { comments: [], verdict: '' }; }
    catch (e) { return { comments: [], verdict: '' }; }
  }
  function save(state) {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
  }
  var state = load();

  function toast(msg) {
    var t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(t._h);
    t._h = setTimeout(function () { t.classList.remove('show'); }, 1800);
  }

  // ---- accordion / deep links ----
  function openSection(id) {
    var sec = document.getElementById(id);
    if (!sec) return null;
    var det = sec.closest('details') || sec.querySelector('details');
    if (det) det.open = true;
    return sec;
  }
  function goTo(id, instant) {
    var el = openSection(id);
    if (el) el.scrollIntoView({ behavior: instant ? 'instant' : 'smooth', block: 'start' });
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = decodeURIComponent(a.getAttribute('href').slice(1));
    if (!document.getElementById(id)) return;
    e.preventDefault();
    history.replaceState(null, '', '#' + id);
    if (a.classList.contains('hlink')) {
      var url = location.href.split('#')[0] + '#' + id;
      copyText(url, 'Link copied');
      return;
    }
    goTo(id);
  });
  if (location.hash) {
    goTo(decodeURIComponent(location.hash.slice(1)), true);
  }

  document.getElementById('expandall').addEventListener('click', function () {
    document.querySelectorAll('.sec details').forEach(function (d) { d.open = true; });
  });
  document.getElementById('collapseall').addEventListener('click', function () {
    document.querySelectorAll('.sec details').forEach(function (d) { d.open = false; });
  });

  // ---- scrollspy ----
  var tocLinks = {};
  document.querySelectorAll('.toc nav a[data-sec]').forEach(function (a) {
    tocLinks[a.getAttribute('data-sec')] = a;
  });
  var spy = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      var id = en.target.id;
      Object.keys(tocLinks).forEach(function (k) {
        tocLinks[k].classList.toggle('active', k === id);
      });
    });
  }, { rootMargin: '-10% 0px -70% 0px' });
  document.querySelectorAll('.sec[id]').forEach(function (s) { spy.observe(s); });

  // ---- comments ----
  function fmtTime(ts) {
    var d = new Date(ts);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) +
      ' ' + d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  }
  function escHtml(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function render() {
    document.querySelectorAll('.cwrap').forEach(function (w) {
      var sec = w.getAttribute('data-sec');
      var list = w.querySelector('.clist');
      var mine = state.comments.filter(function (c) { return c.sec === sec; });
      list.innerHTML = mine.map(function (c) {
        return '<div class="cmt">' +
          (c.quote ? '<div class="q">' + escHtml(c.quote) + '</div>' : '') +
          '<div>' + escHtml(c.text) + '</div>' +
          '<div class="meta">' + fmtTime(c.ts) + '</div>' +
          '<button class="del" data-id="' + c.id + '" title="Delete" aria-label="Delete comment">×</button></div>';
      }).join('');
      document.querySelectorAll('[data-cfor="' + sec + '"]').forEach(function (b) {
        b.textContent = mine.length;
        b.classList.toggle('show', mine.length > 0);
      });
    });
    var total = state.comments.length;
    document.getElementById('ccount').innerHTML =
      '<b>' + total + '</b> comment' + (total === 1 ? '' : 's');
    document.getElementById('v-approve').className =
      state.verdict === 'APPROVE' ? 'on-approve' : '';
    document.getElementById('v-revise').className =
      state.verdict === 'REVISE' ? 'on-revise' : '';
  }
  document.addEventListener('click', function (e) {
    var del = e.target.closest('.cmt .del');
    if (del) {
      state.comments = state.comments.filter(function (c) {
        return String(c.id) !== del.getAttribute('data-id');
      });
      save(state); render(); return;
    }
    var add = e.target.closest('.cform button');
    if (add) {
      var form = add.closest('.cform');
      var ta = form.querySelector('textarea');
      var raw = ta.value.trim();
      if (!raw) return;
      var quote = '';
      var qm = raw.match(/^>\s?([\s\S]*?)\n{2}([\s\S]*)$/);
      var text = raw;
      if (qm) { quote = qm[1].replace(/\n>\s?/g, ' ').trim(); text = qm[2].trim(); }
      state.comments.push({
        id: Date.now() + Math.floor(Math.random() * 1000),
        sec: form.closest('.cwrap').getAttribute('data-sec'),
        quote: quote, text: text, ts: Date.now()
      });
      ta.value = '';
      save(state); render();
    }
  });

  // ---- select-to-quote ----
  var pill = document.getElementById('qpill');
  document.addEventListener('mouseup', function (e) {
    if (e.target.closest('#qpill') || e.target.closest('.cform')) return;
    setTimeout(function () {
      var sel = window.getSelection();
      var txt = sel ? String(sel).trim() : '';
      if (!txt || txt.length < 3 || sel.rangeCount === 0) { pill.style.display = 'none'; return; }
      var node = sel.anchorNode && sel.anchorNode.parentElement;
      var body = node && node.closest('.secbody');
      if (!body) { pill.style.display = 'none'; return; }
      var rect = sel.getRangeAt(0).getBoundingClientRect();
      pill.style.display = 'block';
      pill.style.left = Math.max(12, rect.left + rect.width / 2 - 55 + window.scrollX) + 'px';
      pill.style.top = (rect.top + window.scrollY - 44) + 'px';
      pill._quote = txt.slice(0, 400);
      pill._sec = body.closest('.sec').id;
    }, 0);
  });
  pill.addEventListener('click', function () {
    var sec = document.getElementById(pill._sec);
    if (!sec) return;
    openSection(pill._sec);
    var ta = sec.querySelector('.cform textarea');
    ta.value = '> ' + pill._quote + '\n\n';
    pill.style.display = 'none';
    if (window.getSelection) window.getSelection().removeAllRanges();
    ta.scrollIntoView({ behavior: 'smooth', block: 'center' });
    setTimeout(function () { ta.focus(); }, 350);
  });
  document.addEventListener('scroll', function () { pill.style.display = 'none'; });

  // ---- media lightbox ----
  var lb = document.getElementById('lb');
  var lbfig = document.getElementById('lbfig');
  var lbcap = document.getElementById('lbcap');
  function lbClose() {
    lb.hidden = true;
    lbfig.innerHTML = '';
    document.body.style.overflow = '';
  }
  document.addEventListener('click', function (e) {
    var media = e.target.closest('.media[data-view]');
    if (media) {
      e.preventDefault();
      var src = media.getAttribute('href');
      if (media.getAttribute('data-view') === 'video') {
        lbfig.innerHTML = '<video controls autoplay src="' + src + '"></video>';
      } else {
        lbfig.innerHTML = '<img src="' + src + '" alt="">';
      }
      lbcap.textContent = media.textContent.trim() + ' · ' + src;
      lb.hidden = false;
      document.body.style.overflow = 'hidden';
      return;
    }
    if (!lb.hidden && (e.target === lb || e.target.id === 'lbclose')) lbClose();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !lb.hidden) lbClose();
  });

  // ---- verdict + export ----
  document.getElementById('v-approve').addEventListener('click', function () {
    state.verdict = state.verdict === 'APPROVE' ? '' : 'APPROVE'; save(state); render();
  });
  document.getElementById('v-revise').addEventListener('click', function () {
    state.verdict = state.verdict === 'REVISE' ? '' : 'REVISE'; save(state); render();
  });

  function exportMd() {
    var title = document.body.getAttribute('data-title') || 'Plan';
    var lines = ['# Plan review — ' + title, ''];
    lines.push('**Verdict:** ' + (state.verdict || '(none set)') +
      ' · **Comments:** ' + state.comments.length +
      ' · ' + new Date().toISOString().slice(0, 16).replace('T', ' '));
    lines.push('');
    document.querySelectorAll('.sec').forEach(function (sec) {
      var mine = state.comments.filter(function (c) { return c.sec === sec.id; });
      if (!mine.length) return;
      lines.push('## ' + sec.getAttribute('data-name'));
      mine.forEach(function (c) {
        if (c.quote) lines.push('- > ' + c.quote);
        lines.push((c.quote ? '  ' : '- ') + c.text);
      });
      lines.push('');
    });
    if (state.comments.length === 0) lines.push('_No section comments._');
    return lines.join('\n');
  }
  function copyText(txt, msg) {
    function fallback() {
      var ta = document.createElement('textarea');
      ta.value = txt; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); toast(msg); } catch (e) { toast('Copy failed'); }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(function () { toast(msg); }, fallback);
    } else fallback();
  }
  document.getElementById('copyreview').addEventListener('click', function () {
    copyText(exportMd(), 'Review copied as markdown');
  });
  document.getElementById('dlreview').addEventListener('click', function () {
    var blob = new Blob([exportMd()], { type: 'text/markdown' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'plan-review.md';
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 500);
  });

  render();
  document.body.setAttribute('data-jsready', '1');
})();
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ · plan review</title>
<style>__CSS__</style>
</head>
<body data-plan="__PLANKEY__" data-title="__TITLE__">
<div class="layout">
  <aside class="toc">
    <p class="brand">Plan review</p>
    <p class="planname">__TITLE__</p>
    <div class="toc-tools">
      <button id="expandall" type="button">Expand all</button>
      <button id="collapseall" type="button">Collapse all</button>
    </div>
    <nav>__TOC__</nav>
  </aside>
  <main>
    <p class="eyebrow">Plan · first human gate</p>
    <h1 class="title">__TITLE__</h1>
    <div class="chips">__CHIPS__</div>
    __BET__
    __TIMELINE__
    __SECTIONS__
  </main>
</div>
<div id="qpill">💬 Comment</div>
<div id="lb" role="dialog" aria-modal="true" aria-label="Media preview" hidden>
  <button id="lbclose" type="button" aria-label="Close preview">×</button>
  <figure id="lbfig"></figure>
  <figcaption id="lbcap"></figcaption>
</div>
<div id="bar">
  <span class="cnt" id="ccount"><b>0</b> comments</span>
  <span class="verdict">
    <button id="v-approve" type="button">APPROVE</button>
    <button id="v-revise" type="button">REVISE</button>
  </span>
  <button class="act ghost" id="dlreview" type="button">Download .md</button>
  <button class="act" id="copyreview" type="button">Copy review</button>
</div>
<div id="toast" role="status"></div>
<script>__JS__</script>
</body>
</html>
"""

BET_LABELS = {
    "concept": "Concept",
    "audio": "Audio path",
    "signature": "Signature",
    "arc": "Arc",
}


def build(plan_path: Path, out_path: Path, title_override: str | None):
    text = plan_path.read_text(encoding="utf-8")
    title, bet, validator, preamble, sections = parse_plan(text)
    if title_override:
        title = title_override

    ids: set = set()
    toc, body = [], []
    scene_count = 0
    resolve_media = make_media_resolver(plan_path, out_path.resolve().parent)

    pre_html = ""
    pre_lines = [l for l in preamble if l.strip()]
    if pre_lines:
        pre_subs: list = []
        pre_html = mediafy(render_blocks(preamble, ids, pre_subs), resolve_media)

    all_subs: list = []
    for idx, sec in enumerate(sections, 1):
        sid = slugify(sec["title"], ids)
        subs: list = []
        sec_html = mediafy(render_blocks(sec["lines"], ids, subs), resolve_media)
        all_subs.extend(subs)
        scene_count += sum(1 for s in subs if s["scene"])
        num = f"{idx:02d}"
        clean_title = re.sub(r"^\d+\s*[·.:]\s*", "", sec["title"])
        toc.append(
            f'<a href="#{sid}" data-sec="{sid}"><span class="n">{num}</span>'
            f'{esc(clean_title)}<span class="cb" data-cfor="{sid}"></span></a>'
        )
        for s in subs:
            cls = "sub scene" if s["scene"] else "sub"
            toc.append(
                f'<a class="{cls}" href="#{s["id"]}"><span class="n">·</span>'
                f"{esc(s['title'])}</a>"
            )
        body.append(
            f'<section class="sec" id="{sid}" data-name="{esc(sec["title"])}">'
            f"<details{' open' if idx == 1 else ''}>"
            f'<summary><span class="num">{num}</span>'
            f'<span class="st">{inline(clean_title)}</span>'
            f'<span class="cb" data-cfor="{sid}"></span><span class="chev"></span></summary>'
            f'<div class="secbody">{sec_html}'
            f'<div class="cwrap" data-sec="{sid}">'
            f'<p class="clabel">Review comments</p><div class="clist"></div>'
            f'<div class="cform"><textarea placeholder="Comment on this section… '
            f'(or select any text above to quote it)"></textarea>'
            f'<div class="row"><button type="button">Add comment</button></div></div>'
            f"</div></div></details></section>"
        )

    # scene timeline from §6 h3 timings: "S1 · Name (0–3.6s)"
    scene_re = re.compile(
        r"^S(\d+)\s*·\s*(.*?)\s*\((\d+(?:\.\d+)?)\s*[–-]\s*(\d+(?:\.\d+)?)\s*s?\)(.*)$"
    )
    timed, seen_nums = [], set()
    for s in all_subs:
        m = scene_re.match(s["title"])
        if m and m.group(1) not in seen_nums:
            seen_nums.add(m.group(1))
            timed.append(
                {
                    "num": m.group(1),
                    "name": m.group(2),
                    "a": float(m.group(3)),
                    "b": float(m.group(4)),
                    "peak": "PEAK" in m.group(5).upper(),
                    "id": s["id"],
                }
            )
    timeline_html = ""
    if timed:
        total = max(s["b"] for s in timed)
        segs = []
        for s in timed:
            dur = max(s["b"] - s["a"], 0.1)
            cls = " peak" if s["peak"] else ""
            segs.append(
                f'<a class="tseg{cls}" href="#{s["id"]}" style="flex:{dur:g}" '
                f'title="S{s["num"]} · {esc(s["name"])} ({s["a"]:g}–{s["b"]:g}s)">'
                f'<b>S{s["num"]}</b><span>{dur:g}s</span></a>'
            )
        timeline_html = (
            '<div class="tl-wrap"><div class="tl-head"><b>Timeline</b>'
            f"<span>{total:g}s · click a scene to jump</span></div>"
            f'<div class="timeline">{"".join(segs)}</div></div>'
        )

    if timed:
        scene_count = len(timed)
    chips = [f'<span class="chip">{len(sections)} sections</span>']
    if scene_count:
        chips.append(f'<span class="chip">{scene_count} scenes</span>')
    if bet.get("audio"):
        chips.append(f'<span class="chip">Audio: {esc(bet["audio"][:40])}</span>')
    if validator:
        ok = "✓" in validator and "fails: none" in validator.lower()
        chips.append(
            f'<span class="chip{" ok" if ok else ""}">{esc(validator)}</span>'
        )

    bet_html = ""
    if bet:
        rows = "".join(
            f"<dt>{BET_LABELS[k]}</dt><dd>{inline(bet[k])}</dd>"
            for k in ("concept", "audio", "signature", "arc")
            if k in bet
        )
        bet_html = (
            '<div class="bet"><div class="bet-head"><b>Creative bet</b>'
            "<span>decide in 5 seconds: redirect or keep reading</span></div>"
            f"<dl>{rows}</dl></div>"
        )

    plan_key = re.sub(r"[^\w-]+", "-", title.lower()).strip("-") or "plan"
    page = (
        PAGE.replace("__TITLE__", esc(title))
        .replace("__PLANKEY__", plan_key)
        .replace("__TOC__", "".join(toc))
        .replace("__CHIPS__", "".join(chips))
        .replace("__BET__", bet_html + (f'<div class="sec preamble">{pre_html}</div>' if pre_html else ""))
        .replace("__TIMELINE__", timeline_html)
        .replace("__SECTIONS__", "".join(body))
        .replace("__CSS__", CSS)
        .replace("__JS__", JS)
    )
    out_path.write_text(page, encoding="utf-8")
    return len(sections), scene_count


def main():
    ap = argparse.ArgumentParser(description="Render plan.md as an interactive review HTML")
    ap.add_argument("plan", help="path to plan.md")
    ap.add_argument("-o", "--out", help="output html path (default: alongside plan as plan.html)")
    ap.add_argument("--title", help="override the document title")
    args = ap.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.is_file():
        sys.exit(f"plan-to-html: no such file: {plan_path}")
    out_path = Path(args.out) if args.out else plan_path.with_suffix(".html")

    nsec, nscene = build(plan_path, out_path, args.title)
    print(f"plan-to-html: wrote {out_path} ({nsec} sections, {nscene} scenes)")


if __name__ == "__main__":
    main()
