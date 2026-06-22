---
name: doctor
description: "Read-only connection check for your AIOS. Shows a green/amber/red table of every external tool (Publer, Cloudflare, nano-banana, Higgsfield), whether its software and login are connected yet, and the one next step for anything that isn't. Never changes anything. Trigger phrases: 'doctor', 'what's connected', 'check my setup', 'is everything connected', 'health check', 'what needs setting up'."
---

# /doctor - what's connected, what isn't

> Run this any time you want to see, at a glance, which of your tools are
> connected and which still need a quick setup. It only looks; it never
> changes anything.

## What this does

Prints one tidy table: every external tool your AIOS can use, grouped by
toolkit (Content, Creative, App), with a colour next to each:

- 🟢 **green** - software installed and signed in. Ready to go.
- 🟡 **amber** - not connected yet. Either it's a paid tool you've chosen to
  leave for later, or the software just isn't installed yet. Not a problem.
- 🔴 **red** - a free tool you'll want connected, with the exact next step.

Amber and red never mean you did something wrong. They just mean "not
connected yet". The closing line says so.

## How to run it

Run the checker script. That's the whole command:

```bash
python3 scripts/doctor.py
```

Then read the table back to the owner exactly as printed. Do not re-interpret
or soften the colors; the script's wording is already calm and chosen for
them. If a row is red or amber, the one-line next step beside it tells you
which `/setup` to run.

## Rules for Claude

1. **Read-only. Always.** Never run `/setup` actions, never write to `.env`,
   never install anything, never commit, from inside `/doctor`. This command
   only reports. If she wants to fix a row, that's `/setup`.
2. **Show the table as printed.** The script already speaks in the owner's voice and
   uses the right colors. Just surface it.
3. **If a tool is amber or red, point at the fix gently**, using the next-step
   text the script printed. For example: "Cloudflare isn't connected yet -
   when you want to put your app live, run `/setup app` and I'll walk you
   through it. Nothing's broken."
4. **No Gmail / Calendar row.** Email and calendar are a later, separate
   capability set up with your builder (they need a connection that can't be
   self-served), so they never show here. If you ask about email, explain
   that plainly rather than treating it as a missing tool.
5. **If the registry isn't built yet**, the script says so kindly - relay that
   and offer to run `/setup`, don't treat it as an error on your side.

## What it reads

- `data/skill_registry.json` - the generated list of every external tool and
  what each needs (software + credential). Built by `build_registry.py`; never
  hand-edited.
- `.env` - to see which keys are filled (the values are never shown back).
- It runs each tool's quick verify command where there is one (a fast,
  read-only check), and looks for the tool's software on the machine.

## When she might run this

- "Is everything connected?"
- After `/setup`, to confirm a tool went green.
- When a skill says it needs setting up and you want the overview.
- When your builder is helping remotely - they can ask you to run `/doctor` and
  read them the table, and they'll know exactly which step you're stuck on.
