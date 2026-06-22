---
name: app-design-system
description: >
  Auto-discovers per-app design systems when building frontend code. Enforces design tokens,
  component classes, and visual consistency. Triggers on: design system, app styles, component
  library, CSS tokens, frontend code, UI components, match the design, consistent styling,
  building frontend, app CSS, visual consistency, design tokens, component classes.
user-invocable: false
---

## What This Skill Does

Ensures visual consistency when building or modifying frontend code in any app. Automatically checks for an existing `design-system/` folder and enforces its tokens and components.

When this workspace has a main app under `apps/`, treat any CSS variables already defined in its `index.html`, any brief alongside it, and `context/brand.md` as the source of truth until a locked design system is extracted, and match them by hand.

## When This Activates

Whenever you are:
- Writing HTML, CSS, or JS in any app directory
- Modifying UI components, styles, or layouts in an app
- The user mentions "match the design", "use the design system", or "keep it consistent"

## What To Do

### 1. Check for a Design System

When working on frontend code in an app directory, check:

```
{app-root}/design-system/
  tokens.css      - CSS custom properties (colors, spacing, type, radii)
  components.css  - Reusable component classes
  DESIGN.md       - Human-readable spec (font CDN links, palette, rules)
```

### 2. If Design System Exists

**Read `DESIGN.md` first** - it gives the full picture: font stack with CDN links, color palette, component inventory, and do/don't rules.

Then follow these rules for all frontend code:

- **Colors:** Only use `var(--token-name)` from `tokens.css`. Never introduce hex/rgb values not in the token system.
- **Spacing:** Use the spacing scale tokens (`--sp-1` through `--sp-12`). Match the rhythm of existing components.
- **Typography:** Use the font families defined in tokens. Match existing size/weight/tracking patterns from `components.css`.
- **Components:** Check `components.css` for existing classes before writing custom CSS. Use the established patterns (cards, headers, labels, badges, etc.).
- **New components:** If you need a pattern that doesn't exist, follow the naming convention and design language of existing components. Add the new class to `components.css`.
- **Icons:** Use the icon library specified in `DESIGN.md` with the documented size and color tokens.
- **Animations:** Reuse existing keyframes and entrance patterns from `components.css`.

### 3. If No Design System Exists

Tell the user:

> "No locked design system found for this app yet. For now I'll match the existing styles in the app's HTML (and its brand notes) by hand. When you're ready, I can extract a locked design system once, so your colours, fonts, and spacing stay consistent across every session."

Then proceed with the user's request using good design judgment, reading the app's existing CSS and brand context first (the app's `index.html`, any brief alongside it, and `context/brand.md`). Note that styles may drift between sessions until a locked system is extracted (Phase 2 of `frontend-design`).

## Convention

- Design systems live at `{app-root}/design-system/` - always 3 files
- Extracted via Phase 2 of the `frontend-design` skill (from the app's existing HTML, a plain description, or a mockup - whatever exists). For your app the source is the live `index.html` and brand brief, not a Pencil mockup.
- The design system is a living document - new components get added as the app grows
- `tokens.css` + `components.css` are the source of truth (importable CSS)
- `DESIGN.md` is the companion spec (readable reference)
