#!/usr/bin/env python3
"""Render index.html from page.tmpl.html + data/truth.json.

Deterministic: same inputs -> byte-identical output. Stdlib only.
Fails if the dataset fails validation. The output is a single self-contained
index.html: the full board is server-rendered in the HTML (readable by crawlers
that never run JS), with the dataset embedded as JSON for the interactive layer.
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "truth.json"
TMPL = ROOT / "page.tmpl.html"
APPJS = ROOT / "scripts" / "app.js"
OUT = ROOT / "index.html"

VERDICT_META = {
    "working": ("Working", "v-working"),
    "mixed": ("Mixed", "v-mixed"),
    "conditional": ("Conditional", "v-conditional"),
    "not-working": ("Not working", "v-not-working"),
    "myth": ("Myth", "v-myth"),
    "no-effect": ("No effect", "v-no-effect"),
}
PLATFORM_LABEL = {
    "chatgpt": "ChatGPT",
    "google-ai": "Google AI",
    "perplexity": "Perplexity",
    "claude": "Claude",
    "copilot": "Copilot",
}
IMPACT_LABEL = {"high": "High impact", "medium": "Medium impact", "low": "Low impact"}


def board_cards(data):
    out = []
    for t in data["tactics"]:
        label, cls = VERDICT_META[t["verdict"]]
        pp = t.get("per_platform", {})
        plats = ",".join(pp.keys())
        blob = " ".join([t["name"]] + t.get("aliases", []) + [t.get("category", ""), t.get("one_liner", "")]).lower()
        ev_rows = []
        for ev in t.get("evidence", []):
            ev_rows.append(
                "<li>" + e(ev["claim"])
                + ' <a class="src" href="' + e(ev["source"]) + '" target="_blank" rel="noopener">source &rarr;</a>'
                + ' <span class="evd">(' + e(ev["date"]) + ")</span></li>"
            )
        pp_rows = []
        for pid, v in pp.items():
            pv = VERDICT_META.get(v.get("v"), VERDICT_META["conditional"])
            pp_rows.append(
                '<div class="pprow"><span class="v ' + pv[1] + '">' + pv[0] + "</span>"
                + "<span><b>" + e(PLATFORM_LABEL.get(pid, pid)) + "</b></span>"
                + '<span class="ppn">' + e(v.get("note", "")) + "</span></div>"
            )
        pp_block = ""
        if pp_rows:
            pp_block = '<h4>By platform</h4><div class="pprows">' + "".join(pp_rows) + "</div>"
        out.append(
            '<li data-verdict="' + e(t["verdict"]) + '"'
            + ' data-plats="' + e(plats) + '"'
            + ' data-s="' + e(blob) + '">'
            + '<details class="tcard" id="' + e(t["id"]) + '">'
            + "<summary>"
            + '<span class="pl">+</span>'
            + '<span class="v ' + cls + '">' + label + "</span>"
            + '<span class="tname">' + e(t["name"]) + "</span>"
            + '<span class="tcat">' + e(t.get("category", "")) + "</span>"
            + '<p class="tone">' + e(t["one_liner"]) + "</p>"
            + "</summary>"
            + '<div class="tbody">'
            + "<h4>What the evidence says</h4>"
            + '<ul class="evlist">' + "".join(ev_rows) + "</ul>"
            + pp_block
            + '<div class="ind"><b>For industrial sellers:</b> ' + e(t.get("industrial_note", "")) + "</div>"
            + '<p class="meta">Confidence: ' + e(t.get("confidence", "medium"))
            + " &middot; Last verified " + e(t.get("last_verified", "")) + "</p>"
            + "</div></details></li>"
        )
    return "\n".join(out)


def myths_html(data):
    out = []
    for m in data["myths"]:
        out.append(
            '<article class="mcard"><p class="mclaim">' + e(m["claim"]) + "</p>"
            + '<p class="mreal">' + e(m["reality"]) + "</p>"
            + '<a class="msrc src" href="' + e(m["source"]) + '" target="_blank" rel="noopener">source &rarr;</a></article>'
        )
    return "\n".join(out)


def crawler_row(c):
    new = ' <span class="newb">NEW</span>' if c.get("new") else ""
    return (
        '<div class="cwl"><code>' + e(c["token"]) + "</code>" + new
        + '<span class="cwp">' + e(c["purpose"]) + "</span></div>"
    )


def platforms_html(data):
    out = []
    for p in data["platforms"]:
        crawlers = "".join(crawler_row(c) for c in p.get("crawlers", []))
        srcs = " ".join(
            '<a href="' + e(s["url"]) + '" target="_blank" rel="noopener">' + e(s["label"]) + "</a>"
            for s in p.get("sources", [])
        )
        out.append(
            '<article class="pcard"><h3>' + e(p["name"]) + "</h3>"
            + '<p class="pvendor">' + e(p["vendor"]) + "</p>"
            + '<p class="peng"><b>Engine:</b> ' + e(p["engine"]) + "</p>"
            + '<p class="peng"><b>Model now:</b> ' + e(p["current_model"]) + "</p>"
            + '<p class="pcites"><b>How it cites:</b> ' + e(p["cites"]) + "</p>"
            + '<p class="cwhead">Crawler tokens</p>'
            + crawlers
            + '<p class="pnotes">' + e(p["field_notes"]) + "</p>"
            + '<div class="psrcs">' + srcs + "</div>"
            + '<p class="pmeta">Last verified ' + e(p["last_verified"]) + "</p></article>"
        )
    return "\n".join(out)


def timeline_html(data):
    items = []
    for u in sorted(data["updates"], key=lambda x: x["date"], reverse=True):
        plat = PLATFORM_LABEL.get(u["platform"], u["platform"])
        items.append(
            '<li class="tres"><span class="udate">' + e(u["date"]) + "</span>"
            + '<span class="uimp uimp-' + e(u["impact"]) + '">' + e(IMPACT_LABEL[u["impact"]]) + "</span>"
            + '<span class="uplat">' + e(plat) + "</span>"
            + "<h3>" + e(u["title"]) + "</h3>"
            + '<p class="sum">' + e(u["summary"]) + "</p>"
            + '<p class="ub2b"><b>What it means for you:</b> ' + e(u.get("for_b2b", "")) + "</p>"
            + '<a class="usrc src" href="' + e(u["source"]) + '" target="_blank" rel="noopener">source &rarr;</a></li>'
        )
    return "\n".join(items)


def stats_html(data):
    out = []
    for s in data["stats"]:
        out.append(
            '<article class="stat"><p class="sval">' + e(s["value"]) + "</p>"
            + '<p class="slab">' + e(s["stat"]) + "</p>"
            + '<p class="smeta">as of ' + e(s.get("as_of", ""))
            + ' &middot; <a href="' + e(s["source"]) + '" target="_blank" rel="noopener">source &rarr;</a></p></article>'
        )
    return "\n".join(out)


def e(s):
    return html.escape(str(s), quote=True)


def main():
    check = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate.py")])
    if check.returncode != 0:
        print("build: dataset failed validation, aborting")
        return 1
    data = json.loads(DATA.read_text(encoding="utf-8"))
    tmpl = TMPL.read_text(encoding="utf-8")
    js = APPJS.read_text(encoding="utf-8")
    if "</script" in js:
        print("ERROR: app.js contains a closing script tag")
        return 1
    counts = (
        str(len(data["tactics"])) + " tactic verdicts &middot; "
        + str(len(data["myths"])) + " myths &middot; "
        + str(len(data["platforms"])) + " platforms"
    )
    out = tmpl
    for token, value in {
        "{{SWEEP_ID}}": str(data.get("sweep_id", 1)),
        "{{SWEEP_DATE}}": e(data["sweep_date"]),
        "{{COUNTS}}": counts,
        "{{SWEEP_FEED}}": "#updates-sec",
        "{{BOARD_CARDS}}": board_cards(data),
        "{{MYTHS}}": myths_html(data),
        "{{PLATFORMS}}": platforms_html(data),
        "{{TIMELINE}}": timeline_html(data),
        "{{STATS}}": stats_html(data),
        "{{DATA_JSON}}": json.dumps(data, ensure_ascii=False).replace("</", "<\\/"),
        "{{APP_JS}}": js,
    }.items():
        out = out.replace(token, value)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", out)
    if leftover:
        print("ERROR: unreplaced placeholders:", leftover)
        return 1
    OUT.write_text(out, encoding="utf-8")
    print("rendered index.html:", len(out), "bytes,", len(data["tactics"]), "cards")
    return 0


if __name__ == "__main__":
    sys.exit(main())
