---
name: tasklist
description: "Generate a structured daily task list as a formatted .docx file"
---

# /tasklist

Generate a structured daily task list as a professionally formatted .docx file with a warm coral sunrise theme.

---

## What this command does

Reads your workspace context files, HISTORY.md, the previous day's work log and task list, and today's calendar to produce a categorised daily task list. Tasks are grouped by category (not priority-ordered). The output is a .docx file saved to `outputs/`.

---

## Step 1: Load context

Read these files to understand the current state of the business:

1. `context/business-info.md` — active clients, projects, product status, team
2. `context/current-data.md` — financials, build progress, blockers, metrics
3. `context/strategy.md` — priorities, validation progress, key events, targets
4. `context/personal-info.md` — background, working patterns, brand voice
5. `HISTORY.md` — recent workspace activity and what has changed

CLAUDE.md is already loaded from `/prime`. Use its context summary for current focus and priorities.

---

## Step 2: Find previous day's outputs

Search the `outputs/` directory for:

1. **Previous day's work log** — look for files matching `worklog-*.md` or similar patterns with yesterday's date. Extract:
   - Completed tasks (for context, do not re-add)
   - Not-completed tasks (carry forward)
   - Meeting outcomes and action items
   - Next steps noted

2. **Previous day's task list** — look for files matching `Task_List_*.docx` (or whatever pattern the workspace uses) with yesterday's date. Extract:
   - Any unchecked or incomplete items (carry forward)
   - Note how many days each item has been carrying forward

If no previous work log or task list is found, ask the user for rough notes or confirm they want a calendar-based task list only.

---

## Step 3: Check today's calendar

Use the Notion MCP server to search for today's calendar events.

**Query:** Search Notion with `calendar [today's day] [today's date] [month] [year] today`

Google Calendar syncs to Notion, so calendar events appear in search results with type `google-calendar`. Times are stored in UTC. **Convert to the user's local timezone** (read from `context/personal-info.md` if specified, otherwise ask).

Extract:
- Event name
- Start and end time (converted to local timezone)
- Any relevant context or attendees

If Notion search returns no calendar results, note this and proceed without calendar events.

---

## Step 4: Source and categorise tasks

Tasks come from these sources:

1. **Calendar events** — today's meetings with any prep tasks
2. **Previous work log** — not-completed items carry forward
3. **Previous task list** — unchecked items carry forward with day count
4. **HISTORY.md** — recent activity that implies follow-up work
5. **Context files** — current priorities and blockers from strategy.md and current-data.md
6. **Rough notes** — if the user provides them instead of a work log

**Categorise by project or area, not by priority.** Use categories based on what is actually active in this workspace. Read `context/business-info.md` and `context/strategy.md` to identify the user's active projects, clients, and focus areas — those become your category headings. Typical category shapes:

- Active client work (one heading per significant client, named after the client)
- Product / build work
- Business Development / Outreach
- Learning / Mentorship (if relevant)
- Personal Brand / Content
- Internal and Admin

Only include categories that have tasks today. Do not create empty sections. Do not invent client names — pull them from the context files.

---

## Step 5: Apply carry-forward rules

- Note how many days an item has been carrying forward (e.g. "Day 3")
- Do NOT add urgency flags or escalation language unless the user explicitly asks
- If items have been rolling 3+ days, include a gentle observation in the Notes section at the end
- If the user says to deprioritise something, remove pressure language and keep it as a simple line item
- Carried-forward items get their own section at the bottom (before Internal and Admin) if there are 3 or more. Otherwise fold them into their category with the day count noted.

---

## Step 6: Generate the .docx

Read the docx skill at `/mnt/skills/public/docx/SKILL.md` and follow its instructions for creating the file using Node.js with the `docx` npm package.

### Warm coral sunrise colour palette

| Element | Colour | Hex |
|---------|--------|-----|
| Page background | Off-white warm | No fill (white default) |
| H1 heading text (name + title) | Deep coral | #7A3518 |
| H2 section headings | Coral | #C4582A |
| Body text | Near-black | #1A1A1A |
| Sub-bullets text | Warm grey | #555555 |
| Note callout prefix ("Note:") | Coral accent, bold | #D85A30 |
| Note callout text | Coral accent | #D85A30 |
| Divider lines (bottom border) | Light peach | #FDDCCC |
| Footer text | Warm muted | #8B6B5A |
| Carried forward day count | Coral muted | #C4582A |

### Document specifications

- **Page:** A4 (11906 x 16838 DXA)
- **Margins:** 1440 DXA all sides
- **Font:** Arial throughout
- **Body text:** size 22 (11pt)
- **Heading 1:** size 36-40, bold, colour #7A3518
- **Heading 2:** size 28, bold, colour #C4582A
- **Bullets:** two-level, LevelFormat.BULLET
  - Level 0: filled circle, left indent 720, hanging 360
  - Level 1: open circle, left indent 1440, hanging 360, colour #555555
- **Notes:** indented 720, colour #D85A30, bold "Note:" prefix
- **Footer text:** size 20, colour #8B6B5A
- **Dividers:** bottom border on paragraph, SINGLE style, size 6, colour #FDDCCC
- **All times in the user's local timezone** (read from `context/personal-info.md`)

### Document structure

```
[User Name from context/personal-info.md]   (H1, size 40, bold, #7A3518)
Daily Task List                              (H1, size 40, bold, #7A3518)
[Day Date Month Year] (Local TZ)             (size 22, colour #8B6B5A)

--- divider (coral peach) ---

Today's Calendar (Local TZ)          (H2, #C4582A)
  [bullets: calendar events with times in local timezone]
  [Note: scheduling observations if relevant]

[Category Section]                   (H2, #C4582A)
  [optional context paragraph, plain text size 22]
  [bullet tasks]
    [sub-bullets for detail]

[More category sections as needed]

Carried Forward                      (H2, #C4582A, only if 3+ items rolling)
  [items with day count noted in coral]

Internal and Admin                   (H2, #C4582A)
  [End of day: complete work log]

--- divider (coral peach) ---

Notes                                (bold, size 24, #C4582A)
[summary observations, gentle carry-forward notes, scheduling advice]

--- divider (coral peach) ---

[Footer: "Generated [date] [time] [Local TZ]", colour #8B6B5A, size 20]
```

### Critical docx rules

- Use `LevelFormat.BULLET` with numbering config for bullets. NEVER use unicode bullet characters.
- Use `ShadingType.CLEAR` not `SOLID` for any shading.
- Use paragraph bottom borders for dividers, never tables as dividers.
- Set page size explicitly as A4 (11906 x 16838 DXA).
- Use exact style IDs to override built-in styles: "Heading1", "Heading2".
- After generating, validate the .docx is well-formed (open it, or check the file is non-empty and parses).

### Output filename

`Task_List_[D]_[Month]_[Year].docx`

Example: `Task_List_26_March_2026.docx`

Save to `outputs/tasklist/`. If the user has a Drive routing rule for task lists configured in `context/business-info.md`, also copy there.

---

## Step 7: Present the output

After generating:

1. Tell the user the file path
2. Give a one-line summary: how many tasks, how many carried forward, any scheduling observations
3. Ask if anything needs adjusting

---

## Writing rules

- Use the spelling convention configured in the workspace (UK / US English — read from `context/personal-info.md` if specified, default to UK English)
- Simple, human, direct
- No hype, no jargon, no cliches
- No em dashes (use commas, full stops, or restructure)
- Short paragraphs, readable formatting
- Context paragraphs under section headings are plain text, not bullets
- Do NOT order tasks by priority. Group by category.
- Do NOT invent meetings or tasks not evidenced in the inputs
- Do NOT include internal pricing, margins, or equity details in any output
- Words to avoid: leverage, utilise, cutting-edge, state-of-the-art, revolutionise, synergy, deep dive, circle back, low-hanging fruit, unlock, seamless, empower, holistic, ecosystem, end-to-end

---

## Example note style

Notes should be warm and practical, not corporate:

```
Note: Heavy afternoon. Morning is your window for prep and deep work.
Note: This has carried forward 3 days. Even a skeleton draft today stops it rolling.
Note: Two-minute message that protects the relationship. Do not let it roll.
```
