#!/usr/bin/env python3
"""Project-manager attention layer for the projects/ register.

Reads the ACTIVE project files and surfaces the two things that let projects
quietly die:
  1. No next step defined  -> it will stall.
  2. Not touched in N days  -> it is drifting and at risk of being forgotten.

This is the "nothing gets lost" engine. Run it standalone for a report, or
import load_status() / brief_block() into the morning brief and /review.

Usage:
    python scripts/projects_status.py              # full report
    python scripts/projects_status.py --brief       # one compact block (for #brief)
    python scripts/projects_status.py --stale 21     # change the drift threshold (days)
"""
import os
import sys
import glob
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTIVE = os.path.join(ROOT, "projects", "active")
DEFAULT_STALE_DAYS = 14
NO_ACTION = {"", "none", "n/a", "-", "tbd"}


def _parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return {}
    fm, key = {}, None
    for ln in lines[1:end]:
        if not ln.strip():
            continue
        if ln.lstrip().startswith("- ") and key == "sources":
            fm.setdefault("sources", []).append(ln.lstrip()[2:].strip())
            continue
        if ":" in ln:
            k, _, v = ln.partition(":")
            key = k.strip()
            v = v.strip().strip('"').strip("'")
            fm["sources"] = [] if key == "sources" else fm.get("sources")
            if key != "sources":
                fm[key] = v
            elif v:
                fm["sources"].append(v)
    return fm


def _days_since(date_str):
    if not date_str:
        return None
    try:
        d = datetime.date.fromisoformat(date_str[:10])
    except ValueError:
        return None
    return (datetime.date.today() - d).days


def load_status(stale_days=DEFAULT_STALE_DAYS):
    items = []
    for path in sorted(glob.glob(os.path.join(ACTIVE, "*.md"))):
        fm = _parse_frontmatter(open(path, encoding="utf-8").read())
        na = (fm.get("next_action") or "").strip()
        age = _days_since(fm.get("last_activity", ""))
        items.append({
            "name": fm.get("name", os.path.basename(path)[:-3]),
            "area": fm.get("area", ""),
            "priority": fm.get("priority", ""),
            "last_activity": fm.get("last_activity", ""),
            "age_days": age,
            "next_action": na,
            "no_next": na.lower() in NO_ACTION,
            "drifting": age is not None and age >= stale_days,
            "path": os.path.relpath(path, ROOT),
        })

    def pk(it):
        try:
            return (0, int(it["priority"]))
        except (ValueError, TypeError):
            return (1, 0)

    items.sort(key=pk)
    return items


def _fmt_age(it):
    return f"{it['age_days']}d" if it["age_days"] is not None else "?"


def brief_block(stale_days=DEFAULT_STALE_DAYS):
    items = load_status(stale_days)
    drifting = [i for i in items if i["drifting"]]
    no_next = [i for i in items if i["no_next"]]
    head = f"Projects: {len(items)} active"
    if drifting:
        head += f" · {len(drifting)} drifting (>{stale_days}d)"
    if no_next:
        head += f" · {len(no_next)} with no next step"
    lines = [head]
    for i in drifting[:5]:
        lines.append(f"  • drifting {_fmt_age(i)}: {i['name']}")
    for i in no_next[:5]:
        lines.append(f"  • no next step: {i['name']}")
    return "\n".join(lines)


def report(stale_days=DEFAULT_STALE_DAYS):
    items = load_status(stale_days)
    drifting = [i for i in items if i["drifting"]]
    no_next = [i for i in items if i["no_next"]]
    out = [f"PROJECT STATUS — {datetime.date.today().isoformat()}",
           f"{len(items)} active projects · drift threshold {stale_days} days", ""]
    if drifting:
        out.append(f"DRIFTING ({len(drifting)}) — no logged movement in {stale_days}+ days:")
        for i in drifting:
            out.append(f"  [{_fmt_age(i):>4}] P{i['priority'] or '-'} {i['name']}")
            out.append(f"         next: {i['next_action'] or '(none set)'}")
        out.append("")
    if no_next:
        out.append(f"NO NEXT STEP ({len(no_next)}) — will stall until you set one:")
        for i in no_next:
            out.append(f"  P{i['priority'] or '-'} {i['name']}  ({i['path']})")
        out.append("")
    healthy = [i for i in items if not i["drifting"] and not i["no_next"]]
    out.append(f"ON TRACK ({len(healthy)}): " + ", ".join(i["name"] for i in healthy[:12])
               + (" ..." if len(healthy) > 12 else ""))
    return "\n".join(out)


def main():
    stale = DEFAULT_STALE_DAYS
    if "--stale" in sys.argv:
        stale = int(sys.argv[sys.argv.index("--stale") + 1])
    if "--brief" in sys.argv:
        print(brief_block(stale))
    else:
        print(report(stale))


if __name__ == "__main__":
    main()
