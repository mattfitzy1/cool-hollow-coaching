---
name: voice
description: "Analyse the owner's recent writing and update the Cool Hollow Coaching voice-and-tone profile"
---

# Voice

> Analyse the owner's recent writing and update the Cool Hollow Coaching voice-and-tone profile.

## Variables

source: $ARGUMENTS (optional, defaults to "paste". You can also pass a file path inside `outputs/` or `content/` to analyse saved captions or concepts.)

---

## Instructions

This command updates `context/voice-and-tone.md` with patterns from **the owner's own writing** for Cool Hollow Coaching. It builds and sharpens **their** voice as captured in `context/brand.md` and `context/voice-and-tone.md`. It must never reflect anyone else's voice, and it must never carry over copy from another brand. The voice profile is theirs and Cool Hollow Coaching's, full stop.

This skill is **offline**. It does not read email and does not use any MCP connection. It works only from what you paste or from text already saved in the workspace.

### Step 1: Gather Material

**Default (source is "paste" or not specified):**
- Ask the owner to paste the writing they want analysed. Posts or emails they have written themselves are ideal, plus any notes or longer pieces that sound like them.
- The goal is copy they wrote in their own words, not drafts the system wrote for them.

**If source is a file path inside the workspace:**
- Read that file (e.g. a saved post in `outputs/social/`, or a concept in `content/concepts/`) and analyse the parts they wrote themselves.

If there is not much material yet, that is fine. Note what you can from the brand brief and what they paste, and tell them the profile will sharpen as they write more.

### Step 2: Analyse Patterns

Read through the material and identify:

1. **Openings**: How do they start a post or an email? First lines carry a lot.
2. **Structure**: Sentence and paragraph length, line breaks, use of space, where they land the point.
3. **Vocabulary**: Recurring words and phrases that are theirs.
4. **Tone**: How direct, how warm, how plain. Where they allow feeling and where they stay matter-of-fact.
5. **Closings and CTAs**: How they wrap up and how they point toward the offer or next step.
6. **What's absent**: Words and patterns they avoid. Confirm they stay clear of the words and phrasing flagged in their voice profile.

Compare against the current `context/voice-and-tone.md` to spot:
- New patterns not yet captured
- Patterns that have changed or evolved
- Anything inaccurate that should be corrected

### Step 3: Update the File

Read `context/voice-and-tone.md` and make targeted updates:
- Add new patterns with real examples from their writing
- Update existing patterns if they have evolved
- Remove anything no longer accurate
- Update the "Last updated" date at the bottom

Do NOT rewrite the whole file. Make surgical edits. Keep it unmistakably Cool Hollow Coaching, in their own register, US English.

### Step 4: Report

Tell the owner, in 3-5 short bullets:
- How much material was analysed
- What new patterns were found (if any)
- What was updated in the file
- One plain observation about how their voice is settling

Keep it warm and plain. No jargon.

---

## When to Run

- After they have written a batch of posts or emails themselves
- After they have written longer pieces
- Whenever they correct several drafts in a row (so the system learns the correction)
- Whenever they say "update my voice" or "this doesn't sound like me"
