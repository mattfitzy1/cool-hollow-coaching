# "Never Miss a Job" — Full Tool Spec

**Date:** 25 June 2026
**Status:** Spec for build. Pre-launch, zero clients yet. This is the plan to build, pilot, and scale.
**Companion doc:** [The #1 Blue-Collar Pain Point and the Tool That Kills It](2026-06-25-blue-collar-pain-point-and-tool-concept.md)

---

## 1. What it is, in one line

> **Never miss a job. Never sound like a robot. Never have to set anything up.**

A done-for-you system that catches every missed call for a trades business and turns it into a booked job, automatically, in the owner's own voice. The owner does nothing. We set it up and run it.

---

## 2. Who it is for

The owner-operator who is the reason the phone goes unanswered:

- Home-services or trades firm: plumbing, electrical, HVAC, roofing, landscaping, remodeling.
- Roughly $500K to $5M in revenue, crew of 2 to 15.
- Still on the tools or running the jobs himself.
- No real office manager, or one part-timer drowning in calls.
- Not a tech person, no time to become one.

---

## 3. What it does, step by step

This is the whole flow, from missed call to booked job. Nothing here needs the owner to lift a finger after setup.

1. **A customer calls and the owner can't pick up.** He's under a sink, on a roof, driving.
2. **Within seconds, the customer gets a text** in the business's own voice. Not a robot call. A text, which feels normal and fast: *"Hey, this is Dave at Dave's Plumbing. Sorry I missed you, I'm on a job. What do you need? I'll get you sorted today."*
3. **The customer texts back** what they need. The system asks a couple of simple questions (what's the problem, what's the address, how soon) so the job is qualified before the owner even looks.
4. **The system offers times** from the owner's calendar and books the callback or the visit.
5. **The owner gets a clean summary** on his phone: name, number, job, address, time booked. He walks up to a booked job instead of a missed call.
6. **If it's a quote, the system chases it** automatically over the next 48 hours, the window where most quotes die, so warm leads don't go cold.
7. **Every week, the owner gets one number:** jobs saved and dollars recovered. The proof, in his pocket.

**Why this beats the robot everyone else is selling:** nobody expects a human to text back in four seconds, so it never feels fake. It hits the 5-minute speed-to-lead window every single time, automatically, without a robot voice on the call that customers hang up on.

---

## 4. The text scripts (starting templates)

These are the default scripts, written in the Cool Hollow plain, warm, owner-to-owner voice. Each one gets customized to the individual owner's business name and trade during setup. No hype, no robotic phrasing.

**Instant missed-call reply:**
> "Hey, this is {OwnerName} at {BusinessName}. Sorry I missed your call, I'm out on a job. What do you need a hand with? Text me here and I'll get you sorted today."

**If no reply in 5 minutes (one gentle nudge):**
> "Still here whenever you're ready. Even a quick note on what's going on and your zip code and I'll get you booked in."

**Qualifying questions (sent as the conversation flows, not all at once):**
> "Got it. What's the address so I know where I'm headed?"
> "And how soon do you need someone, today, this week, or just planning ahead?"

**Booking offer (pulls live from calendar):**
> "I can get someone to you {Day} at {Time} or {Day} at {Time}. Which works better?"

**Confirmation:**
> "You're booked for {Day} at {Time}. You'll get a reminder the morning of. Thanks for reaching out to {BusinessName}."

**Quote follow-up (24 hours after a quote, if no reply):**
> "Hey {Name}, just checking you got the quote for {Job}. Happy to walk you through it or tweak anything. Want to lock in a date?"

**Quote follow-up (48 hours, final nudge):**
> "No rush at all, just don't want you waiting on me. The quote holds through {Date} if you'd like to go ahead."

---

## 5. How we build it (the GoHighLevel setup)

The engine is GoHighLevel. We are not inventing technology, we are productizing a configuration of it. Plain-English build steps:

1. **Create the agency account.** One GHL account holds every owner as a separate sub-account.
2. **Build one "master" sub-account** as the template: the missed-call-text-back automation, the qualifying flow, the calendar booking, the quote-chaser, and the weekly recap. Get it perfect once.
3. **Turn that master into a snapshot.** A snapshot is a saved copy of the whole setup that can be dropped onto any new owner's account in minutes. This is what makes 500 possible without 500 separate builds.
4. **For each new owner:** spin up their sub-account from the snapshot, connect their business phone number (or forward their existing line), connect their calendar, swap in their name and trade, register them for business texting (A2P, see below). Live the same day.
5. **At scale, turn on SaaS mode** so new owners self-onboard and get billed automatically.

### The texting compliance step (A2P 10DLC)

US carriers require every business to register before it can send automated texts. It's a one-time form plus a small fee (about $24.50 to register, around $11 a month after). We handle this for the owner as part of setup. It's not optional and it's not hard, it just has to be done per owner. ([HighLevel A2P guide](https://help.gohighlevel.com/support/solutions/articles/155000005200-a2p-10dlc-messaging-fees-registration-monthly-and-carrier-costs))

---

## 6. The account and cost structure (the answer to "what about 500")

**You need one GoHighLevel account, not 500.** Each owner is a sub-account inside it.

| What | Cost | Notes |
|---|---|---|
| GHL software (whole agency) | **$497/mo flat** on SaaS Pro | Covers all 500 owners. Unlimited sub-accounts plus auto-billing and rebilling. |
| Phone number, per owner | ~$1.15 to $2/mo | Rebilled to the owner with markup. |
| Texts, per owner | Pennies per message | Rebilled to the owner with markup. |
| Texting registration, per owner | ~$24.50 once, ~$11/mo | Passthrough, no markup allowed on this part. |

**The point:** the software cost is flat. The only thing that grows with more owners is usage, and in SaaS mode you rebill that usage to the owner with a markup, so it becomes margin. Your GHL bill at 500 owners is still $497 a month, and you're collecting 500 subscriptions on top of it.

Plan pricing held steady into 2026 at $97, $297, and $497. ([GoHighLevel pricing](https://www.gohighlevel.com/pricing))

---

## 7. What we charge for it (recommendation, to lock with Matt)

The math from the research: a missed call is worth $285 or more, a small firm misses dozens a month, and recovering even three jobs is hundreds to thousands of dollars back. So the price can be confident.

**Recommended: a setup fee plus a flat monthly.** A setup fee covers the done-for-you work and filters tire-kickers. A flat monthly is simple for a non-techy owner to say yes to. Exact numbers to be set together, but the framing is fixed:

> "It pays for itself the first time it saves you one job. After that, it's pure profit you were throwing away."

This is the same easy-yes logic as the $50,000-found-for-$5,000 program, shrunk to a tool a prospect feels in week one. Whether it's sold standalone, bundled into Business Without You, or used as a free or cheap front-door taster is a strategy call for Matt.

---

## 8. The rollout path (pilot to scale)

Cheap-first, prove-it-first. No big spend before it works.

- **Phase 1, Pilot (now):** $97 GHL plan, 3 sub-accounts. Build the master setup, run it live on 1 to 3 friendly owners (ideally Cool Hollow Solutions clients who'll give honest feedback). Goal: prove it saves real jobs and capture the first real "dollars recovered" numbers.
- **Phase 2, Refine:** tighten the scripts and flow from what the pilot teaches. Lock the snapshot.
- **Phase 3, Productize:** move to $497 SaaS Pro, turn on auto-onboarding and billing, set the price, open it up.
- **Phase 4, Scale:** sell it as the second front door to the coaching, feed every saved job into the client-win story bank.

---

## 9. How it feeds the coaching

Not a side project. A second front door and a proof engine for Business Without You.

- **A lead magnet that actually pays the prospect.** Like profitabletradie's free guide, but ours saves real money, which earns the right to sell the program.
- **The owner-exit promise, proven.** The phone is the single biggest wire running through the owner. Cut it and he has felt, for real and for a few dollars, what "a business that runs without you" means. That's the program's whole pitch, demonstrated.
- **A data engine for the sales story.** Every saved job is a real, dated, dollar-figured win, exactly the story bank you flagged as missing.

---

## 10. What I need from Matt to start the pilot

Small list, no rush, work through it at your pace:

1. **A yes on the pricing model** (setup fee plus monthly, and rough numbers).
2. **One to three pilot owners** to run it on first. Cool Hollow Solutions clients are perfect.
3. **The GHL account.** This is your first paid subscription, so it's your call. Start at $97 for the pilot. I'll walk you through sign-up one step at a time when you're ready.
4. **A green light to draft the owner-facing one-pager** that explains the tool, so you have something to show a pilot owner.

---

## Sources

- [GoHighLevel pricing](https://www.gohighlevel.com/pricing)
- [HighLevel pricing and rebilling guide](https://help.gohighlevel.com/support/solutions/articles/155000001156-highlevel-pricing-guide)
- [HighLevel A2P 10DLC messaging fees](https://help.gohighlevel.com/support/solutions/articles/155000005200-a2p-10dlc-messaging-fees-registration-monthly-and-carrier-costs)
- [GoHighLevel pricing plans 2026 (GHL Experts)](https://www.ghlexperts.com/gohighlevel-plans-pricing)
