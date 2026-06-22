# New App

> Scope, analyze, and plan a new app from a plain description (or an existing design, if there is one).

## Variables

context: $ARGUMENTS (optional - a plain-English description, a reference HTML file, a .pen file path, a design system path, or any other context about the app)

---

## Instructions

Run a 4-phase process to turn an app idea into a fully scoped, phased Master App Plan ready for iterative `/create-plan` + `/implement` cycles.

**A mockup is optional.** This command works from a plain-English description of the app - that is the default and most common path. A Pencil (`.pen`) mockup, a reference HTML file, or a screenshot is a nice-to-have that sharpens the design phase, but its absence never blocks anything. If there is no mockup, the design system is shaped from the description, the workspace brand context (`context/brand.md`, and any existing apps under `apps/`), and good design judgment, not from a mockup analysis.

**IMPORTANT:** This command produces a PLAN, not code. No app files are created except the Master App Plan document. Implementation happens downstream via `/create-plan` + `/implement`.

---

### Phase 1: Gather Requirements (Interactive)

Purpose: Collect everything needed to scope the app. This phase is conversational.

Steps:
1. If `$ARGUMENTS` was provided, read it as starting context
2. Ask for / confirm each of these (skip what's already clear from context). Keep it conversational and plain-English - never make the user feel they need a mockup or technical artefacts to answer:
   - **App name** - what is this app called?
   - **Purpose** - what problem does it solve? Who uses it? (a personal tool, customer-facing, etc.)
   - **What it should look and feel like** - describe it in your own words. If there is a mockup (a Pencil `.pen` file, a reference HTML file, or even a screenshot) point me at it, but a description alone is completely fine and is the normal way to do this.
   - **Pages/screens** - what are the main views? List them in plain English.
   - **Data sources** - what data does it need? (existing files/tables, new APIs, external services) - "none yet, it's just screens" is a valid answer.
   - **Backend needs** - does it need an API, accounts/login, payments, or background jobs? Or is it a front-end demo for now?
   - **Target location** - where will this app live? (default: `apps/{name}/`)
3. **Only if** a `.pen` file path is provided or open in Pencil, use the Pencil MCP tools to analyse the mockup: `get_editor_state` (see what's open), `batch_get` (discover the node tree), `get_screenshot` (inspect visually), and extract layout, palette, typography, component patterns, spacing, icons. If a reference HTML file is provided instead, read it directly for the same. If neither exists, skip this step entirely - the description plus the workspace brand context is enough.
4. Summarize the gathered requirements back to the user for confirmation, including anything you read from a mockup or reference file if one was provided.

**STOP GATE: Get explicit confirmation that the requirements are complete and correct before proceeding to Phase 2.**

---

### Phase 2: Design System Extraction + Codebase Analysis (Autonomous)

Purpose: Define a locked design system for the app AND understand how this app fits into the codebase.

Tell the user: "Setting up your design system and looking at how this fits with what's already here. This will take a minute."

**Part A: Design System**

Create a design system for the app. Source it from whatever exists, in this order of preference: a Pencil/reference mockup analyzed in Phase 1, the workspace brand context (`context/brand.md`, and the look of any existing apps under `apps/`), then good design judgment shaped by the user's description. A mockup is not required.

1. Create `{app-location}/design-system/` folder
2. Write `tokens.css` - CSS custom properties (from the mockup if there is one, otherwise from the brand context and description):
   - Colour palette (primary, secondary, accent, neutral scale, semantic colours)
   - Spacing scale (derive from the mockup's spacing patterns, or set a sensible rhythm from the description)
   - Typography (font families, sizes, weights, line heights, letter spacing)
   - Border radii, shadows, transitions
3. Write `components.css` - reusable component classes for the repeated patterns the app needs (drawn from the mockup if there is one, otherwise from the described screens):
   - Cards, buttons, inputs, badges, headers, navigation, etc.
   - Use the tokens from `tokens.css` (never hardcode values)
4. Write `DESIGN.md` - human-readable spec:
   - Font CDN links (Google Fonts or equivalent)
   - Color palette with names and hex values
   - Component inventory with usage notes
   - Do/don't rules for maintaining consistency

**Part B: Codebase Analysis**

Launch parallel research agents covering these areas:

**Agent 1: Existing App Patterns**
- Look at the structure of existing apps in the workspace - identify common patterns
- Focus on the most similar existing app to what's being built
- Extract: tech stack choices, folder structure, API patterns, how they connect to databases
- Note: what worked well, what should be done differently

**Agent 2: Database & Schema Analysis**
- Check for existing database schema files - full table inventory
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

1. **Design System** - Show what was defined (from the mockup if there was one, otherwise from the brand context and your description):
   - Colour palette (show the colours)
   - Typography choices
   - Component patterns identified
   - "This design system will keep your styling locked across every coding session."

2. **Existing Assets** - What already exists that we can reuse:
   - Existing DB tables we'll read from
   - Existing API endpoints or query patterns
   - Related code or utilities

3. **New Things Needed** - What we need to create:
   - New DB tables (with proposed schema)
   - New API endpoints (with proposed routes)
   - New files/folders
   - New scripts or utilities

4. **Tech Stack Recommendation** - Based on analysis of existing apps and requirements:
   - Frontend: Vanilla JS vs React/Next.js vs other
   - Backend: FastAPI vs Express vs serverless vs other
   - Styling: Design system CSS (tokens.css + components.css) - always use this
   - Charting: if needed (Chart.js, Recharts, D3, Plotly)
   - Other libraries
   - Rationale for each choice

5. **Open Questions** - Anything that needs user input before planning

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
**Design Source:** {.pen file path, reference HTML file, or "plain-English description"}

---

## App Overview

### Purpose
{What the app does, who uses it, why it matters}

### Pages/Screens
{List of all pages with one-line descriptions}

### Data Sources
{What data it reads/writes, which DB tables, external APIs}

### Design References
{The design source used - a mockup, the brand context, or the user's description - plus the palette summary and key components}

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
{Summary of tokens.css, components.css, DESIGN.md - already created in Phase 2}

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

Phases are ordered by dependency - complete them in sequence.

### Phase 1: Foundation
**What:** Set up folder structure, create DB tables, wire design system imports, create the app entry point and API skeleton.
**Dependencies:** None (this is the foundation)
**Creates:** {list of files}
**Modifies:** {list of files}
**Key details:** {2-4 paragraphs of specific context - enough for /create-plan to expand without re-researching}

### Phase 2: {First Page/Feature}
**What:** {description}
**Dependencies:** Phase 1
**Creates:** {files}
**Modifies:** {files}
**Key details:** {2-4 paragraphs - component breakdown, data flow, API endpoint details, design system classes to use}

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
