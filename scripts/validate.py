#!/usr/bin/env python3
"""Validate data/truth.json before anything renders or ships.

Rules:
  - parses as JSON
  - top-level required keys present
  - platforms/tactics have unique ids; verdicts are from the enum
  - every evidence item, update, platform source and stat carries an https URL
  - dates parse as YYYY, YYYY-MM or YYYY-MM-DD
  - sweep_date present and parseable
Exit 0 = valid. Exit 1 = invalid with reasons printed.
"""
import json
import re
import sys
from pathlib import Path

VERDICTS = {"working", "mixed", "conditional", "not-working", "myth"}
PLATFORM_IDS = {"chatgpt", "google-ai", "perplexity", "claude", "copilot"}
URL_RE = re.compile(r"^https://\S+$")
DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


def main() -> int:
    path = Path(__file__).resolve().parent.parent / "data" / "truth.json"
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"FATAL: truth.json does not parse: {e}")
        return 1

    for key in ("sweep_date", "platforms", "tactics", "myths", "updates", "stats"):
        if key not in data:
            errors.append(f"missing top-level key: {key}")
    if errors and not data.get("sweep_date"):
        print("\n".join(errors))
        return 1

    if not DATE_RE.match(str(data.get("sweep_date", ""))):
        errors.append(f"sweep_date not YYYY-MM-DD: {data.get('sweep_date')}")

    ids = set()
    for p in data.get("platforms", []):
        pid = p.get("id")
        if not pid:
            errors.append("platform without id")
            continue
        if pid in ids:
            errors.append(f"duplicate platform id: {pid}")
        ids.add(pid)
        for s in p.get("sources", []):
            if not URL_RE.match(s.get("url", "")):
                errors.append(f"{pid}: platform source url invalid: {s.get('url')}")
        for c in p.get("crawlers", []):
            if not c.get("token"):
                errors.append(f"{pid}: crawler without token")

    tids = set()
    for t in data.get("tactics", []):
        tid = t.get("id")
        if not tid:
            errors.append("tactic without id")
            continue
        if tid in tids:
            errors.append(f"duplicate tactic id: {tid}")
        tids.add(tid)
        if t.get("verdict") not in VERDICTS:
            errors.append(f"{tid}: verdict '{t.get('verdict')}' not in {sorted(VERDICTS)}")
        if not t.get("one_liner"):
            errors.append(f"{tid}: missing one_liner")
        for ev in t.get("evidence", []):
            if not URL_RE.match(ev.get("source", "")):
                errors.append(f"{tid}: evidence source url invalid: {ev.get('source')}")
            if not DATE_RE.match(str(ev.get("date", ""))):
                errors.append(f"{tid}: evidence date invalid: {ev.get('date')}")
        pp = t.get("per_platform", {})
        for pid, v in pp.items():
            if pid not in PLATFORM_IDS:
                errors.append(f"{tid}: per_platform unknown platform '{pid}'")
            if isinstance(v, dict) and v.get("v") and v["v"] not in VERDICTS | {"no-effect"}:
                errors.append(f"{tid}: per_platform[{pid}] verdict '{v.get('v')}' invalid")
        if not DATE_RE.match(str(t.get("last_verified", ""))):
            errors.append(f"{tid}: last_verified invalid: {t.get('last_verified')}")

    for m in data.get("myths", []):
        if not URL_RE.match(m.get("source", "")):
            errors.append(f"myth source invalid: {m.get('source')}")

    for u in data.get("updates", []):
        if not DATE_RE.match(str(u.get("date", ""))):
            errors.append(f"update date invalid: {u.get('date')} ({u.get('title')})")
        if not URL_RE.match(u.get("source", "")):
            errors.append(f"update source invalid: {u.get('source')} ({u.get('title')})")
        if u.get("impact") not in {"high", "medium", "low"}:
            errors.append(f"update impact invalid: {u.get('impact')} ({u.get('title')})")

    for s in data.get("stats", []):
        if not URL_RE.match(s.get("source", "")):
            errors.append(f"stat source invalid: {s.get('stat')}")
        if not s.get("value"):
            errors.append(f"stat without value: {s.get('stat')}")

    if errors:
        print(f"INVALID — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(
        f"VALID: {len(data.get('platforms', []))} platforms, "
        f"{len(data.get('tactics', []))} tactics, {len(data.get('myths', []))} myths, "
        f"{len(data.get('updates', []))} updates, {len(data.get('stats', []))} stats "
        f"(sweep {data.get('sweep_date')})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
