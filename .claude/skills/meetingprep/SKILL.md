---
name: meetingprep
description: "Generate a focused meeting preparation brief from workspace context"
---

# /meetingprep

Generate a focused meeting preparation brief by reading the full workspace context.

---

## What this command does

Reads your context files, HISTORY.md, and CLAUDE.md to understand the current state of the business, then produces a tight, actionable meeting prep document tailored to who you are meeting and why.

## Input

The user may provide details inline:
```
/meeting-prep Sarah from Acme, discovery call about workflow automation
```

Or just run:
```
/meeting-prep
```

If no details are provided, ask these three questions (keep it quick, no widget needed):

1. **Who are you meeting?** (Name, role, company)
2. **What type of meeting?** (Client / sales / mentor / internal / team / workshop / prospect discovery)
3. **What is the main objective?** (One sentence: what does success look like?)

If the user gives enough context inline, skip the questions and build the brief immediately.

## Context loading

Before writing anything, read these files in order to understand the current state of the business:

1. `context/business-info.md` — products, services, pricing, competitive landscape
2. `context/current-data.md` — financials, build progress, blockers
3. `context/strategy.md` — priorities, validation progress, key events, targets
4. `context/personal-info.md` — the user's background, brand voice, working style
5. `HISTORY.md` — recent activity, what has changed, what was built (if present)

CLAUDE.md is already loaded at session start, so do not re-read it. But do reference its context summary for current priorities and focus areas.

After reading the files, scan for anything specifically relevant to:
- The person or company being met
- The topic of the meeting
- Recent developments that affect the conversation
- Pending decisions or unresolved items related to the meeting

## Meeting type context guide

Pull different context depending on who the meeting is with:

**Client (existing customers, prospects):** Product / service details, pricing, value proposition, build or delivery progress, what is ready to demo, what is not. Never include internal financials, burn rate, or capacity constraints in client-facing prep.

**Sales / pricing:** Lead with outcomes and ROI. Reference the offer structure and any deposit approach. Stay tool-agnostic in framing. Anticipate the most common objection patterns for this market and have the value numbers ready (hours saved, error reduction, cost savings — pull from `context/business-info.md`).

**Mentor / coach:** Current stage, what was discussed last time, what questions to raise, what has changed since last call, progress on commitments made.

**Internal (co-founder, partner, family business stakeholder):** Relationship dynamics, equity structure, commercial priorities, unresolved items. Be direct about anything outstanding.

**Team:** Current task pipeline, role scope, what has been delivered, what is blocked, capacity, commercial terms if relevant.

**Prospect discovery:** Research the company before the call. Prepare questions about their structure, current tooling, team, pain points. Do not pitch. Listen and qualify.

**Workshop:** Logistics, audience profile, content flow, demo plan, soft close approach, lead capture method.

## Negotiation detection

After loading context and understanding the meeting, assess whether this meeting involves a negotiation. A meeting involves negotiation if ANY of the following are true:

- Pricing, fees, or payment terms will be discussed
- Contract terms, scope, or deliverables are being agreed
- Equity, compensation, salary, or commercial structure is on the table
- The meeting involves a proposal, counter-proposal, or terms review
- A partnership, deal, or formal agreement is being shaped
- One party needs something from the other and the terms are not yet settled

If negotiation is detected, include the full **Negotiation Strategy** section in the output (see output format below). If no negotiation is present, skip it entirely.

## Negotiation strategy framework

When a negotiation is detected, build the strategy section using these principles. This is not theory to present to the user. Use these to inform the specific, practical advice in the output.

### Preparation principles

**Know the numbers cold.** Before any negotiation, identify every relevant number: costs, margins, alternatives, market rates, time costs, opportunity costs. Pull these from context files. The user should never be caught without a specific number when challenged.

**Map both positions.** What does the user want? What does the other side likely want? Where do these overlap? Where do they conflict? The overlap is where the deal gets done.

**Identify leverage.** Leverage is not about power — it is about alternatives. Whoever has the better alternative to no deal has more leverage. Be honest about the user's leverage position, even when it is weak. Knowing you have weak leverage is better than pretending you don't.

**Set three numbers for every negotiable item:**
- **Target:** What you actually want. Aim here.
- **Open:** Where you start. Always above target to give room to move.
- **Floor:** The lowest you will accept. Below this, walk away. Define this before the meeting, not during it.

### In-meeting principles

**Anchor first when possible.** The first number on the table shapes the entire conversation. If the user can set the anchor, they should. If the other side anchors first, do not react — reframe with your own number.

**Trade, never give.** Never concede something without getting something back. "I can do that if..." is the most important phrase in negotiation. Every concession should feel earned by both sides.

**Use silence.** After making a proposal or responding to one, stop talking. Let the other side fill the silence. Most people give ground because they are uncomfortable with quiet.

**Name their concern before they do.** If you know their objection, raise it yourself. "You're probably thinking this is a lot for a first engagement." This builds trust and takes the power out of the objection.

**Separate the person from the problem.** Especially important when negotiating with family, long-term partners, or anyone where the relationship matters as much as the deal. Be warm with the person, firm on the terms. These are not in conflict.

### Closing principles

**Summarise and confirm in the room.** Before ending, restate what was agreed in plain language. Get a verbal yes. Follow up in writing within 24 hours.

**If it stalls, name the stall.** "It feels like we're stuck on X. What would need to be true for you to be comfortable with this?" This moves the conversation from positions to interests.

**Know when to pause.** Not every negotiation closes in one meeting. If the other side needs time, give it — but set a specific follow-up date before you leave. Never leave a negotiation open-ended.

## Output format

Write a markdown file saved to `outputs/meeting-prep-[short-description]-[date].md`.

Keep it tight. Maximum 1.5 pages if printed. No padding. Every line earns its place.

Use this structure (include only sections that are relevant to this specific meeting):

```markdown
# Meeting Prep: [Short title]

**Date:** [Date]
**With:** [Name(s), role, company]
**Type:** [Category]

---

## Objective

[What success looks like. 1-3 sentences maximum.]

## Context

[What the user needs to know walking in. Key facts about the person, relationship, recent developments, and anything that has changed since last contact. Pull from context files and HISTORY.md. Keep to one short paragraph or a few bullet points.]

## Questions to ask

[Numbered list. 5-8 questions max, ordered by priority. Each question gets a one-line note on why it matters. For discovery calls, weight this section heavily.]

## Key messages

[The 3-5 things the user should communicate during the meeting. Not a script. Each point is a bullet with the core idea and suggested framing. For sales meetings, lead with outcomes.]

## Watch for

[Potential objections, sensitivities, or dynamics to be aware of. Include a brief suggested response or approach for each. 3-5 items max.]

## Negotiation strategy

> Only include this section if negotiation is detected. If no negotiation, skip entirely.

### Your position

[What the user wants from this negotiation. Be specific: numbers, terms, outcomes. Pull from context files.]

### Their likely position

[What the other side probably wants. What are their constraints, pressures, and motivations? Be honest about what you know vs what you are guessing.]

### Leverage

[Who has the stronger alternative to no deal? Be direct. If the user's leverage is weak, say so and explain how to compensate.]

### The numbers

| Item | Open (start here) | Target (aim here) | Floor (walk away below) |
|------|--------------------|--------------------|-------------------------|
| [Each negotiable item gets a row] | | | |

### Concession plan

[What the user can offer if pushed. Ordered from easiest to give (offer first) to hardest (last resort). Each concession paired with what to ask for in return. Format: "If they push on X, offer Y in exchange for Z."]

### Their likely objections and your responses

| They say | You say | Why this works |
|----------|---------|----------------|
| [Anticipated objection] | [Specific response — not generic, tailored to this meeting] | [One line on the psychology] |

### Red lines

[Non-negotiables. What the user will not accept under any circumstances. 2-4 items maximum. Be clear.]

## Walk away with

[Specific commitments or next steps to push for before the meeting ends. 2-4 concrete items.]

## Before the meeting

[Anything the user needs to do, review, or have ready. Documents to check, numbers to have on hand, materials to prepare. Skip if nothing specific is needed.]
```

## Rules

- UK English. Always.
- Write in the user's voice (see `context/voice-and-tone.md`). No hype.
- No em dashes. Use commas, full stops, or restructure.
- Never include internal financials (burn rate, salary details, credit position) in prep docs for external meetings.
- Never include pricing targets or margins in client-facing prep. Include pricing ranges and offer structure only.
- Keep the language tool-agnostic in client-facing sections. Describe outcomes, not implementations (e.g. "automated customer messaging" not "GHL workflow with Twilio integration").
- Do not pad sections. If a section has only one relevant point, that is fine. If a section is not relevant, leave it out entirely.
- Words to avoid: leverage, utilise, cutting-edge, state-of-the-art, revolutionise, synergy, deep dive, circle back, low-hanging fruit, unlock, seamless, empower, holistic, ecosystem, end-to-end.

## After output

Tell the user:
1. The file path where the prep was saved
2. One line on the single most important thing to get right in this meeting
3. Ask if anything needs adjusting before the meeting
