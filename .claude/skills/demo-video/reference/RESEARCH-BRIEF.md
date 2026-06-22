# Research brief — making the demo videos high-level professional (Phase 2)

Run this as a **`/deep-research`** session in a fresh terminal. Goal: make our AI-narrated explainer videos genuinely good — high-leverage marketing/education that saves us explaining the product. We have a working v1 (the `/demo-video` skill + the post-meeting workflow video at https://aios-demo.pages.dev). Now we learn what actually works.

## Why this matters
These videos should explain the AIOS and our workflows so well that prospects *get it* without a call. High-leverage across sales, marketing, onboarding. So they must look and sound professional, tell a tight story, and not feel like cheap AI slop.

## Track 1 — Great narrated explainer / product videos (LEAD WITH THIS; the user wants links to review)
Find genuinely **well-performing** explainer/product/walkthrough videos (AI-voiced OR human-narrated) that do what we're trying to do: a voice explaining a product/workflow over clean motion/UI. Deliver **real links the user can watch**, grouped by style, each with a short teardown.
- Look across: SaaS product launches & "how it works" (Notion, Linear, Vercel, Stripe, Arc, Raycast, Superhuman, Retool, ramp), AI product launches (OpenAI, Anthropic/Claude, Perplexity, ElevenLabs, Granola, Cluely, etc.), YC/startup demo videos, and top explainer studios.
- For each: link, length, who narrates (human vs AI), script structure (hook → problem → how it works → payoff), pacing, tone, visual style, and **why it works**. Flag the few that best match our "voice talking through a clean workflow" target.
- Also: what LENGTH and STRUCTURE convert best for cold marketing vs onboarding? Hooks that hold attention in the first 5 seconds.
Output: a shortlist of 8-15 reference videos with links + a "what to steal" teardown. the user reviews and picks the ones he wants to sound/look like.

## Track 2 — AI voice craft (make the narration natural + tell the story)
How to make AI narration sound human and *perform* a story, not just read.
- **ElevenLabs specifically:** best models (multilingual v2 vs turbo vs v3/eleven_v3 if available), voice_settings (stability / similarity / style / speed) for natural narration, when to lower stability for expressiveness, the `style` knob trade-offs.
- **Pacing & delivery:** pauses/breaths (SSML `<break>`, ellipses, punctuation tricks), emphasis, sentence length, reading speed, how to script FOR the voice (write for the ear).
- **Voice selection:** which voice archetypes land for B2B trust/warmth; British male vs American vs the user's own cloned voice.
- **Cloning the user's voice:** ElevenLabs Instant Voice Clone (~1-3 min clean audio) vs Professional (~30 min). What makes a good sample set (clean, single speaker, varied prosody, no music). **Sample sources to investigate:** Wispr Flow (does it retain/export raw audio? likely transcribes-and-discards — verify), macOS Voice Memos, any podcast/interview/Loom/webinar recordings of the user, or just record a clean 3-10 min read. Recommend the easiest path to a usable clone.
- What top AI-video creators do (workflows, tools, tips) to avoid the "AI slop" sound.
Output: a concrete **voice playbook** — model + settings + scripting rules + the cloning plan.

## Deliverable
A synthesis we can act on: (1) a ranked reference-video shortlist with links, (2) a voice playbook, (3) 3-5 concrete changes to make to our v1 to level it up. Then we fold the learnings back into the `/demo-video` skill.

## How to start (fresh terminal)
`/prime`, then read `.claude/skills/demo-video/SKILL.md` + this brief, then run `/deep-research` with the brief above (lead with Track 1). Also read `outputs/videos/aios-demo/HANDOFF.md` for the video's technical state.
