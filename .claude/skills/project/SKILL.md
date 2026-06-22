---
name: project
description: >
  Capture, re-file and inspect projects in the project register (projects/).
  Use when the owner wants to start/add a new project, mark one done/parked/killed,
  or see what they are working on and what is drifting.
  Triggers on: start a project, add a project, new project, track this project,
  mark project X done/finished, park project X, shelve/kill project X, project
  status, what's drifting, what am I working on, show my projects, project list,
  what projects are stalling. This is the register of PROJECTS (the containers) -
  the things the owner is working on across the business and their own life.
---

# /project — Project register capture and management

> One-line management of the project register at `projects/`. Backed by
> `scripts/project.py` (engine) and `scripts/projects_index.py` (auto-rebuilds
> the README index after every change, so it never drifts).

## Variables

request: $ARGUMENTS (the project to add, the project + action, or a status ask)

## Background

The register lives in `projects/{active,shipped,parked,shelved}/` - one curated
markdown file per project. `active/` is the tight working list. Use the areas
already in use across the existing project files (read `projects/README.md` to
see them); always pick the closest existing area and do not invent new ones
without reason.

This register tracks **projects** (the containers) - the bigger pieces of work
the owner is carrying, so nothing quietly falls off the radar.

## Decide what the request wants

1. **Add a new project** ("start/add/track a project for X")
2. **Re-file an existing one** ("mark X done", "park X", "shelve/kill X")
3. **Inspect** ("project status", "what's drifting", "what am I working on")

## 1. Add a new project

- Derive the fields from the request; do not over-interview. Only ask the owner if
  the **name** or **area** is genuinely unclear — otherwise infer and proceed,
  stating what you chose.
  - **name**: a clear human name.
  - **area**: the closest existing area (see `projects/README.md`).
  - **next**: the next concrete step (ask if none is evident — a project with no
    next step will stall, which is the whole thing we are preventing).
  - **summary**: one punchy line (<160 chars).
  - **sources**: if the request references existing files (a plan, a memory file,
    an outputs folder, a debrief), pass them comma-separated so the file links back.
  - **bucket**: default `active`. Use another only if the owner says it is already
    done/parked.
- Run:
  ```
  python3 scripts/project.py add "<name>" --area "<area>" --next "<next step>" \
      --summary "<one-liner>" --sources "<path1,path2>"
  ```
- The script writes `projects/<bucket>/<slug>.md` and rebuilds the index. Then
  open the new file and flesh out **Current state** if you know more than the
  skeleton. Confirm to the owner with the path and what you set.

## 2. Re-file an existing project

- Map the verb to a bucket: done/finished/shipped → `shipped`; park/pause → `parked`;
  kill/shelve/drop → `shelved`; reactivate/resume → `active`.
- Find the slug (it is the filename; `python3 scripts/project.py list --all` if unsure).
- Run: `python3 scripts/project.py move <slug> --to <bucket>` (rebuilds the index).
- If a project just moved forward (not buckets), instead edit its file's
  `last_activity` (today) and `next_action`, then run `python3 scripts/projects_index.py`.

## 3. Inspect

- Status / drift: `python3 scripts/project.py status` — shows active projects that
  are drifting (no logged movement 14+ days) or have no next step. Present the
  drifting ones first; these are what is at risk of being lost.
- What am I working on / list: `python3 scripts/project.py list` (active) or
  `--all` (every bucket). For the full grouped view, read `projects/README.md`.

## Rules

- US English, no em dashes, no buzzwords. Never invent facts for a project file -
  ground **Current state** in the sources or leave it as "(fill in)".
- Never hand-edit `projects/README.md` - it is auto-generated; edit the per-project
  file and re-run the index.
- Keep `active/` honest: if the owner adds something that is really just an idea, put it
  in `parked` (or capture it in `content/inbox.md`), not active.
