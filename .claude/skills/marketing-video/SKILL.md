---
name: marketing-video
description: |
  Make a cinematic brand FILM (a short advert) for the brand, start to finish,
  from the brand pack plus any real footage the owner has. Seedance image-to-video,
  music-led, no voice. Use when the owner says "make a brand film", "make a cinematic
  film", "make an advert / ad". Reuses /brand-pack for the
  foundation and scripts/creative_film.py for the stitch; owns the beat-sheet
  pipeline and the revision loop. Spends Higgsfield credits, so it ships
  DORMANT until the owner chooses to turn on the paid video engine.
argument-hint: "[brief or feedback]"
allowed-tools: Bash, Read, Write, Edit
requires:
  - tool: higgsfield
    type: auth                       # key | auth | mcp
    auth: "higgsfield account status"
    requires_bin: [higgsfield, ffmpeg]
    requires_runtime: []
    account: "Higgsfield"
    bundle: creative
    plan: "Paid ~$59/mo (video credits)"
    signup: "https://higgsfield.ai -> Sign up -> pick a plan -> higgsfield auth login"
    where: "Account page, after you pick a plan"
    spend: "Paid credits. Cheap-first defaults on. Cap: HF_MONTHLY_CAP in .env"
    verify: "higgsfield account status"
    optional: true
    dormant: true                    # ships dormant: HIGGSFIELD_ENABLED=false until the owner opts in
---

# Marketing Video

> **Before doing anything with Higgsfield, run `ensure_ready("higgsfield")`.** If its software or its credential is missing, or its verify fails, **do not attempt the task and do not error out.** Run the setup walkthrough (install ffmpeg and the Higgsfield tool if needed, then sign-up, the exact link and click path, the login, then verify) and only once it passes, continue. This skill ships **dormant** (`HIGGSFIELD_ENABLED=false`); it costs paid credits, so it only wakes up when the owner opts in.

```python
from require_key import ensure_ready
ensure_ready("higgsfield")    # paid video engine + ffmpeg, installed and verified first
```

A start-to-finish, repeatable way to make a short branded **film** (an advert, not a
how-to) for the brand. The output is a premium, music-led cut with a calm
narrative arc, delivered as a shareable HD link.

This is the most expensive creative tool, so:
- It is **dormant until paid.** With `HIGGSFIELD_ENABLED=false`, the self-detect
  above leads with the cost ("about $59/month for credits, set this up only when
  you're ready; your free image tools are already connected") and lets the owner skip.
- **Credit discipline is enforced** (cap `HF_MONTHLY_CAP`, stills-first, drafts
  before finals, never auto-regenerate finished media). See `/creative` for the full
  discipline; it applies here too.

## Relationship to /brand-pack and /creative (do not duplicate them)

- **The foundation is `/brand-pack`** → `outputs/creative/{brand}/` with
  `brand.json` + `brand-pack.md`. If the brand already has one, do not re-scrape.
- **The stitch is `scripts/creative_film.py`** + `scripts/creative_lib/render.py`
  (slow + crossfade + music bed + end card, all driven by the `film` block in
  `brand.json`). Do not hand-write a per-project stitch script.
- **This skill OWNS** the film orchestration (beat sheet, grounded stills, i2v clips,
  title cards, deploy) and the **revision loop**. `/creative` makes discrete social
  assets; this makes one narrative film and revises it on feedback.

---

## One-shot checklist (pre-flight - run through this before generating anything)

1. **Does the owner have REAL footage?** If yes, harvest reference frames (`yt-dlp` the
   clip, then `ffmpeg` frames) and GROUND the stills on them via `--image`. This is
   the single biggest accuracy and one-shot win.
2. **Write the beat sheet first.** Mark each beat reused / new / title-card.
3. **Anything text, UI or numbers heavy → a title card, not generation.** AI cannot
   render accurate text or numbers; a branded PNG card can, for 0 credits.
4. **Stills first, open every one for approval, THEN motion.** Lock composition on the
   still - it carries the creative; the clip just animates it.
5. **Reuse unchanged beats; regenerate only what changed.** Never rebuild a whole film
   for a few notes.
6. **480p draft only on risky beats** (hands near objects / morph risk); otherwise
   straight to 1080p once the still has proved the look.
7. **Check `hf account status` before and after; report the credit tally.**
8. **Never auto-regenerate or auto-upgrade finished media without asking** (credit
   discipline - see `feedback_creative_credit_discipline`).

---

## The pipeline (the SOP)

### 1. Foundation (free)
Use the existing brand pack at `outputs/creative/{brand}/`. If anything
has drifted, run `/brand-pack` to refresh it first. Ground the story in the brand's real
method and footage; do not invent it.

### 2. Beat sheet (write it before generating)
Order the beats first. Build an arc that suits the brand (pull tone from
`context/brand.md`). A general shape:
**establishing shot → one core moment that shows the offer → a quiet
explainer title card if needed → a payoff → endcard.** Map each beat to: a
reused clip, a new still+clip, or a title card.

### 3. Stills first (cheap - the still carries the creative)
One `nano_banana_2` 16:9 film frame per NEW beat (2 cr each), via the hf skill / CLI.
GROUND stills on a real reference frame with `--image` when the owner has footage. Open
EVERY still for approval before animating. Lock composition here.

### 4. Beats → 1080p clips
One `seedance_2_0` clip per NEW beat:
```
--start-image {frame}.png --resolution 1080p --duration 5 --aspect_ratio 16:9
```
Motion prompts that suit the brand (push-in, slow dolly, a hand on a desk). Add "no warping, no morphing hands". Draft at **480p (15 cr)** only on risky beats; otherwise straight to
**1080p (45 cr)**. **REUSE unchanged 1080p beats from prior cuts (0 cr).**

### 5. Title cards for anything AI cannot render (text, numbers)
Branded PNG (use the brand background, eyebrow, and typeface from `context/brand.md`)
→ capped clip:
```bash
ffmpeg -y -loglevel error -loop 1 -i titlecard.png \
  -vf "scale=1920:1080:...,fps=30,format=yuv420p" -frames:v 120 video/titlecard.mp4
```
**Cap with `-frames:v N` - never `-t` + `zoompan -loop`, which runs away.** Zero
credits, fully accurate.

### 6. Stitch
```bash
python3 scripts/creative_film.py --brand-dir outputs/creative/{brand} --no-endcard \
  --clips video/v1.mp4 video/v2.mp4 ... video/endcard.mp4
```
`--no-endcard` = we append our own card as the last clip; crossfades + music still
apply across the whole thing. Tune the `film` block in `brand.json` for the pace you
want and save the winning values back so the next film inherits them.

### 7. Music (research the vibe)
Pick a track that fits the brand's tone (check `context/brand.md`). Source:
**Scott Buckley, CC BY 4.0** (scottbuckley.com.au). Set `film.music` to the registry
name and log it in `reference/creative/music/REGISTRY.md`. **The attribution line is
REQUIRED on the page / description if the film is published.** Tracks on hand:
`reverie` (calm, restorative), `aphelion` (epic, slower build), `bornofthesky`
(uplifting build).

### 8. Deliver as an HD link
A bare full-screen player page + the mp4 + a poster, deployed to Cloudflare Pages
(the owner's account, via the `cloudflare-pages` skill):
```bash
python3 scripts/cloudflare_pages.py create-project {name} --branch main   # first time
python3 scripts/cloudflare_pages.py deploy {site_dir} {name} --branch main
```
The page is a single `<video controls playsinline>` on a cream or ink background with
the music attribution line at the foot. Fresh projects 5xx for ~30-60s then go live.
Gives a `*.pages.dev` HD link that does not compress like a messaging app. **The link
is unlisted but public - fine to DM, do not post openly.**

---

## The revision loop

When feedback comes in on a cut:

1. **Watch / read everything.** Pull `ffmpeg` frames from any reference video and read
   the notes. Actually look at the frames - do not work off the words alone.
2. **Decode into an explicit edit list.** One line per change, each mapped to a
   specific beat.
3. **Regenerate only the changed beats.** Reuse every unchanged 1080p clip. Re-still →
   approve → re-clip only what changed → re-stitch.
4. **Re-deploy in place** (same `*.pages.dev` project) so the link already shared
   updates, unless a separate version is wanted.

---

## Rules

- Never generate a logo or wordmark. Use a real mark, recoloured for dark/light cards
  as needed.
- Stay in the brand palette and look (`brand.json` `style_block` / `context/brand.md`).
- Keep the voice on-brand: avoid any words the brand has purged (see `context/voice-and-tone.md`).
- Verify before claiming quality - actually Read the stills and watch the cut.
- Recover finished `hf` jobs via `result_url` (never re-pay).
- Everything under `outputs/creative/{brand}/`.
- Write a `REVIEW-{date}.md` (honest read + credit tally + a decision for the owner) and
  keep `REVISIONS.md` current as cuts evolve.
- Nothing posts from here. The owner shares or publishes the finished link themselves.

## Out of scope (for now)
- **Voiced / narrated films.** The presenter-plus-voice path is parked.
- The paid video engine stays **dormant** until the owner opts in via `/setup`.
