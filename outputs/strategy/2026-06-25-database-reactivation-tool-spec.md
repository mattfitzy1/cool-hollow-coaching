# Database Reactivation — Tool Spec

**Date:** 25 June 2026
**Owner:** Matt's own product. Brand-neutral.
**Companion docs:** [Never Miss a Job spec](2026-06-25-never-miss-a-job-tool-spec.md) | [Build/run/price/bundle playbook](2026-06-25-build-run-price-bundle-playbook.md)
**Why this one:** it makes money the fastest, off a list the owner already owns. No new leads, no ad spend, nothing murky.

---

## 1. What it is, in one line

> **Wake up the customers you already have and turn them back into booked jobs.**

Every trades owner is sitting on a goldmine: a list of past customers who already know him, already paid him once, and have simply gone quiet. Database Reactivation sends those people a friendly text or email, in the owner's voice, that brings a chunk of them back. It is the closest thing to free money in the whole toolkit.

---

## 2. Why it works (and why it's the fast-cash one)

- The owner has **already done the hard part**: earning these customers and building trust. We are not finding new people, we are reminding old ones.
- **No ad spend.** This runs entirely off a list the owner already has.
- **It pays out in days, not months.** A missed-call tool waits for the phone to ring. Reactivation goes out and brings jobs back this week.
- **The list is the owner's own property**, so there is nothing legally murky about him texting his own past customers (with the consent rules below respected).

**Illustrative math (not a claim, just the shape of it):** an owner with 800 past customers, where even 3% book a $300 job, is about $7,200 in work from one campaign. Most trades owners have never done this once.

---

## 3. How it works, step by step

1. **Get the owner's list.** Their past customers, exported from wherever they keep them (QuickBooks, a spreadsheet, their job software, a shoebox of invoices).
2. **Clean and load it** into the system.
3. **Send a warm, personal reactivation message** in the owner's voice. Not a blast that feels like spam. A note that sounds like the owner himself reaching out.
4. **Reply and book.** When someone responds, the system asks what they need and books them straight into the calendar, the same engine as Never Miss a Job.
5. **Hand the owner booked jobs** and a simple tally: messages sent, replies, jobs booked, dollars booked.

One campaign, run over a few days, then repeatable every quarter or around seasonal hooks (AC before summer, heating before winter, gutters before fall).

---

## 4. The campaign templates (starting scripts)

Plain, warm, owner-to-customer. The owner's name and trade drop in automatically. Always with an easy opt-out, which is both polite and legally required.

**Opening reactivation (general):**
> "Hey {FirstName}, it's {OwnerName} from {BusinessName}. It's been a while since we took care of your {Job/Service}. Everything still running okay? If you're due a check or there's anything on your list, I've got some openings this week. Reply STOP to opt out anytime."

**Seasonal hook (example, AC tune-up before summer):**
> "Hey {FirstName}, {OwnerName} here. Summer's coming and the AC calls are about to flood in. Want me to get you booked for a tune-up before the rush hits and the heat does? Reply STOP to opt out."

**Gentle nudge (to non-repliers, a few days later):**
> "No worries if now's not the time, {FirstName}. Just wanted to make sure you weren't waiting on me. The offer holds whenever you need us. Reply STOP to opt out."

**Win-back with a reason to act:**
> "Hey {FirstName}, we had a cancellation open up {Day}. If you've been meaning to get that {Job} sorted, I can slot you in. First come first served. Reply STOP to opt out."

---

## 5. How we build it (GoHighLevel)

Same engine, a different play. Plain steps:

1. **Import the owner's customer list** into their sub-account.
2. **Build the campaign:** the opening message, the timed nudges, the booking flow, the tally report. Save it into the same snapshot family as Never Miss a Job so it deploys fast.
3. **Connect their number and calendar** (already done if they're a Never Miss a Job client).
4. **Send in small batches**, not one giant blast, so replies are manageable and it stays warm.
5. **Watch the bookings land** and report the result.

---

## 6. The compliance line (read this, it keeps you clean)

This is the one tool where the rules matter, so we do it right from day one:

- **Only the owner's real past customers.** People with an existing relationship with the business. Never a bought, scraped, or borrowed list.
- **Every message has an easy opt-out** (Reply STOP), and opt-outs are honored instantly.
- **Register the number for business texting (A2P)**, same as Never Miss a Job.
- **The owner confirms the list is his and these are his customers** before anything sends.

Done this way, it is the owner reaching out to his own customers, which is exactly what he's allowed to do. Stay inside this line and there is nothing to worry about.

---

## 7. How we charge for it

Reactivation is different from the monthly tools, because it delivers a burst of jobs fast. Two good models:

| Model | How it works | Best when |
|---|---|---|
| **One-time campaign fee** | A flat fee per campaign, e.g. $500 to $1,000, run quarterly. | Simple, predictable, easy to explain. |
| **Pay on results (rev-share)** | You take a percentage of the booked revenue the campaign produces, e.g. 10 to 15%. | Near-zero risk for the owner, which makes it the easiest yes when you're new and proving yourself. |

**Recommendation for you right now:** lead with **pay-on-results**. "I'll wake up your old customers, and you only pay me a cut of the jobs it actually books." For an owner that is a no-brainer, because he risks nothing. For you it is fast cash tied directly to the value you create, and it proves your worth so you can sell the monthly tools next.

---

## 8. How it stacks with Never Miss a Job

These two are a natural pair, and together they tell a complete story:

- **Database Reactivation** brings the money in now (past customers).
- **Never Miss a Job** stops the money leaking out (missed calls).

Sell the reactivation first as the "let me prove it with a cut of the results" offer, bank the win, then move the owner onto Never Miss a Job at $149/mo to keep the leads they're currently losing. One earns trust and fast cash, the other earns recurring revenue. That's your wedge.

---

## 9. Next steps

1. **Pick the charging model** (I'd start with pay-on-results).
2. **Find one owner with a past-customer list** willing to let you run a test campaign.
3. **I build the campaign setup** into the snapshot so it's ready to deploy.
4. **Run the first campaign**, capture the real numbers, and you've got both your first cash and your first proof.
