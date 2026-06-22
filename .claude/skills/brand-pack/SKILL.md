---
name: brand-pack
description: |
  Build or refine the brand's creative foundation. Use when the owner says
  "set up my brand pack", "refresh the look", "onboard a new look
  for content", or drops a website / Instagram / screenshots they want the
  creative tools to learn from. This skill builds or refines a brand pack from
  the brand's source of truth (context/brand.md) or from a public footprint, and
  can also build a pack for something genuinely new. Writes brand.json +
  brand-pack.md to outputs/creative/{brand}/. This is the INTAKE + FOUNDATION
  step and the human review gate before any assets are generated (that is the
  /creative skill).
argument-hint: "[brand] [website] [@instagram]"
allowed-tools: Bash, Read, Write, Edit, WebSearch, WebFetch
---

# Brand Pack

Turns brand material into a creative foundation. Output: a `brand.json` (machine
config that drives rendering) + `brand-pack.md` (the human brief), plus a `refs/`
folder of real images if you scrape a site. Ends at a review gate; the owner approves
before `/creative` generates anything.

**The brand source of truth is `context/brand.md`** (palette, type, look) and
`context/voice-and-tone.md` (voice). If a pack already exists at
`outputs/creative/{brand}/` (`brand.json` + `brand-pack.md`), the job is usually to
**read it back, confirm it still matches `context/brand.md`, and refine** rather than
rebuild from scratch. Only run the full scrape-and-research flow below if you are
building a pack for something genuinely new.

## Inputs (ask only for what is missing)
- Brand slug (lowercase) and display name
- Website URL
- Instagram handle (optional)
- Screenshots folder (optional, e.g. `~/Downloads/...`) - posts/feed
- Any notes from the owner

## Steps

### A. If it is the client's own brand (the usual case)
1. Read any existing `outputs/creative/{brand}/brand.json` and `brand-pack.md`.
2. Read `context/brand.md` (the source of truth) and `context/voice-and-tone.md`
   so the pack stays in sync with the live brand.
3. Confirm the palette, the type, and the voice all match `context/brand.md`. If no
   pack exists yet, seed `brand.json` + `brand-pack.md` from `context/brand.md`.
4. Refine only what has drifted. Present the change and stop at the review gate.

### B. If building a pack for something new
1. **Run intake** (deterministic scrape + palette + screenshot ingest):
   ```bash
   python3 scripts/brand_intake.py --brand {slug} --url {url} \
     --instagram {handle} --screenshots {shots_dir}
   ```
   This writes a STARTER `outputs/creative/{slug}/brand.json` + `intake-notes.md`
   and downloads logos/imagery to `refs/`. Read `intake-notes.md` to see what it found.

2. **Verify the real assets.** The intake is best-effort and can miss things. Check
   `refs/`: if the logo is wrong, find and download the correct one
   (`curl -sL <url> -o refs/logo.png`); pull the real imagery if the scraper grabbed
   navigation or placeholder noise.

3. **Look at the screenshots.** Read the ingested screenshots in `refs/screenshots/`.
   They reveal the real style, graphic devices, voice and palette far better than the
   website.

4. **Research the brand.** WebSearch + WebFetch the website for: story, audience,
   positioning, taglines, range, tone of voice. Do not invent facts.

5. **Refine `brand.json`.** Edit it to be accurate and renderer-ready:
   - `palette.accent`, `accent2`, `ink`, `paper` (verify against the real assets)
   - `logo` (correct relative path, or null if there is no real mark to use)
   - `devices` (only true if the brand actually uses them)
   - `campaign.formula` + `campaign.endcard` (their real lines, or a sensible brand line)
   - `style_block` - the image-generation look in plain descriptive words
   - `fonts` - the brand's real fonts if available locally

6. **Write `brand-pack.md`.** Use a standard 10-section structure (north star, story
   pillars, voice, visual identity, style direction, what to avoid, prompt
   scaffolding, reusable fragments, aspect ratios, pre-flight checklist) and fill it
   for the brand. US English, no em dashes, no banned hype words (see CLAUDE.md).

7. **Review gate.** Present a short summary: what you found, the palette, the look,
   and any assumptions or risks. Show the draft. **Stop and ask the owner to approve
   or edit before handing to `/creative`.** Generate no paid assets in this skill.

## Rules
- Never generate a logo or wordmark. Use a real mark, or set `logo` to null.
- Be honest about gaps (missing imagery, uncertain palette) in the summary.
- One brand per run. Keep everything under `outputs/creative/{slug}/`.
- This skill spends no Higgsfield credits (read / scrape / research only).
