#!/usr/bin/env python3
"""Regenerate the static site from editions/*/edition.json.

The site itself has no build step: every page is committed as plain HTML.
This helper only saves you hand-copying when you add a weekly edition.
Usage:  python3 tools/build.py
"""
import json, glob, os, html
from email.utils import format_datetime
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://workplaceleaders.ch/"
TITLE = "Workplace Leader Weekly Agenda"
TAGLINE = "A weekly executive agenda for workplace leaders: Microsoft 365, identity and AI signals that pass the budget, risk and friction gate."

e = html.escape

MARKS = {
    "square": '<rect class="solid" x="1" y="1" width="14" height="14"/>',
    "cross": '<polygon points="6,1.5 10,1.5 10,6 14.5,6 14.5,10 10,10 10,14.5 6,14.5 6,10 1.5,10 1.5,6 6,6"/>',
    "grid": '<rect x="1.5" y="1.5" width="5" height="5"/><rect x="9.5" y="1.5" width="5" height="5"/><rect x="1.5" y="9.5" width="5" height="5"/><rect x="9.5" y="9.5" width="5" height="5"/>',
    "meter": '<circle cx="8" cy="8" r="6.5"/><line x1="8" y1="8" x2="12" y2="4"/>',
    "frame": '<rect x="1.5" y="1.5" width="13" height="13"/><rect x="5.5" y="5.5" width="5" height="5"/>',
    "pulse": '<polyline points="1,8 5,8 7,3 9,13 11,8 15,8"/>',
    "rings": '<circle cx="6" cy="8" r="4.5"/><circle cx="10" cy="8" r="4.5"/>',
    "target": '<circle cx="8" cy="8" r="6.5"/><circle cx="8" cy="8" r="2.5"/>',
    "stop": '<circle cx="8" cy="8" r="6.5"/><line x1="3.4" y1="12.6" x2="12.6" y2="3.4"/>',
    "calendar": '<rect x="1.5" y="2.5" width="13" height="12"/><line x1="1.5" y1="6" x2="14.5" y2="6"/><line x1="5" y1="1" x2="5" y2="3.5"/><line x1="11" y1="1" x2="11" y2="3.5"/>',
}

def mark(kind, size=13, red=False):
    cls = "mk red" if red else "mk"
    return f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 16 16" aria-hidden="true">{MARKS[kind]}</svg>'

def kick(kind, text, red=False):
    return f'<span class="label kick">{mark(kind, 13, red)}{e(text)}</span>'

def url(ed, key):
    if key.startswith("mc:"):
        return "https://mc.merill.net/message/" + key[3:]
    return ed["urls"][key]

LENS = {"Budget": "Budget &amp; Commercial", "Risk": "Risk &amp; Governance", "Friction": "Workplace Friction"}

def head(title, desc, prefix, canonical, og_type="article"):
    return f"""<!doctype html>
<html lang="en-CH">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="{TITLE}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{TITLE}" href="{SITE}feed.xml">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<div class="page">
"""

def mast(prefix, right_left, current):
    nav = [("Latest", prefix or "./", "latest"), ("Archive", prefix + "archive/", "archive"), ("RSS", prefix + "feed.xml", "rss")]
    links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if k == current else ""}>{t}</a>' for t, h, k in nav)
    return f"""<header class="row mast">
  <div class="l label"><a class="brand" href="{prefix or './'}">{mark("cross", 13, True)}{TITLE}</a></div>
  <div class="r label"><span>{right_left}</span><nav aria-label="Site">{links}</nav></div>
</header>
"""

def foot(left):
    return f"""<footer class="hair foot label"><span>{left}</span><span>No cookies, no tracking.</span></footer>
</div>
</body>
</html>
"""

def sechead(num, kicker, title, aside=""):
    t = f"<h2>{e(title)}</h2>" if title else ""
    return f"""<div class="hair row sechead">
  <div class="l"><div class="secnum">{num}</div></div>
  <div class="r"><div class="top">{kicker}{aside}</div>{t}</div>
</div>
"""

def edition_body(ed, prefix, permalink):
    o = []
    o.append(mast(prefix, f'{e(ed["date_long"])} · KW {ed["kw"]} · Europe/Zurich', "latest"))
    # 01 Big Trade-Off
    o.append(f"""<section class="row hero" aria-labelledby="tradeoff">
  <div class="l"><div class="secnum">01</div><div style="margin-top:12px">{kick("square", "The Big Trade-Off", True)}</div></div>
  <div class="r"><h1 id="tradeoff">{ed["headline_html"]}</h1></div>
</section>
<div style="margin-top:56px">
""")
    for i, (k, v) in enumerate(ed["tradeoff"]):
        cls = "trade row " + ("hair decision" if i == 2 else "hair-l")
        o.append(f'<div class="{cls}"><div class="l k">{e(k)}</div><p class="r body">{e(v)}</p></div>\n')
    o.append("</div>\n")
    figs = "".join(f'<div class="fig"><div class="v{" red" if red else ""}">{e(v)}</div><div class="label" style="margin-top:8px">{e(l)}</div></div>' for v, l, red in ed["figures"])
    o.append(f'<div class="row figs hair"><div class="l label" style="padding-top:12px">This week</div><div class="r">{figs}</div></div>\n')
    # 02 Pillars
    o.append(sechead("02", kick("grid", "The 4-Pillar Executive Agenda"), "Four pillars, one decision each."))
    for p in ed["pillars"]:
        srcs = "".join(f'<a class="src" href="{e(url(ed, k))}" rel="noopener">{e(l)} ↗</a>' for l, k in p["sources"])
        o.append(f"""<section class="row pillar hair">
  <div class="l"><div class="pnum">{p["n"]}</div><div style="margin-top:18px">{kick(p["mark"], p["tag"])}</div><div class="pname">{e(p["name"])}</div></div>
  <div class="r">
    <h3>{e(p["subtitle"])}</h3>
    <div class="cols">
      <div class="hair-l"><div class="label">The Reality Check</div><p class="body">{e(p["reality"])}</p></div>
      <div class="hair act"><div class="label red">The Leadership Action</div><p class="body">{e(p["action"])}</p></div>
    </div>
    <div class="srcline"><span class="label">Sources</span><span class="links">{srcs}</span></div>
  </div>
</section>
""")
    # 03 Calls
    o.append(sechead("03", kick("target", "Weekly Executive Action List"), "The 3 calls to make."))
    calls = "".join(f'<div class="call hair"><div class="n">{i+1}</div><div class="who">Call with {e(w)}</div><p class="body">{e(t)}</p></div>' for i, (w, t) in enumerate(ed["calls"]))
    o.append(f'<div class="row calls"><div class="l"></div><div class="r">{calls}</div></div>\n')
    # 04 Anti-pattern
    o.append(sechead("04", kick("stop", "The Anti-Pattern · What to stop doing this week", True), ""))
    o.append(f"""<div class="row anti">
  <div class="l">{mark("stop", 40, True)}</div>
  <div class="r"><div class="head">{e(ed["antipattern_head"])}</div><p class="body">{e(ed["antipattern_body"])}</p></div>
</div>
""")
    # 05 Cliffs
    aside = f'<span class="label kick" style="gap:8px">{mark("square", 10, True)}Decision needed this quarter</span>'
    o.append(sechead("05", kick("calendar", "Upcoming Cliffs"), "Dated deadlines.", aside))
    for d, what, ref, hot in ed["cliffs"]:
        m = f'<span style="margin-right:8px">{mark("square", 10, True)}</span>' if hot else ""
        o.append(f'<div class="row cliff hair-l"><div class="l{" red" if hot else ""}">{m}{e(d)}</div><div class="r"><span class="what">{e(what)}</span><span class="label">{e(ref)}</span></div></div>\n')
    # Appendix
    n = len(ed["items"])
    o.append(sechead("A", kick("grid", "Appendix"), f"The {'ten' if n == 10 else n} signals behind this agenda.", f'<span class="label" data-shown>{n} of {n} shown</span>'))
    def cnt(l): return sum(1 for i in ed["items"] if l in i["lenses"])
    def scnt(s): return sum(1 for i in ed["items"] if i["severity"] == s)
    def btn(key, val, text, c=None, on=False):
        cc = f'<span class="c">{c}</span>' if c is not None else ""
        return f'<button type="button" data-key="{key}" data-value="{val}" aria-pressed="{"true" if on else "false"}">{text}{cc}</button>'
    o.append('<div class="filters">\n')
    o.append(f'<div class="row filter hair-l"><div class="l label">Lens</div><div class="r">{btn("lens","All","All",n,True)}{btn("lens","Budget","Budget &amp; Commercial",cnt("Budget"))}{btn("lens","Risk","Risk &amp; Governance",cnt("Risk"))}{btn("lens","Friction","Workplace Friction",cnt("Friction"))}</div></div>\n')
    sev_btns = btn("sev", "All", "All", None, True) + "".join(btn("sev", s, s, scnt(s)) for s in ["High", "Medium", "Low"] if scnt(s))
    o.append(f'<div class="row filter hair-l"><div class="l label">Severity</div><div class="r">{sev_btns}</div></div>\n')
    o.append(f'<div class="row filter hair-l"><div class="l label">Sort</div><div class="r">{btn("sort","severity","Severity",None,True)}{btn("sort","deadline","Deadline")}</div></div>\n')
    o.append('</div>\n<div class="items" data-items>\n')
    for idx, i in enumerate(ed["items"]):
        sev_mark = mark("square", 10, True) if i["severity"] == "High" else mark("frame", 10)
        mc = f' · {e(i["mc"])}' if i["mc"] else ""
        o.append(f"""<article class="row item hair" data-lenses="{' '.join(i['lenses'])}" data-sev="{i['severity']}" data-date="{i['sortDate']}">
  <div class="l"><div class="idx">A.{idx+1:02d}</div><div class="sev{' red' if i['severity']=='High' else ''}">{sev_mark}{e(i["severity"])}</div><div class="label" style="margin-top:14px">{e(i["deadline"])}</div></div>
  <div class="r">
    <div class="label red">{"  /  ".join(LENS[l] for l in i["lenses"])}</div>
    <h4>{e(i["title"])}</h4>
    <p class="body">{e(i["sowhat"])}</p>
    <div class="meta">
      <div class="wide hair-l"><div class="label">Recommended action</div><div>{e(i["action"])}</div></div>
      <div class="narrow hair-l"><div class="label">Teams affected</div><div>{e(i["teams"])}</div><div class="label" style="margin-top:14px">Source</div><div>{e(i["feed"])}{mc}<br><a class="src" href="{e(url(ed, i['url']))}" rel="noopener">{e(i["site"])} ↗</a></div></div>
    </div>
  </div>
</article>
""")
    o.append("</div>\n")
    o.append(f'<div class="row hair-l" style="margin-top:56px;padding-top:14px"><div class="l label">Discarded this week</div><p class="r body small">{e(ed["discarded"])}</p></div>\n')
    o.append(f'<div class="row hair-l" style="margin-top:24px;padding-top:14px"><div class="l label">Method</div><p class="r body small">{e(ed["method"])}</p></div>\n')
    o.append(f'<div class="row hair-l" style="margin-top:24px;padding-top:14px"><div class="l label">Permalink</div><p class="r body small"><a class="src" href="{permalink}">{permalink}</a></p></div>\n')
    o.append(f'<script src="{prefix}assets/filters.js" defer></script>\n')
    o.append(foot(f'{TITLE} · KW {ed["kw"]} / {ed["date"][:4]}'))
    return "".join(o)

def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    eds = []
    for p in sorted(glob.glob(os.path.join(ROOT, "editions", "*", "edition.json")), reverse=True):
        with open(p, encoding="utf-8") as f:
            eds.append(json.load(f))
    if not eds:
        raise SystemExit("no editions found")
    for i, ed in enumerate(eds):
        permalink = f'{SITE}editions/{ed["date"]}/'
        title = f'{ed["tradeoff_title"]} · {TITLE}, {ed["date_long"]}'
        write(f'editions/{ed["date"]}/index.html', head(title, ed["summary"], "../../", permalink) + edition_body(ed, "../../", permalink))
    latest = eds[0]
    permalink = f'{SITE}editions/{latest["date"]}/'
    write("index.html", head(f'{TITLE}: {latest["tradeoff_title"]}', latest["summary"], "", permalink) + edition_body(latest, "", permalink))
    # archive
    rows = "".join(f"""<div class="row arch hair-l"><div class="l"><div class="secnum" style="font-size:28px">{e(ed["date"])}</div><div class="label" style="margin-top:8px">KW {ed["kw"]}</div></div><div class="r"><a class="t" href="../editions/{ed["date"]}/">{e(ed["tradeoff_title"])}</a><p class="body small" style="margin-top:8px">{e(ed["summary"])}</p></div></div>
""" for ed in eds)
    write("archive/index.html", head(f"Archive · {TITLE}", "All editions of the " + TITLE + ".", "../", SITE + "archive/", "website")
          + mast("../", "All editions", "archive")
          + f'<section class="row hero"><div class="l">{kick("grid", "Archive")}</div><div class="r"><h1>All editions.</h1></div></section>\n<div style="margin-top:56px" class="hair"></div>\n' + rows
          + foot(TITLE))
    # feed
    items = ""
    for ed in eds:
        link = f'{SITE}editions/{ed["date"]}/'
        items += f"""    <item>
      <title>{e(ed["tradeoff_title"])}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{ed["pubdate_rfc822"]}</pubDate>
      <description>{e(ed["summary"])}</description>
    </item>
"""
    write("feed.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{TITLE}</title>
    <link>{SITE}</link>
    <description>{e(TAGLINE)}</description>
    <language>en-ch</language>
    <lastBuildDate>{eds[0]["pubdate_rfc822"]}</lastBuildDate>
    <atom:link href="{SITE}feed.xml" rel="self" type="application/rss+xml"/>
{items}  </channel>
</rss>
""")
    print(f"built {len(eds)} edition(s); latest {latest['date']}")

if __name__ == "__main__":
    main()
