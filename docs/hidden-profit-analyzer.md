# System: Hidden-Profit Analyzer

> Takes an uploaded P&L (CSV, Excel, or PDF) and surfaces pricing gaps, cost leakage, and cash flow timing risk, with one headline dollar figure. Lead-magnet tool for Cool Hollow Coaching's front door.

## Architecture

```
[CSV/Excel/PDF upload] --> [pdf_parser.py, if PDF] --> [analysis.py: load_pnl + 3 checks] --> [Streamlit report in browser]
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
3. Three checks run independently and each return a dollar estimate plus plain-English findings:
   - `check_pricing_margin` — flags gross margin below a 50% benchmark.
   - `check_cost_leakage` — flags expense lines growing faster than 15% month over month, and lists the largest recurring costs.
   - `check_cash_timing` — flags months where outflow exceeds inflow (needs 2+ months of data to run).
4. The app sums the three estimates into one headline "profit and cash risk found" number.

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
- **Used by:** nothing yet. Planned: embed into the future program website, or link standalone from Instagram as a lead magnet.

## Open items

- Benchmarks (50% gross margin, 15% cost growth) are starting defaults, not yet validated against real client data.
- Not yet deployed anywhere public. Currently runs locally only.
- PDF parsing is heuristic (table extraction, then text-line pattern matching) and has not been tested against scanned or image-based PDFs, only text-based ones.

## History

| Date | Change |
|------|--------|
| 2026-06-22 | Initial build and documentation |
| 2026-06-22 | Added PDF upload support (table + text-line extraction) |
