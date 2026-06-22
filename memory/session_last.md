---
name: last-session-summary
description: What was worked on, decisions made, and next steps from the most recent session
---

**Date:** 2026-06-22

**What was worked on:**
- Walked through pricing structure for Tier 1 ($4,750 paid-in-full or $1,800 x3, profit-back guarantee) and reality-checked the $50K profit claim (plausible for $1M-$10M businesses, but unproven in this self-administered format until a real cohort runs it).
- Built the Profit Discovery Audit tool (`apps/profit-discovery-audit/`), the real in-program tool for the Discover the Hidden Profit milestone, covering pricing, cost, customer profitability, service mix, and revenue leakage. Distinct from the free `hidden-profit-analyzer` lead magnet.
- Reordered the curriculum's 7 milestones (Break the Binding Constraint moved from position 4 to 6) and rebalanced the 12-week schedule to keep the CFO's two weeks back to back. Defined a consistent 4-step flow (exercise, model, videos, diagnosis) for every milestone. Saved as the new canonical reference at `context/curriculum.md`.
- Built a CFO-facing pitch deck (`outputs/decks/2026-06-22-cfo-overview.html`) covering progress, curriculum, pricing, the lead funnel, and three open decisions needing Cam's sign-off (platform choice, how hard to commit the $50K guarantee, beta vs. full price for cohort one).
- Built and got approval on the first draft Cool Hollow Coaching brand pack (`outputs/creative/cool-hollow-coaching/`), pulling real palette (#0E4643 deep teal, #589BA8 sage-blue, #B4D351 lime), font (Poppins), and logo reference from Cool Hollow Solutions' live site.
- Drafted a viral Instagram reel script ("The Business That Owns You") in Mark's voice, tied to the hidden-profit analyzer as the CTA.
- Mapped out the voice/face cloning plan for Mark: ElevenLabs Instant/Professional Voice Clone is ready to go (key already in `.env`), explained that HeyGen's earlier failure was likely its own TTS voice, not the avatar, and the fix is feeding a cloned ElevenLabs voice track into the avatar tool instead.

**Key decisions:**
- Pricing full course (not beta-discounted): $1,800 x 3 default, profit-back guarantee framed as a working guarantee, not a settled marketing absolute.
- Milestone order changed: Reclaim Time, Define Destination, Install Dashboard, Discover Hidden Profit, Build Cash Confidence, Break the Binding Constraint, Build the Team.
- Brand pack approved using Cool Hollow Solutions' real colors/font as the starting point. Coaching has no logo of its own yet, two open paths (new mark vs. compass-icon variant), still needs Matt's call.

**Open / unfinished:**
- No connector exists yet for Instagram posting, Buffer, Later, or any scheduler (registry search came back empty). Decision pending on which scheduler to build against.
- Six of the seven per-milestone "models" (Discover the Hidden Profit's is live) still need building: 15-Hour Reclaim scorer, Strategy Razor/Impact Map filter, dashboard selector, cash forecast + decision filter, constraint ranker, hiring/delegation/leadership scorer.
- Logo direction for Cool Hollow Coaching not yet decided.
- Three CFO-facing decisions from the pitch deck still need Cam's actual answer: platform (Skool vs. own build), guarantee language, beta vs. full price for cohort one.
- Mark's voice clone hasn't been started yet, waiting on a clean 2-minute audio recording from him.
- The slide-deck skill's auto-PDF render pipeline (`scripts/render_deck.py`, Playwright) isn't installed in this workspace; decks currently get exported via browser print-to-PDF instead.

**Next steps:**
- Get a clean 2-minute recording of Mark and run the ElevenLabs voice clone.
- Pick a scheduler (Buffer/Later/Publer) so an Instagram-posting connector can be built.
- Decide the logo direction so `/creative` can generate on-brand assets with a real mark.
- Start building the next per-milestone model (likely the 15-Hour Reclaim scorer, since Milestone 1 is first in the new order).
