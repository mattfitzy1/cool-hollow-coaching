# Beta Test Subject: Harbor Fleet Maintenance

A realistic hypothetical company, built to be a believable Business Without You buyer, used to run all seven milestone tools end to end and see where the framework actually holds or breaks before this goes to a paying client.

---

## The business

**Harbor Fleet Maintenance** — commercial vehicle maintenance and repair shop, Lancaster, PA. Services delivery vans and box trucks for local logistics, courier, and distribution companies.

- **Owner:** Dave Sorrentino, founded the shop 9 years ago, grew it from a two-bay garage to a 16-person operation.
- **Revenue:** ~$3.4M/year.
- **Team:** 10 technicians, 2 service writers (front desk/scheduling intake), 1 parts manager, 1 dispatcher, 1 bookkeeper, Dave.
- **Customers:** two large fleet accounts (a regional courier company and a beverage distributor) make up about 55% of revenue, on net-45 payment terms. The rest is a long tail of smaller local fleets and walk-in commercial accounts, mostly paid on completion.

## Why Dave is the single point of failure

- Approves every quote over $500 himself before it goes to the customer.
- Personally negotiates every parts vendor contract and pricing tier.
- Still does about half the technician scheduling himself because the dispatcher defers big jobs to him.
- Reviews every invoice before it goes out.
- Sits in on every technician hire, including straightforward replacements.
- Chases the two big fleet accounts personally when payment runs late, because he has the relationship.
- Works roughly 62 hours a week and has not taken a real vacation in three years.

## Where it hurts

- **Cash:** the two big fleet accounts' net-45 terms create a real squeeze most months, especially when a slow month for walk-in/local work lands at the same time as a big payroll week.
- **Margin:** parts costs have crept up over the last two years and pricing hasn't kept pace; Dave suspects but hasn't measured that some smaller local accounts are barely profitable once tech time is counted properly.
- **No real dashboard:** Dave tracks the business in his head and a paper notebook. He finds out about a problem (a bad week, a churning customer, a vendor price hike) weeks after it started.
- **Team:** technician turnover is high relative to the trade average, and there's no real bench — if Dave's parts manager or lead tech left tomorrow, there's no one trained to step in cleanly.
- **No real strategic filter:** Dave has a list of five or six things he's "going to get to" (a second bay location, a fleet leasing tie-up, online booking, a loyalty program for local accounts) with no way to tell which actually deserves the next dollar and hour.

## Why this is a fair test

Harbor Fleet Maintenance sits squarely in the Tier 1 buyer profile: $1M-$10M revenue, owner-operator, owner is the bottleneck, real but unmeasured profit leakage, real cash timing risk, no dashboard, no bench. It is not a software business, which is deliberate — the seven tools were built generically; if the benchmarks and scoring inside them only make sense for a SaaS-shaped business, that's a finding, not a coincidence.

Data files (one per milestone, matching each tool's expected input format):

| Milestone | Files |
|---|---|
| 1 — Reclaim Time | `m1_time_log.csv` |
| 2 — Define Destination | `m2_initiatives.csv` |
| 3 — Install Dashboard | `m3_metrics.csv` |
| 4 — Discover Hidden Profit | `m4_pnl.csv`, `m4_breakdown.csv` |
| 5 — Cash Confidence | `m5_cash_items.csv`, `m5_recurring_expenses.csv` |
| 6 — Break the Constraint | `m6_constraints.csv` |
| 7 — Build the Team | `m7_roles.csv`, `m7_candidates.csv` |
