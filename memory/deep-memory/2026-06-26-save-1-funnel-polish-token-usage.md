# Save - 2026-06-26 (Friday), Save 1 - Funnel Polish & Token Usage

Quick save before closing the window. Written by /save, not /commit.

---

## What was worked on

- Found and removed the stray `Agent-Reach` repo (61MB, unrelated clone) sitting inside the workspace, moved to Trash, was already gitignored but still added overhead.
- Reviewed the 3 redesigned site pages (`site/index.html`, `discovery.html`, `thank-you.html`) live in browser preview.
- Caught a real compliance issue: homepage claimed "200+ companies guided," invented client logos, and 3 named testimonials with no disclosure that they belong to Cool Hollow Solutions (Mark's existing firm), not Cool Hollow Coaching (pre-launch, zero clients). Matt confirmed the testimonials and stats are real, just need disclosure, not removal.
- Added small-print disclosures under the logo marquee and near the testimonials clarifying the track record belongs to Cool Hollow Solutions.
- Applied Hormozi-style sales mechanics to the homepage copy (hero subhead, problem section, guarantee, final CTA) - outcome-led, risk reversal, concrete specifics. Matt flagged that naming the exact price ($5,000) in the guarantee headline felt premature for cold traffic; reverted to outcome-only framing, price stays in the FAQ for engaged readers.
- Removed the "2,000+ accounts" claim from both index.html and discovery.html per Matt's request (kept "200+ trade owners" and "20 years").
- Toned down the gold glow/glare on the homepage hero and nav buttons (reduced shadow opacity and blur).
- Added a 3-step funnel indicator across pages: homepage shows "Step 1 of 3 - Free Diagnostic," discovery.html shows "Step 2 of 3 - Apply," thank-you.html shows "Step 3 of 3 - Application received."
- Removed the "Are you ready to invest $5,000" question from the discovery.html application form, replaced with a no-dollar readiness question ("Are you ready to actually fix this, not just talk about it?").
- Restructured the homepage testimonials: pulled the 3 real quotes out of one grouped section and spread them through the page (after the problem section, after the offer stack, after the guarantee) as full-width dark-background quote breaks with amber initial badges, bigger and bolder than before. Matt's first reaction was lukewarm ("don't know if I like it") but settled on "just needs more polish," which was then applied.
- Converted the discovery.html application form into a 2-step flow (Step 1: contact info, Step 2: qualifying questions) with a progress bar, Next/Back buttons, and step validation. Matt's reaction: "not quite there yet" - unresolved.
- Found the hidden-profit-analyzer's post-report CTA ("Want us to find the rest?") already exists in code but is a dead link (`APPLY_URL = "#"`) because `site/` isn't deployed to Cloudflare Pages yet. Asked Matt for go-ahead to deploy - no answer yet.
- Spent a chunk of the session diagnosing Matt's fast token/usage burn: identified the large connected-MCP tool list (Lovable, Canva, Adobe, customer-support plugins, small-business plugins, etc., many unused) as the biggest lever, plus screenshots and long single-session conversations. Matt asked for a full list of connected MCPs, which was provided grouped by active vs. available-but-unauthenticated.

## Key decisions

- Testimonials and the "20 years / 200+ owners" stats are real (Cool Hollow Solutions track record) - disclose, don't remove. Saved precedent for any future copy work on these pages.
- Exact price ($5,000) should not headline cold-traffic sections (hero, guarantee) - save for FAQ/application stage once some trust is built. Matches the already-approved diagnostic-first, fit-gate funnel mechanism.
- No invented testimonials, ever, even under pressure to add "more" - the real path to more social proof is asking Mark for additional real quotes from his 200+ Cool Hollow Solutions relationships, not generating new ones.

## Open threads / mid-flight items

- The 2-step application form on discovery.html is not yet landing for Matt ("not quite there yet") - needs another pass once we're back from the token-usage detour. No specifics on what's still wrong.
- Cloudflare Pages deployment of `site/` is still pending Matt's explicit go-ahead (asked twice, no answer yet). This blocks the analyzer's CTA from working and blocks the site going public.
- Matt was mid-way through reviewing the restyled testimonial quote breaks (bigger, bolder, dark background, initials badge) when the session pivoted to token usage - no confirmed reaction yet.
- Token usage: Matt was at 69% of 5-hour limit and 83% of weekly cap earlier in session. Recommended disconnecting unused MCP integrations (Adobe, customer-support plugins, small-business plugins, Figma, Linear, Asana, etc.) as the top lever. No confirmation yet that Matt has acted on this.

## Next steps

1. Get Matt's verdict on the 2-step application form and the new testimonial styling once token pressure eases.
2. Get explicit go/no-go on deploying `site/` to Cloudflare Pages (unblocks the analyzer's dead CTA link).
3. Suggest Matt ask Mark for 2-3 more real client quotes to expand testimonial coverage beyond the current 3.

## Workspace state at save time

- Modified files: `site/discovery.html`, `site/index.html`, `site/thank-you.html` (all uncommitted)
- Untracked files: none reported
- Last commit: 7a9695c chore: update session note
- Not yet saved to git (run /commit later): yes
