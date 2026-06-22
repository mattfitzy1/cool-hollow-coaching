#!/usr/bin/env python3
"""Project register CLI — add, move and inspect projects in projects/.

The per-project markdown files are the source of truth; this script creates and
re-files them, then rebuilds the README index so it never drifts. Used by the
/project skill, but works standalone too.

Usage:
    python scripts/project.py add "Lesson video shoot" \
        --area "Content" --next "Storyboard the three lessons" \
        --summary "Film and edit the module lesson videos" --sources plans/foo.md
    python scripts/project.py move lesson-video-shoot --to shipped
    python scripts/project.py status            # drift / no-next-step report
    python scripts/project.py list [--all]       # active list (or every bucket)
"""
import os
import re
import sys
import glob
import argparse
import datetime
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJ = os.path.join(ROOT, "projects")
SCRIPTS = os.path.join(ROOT, "scripts")
BUCKETS = ["active", "shipped", "parked", "shelved"]


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)[:60]


def find_file(slug):
    for b in BUCKETS:
        p = os.path.join(PROJ, b, f"{slug}.md")
        if os.path.exists(p):
            return p, b
    return None, None


def rebuild_index():
    subprocess.run([sys.executable, os.path.join(SCRIPTS, "projects_index.py")],
                   check=False)


def set_fm_line(text, key, val):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return text
    for i in range(1, end):
        if lines[i].split(":", 1)[0].strip() == key:
            lines[i] = f"{key}: {val}"
            return "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    return text


def cmd_add(args):
    slug = args.slug or slugify(args.name)
    existing, _ = find_file(slug)
    if existing:
        print(f"Already exists: {os.path.relpath(existing, ROOT)} — edit it or use a different --slug.")
        return 1
    bucket = args.bucket
    today = datetime.date.today().isoformat()
    sources = [s.strip() for s in (args.sources or "").split(",") if s.strip()]
    src_block = "\n".join("  - " + s for s in sources) if sources else "  -"
    fm = (
        f"---\nname: {args.name}\narea: {args.area}\nstatus: {bucket}\npriority: \n"
        f"last_activity: {today}\nnext_action: {args.next or 'none'}\n"
        f"summary: {args.summary or args.name}\nsources:\n{src_block}\n---\n"
    )
    body = (
        f"\n# {args.name}\n\n"
        f"**What it is.** {args.summary or '(fill in)'}\n\n"
        f"**Current state.** Created {today}. (fill in)\n\n"
        f"**Next.** {args.next or '(set a next step)'}\n\n"
        f"**Key links.**\n" + ("\n".join("- " + s for s in sources) if sources else "- (add links)") + "\n"
    )
    dest_dir = os.path.join(PROJ, bucket)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, f"{slug}.md")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(fm + body)
    print(f"Created {os.path.relpath(dest, ROOT)}")
    rebuild_index()
    return 0


def cmd_move(args):
    src, cur_bucket = find_file(args.slug)
    if not src:
        print(f"No project file for slug '{args.slug}'.")
        return 1
    if args.to not in BUCKETS:
        print(f"--to must be one of {BUCKETS}")
        return 1
    text = open(src, encoding="utf-8").read()
    text = set_fm_line(text, "status", args.to)
    if args.to != "active":
        text = set_fm_line(text, "priority", "")
    dest = os.path.join(PROJ, args.to, f"{args.slug}.md")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(text)
    if os.path.abspath(dest) != os.path.abspath(src):
        os.remove(src)
    print(f"Moved {args.slug}: {cur_bucket} -> {args.to}")
    rebuild_index()
    return 0


def cmd_status(_args):
    sys.path.insert(0, SCRIPTS)
    import projects_status
    print(projects_status.report())
    return 0


def cmd_list(args):
    buckets = BUCKETS if args.all else ["active"]
    for b in buckets:
        files = sorted(glob.glob(os.path.join(PROJ, b, "*.md")))
        print(f"\n[{b}] ({len(files)})")
        for p in files:
            print("  " + os.path.basename(p)[:-3])
    return 0


def main():
    ap = argparse.ArgumentParser(description="Project register CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="add a new project")
    a.add_argument("name")
    a.add_argument("--area", default="Uncategorised")
    a.add_argument("--bucket", default="active", choices=BUCKETS)
    a.add_argument("--next", default="")
    a.add_argument("--summary", default="")
    a.add_argument("--sources", default="")
    a.add_argument("--slug", default="")
    a.set_defaults(func=cmd_add)

    m = sub.add_parser("move", help="re-file a project to another bucket")
    m.add_argument("slug")
    m.add_argument("--to", required=True)
    m.set_defaults(func=cmd_move)

    s = sub.add_parser("status", help="drift / no-next-step report")
    s.set_defaults(func=cmd_status)

    ls = sub.add_parser("list", help="list projects")
    ls.add_argument("--all", action="store_true")
    ls.set_defaults(func=cmd_list)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
