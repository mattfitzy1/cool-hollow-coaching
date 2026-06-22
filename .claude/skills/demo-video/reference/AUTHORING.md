# /demo-video — Authoring guide (the repeatable process)

This is the end-to-end recipe for making a new branded explainer video. Following it, you should be **~90% there on a new topic** and only tweaking wording, scene content, and timings. Built from the post-meeting workflow video (shipped 2026-06-02, live at https://aios-demo.pages.dev).

## The two canonical files you copy
- **Animation:** `reference/post-meeting-workflow.html` — the proven template (Claude-style warm-paper UI, intro brand card → workspace → summary interstitial → end brand card, all cue-driven, deterministic `seek(ms)`).
- **Audio config:** `reference/audio-config.narrated.json` — the proven narrated config (voice preset + number-normalisation + music + ducking + boops + 2 SFX + cues with `boop_ms`).
- Plus: `reference/voice-presets.json` (saved voices), `assets/sfx/*.wav` (Apple FaceTime end chime + Mail sent sound).

## The proven story arc (keep this shape; swap the content)
1. **Intro** (brand card): "Let me show you how this works in practice. The moment I finish a {trigger}, this is what I do."
2. **Hop / set the scene**: "I've just finished a {call/task} with {Name}, …" — name the persona; one specific situation, not "you can…".
3. **First action + the voice-note reveal**: the narration introduces talking to it — "I'll just voice note my system, asking it to {do X}." — and the **charm (boop) + voice-note pill fire exactly as "voice note" is said** (see `boop_ms`). Then it flows straight into what the system does. One continuous line, not stop-start.
4. **2–3 more action beats**: prompt → (brief think) → result on the right. One idea per beat. Anchor to ONE real number/outcome where you can.
5. **Auto-trigger beat**: something happens automatically off the previous action (no command) — boop OFF for this beat.
6. **Summary interstitial**: "Done. In a few minutes." + 4–5 ticking checkmarks recapping what it did + an outcome line. Fills the closing; doubles as the value recap.
7. **Tier-up close** (end brand card): "…all done right here, in your AI Operating System. And this is just one example. It can run almost any workflow in your business." End on the feeling + the elevation.

## Locked conventions
- **Brand it AIOS, not Claude** (keep the starburst; corner reads "AIOS / AI OPERATING SYSTEM"; end on the client's brand).
- **Spoken narration NEVER says "AIOS"** — always "AI Operating System" (TTS mangles the acronym). Visual text can say AIOS.
- **Write for the ear**: short declarative sentences, commas/full-stops for breath. **Avoid "…" ellipses for pauses** — they sound gappy. For a deliberate pause use an SSML `<break time="0.6s" />` (works on `eleven_multilingual_v2`; NOT on v3).
- Don't repeat a word in close succession (we hit a triple "system" — use "workspace"/"tools"/"it").
- Numbers/currency/percent are auto-spelled-out before TTS (`normalise_numbers`).

## The process — step by step

### 1. Copy the templates to a new slug
```
cp .claude/skills/demo-video/reference/post-meeting-workflow.html outputs/videos/<slug>/<slug>.html
cp .claude/skills/demo-video/reference/audio-config.narrated.json   outputs/videos/<slug>/audio.json
```
Edit `audio.json` paths: `video`, `out`, `voice_dir` → the new slug folder. (SFX paths already point at the skill assets and can stay.)

### 2. Re-skin the animation HTML for the new topic
In `<slug>.html`, change:
- the **stages** (`const S=[...]` starts) and each scene's content (the `.scene` blocks: call tile, debrief notes, deck thumbs, email, CRM — replace with your topic's scenes),
- the **connected-tool chips** in the topbar,
- the **per-stage caption bar** text (`nar(t,'STEP N OF M','…')`),
- the **client/persona name** (search-replace), avatar initials, filenames,
- the **summary checklist rows** (`#sr1..#srN` + `#srOut`),
- intro/end copy.
Keep the engine + builders untouched (see "Animation engine" below).

### 3. Write the narration cues (in `audio.json`)
One cue per beat, following the arc above. Set `voice_preset` (e.g. `danielle` or `ava`). Mark `"boop": false` on the intro, scene-setting, and any automatic beat; `"boop": true` where a voice-note pill appears.

### 4. MEASURE before you time anything (this prevents overlaps)
```
.venv-command/bin/python scripts/measure_demo_cues.py outputs/videos/<slug>/audio.json --gap 1400
```
It prints each cue's REAL duration and a back-to-back timeline. Durations vary a lot by voice (Danielle reads ~20% faster than Ava) and by `speed`, so never eyeball this. It also pre-caches the clips so the later mux is free.

### 5. Lay out the timeline (HTML + config together)
- Set the HTML `const S=[...]` step starts, the intro/hop block times, `const E` (workspace→end-card), and `const TOTAL` so each beat has its measured duration + ~1.5s breathing room.
- In `audio.json`, set each cue `start_ms` = its step start + ~300ms (so the voice lands just after the stage appears).
- **`boop_ms`**: if a voice-note pill appears later than the narration start (a mid-beat confirm), set `boop_ms` to the pill's on-screen time so the charm lands on the pill, not the slide start. Also use it to fire the charm mid-sentence (e.g. on the word "voice note").
- **SFX**: set the `sfx[].ms` to the on-screen moment (call ends → FaceTime chime; email sends → Mail sound). SFX are mixed over the music, not ducked.
- Rule: a cue must not start before the previous cue ends. Re-run step 4's gap check mentally against your `start_ms`.

### 6. Render the silent animation (~7 min for ~60s)
```
.venv-command/bin/python scripts/capture_demo.py outputs/videos/<slug>/<slug>.html --fps 30 --scale 1.25 --width 1920 --height 1080
```
Frame-accurate (drives `seek()` through Chromium). Run it in the background.

### 7. Mux voice + music + boops + SFX
```
.venv-command/bin/python scripts/demo_video_audio.py outputs/videos/<slug>/audio.json
```
Cache keys on voice + text + voice_settings, so changing speed/voice regenerates correctly. `--dry-run` prints the ffmpeg command. Watch: the mux uses `-shortest`, so audio is clipped to the video length — make sure the video (TOTAL) is long enough for the last cue.

### 8. Deploy a shareable link
Build a `share/` folder (single-video `index.html` player + `video.mp4` + `poster.jpg`), then:
```
cp outputs/videos/<slug>/<out>.mp4 outputs/videos/<slug>/share/video.mp4
ffmpeg -y -ss <nice_frame_s> -i .../share/video.mp4 -frames:v 1 -q:v 3 .../share/poster.jpg
.venv-command/bin/python scripts/cloudflare_pages.py deploy outputs/videos/<slug>/share <project> --branch main --commit-message "…"
```
Re-deploying the same project updates the same URL. (The post-meeting video uses project `aios-demo` → https://aios-demo.pages.dev.)

## Animation engine (how the HTML works)
Bottom `<script>` builds a `cues[]` array; `seek(tm)` applies them. Deterministic — no rAF / Date.now / Math.random in page logic. Builders:
- `fade/fadeIn/fadeOut(id,t0,…)`, `move(id,…)` (x/y translate; HubSpot deal uses `window.__PITCH`),
- `type(id,txt,t0,t1)` (streams text; does NOT clear first, so a `setT` "Thinking…" can precede it), `setT`, `caret`, `cls`, `clock` (live call timer), `wave` (voice-note bars), `nar(t0,step,txt)` (caption bar swap).
- Cue rule: nothing affects its element before `t0`; elements start hidden via `.anim{opacity:0}`.
- Overlays by z-index: workspace (low) < `#summary` (25) < brand cards (30).

## Voice (see reference/voice-presets.json)
- Model `eleven_multilingual_v2`; **`style` = 0** (locked, docs say keep at 0); `stability` ~0.4 (expressive) – 0.5; `similarity_boost` ~0.85; `use_speaker_boost` true; `speed` 1.0 (we A/B'd 0.95/1.0/1.05 → 1.0 read best).
- Presets bundle voice_id + these settings. Add a new one by auditioning a library voice (look up its name via the ElevenLabs `/v1/voices/{id}` API) and saving the winning setup. `ava` = warm SA female; `danielle` = calm SA female (the shipped voice).
- Ceiling for "undetectable" = cloning the user's voice (Instant Voice Clone, ~2-min clean read) — see the voice playbook in SKILL.md.

## SFX (sourcing real Apple sounds)
We use the real **FaceTime end chime** (call ends) and **Apple Mail sent** sound (email sends) — instantly recognisable. They're not in accessible system folders, so we sourced them from YouTube clips and trimmed:
```
yt-dlp -x --audio-format wav -o src.wav "<youtube url of the sound>"
ffmpeg -i src.wav -af "silencedetect=noise=-40dB:d=0.08" -f null -   # find the sound's start/end
ffmpeg -y -ss <start> -i src.wav -t <len> -af "afade=t=in:d=0.02,afade=t=out:st=<len-0.13>:d=0.13,highpass=f=120" assets/sfx/<name>.wav
```
Synth fallback exists in `demo_video_audio.py` (`type:"swoosh"`) but the real sample is better. Note for public/commercial use: Apple's chimes are theirs — fine for internal/sales, reconsider for paid ads.

## Gotchas we already hit (don't relearn these)
- Measure cue durations per voice/speed before timing — Danielle ≠ Ava length.
- Ellipses = gappy pauses; use `<break>` for deliberate beats.
- "AIOS" spoken → "AI Operating System".
- The cache keys on voice_settings now, so speed/stability changes DO regenerate.
- `-shortest` clips audio to video length; size TOTAL for the last cue + tail.
- A boop with no on-screen voice-note pill reads as a phantom beep — set `boop:false` or move it with `boop_ms`.
