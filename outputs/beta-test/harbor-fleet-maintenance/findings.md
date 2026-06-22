# Beta Test Findings: Harbor Fleet Maintenance vs. the 7 Milestone Tools

Ran a realistic $1M-$10M owner-operator business through all seven Business Without You tools end to end. Headline result first, then the two findings that matter before this goes in front of a paying client with a guarantee attached.

---

## The headline number

The tools said: **$196,600 in profit found, 34 hours a week reclaimable.** Both clear the promise (15 hours, $50K) with room to spare.

That's the good news. The bad news is in where that $196,600 actually comes from.

---

## Finding 1: Most of the "profit found" number is a benchmark artifact, not real money

Of the $196,600, **$184,000 (94%)** comes from two checks that work the same way: take a generic benchmark (50% gross margin, 20% line margin), compare it to the client's actual margin, multiply the gap by revenue. Only **$12,300** (the leakage check, which just adds up actual discounts and write-offs already on the books) is a hard number tied to real recorded dollars.

Two problems with that 94%:

1. **It scales with how many months of P&L the client happens to upload, not with the real size of the gap.** I gave the tool 3 months of P&L. The margin gap it found was real (32% vs. a 50% benchmark), but the dollar estimate is that percentage gap multiplied by 3 months of revenue. Upload 12 months of the same business instead of 3, and the identical underlying problem produces a number roughly 4x larger. Two coaches running the same client through this tool, one with a quarter of data and one with a year, walk away with two completely different "found" numbers for the same business.
2. **The 50% gross margin and 20% line margin benchmarks are industry-blind.** They're reasonable for a services or software business. They are not reasonable for a vehicle repair shop, a contractor, a distributor, or anything else with real cost of goods — Harbor Fleet's 32% gross margin might be perfectly healthy for that trade. Applying one universal benchmark to every industry means the tool will systematically overstate "profit found" for any lower-margin business model, which is a lot of the $1M-$10M trades and services world this program is aimed at.

This is the one I'd fix before anything else. If a client (or their accountant) asks "found compared to what, and why would the number change if I'd given you a different number of months," there's no good answer right now. That's exactly the conversation that breaks trust in a profit-back guarantee.

**The fix is straightforward:** annualize the benchmark math (gap × annualized revenue, not × however many months got uploaded) and let the benchmark vary by a rough industry/margin-profile input instead of one fixed 50%/20% for everyone. Both are real but contained changes to `profit-discovery-audit/analysis.py`, not a rebuild.

---

## Finding 2: the cash tool doesn't address the cash problem this kind of client actually has

Harbor Fleet's real cash issue is timing: two big accounts on net-45 terms, squeezed against weekly payroll. The Decision Filter (cut weak-case discretionary spend) is the right idea, but for this business it only found $350/week in real savings, a rounding error against a $21,000 weekly payroll. The 13-week forecast itself is solid and correctly built. But the tool has no module for "is receivables timing the actual problem," which it is for almost any B2B services or trade business with a couple of large, slow-paying customers, exactly the buyer profile Business Without You is selling to.

This isn't a bug, it's a gap: the framework as built optimizes for "stop wasting money," when for this entire customer segment the real lever is often "get paid faster" (deposits on big jobs, factoring, tighter terms, milestone billing). Worth a fourth question added to the cash milestone, even informally, before this goes live: where's the money actually stuck, not just where's it being wasted.

---

## One smaller thing worth knowing, not fixing yet

The 15-Hour Reclaim Protocol's "do this in week one" bucket landed at exactly 15 hours for Harbor Fleet, a nice coincidence that matches the headline promise. But it's a coincidence, not a guarantee: the tool buckets tasks into "this week / 2 weeks / 30 days" by splitting the ranked list into thirds by count, not by cumulative hours. A different mix of tasks (a few big ones at the top, lots of small ones lower down) could just as easily put 30 hours in week one and 4 hours in week three. It worked here. It won't always.

---

## Bottom line

The framework's instincts are right and the engineering underneath all seven tools is solid (clean validation, sensible scoring, no crashes on a realistic dataset). The two real findings here are about whether the **numbers the program promises to clients can be trusted to mean what they say**, not whether the code runs. That's worth fixing before this goes in front of someone paying $4,000-5,000 with a profit-back guarantee attached, and it's a much smaller fix than it sounds: mostly contained to `profit-discovery-audit/analysis.py` (annualize the math, make the benchmark configurable by rough business type) plus one added question in the cash milestone.

---

## Update: Finding 1 fixed, second beta test run

`profit-discovery-audit/analysis.py` and `app.py` now annualize every revenue-scaled estimate against a client-stated `period_months` (a number input in the app, not inferred from column headers) and use an industry-aware margin benchmark (trades/repair, retail/distribution, professional services, or high-margin recurring revenue) instead of one fixed 50%/20% for everyone.

Re-running Harbor Fleet through the fixed tool: **$196,600 → $155,600**, still well clear of $50K, but now traceable: every dollar is explicitly "a year" and "for this kind of business" instead of a 3-month figure inflated by a generic benchmark.

A second beta test, Bramblewood Creative (a high-margin marketing agency, the opposite end of the margin spectrum from Harbor Fleet's repair shop), confirms the fix holds in both directions: **$119,100/year found, 25 hours/week reclaimable**, against a 65%/30% benchmark appropriate to a healthy recurring-revenue business, still clearing the promise without overstating it. Full data and run logs in `outputs/beta-test/bramblewood-creative/`.

**One more real crack turned up in this round, since fixed:** all seven apps crash with a raw, technical pandas error (`Error tokenizing data. C error: Expected 4 fields in line 5, saw 5`) the moment a client's CSV has an unquoted comma in a name, e.g. "Smith, Jones & Co" or "Smaller retainers (combined, 5 accounts)" — both real-world-likely names, and exactly the kind of raw error dump the house style rules out. Fixed in all 7 `app.py` files: a `pandas.errors.ParserError` now shows a plain-English, actionable message (put the name in quotes or swap the comma for a dash) instead of the raw exception text.
