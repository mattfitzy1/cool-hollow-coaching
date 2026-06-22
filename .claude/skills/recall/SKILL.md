---
name: recall
description: "Search deep memory, memory files, and context files for detailed information about a person, topic, or date range"
---

# /recall — Deep Context Recall

The user will call this with one of:
- `/recall [person name]` - e.g. "recall the designer", "recall the new contact"
- `/recall [topic]` - e.g. "recall the launch plan", "recall the offer tiers", "recall pricing"
- `/recall [date or period]` - e.g. "recall yesterday", "recall last week", "recall 28 March"

This is an offline skill: it searches your own workspace memory and context only. It does not read email or calendar (those are a Phase-2 capability the owner sets up with their builder, because they need a separate connection).

## How It Works

Search ALL of these sources in parallel:

### 1. Deep Memory
Search `memory/deep-memory/` for files containing the query term. Use Grep to search file contents. Read matching files and extract relevant sections. This is the richest source — it has full detail, exact quotes, and conversation content.

### 2. Memory Files
Check the memory index at `memory/MEMORY.md` for relevant entries. Read any matching memory files for their full content.

### 3. Context Files
Search `context/` files (`strategy.md`, `business-info.md`, `current-data.md`, `personal-info.md`, `brand.md`, `voice-and-tone.md`, and anything in `context/people/`) for mentions of the query term.

### 4. Projects Register
Search `projects/` (the per-project markdown files and `README.md`) for the query term — a person or topic is often tied to a project the owner is working on.

### 5. Content Pipeline
Search `content/` (`inbox.md`, `strategy.md`, `pipeline.md`) and `outputs/social/` so a captured idea or a past post about the topic surfaces too.

### 6. HISTORY.md
Search HISTORY.md for relevant entries.

## Output Format

Present findings organised by source, most detailed first:

```
## Recall: [query]

### Deep Memory
[Detailed findings from deep-memory files, with dates and session references]

### Memory
[Key facts from memory files]

### Context Files
[Current status and references in strategy, business-info, brand, people, etc.]

### Projects & Content
[Any project or content-pipeline references to the query]

### Timeline
[If enough data, present a chronological summary of all touchpoints]
```

## Rules

1. Always search deep memory first — it has the most detail
2. Show exact quotes from deep memory when available — that's the whole point
3. For person recalls, build a complete picture: who they are, every interaction, what was discussed, what was agreed, what's pending
4. For topic recalls, trace the topic through time: when it first came up, how it evolved, current status
5. For date recalls, reconstruct the full day/period from all sources
6. If nothing is found in a source, say "No results" rather than omitting the section
7. End with "Anything specific you want me to dig deeper on?" to prompt follow-up
8. Be thorough but organised — the user wants detail, not a wall of unstructured text
