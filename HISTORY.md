# Workspace History

> Chronological log of all work done in this workspace. Updated every session.
> Most recent entries at the top. Each entry has a date, title, and bullet points.
>
> How it works: when you run `/commit` after meaningful work, Claude adds an entry here
> automatically. You do not need to write this file yourself.

---

## 2026-07-17

### Cool Hollow Solutions scale-up lane opened, acquisition audit built
- Brought the Cool Hollow Solutions restructure into AIOS scope: Matt is now working as the right hand to Mike (Michael Ruckman, Senteo) on realigning and scaling the firm, alignment workshops running August through the week of September 7. Updated CLAUDE.md and opened the project register.
- Saved the full July 17 call debrief (ACE offering model, community design, retainer redesign, pricing psychology) to deep memory, plus a first-pass scale-up diagnostic in outputs/strategy.
- Built a printable client acquisition audit worksheet (with a reusable PDF build script) and, working from the real Master Client List and On Pause sheets, traced every one of the 24 active clients back to a channel: Boardroom, LAN, Local, TSC, Mastermind, Referral, or the original 2021 webinar cohort. Referral and Mastermind counts now reconcile exactly with Matt's original estimates once the older clients are included.
- Drafted a community research brief and an ACE-model worksheet for the community design workstream.

## 2026-07-13

### 12-month self-study curriculum and consultant training notes
- Built a 12-month, part-time, self-directed business study plan (books, textbooks, podcasts) modeled on the influences behind Alex Hormozi and Michael Ruckman, sequenced for realistic part-time reading with a free-first/library-first budget path throughout.
- Compiled distilled learning notes on one anchor book per phase (frameworks, thinking behind each, applied directly to Business Without You).
- Built a separate Independent Consultant's Library: 14 books in priority tiers for general business consulting (not specific to Cool Hollow Coaching), aimed at the side hustle paying down the $15K debt.
- Expanded that into a full 12-week, in-depth consultant training guide pulling the best frameworks, scripts, and behavioral science from all 14 books, exported to a branded PDF.
- While double-checking the notes against the real curriculum, found and fixed a real inconsistency: CLAUDE.md, business-info.md, and current-data.md still showed the pre-June-22 milestone order (constraint-breaking at position 4) instead of the current canonical order in curriculum.md (position 6). Corrected all three.

## 2026-07-10

### CFO-level audit of the 7 milestone tools, two real bugs fixed, team speech drafted
- Ran a full CFO-standard audit of all 7 milestone tools plus the Profit Finder: engineering discipline scored above par overall, with two real issues confirmed against live test scenarios.
- Fixed the Profit Discovery Audit booking healthy revenue growth as fake "cost inefficiency" ($48,000 a year of false findings on a real test case). The check now compares each expense line's growth against revenue growth over the same months, and only flags a cost outpacing revenue.
- Fixed the audit headline double-counting the same margin weakness up to three times (pricing gaps, customer profitability, and service mix all price the same underlying revenue). The headline now takes the largest of the three plus cost inefficiencies and leakage, with the counting logic explained in the app and the client PDF.
- Fixed Cash Confidence silently mangling bad week values (a typo "20" became week 13, a blank became week 1) instead of warning the owner. It now rejects out-of-range or blank weeks with a clear message.
- Fixed Impact Map's wording for a kept-but-failed initiative, it no longer reads as "cut" while sitting in the kept list.
- Wrote up the full audit, plus a project-level risk review (beta-client critical path, single-channel acquisition risk, open pricing blocking three workstreams, key-man risk, the legal review bottleneck), in `outputs/strategy/2026-07-10-tool-audit-and-project-review.md`.
- Drafted the team-update speech to accompany the 18-slide "Progress and Path Forward" deck, in Matt's own words and voice: a printable Word version and an 18-page phone cue-card PDF, one speech beat per slide, for flicking through during the live Zoom presentation.

## 2026-07-09

### QuickBooks P&L support, a live-data rendering bug, and the Profit Finder fix
- Added QuickBooks P&L import to the Profit Discovery Audit: owners can now export straight from QuickBooks (or upload their own spreadsheet) with no re-typing, title rows, month columns, section subtotals, and accounting-style formatting are all handled, and subtotal rows are automatically excluded so nothing is double counted.
- Found and fixed a real bug surfaced by testing against a real client QuickBooks file: Streamlit renders text between two "$" signs as math notation, so any finding with two or more dollar figures (very common) was displaying as broken, garbled text instead of plain English. Fixed across the Profit Discovery Audit and Cash Confidence, the two tools that generate dollar findings; confirmed the other five tools never generate dollar text and were never affected.
- Found and fixed a second, related bug in the same pass: raw QuickBooks account-number prefixes ("66026 66026-Payroll Expense...") were leaking straight into results instead of a clean label. Fixed at the source so every tool that reads a P&L gets clean labels.
- Swept all 7 milestone tools for copy clarity; fixed one real issue (reclaim-protocol was showing "owner_only" with a raw underscore in results prose instead of plain English).
- Carried the same two fixes over to the public Profit Finder lead-magnet tool (profit-finder-coolhollow.streamlit.app), plus found and fixed a third bug there: section headers ("Expenses") were leaking into the cost-line table as fake "$0" line items. Verified live on the deployed site.

### Branded, secured, and rebuilt the 7 milestone tools for client use
- Gave all 7 tools (Reclaim Protocol, Impact Map, Dashboard, Profit Discovery Audit, Cash Confidence, Bottleneck Breakthrough, Team Builder) the Cool Hollow Coaching header and gold house styling, driven from one shared file so future logo changes update everywhere at once.
- Locked in a zero-data-retention policy: nothing uploaded or generated is ever stored on a server. Each tool now offers a branded PDF download of the client's own results, since that download is their only copy. Drafted disclaimer, terms of use, and privacy notice for a lawyer to review before real client data goes through the tools.
- Rebuilt all 7 Excel templates: Instructions, Examples, and a new Starter Ideas tab (common tasks, metrics, constraints, and roles to jog memory, names only, never pre-filled numbers or ratings).
- Found and fixed a real launch blocker: a client filling in the old templates and uploading them got rejected by every tool. Built a shared smart reader so one filled workbook uploads correctly into every box of a multi-file tool.
- Found and fixed a second bug: a "the tool never reads this tab" warning looked bold in the file but silently failed to render bold in Excel/LibreOffice due to a rich-text-in-merged-cell limitation. Verified the fix by converting to PDF and visually checking, not just trusting the file data.

## 2026-07-08

### 18-Slide PowerPoint Team Deck: Progress & Path Forward
- Built editable PowerPoint presentation (18 slides, HTML, PDF) for Mark, Cam, and Hannah to review the full progress since June and the path to product launch.
- Included two new strategic slides: the organic funnel playbook (Hormozi diagnostic-first mechanism + Cardone/Hormozi content lessons on leading with numbers, finance-led positioning, and saveable content) and the full offer menu (in-house/partner x event-based/cyclical matrix with real examples showing how every event has a recurring twin).
- Showcased all 7 milestone tools with live example screens (hidden-profit analyzer, Monday dashboard, cash confidence forecast) to illustrate how each milestone backs real client value.
- Mapped the customer journey, community-first pivot, and team roles (Mark as content face, Cam on CFO milestones, Hannah on hiring, Matt running operations).
- Maintained honesty throughout: pricing undecided, community build open, founding cohort sequencing a live risk — everything reflects what's truly decided vs. still being worked through with Mike.
- All copy follows Cool Hollow voice (direct, warm, outcome-led, no hype) and brand palette (black/white/gold, Poppins headers, Calibri body).

---

## 2026-07-06

### Community-First Pivot and Miro Board Prep Pack
- Debriefed the Mike (Senteo) call: locked in the community-first model. The 12-week program is now the front door, not the product. The recurring community is the real business. This changes the pricing shape, the funnel, and the pitch deck.
- Updated `context/business-info.md` and `context/strategy.md` to reflect the pivot: three-layer offer (entry / ongoing / partner-delivered), freemium + tiered pricing as a capacity valve, Zoom-first recording instead of AI clone.
- Built four filled Miro exercises for the July 14 call with Mike: package breakdown rings, customer journey (before/journey/after), cyclic identification and mapping, and the full CJM Blueprint Components grid (9 rows, 3 columns, color-coded by status).
- Produced `Miro_Board_Prep_Pack.pdf`: a 6-page branded offline briefing (black/white/gold) covering all four exercises, the MVP list, and call questions.

---

## 2026-07-05

### Monday Call Prep: Offer Inventory, Gap Analysis, and a Trades Pricing System
- Drafted two replies to Mike for the Monday pricing call: the exhaustive offer inventory (in-house/partner x event-based/cyclical, 32 items) and a point-by-point response to his 8-part gap analysis (both in `outputs/strategy/`).
- Wrote the three-pains response plan mapping Mike's trade-business pains (pricing, team engagement, sales function) to what exists, what extends, and what gets built new.
- Solved the trades pricing problem standalone: a three-layer system (true cost, price mechanics, close-rate thermostat) with stress tests and a week-by-week rollout (`outputs/strategy/2026-07-05-trades-pricing-system.md`).

## 2026-07-01

### Signature Framework, Funnel Blueprint, and Tool Polish
- Named the method: The Business Without You Method. Three phases: Get Your Time Back, Find the Money, Make It Run Without You.
- Wrote the full signature framework and client acquisition funnel blueprint (outputs/strategy/2026-07-01-signature-framework-and-funnel-blueprint.md).
- Built the 8-beat VSL script structure for the results-page video, with placeholders flagged for the two unverified facts needing confirmation from Mark.
- Mapped a 9-section landing page layout anchored to the diagnostic as the front door.
- Built the internal PDF briefing for Cam and Mark (outputs/strategy/BWY_Signature_Framework_and_Funnel_Blueprint.pdf).
- Closed the Cash Confidence "known gap" flag: receivables-timing module verified present and working.
- Re-skinned all 7 Excel templates to the approved black/white/gold palette.
- Answered the question of how to state an unverified claim in copy: five honest frameworks (mechanism, borrowed proof, "typically", challenge, target).

### Curriculum Correction, Brand Rebrand, and Curriculum PDF
- Corrected Milestone 3 (Install the Dashboard) lead to Mark + Cam (CFO) in both curriculum.md and the June 30 LSDE revision doc.
- Rebranded all 7 milestone Excel templates from the old teal/sage palette to the approved black (#1A1A1A) and gold (#C8A227) palette via template_builder.py.
- Exported the full curriculum as a clean, formatted PDF: outputs/strategy/curriculum-business-without-you.pdf.

---

## 2026-06-30

### Senteo Consultant Call and Curriculum Rebuild
- Attended 67-minute call with Mike Ruckman (Senteo): got feedback on curriculum structure, module length, pricing model, delivery approach, and platform choice.
- Rebuilt the entire curriculum 4-step flow from Exercise/Model/Videos/Diagnosis into Learn, See, Do, Extend based on Mike's organizational psychologist methodology.
- Added a Do step (guided worksheet on a fictional business) to every milestone so owners get a practice rep before touching their own data.
- Capped all video modules at 8 to 15 minutes. Ohio method and Jobs to Be Done added to Milestone 1 content.
- Key decision: do not film any videos until Milestones 1, 2, and 3 are run live on Zoom with 3 to 4 beta clients first.
- Mapped Cool Hollow Coaching against Mike's business maturity model (Balance Sheet to Relationship-Centric). Goal is Relationship-Centric: recurring community revenue, not just one-time program sales.
- Action items logged: call Mark, send Mike calendar invite for Monday 6pm, pricing and MVP definition to be worked through with Mike on Monday.

---

## 2026-06-29

### Funnel Polish: Two-Step Apply Form, Softer Glow, Dropped Unverified Stat
- Converted the discovery.html application into a real 2-step flow (contact info, then qualifying questions) with a progress bar, replacing the single long-scroll form.
- Added a 3-step funnel indicator ("Step 1 of 3" etc.) across index.html and discovery.html so a visitor can see where they are in the diagnostic-then-apply path.
- Dropped the "2,000+ accounts" claim from index.html's story section, since it wasn't a number Matt could stand behind for Cool Hollow Coaching specifically. Added a small-print disclosure clarifying the "200+ companies" track record belongs to Cool Hollow Solutions, not Coaching.
- Softened the gold button glow and hero glow (lower opacity, more blur) per earlier feedback that it read too bright.
- Refreshed `key-metrics.md` exchange rates and saved a deep-memory note from the prior session's funnel work.

## 2026-06-26

### Hormozi Funnel Mechanism, Blue-Collar Redesign, and Lead-Gated Analyzer
- Read the Hormozi/Acquisition.com funnel teardown and the blue-collar synthesis doc, approved adopting the mechanism: free diagnostic gated by email capture, immediate post-result pitch, fit-gated application before any sales call. Saved both as standing project memories for future funnel and content work.
- Added a name/email capture gate to the hidden-profit analyzer (`apps/hidden-profit-analyzer/app.py`): the report no longer renders until the visitor submits contact info, which saves to a local gitignored `leads.csv`. Added a post-report CTA pointing to the application.
- Retargeted all three site pages (`site/index.html`, `discovery.html`, `thank-you.html`) from generic "business owner" language to named trades (HVAC, plumbing, electrical, roofing, construction), using the swipe-template hooks from the synthesis research.
- Full redesign pass after feedback that the pages weren't on-brand: swapped the elegant italic serif (Fraunces) for Barlow Condensed + Manrope, a bolder industrial pairing that fits the blue-collar audience. Fixed a real bug where several trust-strip logos (Premier HVAC, Cline Collision, Laurel Asphalt, Luxus Property) were invisible, white-on-white, by classifying each logo as light or dark and giving only the dark ones a white backing chip.
- Trimmed the homepage from ~12 sections to 8 (deleted a fully redundant "more than a coaching program" section, cut the FAQ from 11 questions to 6, fixed a stale product-name mismatch in one FAQ answer), and reduced competing CTAs down to one dominant action per page instead of "Apply Now" competing with the diagnostic everywhere.
- Brought `thank-you.html` onto the current black/gold brand palette; it had been left on the old teal/sage scheme since before the rebrand.

### Workspace tidy-up
- Confirmed no secrets staged; added `.claude/launch.json` (local static-server config for previewing `site/`) and a leads.csv gitignore rule.

### Never-Miss-a-Job Concept and Hormozi/Cardone Teardown
- Deep research teardown of Hormozi and Cardone Ventures' blue-collar funnels: hook patterns, audience sentiment and weak spots, and where Cool Hollow can position against them, with a synthesis report tying it together.
- Spec'd out a new "never miss a job" tool concept and checked it against market saturation before committing further.
- Drafted a database reactivation tool spec and a build-run-price bundle playbook for packaging services around these tools.
- Wrote a marketing one-pager and sales video script for never-miss-a-job, and an AI operator product vision doc.
- Installed the `claude-for-safari` skill (third-party, controls the real Safari browser) for use in another session; flagged its Snyk High Risk rating and the multi-tab visibility caveat, saved to memory for future reference.

### Tier 2 Pricing Update and Blue-Collar Niche Market Research
- Updated the scaling plan deck: Tier 2 now priced at **$25,000–$35,000/year** (raised from $22,000). Revised all references in the deck including the long-term revenue math (25 Tier 2 members at the new range), year-two projections (10 members at ~$30K = $300K), and supporting footnotes.
- Built comprehensive **blue-collar high-ticket coaching market research** in three formats (Markdown, HTML, PDF): validated the niche with data on $16–20B coaching market, $650–750B home services, and four major competitors (Breakthrough Academy $38.7K–$105.3K, Contractor Fight $697/mo, Tommy Mello tiered, CertainPath $399+/mo). Identified Cool Hollow's unowned gap: owner-exit + CFO expertise (vs competitors' growth/scale focus), with defensible pricing at $5K–$35K vs market's $38K–$105K. Confirmed the niche does not cap the $1.5M goal (900K+ contractor establishments in addressable universe) and documented the engagement science for time-poor owners (short lessons, high price, community accountability).

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

### GTD System, Logo on Landing Pages, Deck v2
- Installed the Productivity OS (GTD): `gtd/` inbox, next-actions, projects, areas, waiting-for, someday-maybe, dashboard, and refresh/inbox-capture scripts, customized to Cool Hollow Coaching's own areas (Content & Social, Funnel & Lead Gen, Product & Delivery, Platform & Tools, Finance & Pricing, Team & Partners).
- Installed Intel OS collection scripts (Fireflies/Fathom meeting collectors, Slack classifier, shared `data/data.db` tables) ahead of getting a recorder connected; decided to use a personal Fathom account rather than fight the office Google Workspace admin lock.
- Recolored the Cool Hollow compass-mark logo to the Coaching gold/black/champagne palette and added it to both `site/index.html` (top-left nav) and `link-in-bio/index.html` (centered top).
- Rebuilt the team launch and scaling deck as v2: added the logo, a new organic-marketing (attract/capture/convert) slide, a cost-to-run slide framing the ~$850/month stack as funnel-building not overhead, and upgraded year-two growth numbers (15 new Tier 1 clients/month, 4 new Tier 2 members/month, ~$1.9M), with explicit "not a made up figure" arithmetic behind the $3M goal. Checked older slides for consistency with the new numbers.

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
