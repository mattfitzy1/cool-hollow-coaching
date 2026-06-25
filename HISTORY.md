# Workspace History

> Chronological log of all work done in this workspace. Updated every session.
> Most recent entries at the top. Each entry has a date, title, and bullet points.
>
> How it works: when you run `/commit` after meaningful work, Claude adds an entry here
> automatically. You do not need to write this file yourself.

---

## 2026-06-24

### Brand & Growth Roadmap and condensed explainer video
- Built a full Brand & Growth Roadmap from the marketing discovery call with Sam (and Josh): positioning (blue-collar niche, layered hook), offer ladder, story bank, content engine ("media company that sells coaching"), funnel, GoHighLevel, social audit, 90-day plan, and an in-house-vs-agency comparison. Saved as `outputs/strategy/2026-06-24-brand-and-growth-roadmap.md` (+ styled HTML + PDF). Purpose: show Cam we can build the marketing in-house instead of paying the agency's full fee.
- Stood up markdown-to-HTML and HTML-to-PDF helpers (`scripts/md_to_html.py`, `scripts/html_to_pdf.py`) so strategy docs render as clean branded pages/PDFs without pandoc.
- Built a 100-second condensed-roadmap explainer video (`outputs/videos/cool-hollow-brand/cool-hollow-brand-explainer.mp4`, 8.7MB): kinetic typography in the black/gold brand, ElevenLabs voiceover (Eric), synth music bed. Wrote the full render pipeline from scratch (`scripts/video/`) since the demo-video skill shipped without its engine code: TTS + timeline + music mix, Playwright frame capture, resume-on-stall capture, ffmpeg mux.
- Connected ElevenLabs (free tier) for voiceover; key stored in `.env`.

### Decisions
- Audience: niche on blue-collar owner-operators ($500K-$10M), not industry-agnostic. "We own the blue-collar space."
- Messaging: drop the bare "$50k found" claim as the lead; lead with the life (a business that runs without you), prove with real client stories.
- Offer framing: the $5K program is the front door that scales all of Cool Hollow; Tier 2 = $22K/year, open to all owners, 1-on-1 coaching twice a week.
- Video style: narrative/roadmap, not slogan montage; lock the script before rendering.

## 2026-06-23

### Team Launch and Scaling Plan Deck
- Built a 16-slide team-facing deck (`outputs/decks/2026-06-23-team-launch-scaling-plan.html` + PDF) in the black/white/gold Poppins brand: the launch plan, filming load, Tier 1 scaling, paid-ads option, Tier 2 outline, and the combined picture.
- Rewrote all copy to be plain and straight (not salesy), reframed the first cohort as "the people closest to us whose advice we trust," and listed the built tool under each of the 7 milestones.
- Set Tier 1 year one at ~$95k context-corrected (Cool Hollow Solutions now ~$95k/month, 45 clients), Tier 1 program goal $150k-$215k year one building to $300k-$450k by 18 months, Tier 2 priced at $22,000/year (exponential model), and a "what it's worth per week" snapshot (~$11,900/week for ~3 hrs at 80 Tier 1 + 10 Tier 2).
- Moved the dashboard module (milestone 3) from Mark to Cam: Mark now 13 lessons, Cam 11.

### Instagram Front Door Live: Profile, Bio, and Branded Link Hub
- Set the Instagram identity: handle `@businesswithoutyou`, name field `Mark · Business Without You`, all saved to `outputs/content/cool-hollow-coaching/instagram-profile.md`.
- Built a self-hosted, branded link-in-bio page (`link-in-bio/index.html`, black/gold/Poppins) instead of Linktree, so it carries no third-party branding or fee. Deployed it free to Cloudflare Pages, live at `business-without-you.pages.dev`.
- Wired the page buttons: Free Profit Finder (the deployed tool), Explore Cool Hollow (coolhollowsolutions.com), Cool Hollow Solutions + Mastermind Instagram (credibility), and a "Coming soon" Skool community button (parked until the link is ready).
- Finalized the bio after several rounds: "The same team behind Cool Hollow Solutions, now helping you step back. / Discover hidden profit and buy back your time. / Free Profit Finder ↓" (137 chars). Leads with credibility, keeps it honest (no selling the unbuilt program).
- Strategy decided: cross-promote from Cool Hollow Solutions and the Mastermind Instagram accounts to borrow credibility for the cold-start page; keep comment-to-DM manual for now to respect the no-automation-messaging rule. Skool link still outstanding.

### Hidden-Profit Analyzer Deployed Live
- Deployed the hidden-profit analyzer to Streamlit Community Cloud (free host), connected to the private GitHub repo. It is now public and working at `profit-finder-coolhollow.streamlit.app`.
- Verified end to end in the cloud with a real P&L: numbers match local exactly (e.g. Elite Restoration: revenue $1,435,139, gross margin 53%, operating margin -5%, costs at 105% of revenue).
- Fixed a display bug where Streamlit read the `$` in findings as LaTeX math (amounts showed in italics with no dollar sign); escaped them so dollar amounts render correctly. Auto-redeployed on push.
- Renamed the app URL to the clean `profit-finder-coolhollow.streamlit.app`.
- Tool is now genuinely bio-ready (it is a real, free value tool, so linking it breaks no "don't sell what isn't built" rule). Remaining: paste the live link into the IG bio; tidy negative-number formatting ("$-69,707" -> "-$69,707").

### Hidden-Profit Analyzer: Section-Aware Reader, Validated on Real P&Ls, Richer Insights
- Rebuilt the analyzer's P&L reader to classify lines by their section header (Income / Cost of Goods Sold / Expenses), the way an accountant reads a P&L, instead of guessing from line names. This fixes the failure found earlier (it had reported 100% and -2368% margins on real files).
- Validated against four real QuickBooks/Xero exports (two garage-door PDFs, a trades-company PDF, a restoration-company Excel). Computed revenue, COGS, and gross profit match each file's own stated totals to the cent. Real files are not stored; their structure is captured as synthetic backtest cases 6 and 7. Backtest now 7/7.
- Text-first PDF parsing keeps account codes ("40200 Sales") in the label instead of counting them as money. New `excel_parser.py` handles title rows, sheet selection, and amount-column detection so Excel uploads are robust.
- Expanded the report into genuinely useful, still-honest insights: profit snapshot (gross + operating margin, "you keep X cents per dollar"), where the money goes (top costs as a share of revenue, biggest lever), and levers (what a 1% price rise or 5 margin points is worth, plus breakeven revenue). All what-ifs labeled as what-ifs; no invented numbers.
- Established the honest framing: the tool surfaces signals and opens the conversation; it does not manufacture a "found $50,000" figure (that is the CFO's work inside the program). Nudged owners to upload monthly columns so cost-creep and cash-timing checks can run.

### First IG Post Live, Carousel Built, Hidden-Profit Analyzer Rebuilt for Honesty
- Went live with the first Instagram post (the "two-week vacation" carousel) on the new coolhollow.os page, on the free Publer path. Built it into a complete, paste-ready unit: 5 slides plus 3 quote graphics rendered as on-brand JPGs (black/gold/Poppins), caption, hashtags, and a LinkedIn rewrite. Saved to `outputs/content/cool-hollow-coaching/`.
- Set three standing rules from Matt: (1) default to "founder thinking mode" first-principles answers; (2) zero budget right now, free/manual paths only, flag anything paid; (3) never advertise, promise, or sell anything not yet built. Pre-launch copy stays problem/authority only, no buy or waitlist CTAs.
- Reviewed the two Mark video clips Matt posted: both carry Cool Hollow *Solutions* branding baked in (wrong brand for the Coaching page). Path agreed: get raw unbranded footage from Mark's archive and rebuild in Coaching's brand. Drafted a new honest bio (no product promise).
- Rebuilt the hidden-profit analyzer's math to be honest: reports margin, cost creep, and cash timing separately instead of one inflated "profit found" total; excludes subtotal/total rows so real P&Ls do not double count; removed the unbacked "$50k" promise and the unbuilt-$5k-program sell from the app copy; added a privacy line and a "how we read your file" transparency table. Added `backtest.py` (5 hand-checked P&Ls, all passing) and a README.
- Tested the analyzer on two real P&Ls (a door company PDF, a restoration company Excel). Both broke it: keyword classification cannot read real hierarchical P&Ls (reported 100% and -2368% margins). Diagnosis: it must read by section header (Income/COGS/Expenses), not line-name keywords. NOT ready for prospects; reader rebuild is the next session's first task, with both files locked in as tests.

### Reviewed Third-Party Repos, Verified Milestone Tools, Saved UI/UX Reference Skill
- Reviewed about a dozen GitHub repos Matt considered adding (Ruflo, addyosmani/agent-skills, system-prompts-leaks, Canopy, an unfiltered AI video studio, stop-slop, superpowers, and others). Recommended against nearly all of them: most were software-engineering tooling aimed at dev teams, not a fit for a one-person coaching business, and a couple (the no-content-filter video studio, the autonomous-agent infrastructure) carried real brand or operational risk.
- Saved one exception, `ui-ux-pro-max` (a design-pattern reference skill), into `.claude/skills/ui-ux-pro-max/`, for layout and conversion-flow reasoning on future site/landing page work, with locked brand colors and voice always overriding its generic suggestions.
- Ran a functional test across all seven Business Without You milestone tools against their sample data. All passed; added a missing `sample_receivables.csv` to Cash Confidence so its optional receivables-timing check (added last session) is actually covered by a test.
- Compared HeyGen, Higgsfield, and ElevenLabs pricing for Mark's AI video/voice clone. Recommendation: keep Higgsfield for general creative content, add ElevenLabs (~$22/mo) specifically for voice quality, since that was HeyGen's actual weak point.
- Set a standing rule: always self-review code for bugs and data leaks before calling a task done, instead of installing third-party engineering-workflow plugins for that purpose.

## 2026-06-22

### Brand Color Swap, Mark's Voice Profile, Funnel Site Draft, Meeting Prep
- Switched the brand palette from teal/sage/lime to black, white, and gold across `context/brand.md`, `brand.json`, and `brand-pack.md`. Locked the decision to keep Cool Hollow Solutions' compass icon as Coaching's device, recolored, rather than commissioning a new mark. The exploratory logo draft shares the new colors but still has real rendering bugs (broken icon geometry, wordmark clipping) and is not an approved file.
- Captured Mark's actual speaking voice in `context/mark-voice-profile.md` from real unscripted clips, separate from the general brand voice, for any script he delivers on camera.
- Reviewed Cloudflare Pages as the hosting path for a public funnel site (`site/`), a first homepage/discovery/thank-you draft, and Streamlit Community Cloud as the separate path needed for the seven Python tools.
- Built two more pitch decks: a Skool funnel structure walkthrough for the team, and a business plan overview for an outside consultant meeting, plus a written meeting-prep brief with tailored questions.
- Softened the hidden-profit analyzer's lead line to drop an implied track-record claim Cool Hollow Coaching hasn't earned yet (pre-launch, zero clients).

### Workspace tidy-up and backup
- Backed up the two beta-test runs (Bramblewood Creative, Harbor Fleet Maintenance) and the first Cool Hollow Coaching creative test image, none of which had been pushed to GitHub yet.
- Added Office lock files (`~$*.xlsx`) and local Streamlit logs to `.gitignore` so they stop showing up as changes.

### All 7 Business Without You Milestone Tools Built
- Built the six remaining per-milestone models, completing the full set: the 15-Hour Reclaim Protocol (`apps/reclaim-protocol/`), the 12-Month Impact Map (`apps/impact-map/`), the Monday Morning Dashboard (`apps/dashboard-selector/`), Cash Confidence (`apps/cash-confidence/`), the Bottleneck Breakthrough Plan (`apps/bottleneck-breakthrough/`), and Build the Team (`apps/team-builder/`). Each is a Streamlit app with its own scoring logic, tested against sample data, and documented in `docs/`.
- Built a branded Cool Hollow Coaching Excel template for all seven tools (including the previously-undocumented Profit Discovery Audit), each with an Instructions tab, dropdown and range validation, greyed-out example rows, and an in-app download button so a client never leaves the tool to get one.
- Code review pass across all seven: fixed a duplicate-initiative-name bug in the Impact Map, an alphabetical month-sorting bug and a milestone mislabel in the Profit Discovery Audit, and added a role-name-typo warning to Build the Team.
- Added a fourth, optional check to Cash Confidence: receivables timing, naming exactly how much cash is overdue against a client's own payment terms.

### Profit Discovery Audit, Curriculum Restructure, CFO Deck, Brand Pack
- Built the in-program Profit Discovery Audit tool (`apps/profit-discovery-audit/`), covering all five areas of the Milestone 5 framework: pricing gaps, cost inefficiencies, customer profitability, service mix, and revenue leakage. Distinct from the free `hidden-profit-analyzer` lead magnet.
- Reordered the 7 milestones (moved Break the Binding Constraint from position 4 to 6) and rebalanced the 12-week delivery schedule so the CFO's two weeks stay back to back. Saved as the new canonical reference at `context/curriculum.md`, including a 4-step exercise/model/videos/diagnosis flow for every milestone and a build-status table for the remaining per-milestone models.
- Built a CFO-facing overview pitch deck (`outputs/decks/2026-06-22-cfo-overview.html`) covering progress to date, the curriculum, pricing and guarantee structure, the organic lead funnel, and three open decisions for sign-off.
- Built the first draft Cool Hollow Coaching brand pack (`outputs/creative/cool-hollow-coaching/`), pulling real palette, font, and logo data from Cool Hollow Solutions' live site rather than guessing. Approved by the owner; logo direction still open.

### Initial Setup
- Rebuilt the context layer (business, personal, strategy, current-data) with the corrected business structure: Cool Hollow Coaching is the online scale-up arm of Cool Hollow Solutions (Mark's existing 35-client, $60K/month in-person advisory firm)
- Built a working first version of the hidden-profit analyzer at `apps/hidden-profit-analyzer/` (Streamlit app, CSV/Excel upload, checks pricing/margin, cost leakage, and cash timing)
- Initialized Git tracking and connected the workspace to GitHub (`mattfitzy1/cool-hollow-coaching`, private repo)
- Set up the documentation system (`docs/` folder with a routing index and templates)
