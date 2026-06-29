---
name: last-session-summary
description: "Quick /save snapshot - 2026-06-26 save-1 - funnel polish + token usage diagnosis"
---

**Date:** 2026-06-26 (Friday - /save snapshot, not a full /commit)

**What was worked on:**
- Removed a stray 61MB `Agent-Reach` repo from the workspace (moved to Trash), unrelated clone that was adding overhead.
- Caught and fixed a real compliance issue on the homepage: invented-looking "200+ companies" stat, client logos, and 3 testimonials with no disclosure. Matt confirmed these are real (Cool Hollow Solutions' track record), so added small-print disclosures instead of removing them.
- Applied Hormozi-style sales mechanics to homepage copy (hero, problem section, guarantee, CTA). Matt flagged that naming the exact $5,000 price in the guarantee felt premature for cold traffic - reverted to outcome-only framing, price stays in the FAQ.
- Removed the "2,000+ accounts" claim from index.html and discovery.html per Matt's request.
- Toned down the gold glow/glare on the homepage hero per Matt's feedback.
- Added a 3-step funnel indicator across all 3 pages (Step 1 of 3 / 2 of 3 / 3 of 3).
- Removed the "$5,000" question from the discovery.html application form, replaced with a no-dollar readiness question.
- Restructured homepage testimonials from one grouped section into 3 full-width quote breaks spread through the page, then restyled them bigger/bolder with initials badges after Matt's "needs more polish" feedback.
- Converted discovery.html's application form into a 2-step flow with progress bar and validation. Matt's reaction: "not quite there yet" - unresolved, paused before refining further.
- Confirmed the analyzer's "Want us to find the rest?" CTA exists in code but is a dead link until `site/` deploys to Cloudflare Pages. Asked Matt for go-ahead twice, no answer yet.
- Diagnosed Matt's fast token usage: biggest lever is the large list of connected-but-unused MCP integrations (Adobe, customer-support plugins, small-business plugins, Figma, Linear, Asana, etc.). Gave Matt a full grouped list of active vs. available-but-unauthenticated connections on request.

**Key decisions:**
- Testimonials/stats stay, with disclosure, not removal, since they're real (Cool Hollow Solutions' track record, not Coaching's).
- Exact pricing stays out of cold-traffic sections (hero, guarantee headline) - lives in the FAQ and later funnel stages instead, consistent with the approved diagnostic-first funnel mechanism.
- Never invent new testimonials under pressure to add "more" - real path is asking Mark for more real quotes from his client base.

**Open / unfinished:**
- 2-step application form on discovery.html still isn't landing for Matt ("not quite there yet") - no specifics yet on what's wrong, paused mid-feedback.
- Cloudflare Pages deployment of `site/` still pending Matt's go-ahead - blocks the analyzer's CTA and going public.
- New testimonial quote-break styling was applied but not yet confirmed by Matt (session pivoted to token usage before he reacted).
- Token usage: Matt was at 69% of 5-hour limit / 83% of weekly cap. Recommended disconnecting unused MCP integrations - not yet confirmed done.

**Next steps:**
- Get Matt's verdict on the 2-step form and new testimonial styling once token pressure eases.
- Get explicit go/no-go on Cloudflare Pages deployment for site/.
- Suggest Matt ask Mark for 2-3 more real client quotes to expand testimonial coverage.

**Save type:** /save (quick) - not yet saved to git, no HISTORY entry.
