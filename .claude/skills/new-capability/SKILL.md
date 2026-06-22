---
name: new-capability
description: >
  Build custom API integration capabilities for the workspace. Use when adding a new
  API, connecting a service, building a capability, or integrating an external tool.
  New capability, add capability, API integration, connect service, add integration,
  build capability, service integration, add API, connect API, new integration.
  Runs deep web research on official API docs, interactive scoping, and produces
  a complete Context Skill. Strictly custom-built from primary API documentation,
  no third-party skills or marketplace integrations.
user-invocable: false
---

# /new-capability — Capability Factory

Systematically build custom API integration capabilities for this workspace. Takes a service name and runs a 7-stage interactive workflow: gather intent, deep-dive official API docs via web research, scope read/write operations, design the integration architecture, write an exploration doc, generate an implementation plan, and hand off to `/implement`.

The output is always the same: a Context Skill (`user-invocable: false`) that auto-loads when relevant topics come up in conversation. Built from official API documentation only.

**Output chain:** exploration doc → implementation plan → `/implement` handoff

---

## Anti-Marketplace Rule (HARD CONSTRAINT)

Do NOT suggest, recommend, or use:
- Pre-built MCP servers from any marketplace or registry
- Third-party wrapper skills or plugins
- Community-built integrations or "awesome-mcp" lists
- Any pre-packaged solution not built from this workspace's patterns

**Why this rule exists:** Third-party skills are black boxes. You don't know what they actually do, what endpoints they skip, what they'll break when the API changes, or when the maintainer stops updating them. They almost always cover 20% of the API surface and leave you stuck when you need the other 80%. They create invisible dependencies on someone else's maintenance schedule.

The whole point of `/new-capability` is to build capabilities that are fully understood, fully controlled, and fit exactly into your workspace. This isn't optional. It's the reason the skill exists.

**Redirect script:** If the user mentions a pre-built integration, acknowledge it exists but redirect: "That covers basic reads but won't handle [specific operations from their intent]. Building custom from the official docs gives you full control and exactly the operations you need. Takes a bit longer upfront but you never hit a wall."

---

## Stage 1: INTENT — What Do You Need This For?

**Goal:** Understand business context before burning tokens on research.

Ask these questions:

1. **What service are you connecting?** Confirm the exact product and API. ("Google Calendar" vs. "Google Workspace" vs. "CalDAV" are very different scopes.)
2. **What role does this play in your business?** What problem does connecting it solve? Why now?
3. **What specific use cases?** Concrete examples, not abstract needs. ("Check my calendar before sending daily briefs" vs. "full event CRUD for a scheduling feature" shapes research completely differently.)
4. **Which existing commands/workflows/crons would use this?** Ground it in the workspace.
5. **Do you already have API access set up?** Account, API key, OAuth app, or is that part of the work?
6. **Any constraints?** Read-only, specific plan tier, multiple accounts, rate limit concerns?

**Output:** A clear intent statement that shapes all subsequent research. Save it internally for the exploration doc.

**STOP — wait for user responses before proceeding.**

---

## Stage 2: RESEARCH — Deep API Discovery

**Goal:** Complete understanding of the API surface from official primary sources.

### Research Methodology (follow this checklist in order)

1. **Official API documentation** — Web search for `{service} API documentation`, `{service} REST API reference`, `{service} developer docs`. Find the canonical docs site. Read the getting-started guide and API reference.

2. **Authentication** — What auth model? API key, OAuth2, service account, JWT? What scopes/permissions are needed for the operations identified in Stage 1? Token refresh requirements?

3. **SDK availability** — Is there an official Python SDK? Well-maintained? What version? Does it cover the endpoints you need? Or is raw HTTP the better path? Check PyPI for install instructions.

4. **Endpoint inventory** — Catalog every relevant endpoint group. For each: HTTP method, path, one-line description, required parameters, response shape summary. Group by domain (e.g., Calendar: Events, Calendars, Settings).

5. **Rate limits and quotas** — Hard limits per minute/day/month? Quota differences by plan tier? Burst limits? Retry-After header behavior?

6. **Webhooks/real-time** — Push notifications, websockets, or event subscriptions? Relevant to the user's use cases?

7. **Known limitations** — Search for `{service} API limitations`, `{service} API gotchas`, `{service} API breaking changes`. Check GitHub issues, Stack Overflow, developer forums. Note undocumented behavior.

8. **Existing workspace state** — Check if this service is already partially connected anywhere in the workspace. Look for existing skills, scripts, or env vars related to the service.

### Anti-Marketplace Reminder

If the user mentions a pre-built integration during research, use the redirect script from the Anti-Marketplace Rule section above.

### Present Findings In This Format

- **Auth model summary** — type, scopes needed, token refresh requirements
- **SDK recommendation** — official SDK vs. raw HTTP, with reasoning
- **Endpoint groups by domain** — organized by logical grouping (Events, Members, Settings, etc.)
  - For each group: key endpoints table with method, path, one-line description
- **Rate limits table** — limits, quotas, retry behavior
- **Known gotchas** — numbered list of pain points, undocumented behavior, common mistakes
- **Workspace integration points** — which existing systems would use this capability

**STOP — present findings, wait for user input before proceeding.**

---

## Stage 3: SCOPE — Read/Write Priority Matrix

**Goal:** User picks exactly which operations they need. No more, no less.

### Present a Capability Matrix

For each endpoint group identified in research:

```
### {Domain} (e.g., Events)

#### Read Operations
- [ ] List all → GET /resource
- [ ] Get single → GET /resource/{id}
- [ ] Search/filter → GET /resource?query=...

#### Write Operations
- [ ] Create → POST /resource
- [ ] Update → PUT/PATCH /resource/{id}
- [ ] Delete → DELETE /resource/{id}

#### Subscribe
- [ ] Webhook → POST /webhooks
```

### Scope Discipline

Push back on scope creep: "You mentioned [intent from Stage 1]. Do you actually need [obscure endpoint] for that, or can we skip it?"

### Map to Workspace

For each selected operation, note:
- Which existing commands/skills/crons would call this?
- Does this feed a database? Which table?
- Does this need a cron job? What schedule?
- Interactive during sessions, or fully automated?

**STOP — confirm final scope before proceeding.**

---

## Stage 4: DESIGN — Integration Architecture

**Goal:** Design the complete capability before writing anything.

**Before designing:** If you have any existing Context Skills in `.claude/skills/`, read one to calibrate the output quality and match the pattern. If this is your first capability, use the template below as your guide.

### Design Decisions Checklist

#### 1. File Inventory

Determine which files this capability needs:

| File | When to include |
|------|----------------|
| `.claude/skills/{service}/SKILL.md` | Always. The auto-loading Context Skill. |
| `reference/services/{service}.md` | Recommended. Deep reference doc with full endpoint details. |
| `scripts/{service}/client.py` or `scripts/utils/{service}.py` | When auth needs wrapping, retry logic, or the API has quirks that benefit from a client class. |
| Entry in `.env.example` | Always. Credential template for API keys/tokens. |

#### 2. Auth Architecture

Design the full auth flow:
- **API key:** Store in `.env`, load via `os.getenv()` in client or inline. Straightforward.
- **OAuth2:** Needs: token storage location, refresh flow, initial authorization script (`scripts/setup_{service}_oauth.py`), scopes. Spec the complete flow including first-time setup.
- **Service account:** JSON key file, store path in `.env`, load with the service's SDK.

#### 3. SKILL.md Structure

The resulting Context Skill follows this template:

```
---
name: {service}
description: >
  {Service Name} API integration — {what it does}.
  {Natural language keywords for auto-discovery}.
  {Routing note: "For X, use Y instead."}
user-invocable: false
---

# {Service Name} API

{One-line: what this is, how many endpoints, scope.}

## Setup

{Auth initialization code block — copy-paste ready.}

## Key Endpoints

{Quick-reference tables grouped by domain. Columns: Method | What | Code.}

## Common Patterns

{3-5 copy-paste code blocks for the most frequent workflows.}

## Reference

{Lookup tables: IDs, field names, enum values, status codes.}

## Rate Limits

{Limits, quotas, retry behavior.}

---

## Maintenance

> **Self-improvement rule:** If you used this skill and discovered
> something not documented here — a gotcha, API quirk, new pattern,
> or better approach — add it below before finishing your task.
> Keep entries concise (one line each). If this section grows beyond
> 10 items, refactor learnings into the main body above.

### Known Gotchas

(none yet)

### Improvement Backlog

(none yet)
```

#### 4. Validation Test Matrix

For every scoped read/write operation, define a concrete test:

| # | Operation | Test Description | Expected Result | Self-Heal Strategy |
|---|-----------|-----------------|-----------------|-------------------|
| 1 | List items | Fetch all items from the primary resource | Array of items returned, status 200 | Check auth, check base URL, check required headers |
| 2 | Get single | Fetch one item by ID from test 1 | Item fields match, status 200 | Check ID format, check API version |
| 3 | Create | Create a test item with required fields | Item ID returned, item visible via read | Check required fields, check payload format |
| 4 | Update | Modify a field on the test item | Updated field returned on re-read | Check PUT vs PATCH, check required fields on update |
| 5 | Delete | Delete the test item | 404 on re-read, or 200 with deleted flag | Check soft-delete vs hard-delete behavior |

Tests run sequentially during implementation. If a test fails: read the error, diagnose, fix the code, re-run. Loop until pass. After 3 failed attempts on the same test, surface as a hard blocker to the user (missing permissions, plan limitations, undocumented API behavior).

#### 5. Self-Healing Design

The resulting skill includes two Maintenance subsections:
- **Known Gotchas** — one-liner issues discovered during use. Grows organically as the capability is used.
- **Improvement Backlog** — larger items needing a dedicated session. Track them here rather than losing them.

When gotchas hit 10+ items, refactor the patterns into the main SKILL.md body.

### Present the Full Design

Show the complete architecture: file inventory, auth flow, SKILL.md outline with section headers, validation test matrix, and self-healing plan.

**STOP — confirm design before proceeding.**

---

## Stage 5: EXPLORATION DOC — Write the Handoff Artifact

**Goal:** Compile everything into a single, extensive exploration document.

**File:** `plans/explore-YYYY-MM-DD-{service}-capability.md`

### Required Sections

Use this template for the exploration doc:

```markdown
# Explore: {Service Name} API Capability

**Created:** YYYY-MM-DD
**Status:** Explored
**Origin:** {One-line: what capability is being built and why}

---

## Intent

{Full intent statement from Stage 1: service, business context, use cases, constraints}

## API Research

### Authentication
{Auth model, scopes, token refresh, SDK or raw HTTP recommendation}

### Endpoint Inventory
{Full endpoint tables by domain group — method, path, description, required params}

### Rate Limits
{Limits table, quota notes, retry behavior}

### SDK Analysis
{Official SDK assessment — version, coverage, recommendation}

### Known Gotchas
{Numbered list from web research — limitations, undocumented behavior, common mistakes}

## Scoped Operations

### Read Operations
{Confirmed read operations with workspace mapping}

### Write Operations
{Confirmed write operations with workspace mapping}

### Out of Scope
{Endpoints explicitly excluded with reasoning}

## Architecture Design

### File Inventory
{Complete list of files to create/modify}

### Auth Flow
{Step-by-step auth setup including first-time configuration}

### SKILL.md Structure
{Planned section headers and content summary for each}

### Validation Test Matrix
{Full test table from Stage 4}

## Decisions Log
{All decisions made during interactive stages, alternatives considered}

## Workspace Connections
{Which existing systems use this, data flow, cron integration}
```

**This is the critical artifact.** If it's thin, the plan will be thin. If it's thorough, the plan will produce a working capability on the first `/implement` run. Be exhaustive.

Present the doc path and confirm it's saved.

---

## Stage 6: PLAN — Generate Implementation Plan

**Goal:** Chain directly into plan generation while all context is fresh.

**Prompt the user:** "Exploration doc complete. I have all the context from research and scoping. Want me to write the implementation plan now?"

**If yes:** Generate a phased plan at `plans/YYYY-MM-DD-{service}-capability.md`.

### Plan Format (HARD REQUIREMENT)

**You MUST read `.claude/commands/create-plan.md` and use its exact plan format.** This is not optional. The plan must include every section from the `/create-plan` template. The `/implement` command expects the strict format and will not work properly with a loose structure.

### Plan Step Structure

The Step-by-Step Tasks section should follow these phases (adapt to the specific capability):

1. **Auth setup and basic connectivity** — prove the API key/OAuth flow works with a single test request
2. **Build client wrapper / CLI tool — read operations** — core read operations, search, fetch
3. **Add write operations** — create, update, delete with payload formatting
4. **Write the Context Skill SKILL.md** — auto-loading capability with all sections from the design
5. **Write the reference doc** — deep documentation at `reference/services/{service}.md`
6. **Register the capability** — add to `.env.example` and any service index you maintain
7. **Validation** — run every test in the matrix sequentially. Self-heal until all pass or hard blocker identified.
8. **Smoke test** — use the capability in a real workflow from the intent statement. Confirm end-to-end.

**Each step includes:**
- Detailed description of what to do
- Specific bullet-pointed actions
- Files affected (with paths)
- Validation criteria (how to know the step is done)

---

## Stage 7: HANDOFF — Guide to Implementation

**Goal:** Set the user up for a clean implementation session.

**Output:**

```
Plan complete at plans/YYYY-MM-DD-{service}-capability.md

To build this capability, start a fresh session:

/prime
/implement plans/YYYY-MM-DD-{service}-capability.md

The plan includes validation tests for every operation.
Implementation will self-heal until full read/write capability is confirmed.
```

---

## Critical Rules

1. **Interactive** — present findings at every stage, wait for responses. Never complete all stages autonomously. The stop gates between stages are mandatory.
2. **Anti-marketplace** — zero tolerance for third-party skills, MCP servers, or pre-built integrations. This is not a preference, it's a hard constraint.
3. **Workspace-aware** — always ground the design in existing workspace patterns. If you have existing capabilities, read one before designing. Match the pattern to what's already working.
4. **Exhaustive research** — Stage 2 must go deep on the web. Thin research produces thin plans that stall during implementation. Search multiple queries, read multiple doc pages, find the gotchas.
5. **Self-healing** — the test matrix is mandatory. Every scoped operation gets a concrete test with expected result and self-heal strategy. No shipping untested capabilities.
6. **Quality bar** — the resulting Context Skill must be production-grade. If it wouldn't hold up next to a well-built API integration, it's not done.
7. **Plan format compliance** — Stage 6 plan MUST use the exact `/create-plan` template. Read `.claude/commands/create-plan.md` before writing the plan. Every section from that template is required. No shortcuts, no "phases-only" format.

---

## Maintenance

> **Self-improvement rule:** If you used this skill and discovered something not documented here (a gotcha, better research approach, improved stage flow, or pattern worth codifying) add it below before finishing your task. Keep entries concise. If this section grows beyond 10 items, refactor learnings into the main body above.

### Known Gotchas

- `/create-plan` and `/implement` live at `.claude/skills/create-plan/` and `.claude/skills/implement/` in this workspace, not `.claude/commands/`. Stage 6 must read the skill's SKILL.md for the plan template.

### Improvement Backlog

(none yet)
