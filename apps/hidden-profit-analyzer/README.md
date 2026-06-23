# Hidden-profit analyzer

A first-look tool for Cool Hollow Coaching. An owner uploads a profit and loss
(CSV, Excel, or PDF) and gets a plain-English read of three things from their own
numbers. It is the honest lead magnet: it proves the program's worldview without
selling anything.

## What it does

Reads the uploaded P&L and reports three things, kept **separate** and labeled honestly:

1. **Pricing and margin.** The actual gross margin, plus a clearly-conditional
   sensitivity ("every 5 points of margin is worth about $X"). Never a claim that
   money exists today.
2. **Cost creep.** Line items that genuinely grew from the first month to the last,
   with the real dollar increase.
3. **Cash timing.** Months where money out exceeded money in, straight from the figures.

It **never** sums these into a single "profit found" headline (they are different
kinds of thing), and **never** invents a benchmark or a number the P&L does not support.

## How it stays honest

- Subtotal and total rows ("Total Revenue", "Gross Profit", "Net Income", and so on)
  are detected and excluded, so nothing is double counted.
- Unknown cost labels ("Utilities", "Insurance") default to expense rather than being
  silently dropped, so the totals stay true.
- Every report shows a "How we read your file" table so the user can confirm nothing
  was misread before trusting the numbers.

## Running it

```
.venv/bin/streamlit run app.py      # the app
.venv/bin/python backtest.py        # the proof: 5 hand-checked P&Ls, all must pass
```

## Backtest

`backtest.py` holds five P&Ls worked out by hand (healthy business, a creeping
subscription, loss-making months, a P&L full of subtotals, and messy `$1,200` /
`(500)` formatting). It asserts every headline figure. **Do not change the analysis
without re-running this and keeping it green.**

## Known limitations (be honest about these)

- **Revenue labels.** A revenue line that does not contain revenue, sales, income, or
  turnover (for example "Consulting Fees") will read as a cost. The "How we read your
  file" table is there to catch this. Check it on any real client P&L before trusting
  the numbers.
- **Benchmarks.** The margin sensitivity is a what-if, not an industry benchmark. The
  tool deliberately does not claim a "healthy margin" target, because that varies by
  industry and would be inventing a standard.

## Not yet live

This runs locally and passes its backtest. Before it goes in front of a prospect it
still needs: (1) a backtest against a couple of real, anonymized P&Ls, (2) a decided,
free public host, and (3) a final read of the privacy wording. Do not link it from
the Instagram bio until those are done.
