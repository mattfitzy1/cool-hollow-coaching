# New App

> Turn Pencil designs into production apps with a 4-phase planning command that does the architecture thinking for you.

## What This Does

- Gives you a `/new-app` command that reads your Pencil mockup and produces a phased Master App Plan
- Automatically extracts a design system (colors, fonts, spacing) from your mockup so styling stays locked across sessions
- Analyzes your existing codebase for reusable patterns before writing anything new
- Produces build phases designed for `/create-plan` + `/implement` — you build one chunk at a time

## What You Need

- A computer (Mac or Linux)
- Claude Code installed
- The AIOS Starter Kit with `/create-plan` and `/implement` commands
- A Pencil account (free at pencil.dev)

## How to Install

1. Give this folder to Claude Code
2. Say: "Read INSTALL.md and help me set this up"
3. Follow along — Claude handles everything

**Estimated setup time:** 5-10 minutes

## Running Cost

Free. Pencil has a free tier. This module is pure methodology — no scripts, no API keys, no ongoing costs.

## What's Inside

| File | Purpose |
|------|---------|
| `INSTALL.md` | Installation guide (Claude reads this) |
| `README.md` | This file — human overview |

The install creates three things in your workspace:
- A `/new-app` command (`.claude/commands/new-app.md`)
- A Design System Enforcer skill (`.claude/skills/app-design-system/SKILL.md`)
- A Pencil MCP connection (so Claude can read your `.pen` design files)

## How It Works

Design your app in Pencil, then run `/new-app` and the workflow guides you through:

1. **Gather Requirements** — Claude reads your Pencil mockup, asks about purpose, data sources, and backend needs
2. **Extract & Analyze** — Pulls a design system from your mockup (colors, fonts, components) and researches your codebase for patterns to reuse
3. **Scope Review** — Presents everything it found: design system, tech stack recommendation, database plan. You confirm before anything is locked.
4. **Master Plan** — Generates a phased build plan. Each phase is a self-contained chunk you implement with `/create-plan` + `/implement`.

The Design System Enforcer runs in the background during every coding session, making sure you only use the locked tokens from your design system. No more style drift.

## The Full Pipeline

```
Pencil mockup → /new-app → Master Plan → /create-plan (per phase) → /implement → working app
```

---

> A plug-and-play module from Liam Ottley's AAA Accelerator — the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
