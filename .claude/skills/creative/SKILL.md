---
name: creative
description: |
  Generate a batch of on-brand short-form social assets for the brand. Use when
  the owner says "make content", "create a carousel about X",
  "make me three slides", "make a reel". Produces a campaign carousel,
  hero stills, and a short reel via the Higgsfield (hf) pipeline, composited with
  the brand-skinned template renderer, plus a contact sheet, captions and a review
  doc. Reads outputs/creative/{brand}/brand.json. Spends Higgsfield credits
  (cheap-first, capped, approval-gated).
argument-hint: "[brief]"
allowed-tools: Bash, Read, Write, Edit
requires:
  - tool: higgsfield
    type: auth                       # key | auth | mcp
    auth: "higgsfield account status"
    requires_bin: [higgsfield, ffmpeg]
    requires_runtime: []
    account: "Higgsfield"
    bundle: creative
    plan: "Paid ~$59/mo (image/video credits)"
    signup: "https://higgsfield.ai -> Sign up -> pick a plan -> higgsfield auth login"
    where: "Account page, after you pick a plan"
    spend: "Paid credits. Cheap-first defaults on. Cap: HF_MONTHLY_CAP in .env"
    verify: "higgsfield account status"
    optional: true
  - tool: nano-banana
    type: mcp                        # configured = MCP status tool returns connected
    status_tool: "get_configuration_status"
    requires_bin: []
    requires_runtime: [node]
    account: "Google Gemini (nano-banana)"
    bundle: creative
    plan: "Free tier"
    signup: "https://aistudio.google.com/apikey"
    where: "Paste into GEMINI_API_KEY in .env"
    spend: "Free tier. The cheapest creative tool, default for hero shots."
    verify: "nano-banana get_configuration_status"
    optional: false
---

# Creative

> **Before doing anything with Higgsfield, run `ensure_ready("higgsfield")`.** If its software or its credential is missing, or its verify fails, **do not attempt the task and do not error out.** Run the setup walkthrough (install the software if needed, then what to sign up for, the exact link and click path, where the key goes in `.env`, then verify) and only once it passes, continue with what the owner originally asked. The same applies to `ensure_ready("nano-banana")` for the free hero-shot path.

```python
from require_key import ensure_ready
ensure_ready("higgsfield")    # paid video/scene engine - installs binaries + login if missing
ensure_ready("nano-banana")   # free hero shots via the owner's own Gemini key
```

The orchestrator. Takes the approved brand pack and produces a
short-form social batch. Engine pieces:
- `scripts/creative_pipeline.py` - generate + download scenes/heroes/reels (hf)
- `scripts/creative_lib/render.py` - brand-skinned templates (slide/quote/endcard)
- `scripts/creative_pack.py` - contact sheet, db logging, credit summary

Prerequisite: `outputs/creative/{brand}/brand.json` exists and is approved.
If not, run `/brand-pack` first.

## Credit discipline (always, the cap is enforced)
This is the load-bearing rule for the owner, who is on bypass and should never be
surprised by a bill. `ensure_ready` reads a running monthly tally and **hard-refuses
any call that would push past `HF_MONTHLY_CAP`** (in `.env`, default 30), telling the owner
to raise it explicitly if they mean to. Within the cap:

- **Iterate cheap, finalise at 1080p.** Video model is Seedance 2.0 (`seedance_2_0`).
  While iterating, render **`--draft` (480p, ~15 cr)**; render **`--final` (1080p,
  ~45 cr)** only on beats the owner has approved. Same model, start image and prompt, so a
  draft upgrades to final with zero rework, only the resolution changes.
- **Iterate on stills, not video.** The still carries the creative decision (2-7 cr);
  the video just animates it. Lock composition on the still before spending on a clip.
- **Free first.** Hero shots default to nano-banana (the owner's free Gemini tier). Reach for
  paid Higgsfield only when the free path cannot do the job.
- **Never auto-upgrade or regenerate finished media without asking.** Do not render
  finals nobody approved, and do not re-render a finished film. Recover a finished
  Higgsfield job via its `result_url` rather than re-paying. (See
  `feedback_creative_credit_discipline`.)
- **No voiceover.** Music-led only (free CC-BY library).
- **Report the credit tally** at the end of every run.
- Per-brand settings live in the `film` block of `brand.json` so preferences are
  remembered and improve over time. Tune per run, then save the winning values back.

## Default MVP batch (unless the brief says otherwise)
- A campaign carousel: 4-5 content slides + 1 end card
- 2 photoreal hero stills
- (Optional, paid) a short cinematic reel or film: 4-5 motion clips + brand end card
  + music bed

## Steps

1. **Load the pack.** Read `brand.json` (palette, style_block, campaign
   formula/endcard, models) and skim `brand-pack.md` for voice + look. Check the
   Higgsfield balance: `hf account status`.

2. **Plan the batch (your creative judgement).** For each carousel slide pick: a
   theme / pillar (from the brand pack), an on-brand scene that suits it, and a
   headline in the brand voice (see `context/voice-and-tone.md`). Pick a strong
   moment for any reel. Keep it on-brand and varied. Write
   `outputs/creative/{brand}/jobs.json`:
   ```json
   { "scenes": [ {"name":"s1","prompt":"<on-brand scene, negative space for text>","aspect":"4:5"}, ... ],
     "heroes": [ {"name":"hero-1","ref":"refs/<image>.png","prompt":"<scene>","aspect":"4:5"} ],
     "reels":  [] }
   ```
   The scene `prompt` should describe ONLY the scene (the style_block is
   auto-appended) and leave negative space where text will sit.

3. **Generate scenes + heroes** (parallelisable; safe to run in background):
   ```bash
   python3 scripts/creative_pipeline.py batch --brand-dir outputs/creative/{brand} --jobs outputs/creative/{brand}/jobs.json
   ```

4. **Composite the carousel** with the renderer (one call per slide):
   ```bash
   python3 scripts/creative_lib/render.py slide --brand-dir outputs/creative/{brand} \
     --bg images/s1-bg.png --l1 "A grounding place" --l2 "to begin." --out slides/01.jpg
   python3 scripts/creative_lib/render.py endcard --brand-dir outputs/creative/{brand} --out slides/05-endcard.jpg
   ```
   (Quote / tip cards: `render.py quote ...`.)

5. **Video (optional, paid).** Two shapes - a single short reel, or a full cinematic
   film.

   **a) Single reel** (one motion clip, for a quick social post):
   ```bash
   python3 scripts/creative_pipeline.py reel --brand-dir outputs/creative/{brand} \
     --name reel-rolldown --start images/hero-1.png \
     --prompt "<slow push-in, calm, no text>" --aspect 9:16 --draft
   ```
   (Draft 480p first; re-run with `--final` only once the owner approves.)

   **b) Cinematic film** (4-5 clips + end card + music):
   1. Generate the motion clips: write a `reels` jobs file (one entry per beat,
      `start` = a scene/hero image, 16:9, draft first) and run
      `creative_pipeline.py batch --draft`. Use subtle, calm motion prompts (push-in,
      drift, slow dolly - no fast cuts, no text).
   2. Stitch into the finished film with the reusable assembler, which reads the
      `film` block from `brand.json` (no per-project bash):
      ```bash
      python3 scripts/creative_film.py --brand-dir outputs/creative/{brand} \
        --clips video/v1.mp4 video/v2.mp4 video/v3.mp4 video/v4.mp4 \
        --endcard-bg images/<a calm scene>.png
      ```
      It renders the brand end card (config-driven), slows + crossfades the clips,
      lays the music bed (from `reference/creative/music/`, faded in/out), and muxes
      to `{brand}-film-{date}.mp4`. No voiceover.

   **The `film` block in `brand.json`** (edit to tune; remembered):
   ```json
   "film": { "resolution":"1080p", "aspect":"16:9", "crossfade":0.8,
             "slow_factor":1.15, "voiceover":false, "music":"reverie",
             "music_volume":0.85, "fade_in":2.0, "fade_out":3.5,
             "endcard_seconds":4, "pace":"serene" }
   ```
   Music tracks + attribution live in `reference/creative/music/REGISTRY.md`
   (CC-BY only; the attribution line is required if a film is published).

6. **Pack out.** Log composited slides, build the contact sheet, print the tally:
   ```bash
   python3 scripts/creative_pack.py log --brand-dir outputs/creative/{brand} --type slide --paths outputs/creative/{brand}/slides/*.jpg
   python3 scripts/creative_pack.py contact --brand-dir outputs/creative/{brand} --title "social batch"
   python3 scripts/creative_pack.py summary --brand-dir outputs/creative/{brand}
   ```

7. **Captions + review doc.** Write suggested captions (the brand voice) and a
   `REVIEW-{date}.md`: what was made, the honest read, decisions for the owner, credits
   used. Copy `CONTACT-SHEET.jpg` + any reel to the Desktop for easy review.

8. **Present + verify.** Read back the generated slides/heroes yourself (Read the
   images) before claiming they are good. Surface the contact sheet and ask for
   keep/kill/redo. Re-run individual jobs cheaply for any that miss.

## Rules
- Never generate a logo or wordmark. Carousel slides composite real imagery; heroes
  use nano_banana with a real image as `--image` reference where one exists.
- Stay in palette and the brand look (brand.json `style_block` / `context/brand.md`).
  Use the brand's defined colors and accents.
- Keep the voice on-brand: avoid any words the brand has purged (see `context/voice-and-tone.md`).
- Verify before claiming quality (actually Read the outputs).
- Credit guide: scenes ~7cr (gpt_image_2), heroes ~2cr (nano_banana_2), video
  ~45cr/5s (seedance_2_0 @1080p). A carousel + heroes ~60cr; a 4-5 clip film ~200cr +
  the hero. Report the tally. The `HF_MONTHLY_CAP` hard-refusal is your backstop.
- Video is always Seedance 2.0 @1080p for finals. Draft at 480p while iterating.
- Film settings live in `brand.json` `film` - tune per run, then save the winners
  back so the next film inherits them. Don't hand-write per-project stitch scripts;
  use `scripts/creative_film.py`.
- Nothing posts from here. Approved assets land in `outputs/social/{brand}/`
  for the content skills to draft from, and the owner publishes every one themselves.
- For a **marketing film** (an ad, not a how-to): use the `/marketing-video` skill,
  which owns the beat-sheet pipeline.
