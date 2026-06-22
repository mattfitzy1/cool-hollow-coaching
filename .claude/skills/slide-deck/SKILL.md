---
name: slide-deck
description: Build a 16:9 presentation deck as paired HTML and PDF using the AIOS theme (deep teal + sage, Fraunces + Inter). Use when the user asks to make a deck, slide deck, presentation, pitch deck, scope deck, build slides, create a presentation, or convert an HTML deck to PDF. Produces a single HTML file (for live presenting + iteration) and a matching PDF (for sending to clients) via the Playwright-based render script. Output is identical between formats — pixel-exact.
---

# /slide-deck

The permanent workflow for building presentation decks. HTML for live presentation + iteration. PDF for sending. Both rendered from the same source so they look identical.

Reference implementation: see `template.html` in this skill folder for the canonical structure (cover, agenda, content, contact close).

---

## When to invoke

Trigger phrases: "build a deck", "make slides", "create a presentation", "scope deck for X", "pitch deck for Y", "convert this HTML to PDF". Also when iterating on an existing deck ("change slide 3", "add a closing slide", etc.).

---

## The workflow (3 steps)

1. **Build the HTML** at `outputs/decks/YYYY-MM-DD-<topic>.html`. Start from `template.html` in this skill folder. Use the component patterns below.
2. **Render the PDF** with the permanent tool:
   ```
   .venv-command/bin/python scripts/render_deck.py outputs/decks/YYYY-MM-DD-<topic>.html
   ```
   If `scripts/render_deck.py` is configured to mirror to Desktop or a Drive folder by filename pattern, that runs automatically. Otherwise the PDF is written next to the HTML in `outputs/decks/`.
3. **Review and iterate.** When the user flags a slide, edit the HTML, re-run the render command. PDF is one command from any HTML state.

---

## Design system (at a glance)

| Token | Value | Where used |
|---|---|---|
| `--deep-teal` | `#1F4E4A` | Title panels, headings on dark, button accents |
| `--sage` | `#A8B5A0` | Subtle accents, secondary text on teal |
| `--sage-soft` | `#D6DED0` | Soft callout backgrounds, accent panels |
| `--sage-faint` | `#ECEFE7` | Card icon backgrounds, alternating rows |
| `--off-white` | `#FAF8F3` | Slide background |
| `--ink` | `#0E2B2A` | Body headings |
| `--body` | `#4A5957` | Body copy |
| `--muted` | `#7A8583` | Footnotes, slide-num |
| `--gold` | `#C89968` | Phase tags, "when" labels |
| `--border` | `#E3DFD3` | Card borders |

Typography: **Fraunces** (display serif) for h1/h2/h3, **Inter** (sans) for body and UI labels. Both loaded via Google Fonts CDN. Lucide icons via CDN script tag.

Slide size: **1920×1080** at render time (16:9 widescreen). Anything that needs to fit must fit at that size — design for it.

---

## Component patterns

All slides are `<section class="slide">...</section>`. Each slide has top-left `slide-tag` (uppercase eyebrow) and top-right `slide-num` (`NN / total`), and an optional bottom-aligned `footnote` for research citations or caveats.

### Title slide (split panel)
Deep teal panel left, white content right. Used for slide 1.
```html
<section class="slide slide--title">
  <div class="title-grid">
    <div class="title-panel">
      <div><div class="title-meta">For [Audience]</div></div>
      <div class="wordmark">AIOS<span class="accent">.</span></div>
      <div class="title-meta">[Client]</div>
    </div>
    <div class="title-content">
      <div class="title-eyebrow">Build Scope &middot; v1</div>
      <h1>What we're<br>building.</h1>
      <p class="title-tagline">[Subtitle]</p>
      <div class="title-byline">[Author Name] &middot; [Date]</div>
    </div>
  </div>
</section>
```

### Stat cards (3-up)
Big numbers with labels. Anchor research findings.
```html
<section class="slide">
  <div class="slide-tag">The Homework</div>
  <div class="slide-num">02 / 16</div>
  <h2>[Headline].</h2>
  <p class="lede">[Lede].</p>
  <div class="stats">
    <div class="stat">
      <span class="stat-label">Adoption ceiling</span>
      <div class="stat-number">~10%</div>
      <p class="stat-body">[Body].</p>
    </div>
    <!-- repeat 2 more -->
  </div>
  <div class="footnote">Sources: [...].</div>
</section>
```

### Module cards (2-up with phase tag)
Two side-by-side cards with deep-teal left accent. Use for module pairs (D1+D2, L1+L2, etc.).
```html
<div class="modules">
  <div class="module">
    <div class="module-head">
      <span class="module-tag">D1</span>
      <span class="module-phase">Phase 1</span>
    </div>
    <h3>[Module name]</h3>
    <p>[What it does.]</p>
    <p class="why"><strong>Why first:</strong> [reason].</p>
  </div>
  <!-- repeat -->
</div>
```

### Capability grid (5×2)
Ten generic capabilities as small cards with Lucide icons. Use for "what comes standard" slides.
```html
<div class="caps">
  <div class="cap">
    <div class="cap-icon"><svg ...></svg></div>
    <h4>[Capability]</h4>
    <p>[Description.]</p>
  </div>
  <!-- repeat 9 more -->
</div>
```

### Phased timeline (3-up cards)
Numbered circles, "when" label, title, bullet list, optional gate tag.
```html
<div class="phases">
  <div class="phase">
    <div class="phase-num">1</div>
    <div class="phase-when">Build trip + 4 weeks</div>
    <h3>[Phase title]</h3>
    <ul>
      <li>[Item]</li>
    </ul>
    <span class="phase-gate">No compliance gate</span>
  </div>
  <!-- repeat -->
</div>
```

### Two-column controls list (numbered) + gates panel
For the compliance slide pattern.
```html
<div class="comp-grid">
  <div>
    <div class="label-sm">The six operational controls</div>
    <div class="controls">
      <div class="control">
        <div class="control-num">1</div>
        <div class="control-text"><strong>[Control].</strong> [Authority].</div>
      </div>
      <!-- repeat -->
    </div>
  </div>
  <div>
    <div class="label-sm">The three phase-transition gates</div>
    <div class="gates">
      <div class="gate">
        <div class="gate-title">Gate 1 &middot; [Name]</div>
        <div class="gate-text">[Body].</div>
      </div>
    </div>
  </div>
</div>
```

### Checklist (2-column ticks)
"What stays human" / boundaries pattern. Sage-soft circular check icons.
```html
<div class="humans">
  <div class="human">
    <div class="human-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6 9 17l-5-5"/></svg></div>
    <div class="human-text"><strong>[Item.]</strong> [Detail.]</div>
  </div>
</div>
```

### Out-of-scope cards (2x3 with warning icons)
For "things we're not building." Triangle warning icons.
```html
<div class="scope-cards">
  <div class="scope-card">
    <div class="scope-card-title">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 2 10 18H2z"/><path d="M12 9v4M12 17h.01"/></svg>
      [Item]
    </div>
    <p class="scope-card-text">[Reason it's out.]</p>
  </div>
</div>
```

### Success criteria table
Three-column: module / lead metric / lag metric.
```html
<div class="success-table">
  <div class="success-row head">
    <div class="success-cell">Module</div>
    <div class="success-cell">Lead metric</div>
    <div class="success-cell">Lag metric</div>
  </div>
  <div class="success-row">
    <div class="success-cell"><strong>L2</strong> [Module]</div>
    <div class="success-cell">[Quality measure]</div>
    <div class="success-cell">[Hours measure]</div>
  </div>
</div>
```

### Numbered steps (5-up timeline)
Sage-soft circles with step numbers, "when" label, title, body. Use for "what happens next" / process slides.
```html
<div class="next-steps">
  <div class="step">
    <div class="step-num">1</div>
    <div class="step-when">Now</div>
    <h4>[Step]</h4>
    <p>[Body.]</p>
  </div>
</div>
```
The grid template column count adjusts in CSS — for 4 steps it's `repeat(4, 1fr)`, for 5 it's `repeat(5, 1fr)`. Keep the grid count in the CSS aligned with the step count.

### Close slide (split panel)
Mirror of title slide. Cream content left + contact card, deep teal right with closing line.
```html
<section class="slide slide--close">
  <div class="close-grid">
    <div class="close-content">
      <div class="title-eyebrow">[Project name]</div>
      <h2>[Closing line.]</h2>
      <p class="close-tagline">[Subtitle.]</p>
      <div class="close-contact">
        <div class="close-contact-row"><span><strong>[Author Name]</strong></span><span>[Role]</span></div>
        <div class="close-contact-row"><span>Email</span><span>[email@example.com]</span></div>
        <div class="close-contact-row"><span>Calendly</span><span>[calendly.com/handle]</span></div>
        <div class="close-contact-row"><span>v1 &middot; [Date]</span><span>For [Audience]</span></div>
      </div>
    </div>
    <div class="close-panel">
      <div class="close-panel-meta">[Client]</div>
      <div class="close-panel-content">
        <h3>[Punchline.]</h3>
        <p>[Reinforcement.]</p>
      </div>
      <div class="close-panel-meta">[Project] &middot; [Version]</div>
    </div>
  </div>
</section>
```

---

## Footnote pattern

Use `<div class="footnote">` for source citations or research caveats. Sits absolute-bottom of the slide, italic, muted. Only on slides where research backs a claim.
```html
<div class="footnote">Sources: T3 2026 Survey (n>2,000); Kitces Research 2025 (n>700).</div>
```

---

## Render + sync

```
.venv-command/bin/python scripts/render_deck.py outputs/decks/<file>.html
```

The script:
1. Renders 16 (or however many) slides at 1920×1080 via Playwright (proper font + JS waits).
2. Assembles into a 16:9 landscape PDF (20×11.25 in) with `img2pdf` (lossless).
3. Auto-syncs to Desktop and `My Drive/Clients/<ClientName>/` based on filename match.

Output PDF is pixel-exact to the HTML rendering. No print-CSS reflow, no layout shifts.

---

## File naming + routing

| File | Path |
|---|---|
| HTML deck (working source) | `outputs/decks/YYYY-MM-DD-<topic>.html` |
| PDF (generated) | `outputs/decks/<Client>_<Topic>_<Version>_<Date>.pdf` |
| Desktop copy | auto |
| Drive copy | `My Drive/Clients/<Client>/` based on filename match |

Filename heuristic for Drive: include the client name (e.g. `<ClientName>_<Topic>_v1_<Date>.pdf`) in the PDF filename and the script picks up the matching Drive folder automatically — only if `scripts/render_deck.py` has been configured with the user's Drive paths.

---

## Iteration workflow

When the user says "change [thing] on slide N":
1. Open the HTML at `outputs/decks/<file>.html`
2. Find slide N (sections are in order — count `<section class="slide">` tags)
3. Edit
4. Re-run `python scripts/render_deck.py <file>.html`
5. Show the result

Don't rebuild from scratch. The HTML is the working source.

---

## Common gotchas

- **Page size mismatch.** Always design for 1920×1080. Don't trust how it looks at smaller viewports — that's just the screen experience, the render is fixed.
- **Lucide icons.** Use inline SVG snippets (copy from existing decks) or rely on the `<i data-lucide="name">` pattern with the lucide CDN script. Playwright waits for the script to run, so icons render correctly.
- **Fonts.** Fraunces + Inter are loaded via Google Fonts. The render script waits for `document.fonts.ready` so the fonts are guaranteed loaded at screenshot time.
- **Ems dashes.** Hard rule from voice profile — never use them. The CSS substitutes them with regular dashes; double-check any new copy.
- **Filename routing.** If the Drive auto-sync to a client folder doesn't pick up the right folder, the filename probably doesn't include the client name. Add it.
- **Adding/removing slides.** Update the `slide-num` (`NN / total`) on every slide so they stay in sync. Counter in the bottom-right of each slide.

---

## Related files

- `template.html` (this folder) — clean starter deck with title, content, close, plus reference instances of every component pattern. Copy this as the starting point for new decks.
- `scripts/render_deck.py` — the render tool. Already supports any HTML deck following the slide-section convention.
- `outputs/decks/` — once you've built a few decks, the most recent worked example lives here as a reference.
