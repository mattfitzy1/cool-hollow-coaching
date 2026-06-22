# System: Hidden-Profit Analyzer

> Takes an uploaded P&L (CSV or Excel) and surfaces pricing gaps, cost leakage, and cash flow timing risk, with one headline dollar figure. Lead-magnet tool for Cool Hollow Coaching's front door.

## Architecture

```
[CSV/Excel upload] --> [analysis.py: load_pnl + 3 checks] --> [Streamlit report in browser]
```

## Key Files

| File | Purpose |
|------|---------|
| `apps/hidden-profit-analyzer/app.py` | Streamlit web app: file upload, renders the report |
| `apps/hidden-profit-analyzer/analysis.py` | Core logic: normalizes the P&L, runs the three checks |
| `apps/hidden-profit-analyzer/sample_pnl.csv` | Sample file for testing the upload flow |
| `apps/hidden-profit-analyzer/.venv/` | Local Python environment (not tracked in Git) |

## How It Works

1. User uploads a CSV or Excel P&L. First column is the line item name; remaining columns are either one `amount` column (totals only) or one column per month.
2. `load_pnl()` normalizes this into rows of `category` (revenue, cogs, expense, other), `line_item`, `month`, `amount`. Category is guessed from keywords in the line item name.
3. Three checks run independently and each return a dollar estimate plus plain-English findings:
   - `check_pricing_margin` — flags gross margin below a 50% benchmark.
   - `check_cost_leakage` — flags expense lines growing faster than 15% month over month, and lists the largest recurring costs.
   - `check_cash_timing` — flags months where outflow exceeds inflow (needs 2+ months of data to run).
4. The app sums the three estimates into one headline "profit and cash risk found" number.

## Configuration

No API keys needed. Runs entirely locally on Python + Streamlit + pandas + openpyxl.

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
pip install streamlit pandas openpyxl
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

## Dependencies

- **Depends on:** Python 3.9+, streamlit, pandas, openpyxl.
- **Used by:** nothing yet. Planned: embed into the future program website, or link standalone from Instagram as a lead magnet.

## Open items

- Benchmarks (50% gross margin, 15% cost growth) are starting defaults, not yet validated against real client data.
- Not yet deployed anywhere public. Currently runs locally only.
- PDF upload not yet supported, CSV/Excel only.

## History

| Date | Change |
|------|--------|
| 2026-06-22 | Initial build and documentation |
