# New Capability

> Build custom API integrations from official docs — structured, tested, self-healing.

## What This Does

- Gives you a `/new-capability` command that runs a 7-stage guided workflow for connecting any API to your workspace
- Researches official API docs, scopes exactly what you need, designs the architecture, and generates an implementation plan
- Produces a Context Skill that auto-loads whenever the connected service comes up in conversation
- Every integration includes validation tests and self-improving documentation

## What You Need

- A computer (Mac or Linux)
- Claude Code installed
- The AIOS Starter Kit with `/create-plan` and `/implement` commands already set up

## How to Install

1. Give this folder to Claude Code
2. Say: "Read INSTALL.md and help me set this up"
3. Follow along — Claude handles everything

**Estimated setup time:** 2 minutes

## Running Cost

Free. This module is pure methodology (no scripts, no API keys). The APIs you connect will have their own costs and requirements.

## What's Inside

| File | Purpose |
|------|---------|
| `INSTALL.md` | Installation guide (Claude reads this) |
| `README.md` | This file — human overview |

The install creates two files in your `.claude/` folder: a skill definition and a command invoker. No Python scripts, no dependencies.

## How It Works

Run `/new-capability [service name]` and the workflow guides you through:

1. **Intent** — What service, what problem, what use cases
2. **Research** — Deep dive into official API docs
3. **Scope** — Pick exactly which read/write operations you need
4. **Design** — Architecture, auth flow, file inventory, test matrix
5. **Exploration Doc** — Everything compiled into a reference artifact
6. **Plan** — Implementation plan in `/create-plan` format
7. **Handoff** — Ready for `/implement` in a fresh session

Each stage has a stop gate where you review and confirm before moving on.

---

> A plug-and-play module from Liam Ottley's AAA Accelerator — the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
