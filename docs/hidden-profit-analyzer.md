# System: Hidden-Profit Analyzer

> Takes an uploaded P&L (CSV, Excel, or PDF) and surfaces pricing gaps, cost leakage, and cash flow timing risk, kept as separate honest findings (no inflated single number). Lead-magnet tool for Cool Hollow Coaching's front door, gated behind email capture.

## Architecture

```
[CSV/Excel/PDF upload] --> [pdf_parser.py, if PDF] --> [analysis.py: full breakdown] --> [email/name gate, saves to leads.csv] --> [Streamlit report] --> [CTA to site/discovery.html]
```

## Key Files

| File | Purpose |
|------|---------|
| `apps/hidden-profit-analyzer/app.py` | Streamlit web app: file upload, renders the report |
| `apps/hidden-profit-analyzer/analysis.py` | Core logic: normalizes the P&L, runs the three checks |
| `apps/hidden-profit-analyzer/pdf_parser.py` | Extracts a P&L-shaped table from an uploaded PDF (table extraction first, text-line fallback) |
| `apps/hidden-profit-analyzer/sample_pnl.csv` | Sample CSV for testing the upload flow |
| `apps/hidden-profit-analyzer/sample_pnl.pdf` | Sample PDF for testing the PDF upload flow |
| `apps/hidden-profit-analyzer/requirements.txt` | Pinned dependency versions |
| `apps/hidden-profit-analyzer/.venv/` | Local Python environment (not tracked in Git) |

## How It Works

1. User uploads a CSV, Excel, or PDF P&L.
   - CSV/Excel: first column is the line item name; remaining columns are either one `amount` column (totals only) or one column per month.
   - PDF: `pdf_parser.parse_pdf()` first tries pdfplumber's table extraction (works for clean QuickBooks/Xero exports), then falls back to line-by-line text parsing that matches a label followed by one or more dollar amounts. Either path produces the same line_item + amount-column shape as a CSV upload.
2. `load_pnl()` normalizes this into rows of `category` (revenue, cogs, expense, other), `line_item`, `month`, `amount`. Category is guessed from keywords in the line item name.
3. `run_full_analysis()` returns five sections, each kept separate and never summed into one number: profit snapshot (margins), where the money goes (top cost lines), leverage (the biggest dollar moves), cost creep (line items genuinely growing), and cash timing (months where outflow exceeded inflow).
4. Before the report renders, `st.session_state.get("lead_captured")` gates it: a name/email/business form must be submitted first. On submit, `save_lead()` appends to `leads.csv` in this folder (gitignored, real contact info, never committed) and the report unlocks via `st.rerun()`.
5. Right after the report, a CTA ("Want us to find the rest?") links to `site/discovery.html` via `APPLY_URL` — the pattern-interrupt step that pitches the program the moment the result lands, instead of waiting for a follow-up email. `APPLY_URL` is `"#"` until `site/` is deployed to Cloudflare Pages.

## Configuration

No API keys needed. Runs entirely locally on Python + Streamlit + pandas + openpyxl + pdfplumber.

## Common Operations

**Start the app:**
```bash
cd apps/hidden-profit-analyzer
source .venv/bin/activate
streamlit run app.py
```

**Set up the environment from scratch:**
```bash
cd apps/hidden-profit-analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Test the analysis logic directly:**
```bash
source .venv/bin/activate
python3 -c "
import pandas as pd
from analysis import run_full_analysis
print(run_full_analysis(pd.read_csv('sample_pnl.csv')))
"
```

**Test the PDF parser directly:**
```bash
source .venv/bin/activate
python3 -c "
from pdf_parser import parse_pdf
from analysis import run_full_analysis
with open('sample_pnl.pdf', 'rb') as f:
    print(run_full_analysis(parse_pdf(f)))
"
```

## Dependencies

- **Depends on:** Python 3.9+, streamlit, pandas, openpyxl, pdfplumber.
- **Used by:** `site/index.html` and `site/discovery.html` link to it as the primary front-door CTA. It links back out to `site/discovery.html` after the report.

## Open items

- Benchmarks (50% gross margin, 15% cost growth) are starting defaults, not yet validated against real client data.
- `APPLY_URL` in `app.py` is a placeholder until `site/` is deployed to Cloudflare Pages.
- PDF parsing is heuristic (table extraction, then text-line pattern matching) and has not been tested against scanned or image-based PDFs, only text-based ones.
- `leads.csv` is a local file on whatever machine runs the Streamlit deploy; no CRM/GoHighLevel hookup yet, so leads need to be pulled manually until that's wired.

## History

| Date | Change |
|------|--------|
| 2026-06-22 | Initial build and documentation |
| 2026-06-22 | Added PDF upload support (table + text-line extraction) |
| 2026-06-23 | Deployed to Streamlit Community Cloud at profit-finder-coolhollow.streamlit.app |
| 2026-06-25 | Added email/name capture gate before the report, and a post-report CTA to apply for Business Without You, adopting the Hormozi funnel mechanism (diagnostic → email gate → immediate pitch → fit application) |

Note: this doc covers the lead-magnet tool. For the in-program Milestone 4 tool, see `docs/profit-discovery-audit.md`.
