---
name: demo-video
description: Build a branded animated explainer/demo video (product walkthroughs, workflows, "how it works") as an HTML animation, rendered to MP4 with a synth music bed and an optional AI voiceover (ElevenLabs), then deployed to a shareable Cloudflare Pages link. Use when the user wants a marketing/education video that shows the AIOS (or any product/workflow) in action — e.g. "make a demo video of the post-meeting workflow", "an explainer for X", "a narrated walkthrough of Y". Two narration modes: voice-notes (spoken commands) or narrated (a voice talks you through it). Triggers: demo video, explainer video, product video, walkthrough video, marketing video, narrated video, voiceover video, "make a video showing...".
---

# /demo-video

Builds the kind of clean, animated, Claude-style explainer video we built for the **post-meeting workflow** (the reference). Keep the engine generic.

> **To make a new video, follow `reference/AUTHORING.md`** — the full repeatable recipe (proven story arc, the copy-and-reskin process, the measure-then-time discipline, voice + SFX + summary). This SKILL.md is the overview; AUTHORING.md is the step-by-step.

> Status: v1.2 (2026-06-02). Reference output: the post-meeting workflow video → live at https://aios-demo.pages.dev (Danielle voice, ~63s, FaceTime + Mail SFX, end summary slide). Voice/storytelling research DONE — `outputs/deep-research/2026-06-02-explainer-video-craft/synthesis.docx`. The reference HTML + config are the SHIPPED final, so a new topic starts ~90% there.

## What it produces
A 16:9 1080p MP4: a designed reconstruction of a product/workflow (NOT a screen recording), in our brand, with music and optional AI voiceover, plus a shareable web link. Honest framing: it's a *depiction* built to look clean, the way most product hero videos are made.

## The pipeline (full detail in `reference/AUTHORING.md`)
1. **Copy + re-skin the HTML** from `reference/post-meeting-workflow.html` (the shipped final) to a new slug; swap stages/scenes/captions/persona/summary. Single file, deterministic `window.seek(ms)` + `window.TOTAL`, no build step.
2. **Write the cues** in a copy of `reference/audio-config.narrated.json` (set `voice_preset`, the narration cues, `boop`/`boop_ms`, `sfx` times).
3. **MEASURE the cues** (the step that prevents overlaps — durations vary a lot by voice/speed):
   `.venv-command/bin/python scripts/measure_demo_cues.py outputs/videos/<slug>/audio.json --gap 1400`
   Prints each cue's real duration (and pre-caches the clips so the mux is free). Use it to set the HTML timeline + `start_ms`.
4. **Render to silent MP4** (~7 min for ~60s, run in background):
   `.venv-command/bin/python scripts/capture_demo.py outputs/videos/<slug>/<file>.html --fps 30 --scale 1.25 --width 1920 --height 1080`
5. **Mux audio** (voice + music bed + ducking + boops + SFX):
   `.venv-command/bin/python scripts/demo_video_audio.py <config.json>` (`--dry-run` prints the ffmpeg cmd). Cache keys on voice+text+voice_settings. NOTE `-shortest` clips audio to the video length — size TOTAL for the last cue.
6. **Deploy:** `share/` folder (player `index.html` + `video.mp4` + `poster.jpg`) →
   `.venv-command/bin/python scripts/cloudflare_pages.py deploy outputs/videos/<slug>/share <project> --branch main --commit-message "..."` (same project = same URL).

**Two narration modes:** narrated (a voice talks through it — the shipped default) or voice-notes (cues are the spoken commands timed to each pill).

**SFX** (config `sfx: [...]`): file-based (real samples — the FaceTime end chime + Apple Mail sent sound live in `assets/sfx/`) or synth (`type:"swoosh"`). Each is placed at an absolute `ms`, mixed over the music. Source new Apple sounds with yt-dlp + trim (recipe in AUTHORING.md).

**End summary interstitial:** `#summary` overlay (in the reference HTML) — a "Done. In a few minutes." card with ticking checkmarks that recaps the workflow during the closing VO, before the brand card. Fills the closing and doubles as the value recap.

## The animation engine (how to author the HTML)
Bottom `<script>` builds a `cues[]` array; `seek(tm)` applies them. Deterministic (no rAF/Date.now/Math.random in the page logic — Math.random is only in the audio bed). Builders:
- `fade/fadeIn/fadeOut(id,t0,...)`, `move(id,...)` (x/y translate; the HubSpot deal uses `window.__PITCH` measured at load).
- `type(id,txt,t0,t1)` (streams text; does NOT clear before t0, so a `setT` can show "Thinking…" first), `setT`, `caret`, `cls`, `clock` (the live call timer), `wave` (voice-note waveform), `nar(t0,step,txt)` (swaps the plain-English caption bar).
- Cue rule: a cue never affects its element before `t0`. Elements start hidden via `.anim{opacity:0}`.
Layout: topbar (AIOS lockup + connected tool chips) → narration caption bar (`#narWrap`) → split (chat left / workspace right). Chat = **one exchange at a time** (`.turn` fades in/out, no scrolling). Workspace `.scene`s fade in AFTER the prompt + a "Thinking…" beat (left → right causality). `const S=[...]` holds the stage starts.

## Conventions (locked)
- **Brand it AIOS**, not Claude. Keep the Claude starburst symbol, but the corner reads "AIOS / AI OPERATING SYSTEM". On-screen captions can say "Your AIOS does X". End on the client's brand.
- **Spoken narration NEVER says "AIOS"** — always "AI Operating System". ElevenLabs mangles the acronym (reads it as letters/garbles it). This is a locked rule for all TTS cue text. (Visual text is fine; it's only the voice.)
- **Per-stage caption bar** in plain English (dummy-proof). Big fonts (phone-readable). Slow, well-separated pacing.
- **One idea per beat**, prompt → think → result. Generic, widely-relatable content unless tailoring to a named prospect.
- Synth music (`lofi` calm / `upbeat` energetic) — for public ads, swap a licensed track (mux any file in place of the bed).
- Third-party tool names (Gmail/HubSpot/etc.) shown as plain integration chips, not exact logos.

## Knobs to change per video
Topic & stages (the `S` array + scenes + tool cards), the caption text (`nar(...)`), the connected-tools chips, the client/example names, `music` (lofi/upbeat) + tempo, narration mode + script + `voice_id`, the intro/end copy.

## Voice
ElevenLabs (`ELEVENLABS_API_KEY` in `.env`). Voices are saved as **presets** in `reference/voice-presets.json` (each bundles voice_id + model + settings + pace). A config sets `"voice_preset": "<name>"` (inline `voice_id`/`voice_settings` override). Current presets: **`danielle`** (calm SA female — the shipped voice, default), **`ava`** (warm SA female). Add a new one by auditioning a library voice (get its name via the ElevenLabs `/v1/voices/{id}` API) and saving the winning setup. Cache keys on voice+text+settings, so swapping preset/speed regenerates correctly. **Cloning the user's voice** is the path to "undetectable" — see the playbook below.

`boop_ms`: a cue can place its UI charm independently of the narration start (use when a voice-note pill appears mid-beat, e.g. a confirm, or to land the charm on the word "voice note"). `boop:false` for beats with no on-screen voice-note (intro, scene-setting, auto-triggers).

## Voice & storytelling playbook (research-backed, 2026-06-02)
From the Phase-2 deep research (`outputs/deep-research/2026-06-02-explainer-video-craft/synthesis.docx` — read it before scripting a new video). Defaults below are already baked into `scripts/demo_video_audio.py` (`DEFAULT_VOICE_SETTINGS` + `normalise_for_speech`) and `reference/audio-config.narrated.json`.

**Voice settings (ElevenLabs):**
- `model`: `eleven_multilingual_v2` — docs-named for video narration, normalises numbers, stable on short cues. `eleven_v3` is GA but drops `<break>` tags and needs >250-char prompts to stay stable, so do NOT use it per-short-cue. Turbo is deprecated.
- `style`: **0** (locked). Docs: "keep this setting at 0 at all times" — anything above adds artefacts/instability. The old 0.22 was hurting it.
- `stability`: 0.5 default; **audition 0.50 vs 0.60** on the real script (low = more expressive, high = more consistent). `similarity_boost`: ~0.85. `use_speaker_boost`: true. Optional `speed`: ~0.96 for a calmer read.
- Voice selection beats every slider — audition a Narrator/Documentary-tagged voice against the script with style=0 before locking.

**Number normalisation** (auto, `normalise_numbers: true`): currency (`R50,000` → "fifty thousand rand"), percentages (`75%` → "seventy-five percent") and comma-grouped numbers are spelled out before TTS. Small bare integers ("2 seconds") are left for the model.

**Script spine — copy "A day with Claude"** (Anthropic, https://www.youtube.com/watch?v=oqUclC3gqKs, the closest reference to our format): one named persona doing a real day, NOT "you can do X"; sync every UI action to the word that names it; anchor each beat to ONE real number/outcome (one proof number beats ten adjectives); end on a *feeling*, not a feature. Open with the outcome/vision in the first 5 seconds — no logo intro, change something on screen by ~0:02. Write for the ear: short declarative sentences, one idea per beat, ~130–160 wpm, commas/ellipses for breath.

**Length & the two-cut rule:** cold/landing/ad cut = **under 60–90s** (where our ~54s sits); onboarding/explainer cut = **2–5 min**. Build BOTH from the same workflow — never use the cold cut to teach or the long cut to convert. Strategic call for the user to make per video: a high-ticket retainer video should usually *earn the call*, not fully replace it (Vidyard) — decide before scripting whether the primary asset teases or fully explains.

**Cloning the user's voice:** easiest path = record one clean 2-min read on his best mic in explainer tone → ElevenLabs **Instant Voice Clone** (IVC, ~1–2 min audio, any paid plan) → A/B against the stock voice. IVC can struggle with the SA accent; only escalate to **Professional Voice Clone** (30 min read + live verification, Creator plan, 3–6 hr training) if IVC sounds generic. Note: Wispr Flow *does* retain exportable audio (History → Extract audio) unless Privacy Mode is on, but its clips are short/dry/laptop-mic — a poor clone source. Don't salvage; record clean.

## Files
- `reference/AUTHORING.md` — **the repeatable recipe (read this to make a new video).**
- `reference/post-meeting-workflow.html` — the SHIPPED final animation, the template to clone.
- `reference/audio-config.narrated.json` — the SHIPPED final narrated config (voice preset + SFX + boop_ms + cues).
- `reference/voice-presets.json` — saved voices (`danielle`, `ava`).
- `assets/sfx/call_end.wav` (FaceTime end chime), `assets/sfx/mail_sent.wav` (Apple Mail sent) — real sourced SFX.
- `scripts/measure_demo_cues.py` — measure each cue's real duration + suggest a non-overlapping timeline (run before timing).
- `scripts/capture_demo.py` — HTML → silent MP4 (frame-accurate).
- `scripts/demo_video_audio.py` — TTS + music + ducked mix + boops + SFX + mux (config-driven; voice presets, number-normalisation, `boop_ms`, `sfx`).
- `scripts/cloudflare_pages.py` — deploy the share folder.
- `reference/RESEARCH-BRIEF.md` — the Phase-2 deep-research brief (voice craft + example teardown).
