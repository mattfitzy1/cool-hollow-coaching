# Workspace History

> Chronological log of all work done in this workspace. Updated every session.
> Most recent entries at the top. Each entry has a date, title, and bullet points.
>
> How it works: when you run `/commit` after meaningful work, Claude adds an entry here
> automatically. You do not need to write this file yourself.

---

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
