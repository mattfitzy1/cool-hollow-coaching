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

- **Reads by section, not by guesswork.** A real P&L is read by its section headers
  (Income, Cost of Goods Sold, Expenses). Every line takes its section's category, the
  way an accountant reads it, so a revenue line named "Water Remediation" or a cost
  named "Clopay" is classified correctly even though the name gives no clue. Files with
  no section headers (a bare CSV) fall back to keyword classification.
- Subtotal and total rows ("Total Revenue", "Gross Profit", "Net Income", and so on)
  are detected and excluded, so nothing is double counted.
- PDFs are read line by line as text, which keeps account codes ("40200 Sales") glued
  to the label instead of being split out and counted as money.
- Every report shows a "How we read your file" table so the user can confirm nothing
  was misread before trusting the numbers.

## Validated against real P&Ls

The reader was checked against four real QuickBooks/Xero exports (two garage-door PDFs,
a trades-company PDF, and a restoration-company Excel). For each, the computed revenue,
COGS, and gross profit match the file's own stated totals to the cent. Those real files
are not stored in the repo; their structure is captured in synthetic backtest cases 6
and 7 instead.

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

- **Non-standard layouts.** Section reading depends on recognizable headers (Income,
  Cost of Goods Sold, Expenses). A P&L with unusual section names, or a scanned/image
  PDF with no extractable text, may not read cleanly. The "How we read your file" table
  is there to catch this. Check it on any real client P&L before trusting the numbers.
- **Header-less files.** A bare CSV with no section headers falls back to keyword
  classification, which can misread a revenue line like "Consulting Fees" as a cost.
  Section-structured files (most real exports) do not have this problem.
- **Benchmarks.** The margin sensitivity is a what-if, not an industry benchmark. The
  tool deliberately does not claim a "healthy margin" target, because that varies by
  industry and would be inventing a standard.

## Not yet live

This runs locally, passes its backtest, and reads four real P&Ls correctly to the cent.
Before it goes in front of a prospect it still needs: (1) a decided, free public host,
and (2) a final read of the privacy wording. Do not link it from the Instagram bio
until those are done.
