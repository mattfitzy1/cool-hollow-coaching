---
name: debrief
description: "Capture detailed meeting or call notes into deep memory immediately. Handles transcripts with speaker identification and voice-dumped notes."
---

# /debrief — Capture Meeting Detail Into Deep Memory

The user will call this in one of these ways:
- `/debrief` followed by voice-dumped notes about a meeting they just had
- `/debrief` followed by a pasted meeting transcript
- `/debrief` with no input, then prompted to provide notes or transcript

## Step 1: Identify the Meeting

Ask (or infer from the input):
- Who was in the meeting?
- When did it happen? (default to today if not specified)
- What was the purpose/topic?

If the user provides a transcript, move to Step 2. If they provide rough voice notes, skip to Step 3.

## Step 2: Transcript Processing (Speaker Identification)

When a transcript is pasted, it often comes from tools like Notion or other transcription services where speakers are NOT identified. The skill needs to figure out who said what.

### 2a: Confirm Participants
Ask: "Who was in this meeting? I need names so I can figure out who's speaking."

### 2b: Identify Speaking Patterns
Before assigning speakers, consider:
- **The owner's speaking patterns** (from `context/voice-and-tone.md` and `context/personal-info.md`): as the founder, they will reference the brand, the offer, their own work, and the business. Pick up their phrasing from their voice profile as you read more debriefs.
- **Known people** (from `memory/` and `context/people/`): check what you have on the other participants. What's their background? What topics would they likely raise?
- **Contextual clues**: who introduces topics, who asks questions vs answers them, who refers to their own work or business.

### 2c: First Pass — Auto-assign with Confidence
Go through the transcript and assign speakers based on the patterns above. For each section:
- If confident (clear pattern match): assign silently
- If uncertain (could be either speaker): mark with [?] and flag the assumption

### 2d: Present for Review
Show the processed transcript with speaker assignments. Format:

```
**[Speaker Name]:** "What they said..."
**[Speaker Name]:** "What they said..."
**[Owner? - assumed because references the business]:** "What they said..."
```

Tell the user: "I've assigned speakers based on what I know about each person. Sections marked with [?] are my best guesses — the reasoning is in brackets. Skim through and correct anything that's wrong."

### 2e: Corrections
Let the user correct any misassignments. Apply corrections and learn from them (note any new speaking patterns in the deep memory entry for future reference).

## Step 3: Structure the Notes

Whether from transcript or voice dump, organise into:

1. **Meeting Summary** — 2-3 sentence overview
2. **Key Discussion Points** — what was discussed, organised by topic
3. **Decisions Made** — specific decisions with who decided and why
4. **Action Items** — who needs to do what, by when
5. **Quotes Worth Keeping** — exact words that matter (commitments, strong opinions, specific numbers)
6. **Open Questions** — things left unresolved
7. **Relationship Notes** — anything learned about the other person's situation, priorities, personality, preferences

## Step 4: Confirm

Present the structured notes back to the user: "Here's what I've captured. Anything to add or correct before I save?"

## Step 5: Save to Deep Memory

Write to `memory/deep-memory/YYYY-MM-DD-debrief-[person/topic].md`

Format:
```markdown
# Debrief — [Meeting Name], [Date]

**Participants:** [names]
**Time:** [time if known]
**Location/Format:** [in person / Google Meet / phone etc.]
**Purpose:** [what the meeting was about]

---

## Summary
[2-3 sentences]

## Discussion
[Detailed, organised by topic. Include who said what where relevant.]

## Decisions
[Bulleted list with reasoning]

## Action Items
- [ ] [Person]: [action] — [deadline if known]

## Quotes
> "[Exact quote]" — [Person]

## Open Questions
[Things left unresolved]

## Relationship Notes
[What was learned about the other person]

## Speaker Pattern Notes
[Any new speaking patterns identified for future transcript processing — e.g. "this person tends to open with a question before making their point", "always says 'to be honest' before a strong opinion"]
```

## Step 6: Update Memory (if needed)

If the meeting revealed new information that should be in the regular memory system (new contact, new decision, new project), write or update the relevant memory file. Deep memory is the detail archive; regular memory is the quick-reference layer.

## Rules

1. **Accuracy over speed.** Always confirm speaker assignments. Never guess silently on something important.
2. **Capture exact words for commitments.** If someone says "I'll send that by Friday" or "We agreed on R15,000" — quote it exactly.
3. **Voice input will be messy.** Clean it up but preserve the meaning. Don't add detail that wasn't there.
4. **Learn over time.** Each debrief adds to the pattern library for speaker identification. Note new patterns in the Speaker Pattern Notes section.
5. **Don't wait for /commit.** The whole point of /debrief is immediate capture. Write to deep memory straight away.
6. **Reference existing context.** Read relevant memory files before processing to understand who the participants are and what topics are likely.
