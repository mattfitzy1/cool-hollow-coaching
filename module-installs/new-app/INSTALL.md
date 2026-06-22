# New App — AIOS Module Installer

> A plug-and-play module from the AAA Accelerator.
> Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)

---

## FOR CLAUDE

You are helping a user install this AIOS Module. Follow these rules:

**Behavior:**
- Assume the user is non-technical unless they tell you otherwise
- Explain what you are doing at each step in plain English BEFORE doing it
- Celebrate small wins ("Design system skill is in place — your apps will stay visually consistent now!")
- If something fails, do not dump error logs — explain the problem simply and suggest the fix
- Never skip verification steps — if a check fails, stop and help the user fix it
- Use encouraging language throughout — they are building something real

**Pacing:**
- Do NOT rush. Pause after major milestones.
- After prerequisites: "Everything looks good. Ready to install?"
- After Pencil setup: "Pencil is connected — you can now design directly in your browser and Claude will read your mockups."
- After installation: "Files are in place. Let's verify everything works."
- After test: "You're all set! Here's how to use it to build your first app."

**Error handling:**
- If `.claude/` folder doesn't exist → they need Claude Code installed first
- If files already exist at the target paths → ask before overwriting
- If Pencil MCP isn't connecting → walk through the setup again, check the URL is correct
- Never say "check the logs" — find the problem and explain it

---

## OVERVIEW

This module gives you `/new-app` — a structured command that turns your Pencil designs into production-ready apps through a 4-phase planning process.

Here's the problem it solves: you have a design mockup and you want to build it as a working app with Claude Code. But going from mockup to code is messy. Styling drifts between sessions, database structure is an afterthought, and the codebase falls apart when you add a second page. `/new-app` fixes this by doing the architecture thinking before any code is written.

The command reads your Pencil mockup, asks smart questions about what you're building, analyzes your existing codebase for reusable patterns, then produces a Master App Plan broken into phases. You build each phase one at a time with `/create-plan` + `/implement`. The result is a properly architected app with consistent styling, clean structure, and a clear build path.

You also get a Design System Enforcer — a background skill that automatically keeps your colors, fonts, and spacing consistent across every coding session. No more style drift.

**What you'll have when it's done:** A `/new-app` command and a design system skill. Together they give you a repeatable pipeline: Pencil design → `/new-app` → `/create-plan` + `/implement` → working app.

**Setup time:** 5-10 minutes (installs files + connects Pencil).

**Running cost:** Free. Pencil has a free tier. The module itself is pure methodology — no scripts or API keys.

---

## SCOPING

**RECOMMENDED** (install everything, connect Pencil, ready to build)
- The `/new-app` command (4-phase app planning workflow)
- The Design System Enforcer skill (keeps styling consistent)
- Pencil MCP connection (so Claude can read your design mockups)

Estimated setup time: 5-10 minutes

**CUSTOM** (walk through each piece)
- Option 1: Skip Pencil setup (if you already have it connected or want to describe designs verbally instead)
- Option 2: Skip Design System Enforcer (if you handle styling manually)

Ask: "Want to go with RECOMMENDED, or would you like to walk through the options?"

If RECOMMENDED → proceed with all components.
If CUSTOM → walk through each option, explain trade-offs, let them choose.

---

## PREREQUISITES

Check each prerequisite. Verify it works before proceeding to the next.

### Claude Code CLI
```bash
claude --version
```
If not installed:
```bash
npm install -g @anthropic-ai/claude-code
```
If npm not installed: install Node.js first from https://nodejs.org (download the LTS version, run the installer).

### Workspace .claude/ folder
```bash
ls .claude/
```
You should see a `.claude/` folder in your workspace root. If it doesn't exist:
```bash
mkdir -p .claude/commands .claude/skills
```

### /create-plan and /implement commands
```bash
ls .claude/commands/create-plan.md .claude/commands/implement.md
```
Both files should exist. `/new-app` produces a Master Plan that feeds into `/create-plan` and `/implement` for the actual build phase. If you don't have these, install the AIOS Starter Kit first.

[VERIFY] All prerequisites should show results without errors.
Ask: "Everything checks out. Ready to connect Pencil?"

---

## PENCIL SETUP

Pencil is a design tool that creates `.pen` files. When connected as an MCP server, Claude can read your mockups directly — extracting layout, colors, typography, and component structure from your designs.

### Step 1: Create a Pencil account

1. Go to https://pencil.dev
2. Sign up for a free account (or sign in if you already have one)
3. You'll land on the Pencil editor — this is where you'll create your app mockups

### Step 2: Connect Pencil to Claude Code

Pencil connects to Claude Code as an MCP (Model Context Protocol) server. This lets Claude read and write to your `.pen` design files.

**Option A: Connect via Claude Code settings (recommended)**

Run this command to add Pencil as an MCP server:
```bash
claude mcp add pencil --transport sse --url "https://mcp.pencil.dev/sse"
```

**Option B: Connect manually via settings file**

Add this to your `.claude/settings.local.json` file under `mcpServers`:
```json
{
  "mcpServers": {
    "pencil": {
      "type": "sse",
      "url": "https://mcp.pencil.dev/sse"
    }
  }
}
```

If the file doesn't exist yet, create it with the full structure:
```json
{
  "permissions": {
    "allow": []
  },
  "mcpServers": {
    "pencil": {
      "type": "sse",
      "url": "https://mcp.pencil.dev/sse"
    }
  }
}
```

### Step 3: Authenticate (if prompted)

When Claude first tries to use Pencil tools, you may be redirected to sign in with your Pencil account. This is normal — it's linking your Pencil account to Claude Code. Follow the browser prompts, authorize the connection, then return to Claude Code.

### Step 4: Verify Pencil is connected

Restart Claude Code (close and reopen, or run `claude` again), then ask Claude:

"Can you check if Pencil is connected? Try running `get_editor_state`."

Claude should be able to call Pencil MCP tools. If it can, you'll see editor state info returned.

If it fails:
- Make sure you restarted Claude Code after adding the MCP config
- Double-check the URL is exactly `https://mcp.pencil.dev/sse`
- If you're prompted for auth again, complete the sign-in flow in the browser
- Try Option B if Option A didn't work (or vice versa)

[VERIFY] Claude can call Pencil tools successfully.
Ask: "Pencil is connected. Now let's install the command and skill files."

---

## INSTALL

### Step 1: Create the skill folder

```bash
mkdir -p .claude/skills/app-design-system
```

### Step 2: Install the Design System Enforcer skill

Write the following file to `.claude/skills/app-design-system/SKILL.md`:

````markdown
---
name: app-design-system
description: >
  Auto-discovers per-app design systems when building frontend code. Enforces design tokens,
  component classes, and visual consistency. Triggers on: design system, app styles, component
  library, CSS tokens, frontend code, UI components, match the design, consistent styling,
  building frontend, app CSS, visual consistency, design tokens, component classes.
user-invocable: false
---

## What This Skill Does

Ensures visual consistency when building or modifying frontend code in any app. Automatically checks for an existing `design-system/` folder and enforces its tokens and components.

## When This Activates

Whenever you are:
- Writing HTML, CSS, or JS in any app directory
- Modifying UI components, styles, or layouts in an app
- The user mentions "match the design", "use the design system", or "keep it consistent"

## What To Do

### 1. Check for a Design System

When working on frontend code in an app directory, check:

```
{app-root}/design-system/
  tokens.css      — CSS custom properties (colors, spacing, type, radii)
  components.css  — Reusable component classes
  DESIGN.md       — Human-readable spec (font CDN links, palette, rules)
```

### 2. If Design System Exists

**Read `DESIGN.md` first** — it gives the full picture: font stack with CDN links, color palette, component inventory, and do/don't rules.

Then follow these rules for all frontend code:

- **Colors:** Only use `var(--token-name)` from `tokens.css`. Never introduce hex/rgb values not in the token system.
- **Spacing:** Use the spacing scale tokens (`--sp-1` through `--sp-12`). Match the rhythm of existing components.
- **Typography:** Use the font families defined in tokens. Match existing size/weight/tracking patterns from `components.css`.
- **Components:** Check `components.css` for existing classes before writing custom CSS. Use the established patterns (cards, headers, labels, badges, etc.).
- **New components:** If you need a pattern that doesn't exist, follow the naming convention and design language of existing components. Add the new class to `components.css`.
- **Icons:** Use the icon library specified in `DESIGN.md` with the documented size and color tokens.
- **Animations:** Reuse existing keyframes and entrance patterns from `components.css`.

### 3. If No Design System Exists

Tell the user:

> "No design system found for this app. I'll extract one from your Pencil mockup during the /new-app process. This locks your colors, fonts, and spacing so styling stays consistent across sessions."

Then proceed with the user's request using good design judgment, but note that styles may drift between sessions without a locked system.

## Convention

- Design systems live at `{app-root}/design-system/` — always 3 files
- Created during Phase 2 of `/new-app` when Claude analyzes Pencil mockups
- The design system is a living document — new components get added as the app grows
- `tokens.css` + `components.css` are the source of truth (importable CSS)
- `DESIGN.md` is the companion spec (readable reference)
````

[VERIFY]
```bash
cat .claude/skills/app-design-system/SKILL.md | head -5
```
Expected: The file starts with the YAML frontmatter (`---`, `name: app-design-system`).

### Step 3: Install the /new-app command

Write the following file to `.claude/commands/new-app.md`:

````markdown
# New App

> Scope, analyze, and plan a new app from a Pencil design.

## Variables

context: $ARGUMENTS (optional — description, .pen file path, design system path, or other context about the app)

---

## Instructions

Run a 4-phase process to turn a Pencil design into a fully scoped, phased Master App Plan ready for iterative `/create-plan` + `/implement` cycles.

**IMPORTANT:** This command produces a PLAN, not code. No app files are created except the Master App Plan document. Implementation happens downstream via `/create-plan` + `/implement`.

---

### Phase 1: Gather Requirements (Interactive)

Purpose: Collect everything needed to scope the app. This phase is conversational.

Steps:
1. If `$ARGUMENTS` was provided, read it as starting context
2. Ask for / confirm each of these (skip what's already clear from context):
   - **App name** — what is this app called?
   - **Purpose** — what problem does it solve? Who uses it? (internal tool, customer-facing, etc.)
   - **Pencil mockup** — where is the `.pen` file? Get the file path or ask them to open it in Pencil.
   - **Pages/screens** — what are the main views? List them. (If the Pencil file shows them, extract this.)
   - **Data sources** — what data does it need? (existing database tables, new APIs, external services)
   - **Backend needs** — does it need an API? Real-time data? Authentication? Background jobs?
   - **Target location** — where will this app live? (default: `apps/{name}/`)
3. If a `.pen` file path is provided or open in Pencil, use the Pencil MCP tools to deeply analyze the mockup:
   - Call `get_editor_state` to see what's currently open
   - Call `batch_get` with patterns to discover the full node tree
   - Call `get_screenshot` to visually inspect the design
   - Extract: layout structure, color palette, typography, component patterns, spacing, icons
   - Call `get_style_guide` if relevant for additional design direction
4. Summarize the gathered requirements back to the user for confirmation, including what you extracted from the Pencil file

**STOP GATE: Get explicit confirmation that the requirements are complete and correct before proceeding to Phase 2.**

---

### Phase 2: Design System Extraction + Codebase Analysis (Autonomous)

Purpose: Extract a locked design system from the Pencil mockup AND understand how this app fits into the codebase.

Tell the user: "Extracting your design system and analyzing the codebase. This will take a minute."

**Part A: Design System Extraction**

From the Pencil analysis in Phase 1, create a design system for the app:

1. Create `{app-location}/design-system/` folder
2. Write `tokens.css` — CSS custom properties extracted from the mockup:
   - Color palette (primary, secondary, accent, neutral scale, semantic colors)
   - Spacing scale (derive from the mockup's spacing patterns)
   - Typography (font families, sizes, weights, line heights, letter spacing)
   - Border radii, shadows, transitions
3. Write `components.css` — reusable component classes based on repeated patterns in the mockup:
   - Cards, buttons, inputs, badges, headers, navigation, etc.
   - Use the tokens from `tokens.css` (never hardcode values)
4. Write `DESIGN.md` — human-readable spec:
   - Font CDN links (Google Fonts or equivalent)
   - Color palette with names and hex values
   - Component inventory with usage notes
   - Do/don't rules for maintaining consistency

**Part B: Codebase Analysis**

Launch parallel research agents covering these areas:

**Agent 1: Existing App Patterns**
- Look at the structure of existing apps in the workspace — identify common patterns
- Focus on the most similar existing app to what's being built
- Extract: tech stack choices, folder structure, API patterns, how they connect to databases
- Note: what worked well, what should be done differently

**Agent 2: Database & Schema Analysis**
- Check for existing database schema files — full table inventory
- Identify which existing tables the new app needs
- Identify what NEW tables might be needed
- Check for existing query patterns in similar apps
- Note: column types, relationships, indexes needed

**Agent 3: Reusable Code & Technical Environment**
- Search for existing code that does similar things (API endpoints, UI components, data processing)
- Check for utilities, API clients, or shared modules relevant to this app
- Look at how similar apps handle: error handling, CORS, static file serving, DB connections
- Check what's already installed (requirements.txt, package.json)
- Identify deployment patterns (local only? Vercel? cloud?)

After all agents complete, compile findings into a structured analysis.

---

### Phase 3: Scope Review & Confirmation (Interactive)

Purpose: Present all findings, get user alignment, and lock the scope.

Present findings in this order:

1. **Design System** — Show what was extracted from the Pencil mockup:
   - Color palette (show the colors)
   - Typography choices
   - Component patterns identified
   - "This design system will keep your styling locked across every coding session."

2. **Existing Assets** — What already exists that we can reuse:
   - Existing DB tables we'll read from
   - Existing API endpoints or query patterns
   - Related code or utilities

3. **New Things Needed** — What we need to create:
   - New DB tables (with proposed schema)
   - New API endpoints (with proposed routes)
   - New files/folders
   - New scripts or utilities

4. **Tech Stack Recommendation** — Based on analysis of existing apps and requirements:
   - Frontend: Vanilla JS vs React/Next.js vs other
   - Backend: FastAPI vs Express vs serverless vs other
   - Styling: Design system CSS (tokens.css + components.css) — always use this
   - Charting: if needed (Chart.js, Recharts, D3, Plotly)
   - Other libraries
   - Rationale for each choice

5. **Open Questions** — Anything that needs user input before planning

**STOP GATE: User must confirm:**
- Design system looks correct
- Tech stack choices
- Scope (pages, features, data)
- New DB tables / API endpoints
- Any open questions resolved

"Type 'locked' when you're happy with the scope, or tell me what to change."

---

### Phase 4: Generate Master App Plan (Output)

Purpose: Produce the comprehensive Master App Plan document.

Create the plan at `plans/{date}-new-app-{name}.md` with this structure:

```markdown
# Master App Plan: {App Name}

**Created:** {date}
**Status:** Draft
**App Location:** {app-location}/
**Design System:** {app-location}/design-system/
**Pencil Source:** {.pen file path or "verbal description"}

---

## App Overview

### Purpose
{What the app does, who uses it, why it matters}

### Pages/Screens
{List of all pages with one-line descriptions}

### Data Sources
{What data it reads/writes, which DB tables, external APIs}

### Design References
{What was extracted from the Pencil mockup — palette summary, key components}

---

## Technical Architecture

### Tech Stack
{Locked decisions with rationale}

### Folder Structure
{Complete proposed directory tree}

### Database
{New tables with full schema, modifications to existing tables}

### API Endpoints
{Every endpoint with method, path, request/response shape}

### Design System
{Summary of tokens.css, components.css, DESIGN.md — already created in Phase 2}

---

## Codebase Analysis Findings

### Relevant Existing Code
{What we found that's reusable, with file paths}

### Patterns to Follow
{Conventions from existing apps that apply here}

### Patterns to Avoid
{What didn't work well in existing apps}

---

## Phased Implementation

### How to Use This Plan

Each phase below is a self-contained chunk. To implement:

1. Run `/create-plan` referencing a specific phase:
   "Create an implementation plan for Phase {N} of plans/{date}-new-app-{name}.md"
2. Review the detailed plan
3. Run `/implement` on the detailed plan
4. Repeat for next phase

Phases are ordered by dependency — complete them in sequence.

### Phase 1: Foundation
**What:** Set up folder structure, create DB tables, wire design system imports, create the app entry point and API skeleton.
**Dependencies:** None (this is the foundation)
**Creates:** {list of files}
**Modifies:** {list of files}
**Key details:** {2-4 paragraphs of specific context — enough for /create-plan to expand without re-researching}

### Phase 2: {First Page/Feature}
**What:** {description}
**Dependencies:** Phase 1
**Creates:** {files}
**Modifies:** {files}
**Key details:** {2-4 paragraphs — component breakdown, data flow, API endpoint details, design system classes to use}

### Phase 3: {Second Page/Feature}
...

### Phase N: Polish & Validation
**What:** Entrance animations, responsive behavior, error states, loading states, final design system compliance check.
**Dependencies:** All previous phases
**Key details:** {specifics}

---

## Validation Checklist

- [ ] App runs locally without errors
- [ ] All pages render with correct data
- [ ] Design system tokens and components used throughout (no arbitrary hex/spacing values)
- [ ] API endpoints return correct data shapes
- [ ] Responsive on mobile and desktop
- [ ] Error states handled gracefully

---

## Notes

{Any additional context, future considerations, related ideas}
```

After generating the Master Plan:

1. Report to the user:
   - Summary of the plan
   - Number of phases
   - Total files to create/modify
   - Recommended first step: "Run `/create-plan` referencing Phase 1 to get started"
2. The Master Plan is now the single source of truth for this app build
````

[VERIFY]
```bash
cat .claude/commands/new-app.md | head -5
```
Expected: The file starts with `# New App`.

---

## TEST

This module doesn't have a runtime test since it's methodology (no scripts, no API calls). Instead, verify the installation:

### Verification test

```bash
echo "Checking skill..." && ls .claude/skills/app-design-system/SKILL.md && echo "Checking command..." && ls .claude/commands/new-app.md && echo "All good!"
```
Expected output: Both file paths listed, ending with "All good!"

### Usage test

Tell the user to try it. First, make sure they have a Pencil file ready (or they can create a quick one):

1. Open Pencil at https://pencil.dev
2. Create a simple mockup — even just a header, a card, and a button is enough to test
3. Save the `.pen` file somewhere in your workspace

Then run:

```
/new-app
```

The command should start asking about the app name, purpose, and Pencil file location (Phase 1). If it does, the module is working. They can cancel out of the test run.

If it works: "You're all set! You now have a complete design-to-code pipeline. Any time you want to build an app, design it in Pencil, then run `/new-app` and it'll handle the architecture and planning. You build each phase with `/create-plan` + `/implement`."

If the command doesn't trigger: Check that `.claude/commands/new-app.md` exists and starts with `# New App`. The file name must match exactly.

---

## WHAT'S NEXT

Now that `/new-app` is installed, here are your options:

1. **Build your first app** — Open Pencil, design a simple dashboard or tool, save the `.pen` file, and run `/new-app`. The command will extract your design system and produce a phased build plan.
2. **Learn Pencil basics** — Pencil works like Figma but produces files Claude can read natively. Spend 10 minutes designing a simple layout. The better your mockup, the better the extracted design system.
3. **Pair with /new-capability** — If your app needs external API data (Stripe, Google Calendar, CRM, etc.), run `/new-capability [service]` first to build the API integration, then reference it when scoping your app with `/new-app`.

---

> A plug-and-play module from Liam Ottley's AAA Accelerator — the #1 AI business launch
> & AIOS program. Grab this and 15+ more at [aaaaccelerator.com](https://aaaaccelerator.com)
