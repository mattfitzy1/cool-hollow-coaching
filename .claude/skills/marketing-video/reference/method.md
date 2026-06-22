# Brand Film Method - deep reference (the cinematic-ad pipeline)

The deep reference behind the `marketing-video` skill: the film-specific choices,
the costs table, and the gotchas that cost time and credits the first time. The
SKILL.md has the SOP and the checklist; this doc is the why and the recovery
playbook. The engine lives in `scripts/creative_*` plus the `/brand-pack` and
`/creative` skills.

## The shape that works

1. **Foundation (free).** Use the brand pack at
   `outputs/creative/{brand}/` (`brand.json` + `brand-pack.md` + `refs/`). If
   it has drifted, refresh it with `/brand-pack`.
   - If the owner has real footage, **watch it** (`yt-dlp` the URL, then `ffmpeg`
     frames) so the story and the movement are grounded, not invented.
2. **Stills first, the still carries the creative (cheap).** Generate frames with
   `nano_banana_2 --image refs/{real-image}.png` (2 cr each). Make both:
   - 4:5 social heroes (deliverables), and
   - 16:9 film frames (start images for the clips), one per beat.
   Look at every still before animating. Lock composition here. Grounding a shot on a
   real reference frame via `--image` is the biggest one-shot accuracy win.
3. **Beats → 1080p clips.** One `seedance_2_0` clip per beat, `--start-image
   {frame}.png --resolution 1080p --duration 5 --aspect_ratio 16:9`, calm motion
   prompts (push-in, slow dolly, a hand placing a mat), "no warping / no morphing
   hands". Draft at `480p` (15 cr) only on risky beats; approved beats go to `1080p`
   (45 cr). Final is always 1080p (720p looks blurry full-screen).
4. **End card that reads cleanly.** Build a clean card on the brand base with the
   wordmark, an eyebrow, and the brand tagline (pull colors, type, and tagline from
   `brand.json` / `context/brand.md`). Render
   PNG → ~4.5s clip **capped with `-frames:v N`** (NOT `-t` + `zoompan -loop`, which
   runs away to hundreds of seconds).
5. **Stitch** with `scripts/creative_film.py --no-endcard --clips v1 v2 v3
   endcard.mp4`. `--no-endcard` means we append our own card as the last clip;
   crossfades + music bed still apply across the whole thing. Tune `brand.json`
   `film` for the pace you want, and save the winning values back. The script
   auto-discovers `video/v*.mp4` if `--clips` is omitted.
6. **Music - match the brand register.** Pick a track that fits the brand's tone
   (e.g. restorative and cinematic, or upbeat and confident, per `brand.json`).
   Source: Scott Buckley free CC-BY
   4.0 library (scottbuckley.com.au). If a track needs trimming to its strongest
   section, measure per-window mean volume with `ffmpeg volumedetect` and cut from
   where it kicks in. Keep the full track as `{name}-full.mp3`; the trimmed working
   file is `{name}.mp3`. Log the track + attribution in
   `reference/creative/music/REGISTRY.md`. **Attribution line is required in the
   description if published.**
7. **Deliver as an HD link (no website).** Bare full-screen `<video controls
   playsinline>` page + the mp4 + a poster, deployed to Cloudflare Pages (her
   account): `cloudflare_pages.py create-project {name} --branch main` then `...
   deploy {dir} {name}`. Fresh projects 5xx for ~30-60s then go live. Gives a
   `*.pages.dev` HD link that does not compress like a messaging app. The link is
   unlisted but public - fine to DM, do not post openly.

## Costs (per job)

| job | cost |
|---|---|
| nano_banana_2 hero/frame | 2 cr |
| gpt_image_2 scene | 7 cr |
| seedance_2_0 480p 5s (draft) | 15 cr |
| seedance_2_0 1080p 5s (final) | 45 cr |

A 3-beat 1080p film is roughly 145 cr all-in (3 x 45 clips + ~5 stills). A
3-new-beat revision round is roughly 141 cr (6 stills + 135 clips). Check `hf
account status` before and after; report the tally. The `HF_MONTHLY_CAP` hard
refusal is the backstop.

## Gotchas that cost time and credits

- **`hf` result URL is `result_url`** on the job object - NOT `results.raw.url`. A
  wrong parser makes finished jobs look like FAILs. Jobs complete server-side even
  when `--wait` errors. **Recover via `hf generate list` / `hf generate get {id}` and
  download `result_url` - never re-pay.**
- **`zoompan` + `-loop 1 -t` runs away** (can produce a 500s "4.5s" clip). Cap title
  cards with `-frames:v N` (e.g. 120 frames @ 30fps = 4s).
- **Never auto-regenerate or auto-upgrade finished media** without asking (credit
  discipline - `feedback_creative_credit_discipline`).
- If reference footage or notes arrive as files, have them saved locally so the frames
  and transcripts can be read directly.

## Engine: cinematic film
Seedance image-to-video, music-led, no voice. Premium, ad feel. This is the
`marketing-video` skill. The voiced / narrated path is parked.
