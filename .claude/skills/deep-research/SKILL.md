---
name: deep-research
description: >
  Multi-platform deep research system using parallel topic-scoped AI agents. Orchestrates
  research across Firecrawl (web), Supadata (YouTube/video), Reddit (community), X-Search
  (real-time discourse), Academic (papers), Podcast-Search (audio), and Substack (newsletters).
  Two-phase: recon scan to find where signal lives, then parallel Opus agents go 3+ levels
  deep on topic angles with signal scoring, triangulation, source profiling, and critic review.
  Use when: deep research, research this topic, investigate, find signal, who are the thought
  leaders on, what's happening in, multi-platform research, intelligence gathering, dive deep,
  research agents. Returns per-agent synthesized reports + master synthesis in
  outputs/deep-research/{date}-{slug}/. Prompt templates live in prompts/.
user-invocable: true
---

# Deep Research Skill

Multi-agent research orchestration across 7 platforms. Topic-scoped parallel agents go
3+ levels deep, score sources rigorously, triangulate claims, and produce critically cited
synthesis reports.

**Output location:** `outputs/deep-research/{date}-{topic-slug}/`
**Prompt templates:** `.claude/skills/deep-research/prompts/`

---

## The Flow

```
/deep-research "brain dump"
  -> Scope Interview (3-4 questions)
  -> Recon Agent (Sonnet, 2-3 min) -> recon.md
  -> HUMAN CHECKPOINT -- review recon, confirm agent roster
  -> Parallel Topic Agents (Opus max, 10-20 min each) -> 01-angle.md, 02-angle.md, ...
  -> Critic Agent (Opus max, review-only) -> critic-notes.md
  -> Synthesis Agent (Opus max) -> synthesis.md
  -> Word Doc Export (mandatory) -> ~/Desktop/Deep Research - {slug}/*.docx
```

---

## Phase 1 MVP (Start Here)

For the first research run, skip recon and critic. Run topic agents directly.

1. Ask the user the scope interview questions
2. Determine 3-6 topic angles based on the brain dump
3. Create session folder: `outputs/deep-research/{date}-{topic-slug}/`
4. Launch all topic agents simultaneously (batch in one message)
5. Run synthesis agent on all outputs
6. **Run the Word doc export** (see "Word Doc Export" section below) — mandatory, every session

---

## Phase 2: Full Flow

Add recon and critic once the core loop is validated.

1. Scope interview
2. Launch recon agent using `prompts/recon.md` template, populate all variables
3. Show recon.md to user, ask for confirmation/adjustments to agent roster
4. Generate topic angle list from recon + user input
5. Launch all topic agents simultaneously, each populated from `prompts/topic-agent.md`
6. Launch critic agent from `prompts/critic.md` once all topic agents complete
7. Launch synthesis agent from `prompts/synthesis.md`
8. **Run the Word doc export** (see "Word Doc Export" section below) — mandatory, every session

---

## Scope Interview Questions

Ask these at the start of every session:

1. **Core question:** What's the main thing you're trying to find out or understand?
2. **Time period:** How recent does the information need to be? (last 30 days / 90 days / 1 year / any)
3. **Starting points:** Any known people, publications, repos, or platforms to prioritize?
4. **Depth vs breadth:** Focused on one specific angle, or broad survey of the space?

---

## Populating the Agent Templates

### Session variables (set at scope interview):
- `{TOPIC_BRAIN_DUMP}` -- user's full brain dump, verbatim
- `{TIME_PERIOD}` -- recency requirement from scope interview
- `{STARTING_POINTS}` -- known people/publications/repos (or "none")
- `{SESSION_SLUG}` -- `{YYYY-MM-DD}-{kebab-case-topic}`, e.g. `2026-03-27-ai-engineering-tooling`

### Recon variables:
- All session variables

### Topic agent variables:
- All session variables
- `{TOPIC_ANGLE}` -- the specific angle this agent is researching
- `{N}` -- agent number (01, 02, 03...)
- `{ANGLE_SLUG}` -- kebab-case version of the angle, e.g. `practitioner-shipping-reality`
- `{RECON_HOT_PLATFORMS}` -- from recon.md (or "unknown, check all" if skipping recon)
- `{RECON_KEY_PEOPLE}` -- from recon.md (or "none identified yet")
- `{RECON_QUERIES}` -- from recon.md (or "generate your own")

### Critic variables:
- `{TOPIC_BRAIN_DUMP}` -- session context
- `{SESSION_SLUG}` -- session folder name
- `{LIST_OF_AGENT_REPORT_FILES}` -- comma-separated list of report filenames

### Synthesis variables:
- All session variables
- `{LIST_OF_AGENT_REPORT_FILES}` -- comma-separated list of report filenames

---

## Launching Agents in Parallel

CRITICAL: To get true parallel execution, all topic agent calls must be in a single message.
Do not launch them sequentially. Use multiple Agent tool calls in one response.

Each topic agent should:
- Use the `general-purpose` subagent type
- Have the full populated prompt from `prompts/topic-agent.md`
- Write output to its specific file path

---

## Typical Agent Roster Examples

**"AI engineering tooling trends"** (4 agents):
- Agent 1: What practitioners are actually shipping and what's breaking in production
- Agent 2: Key thought leaders and their frameworks, who's setting the direction
- Agent 3: Academic and research frontier vs production reality gap
- Agent 4: Tool ecosystem, what's emerging, what's consolidating, what's dying

**"Understanding [person]'s work and influence"** (3 agents):
- Agent 1: Their published work, talks, and primary sources
- Agent 2: How their ideas are being applied by others, reception and criticism
- Agent 3: The people and ideas that influenced them, intellectual lineage

**"Market landscape for [category]"** (5 agents):
- Agent 1: Incumbent players and their positioning
- Agent 2: Emerging challengers and new entrants
- Agent 3: Practitioner sentiment, what's working, what's not
- Agent 4: Academic research direction
- Agent 5: Business model and pricing landscape

---

## Signal Quality Quick Reference

```
RECENCY:     Primary work (any date): 2 | <30d: 3 | <90d: 2 | <1yr: 1 | old current-tech: 0
SOURCE:      Primary/academic: 3 | Named practitioner: 2 | Tech journalism: 1 | Aggregator: 0
SPECIFICITY: Numbers/code/failures: 2 | Some specifics: 1 | Generic: 0
INDEPENDENT: Not citing existing: 1 | Cites existing: 0.5 | Same org: 0
Score >=5: pursue | 3-4: include with caveat | <3: drop
```

High-value domains: arxiv.org, github.com/issues, github.com/discussions, official docs
Low-value domains: SEO farms, /blog/ai-guide-YYYY patterns, AI-pivot domains post-2023

---

## Workspace-Specific Notes

**Supadata import path:** This workspace has `supadata.py` at the root, NOT at `scripts/utils/supadata.py`. Topic agents should import as `from supadata import SupadataClient` (not `from scripts.utils.supadata`). The prompt templates in `prompts/` have been adjusted for this.

---

## Word Doc Export (mandatory, every session)

After the synthesis agent has written `synthesis.md`, run the Word doc export. This is a hard rule. the user reads research in Word, not in markdown. Skip this step and the research is half-delivered.

**Run from the workspace root:**

```bash
source .venv-command/bin/activate
python scripts/research_to_docx.py outputs/deep-research/{SESSION_SLUG}/
```

**What it does:**
- Finds every `.md` file in the session folder (topic reports + synthesis)
- Converts each to `.docx` via pandoc with TOC and GFM-flavoured tables
- Writes them locally to `~/Desktop/Deep Research - {SESSION_SLUG}/`
- Uploads each to Google Drive: `My Drive > Research > Deep Research - {SESSION_SLUG}/` so they read on phone too
- Markdown files stay where they are. Word output is a read-only mirror.

**Confirm to the user** at the end of the session: list the Desktop folder path AND the Drive folder URL printed by the script. They will read from one or the other.

**Skip Drive upload** with `--no-drive` if connectivity is broken. Local Desktop output still happens. Re-run later when Drive is reachable.

**Setup notes for fresh machines:**
- pandoc: `brew install pandoc`
- Drive auth: uses cached `token-drive.json` at workspace root. First run opens a browser for OAuth. Folder ID for My Drive > Research is hardcoded in `scripts/research_to_docx.py` (`DRIVE_RESEARCH_FOLDER_ID`); override via env var if needed.
