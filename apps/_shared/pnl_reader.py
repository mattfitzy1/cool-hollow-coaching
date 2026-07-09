"""
Shared "accepts anything" P&L reader for the milestone tools.

Owners should never have to re-type their numbers into our template just to
run a tool. This reader takes whatever P&L a client actually has and returns
the same clean shape either way:

- Our branded template (the "P&L" tab with a "Line Item" header),
- a QuickBooks P&L export (Excel or CSV): company-name title rows, a header
  row with a blank first cell and month/Total columns, Income / Cost of
  Goods Sold / Expenses section structure, subtotal rows, $1,200 and (500)
  style formatting,
- or the client's own simple spreadsheet (a label column plus amount columns).

Output: DataFrame with line_item, category (revenue / cogs / expense /
leakage / other) and one or more numeric amount columns. Section-header and
subtotal rows are removed so nothing is ever double counted, and a grand
"Total" column is dropped whenever real month columns exist for the same
reason. Ported from the hidden-profit-analyzer's proven parsing, extended
with the leakage category the Profit Discovery Audit needs.
"""

from __future__ import annotations

import re

import pandas as pd

from text_safety import clean_line_item

# Category keywords, aligned with profit-discovery-audit/analysis.py
REVENUE_KEYWORDS = ["revenue", "sales", "income"]
COGS_KEYWORDS = ["cogs", "cost of goods", "cost of sales", "direct cost"]
LEAKAGE_KEYWORDS = ["discount", "write-off", "writeoff", "credit memo", "bad debt", "refund"]

# Section headers, the way QuickBooks and most accountants label them
REVENUE_HEADERS = {"income", "revenue", "sales", "ordinary income", "income / revenue", "revenues"}
COGS_HEADERS = {"cost of goods sold", "cost of sales", "cogs", "cost of revenue", "costs of goods sold"}
EXPENSE_HEADERS = {"expenses", "expense", "operating expenses", "operating expense", "overhead",
                   "general & administrative", "payroll expenses", "selling general & administrative"}
OTHER_HEADERS = {"other income", "other expenses", "other expense",
                 "other income / expense", "other income/expense"}

TOTAL_PATTERNS = [
    "total", "subtotal", "sub-total", "gross profit", "gross margin", "gross income",
    "net profit", "net income", "net loss", "net ordinary income", "operating income",
    "operating profit", "ebitda", "ebit", "profit before tax", "income before tax",
    "profit/(loss)", "grand total", "bottom line",
]

_MONTHS = {
    "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
    "january", "february", "march", "april", "june", "july", "august", "september",
    "october", "november", "december",
}
_AMOUNT_HEADER_HINTS = {"total", "amount", "balance", "ytd", "year to date"}
_SKIP_SHEETS = {"instructions", "examples", "example", "starter ideas"}
_BLANK_CELLS = {"", "-"}


def _to_number(value) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    s = str(value).strip()
    negative = s.startswith("(") and s.endswith(")")
    s = re.sub(r"[,$()%\s]", "", s)
    if s in _BLANK_CELLS:
        return 0.0
    try:
        number = float(s)
    except ValueError:
        return 0.0
    return -number if negative else number


def _strip_code(label: str) -> str:
    return re.sub(r"^(?:\d+\s+)+", "", str(label)).strip()


def _norm_label(label: str) -> str:
    s = _strip_code(label).lower().strip()
    s = re.sub(r"[^a-z0-9& ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _is_total_row(label: str) -> bool:
    t = label.lower().strip()
    return any(p in t for p in TOTAL_PATTERNS)


def _section_for(norm_label: str):
    if norm_label in REVENUE_HEADERS:
        return "revenue"
    if norm_label in COGS_HEADERS:
        return "cogs"
    if norm_label in EXPENSE_HEADERS:
        return "expense"
    if norm_label in OTHER_HEADERS:
        return "other"
    return None


def _keyword_category(label: str) -> str:
    text = label.lower()
    if any(k in text for k in LEAKAGE_KEYWORDS):
        return "leakage"
    if any(k in text for k in COGS_KEYWORDS):
        return "cogs"
    if any(k in text for k in REVENUE_KEYWORDS):
        return "revenue"
    return "expense"


def _looks_like_amount_header(value) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    text = str(value).strip().lower()
    if not text:
        return False
    if text in _AMOUNT_HEADER_HINTS:
        return True
    first = text.replace(",", " ").split()[0] if text.split() else ""
    if first in _MONTHS:
        return True
    return bool(re.fullmatch(r"(19|20)\d\d", first))


def _looks_like_template_header(value) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    return str(value).strip().lower().replace(" ", "_") == "line_item"


def _extract_table(raw: pd.DataFrame) -> pd.DataFrame:
    """From a header-less frame, find the real header row (our template's
    'Line Item' row, or a QuickBooks-style row of month/Total labels above
    the numbers), drop the title rows above it, and name the columns."""
    raw = raw.dropna(axis=1, how="all").dropna(axis=0, how="all").reset_index(drop=True)
    if raw.empty or raw.shape[1] < 2:
        raise ValueError(
            "This file does not look like a P&L, it needs a label column and at "
            "least one amount column."
        )

    label_col = raw.columns[0]
    amount_cols = list(raw.columns[1:])

    header_idx = None
    for i in raw.index[:10]:
        if _looks_like_template_header(raw.at[i, label_col]):
            header_idx = i
            break
        if any(_looks_like_amount_header(raw.at[i, c]) for c in amount_cols):
            header_idx = i
            break

    if header_idx is not None:
        headers = []
        for k, c in enumerate(amount_cols):
            label = raw.at[header_idx, c]
            label = str(label).strip() if label is not None and not pd.isna(label) else ""
            headers.append(label or f"amount_{k}")
        body = raw.loc[header_idx + 1:]
    else:
        headers = [f"amount_{k}" for k in range(len(amount_cols))]
        body = raw

    out = pd.DataFrame({"line_item": body[label_col].values})
    for h, c in zip(headers, amount_cols):
        out[h] = body[c].values
    return out


def _choose_sheet(sheets: dict) -> pd.DataFrame:
    """Prefer a sheet named like a P&L, otherwise the fullest data sheet.
    Our template's Instructions/Examples/Starter Ideas tabs are never data."""
    best, best_score = None, -1
    for name, frame in sheets.items():
        if name.strip().lower() in _SKIP_SHEETS:
            continue
        score = int(frame.notna().sum().sum())
        lname = name.lower()
        if "p&l" in lname or "profit" in lname or "loss" in lname or "pnl" in lname:
            score += 100000
        if score > best_score:
            best, best_score = frame, score
    if best is None:
        raise ValueError(
            "This workbook only contains Instructions/Examples tabs. Fill in the "
            "P&L tab, or upload your own P&L export, and try again."
        )
    return best


def _has_amount(row, amount_cols) -> bool:
    for c in amount_cols:
        v = row[c]
        if v is None:
            continue
        if isinstance(v, float) and pd.isna(v):
            continue
        if str(v).strip() == "":
            continue
        return True
    return False


def _classify_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Walk the rows in document order: track the current section (Income,
    COGS, Expenses), drop section-header and subtotal/total rows, and give
    every remaining leaf row a category."""
    df = df.copy()
    df["line_item"] = df["line_item"].astype(str).str.strip()
    df = df[df["line_item"].str.len() > 0]
    df = df[df["line_item"].str.lower() != "nan"]

    amount_cols = [c for c in df.columns if c != "line_item"]

    keep_rows, categories = [], []
    current = None
    for idx, row in df.iterrows():
        label = row["line_item"]
        if _is_total_row(label):
            continue
        if not _has_amount(row, amount_cols):
            section = _section_for(_norm_label(label))
            if section is not None:
                current = section
            continue
        if any(k in label.lower() for k in LEAKAGE_KEYWORDS):
            category = "leakage"
        elif current is not None:
            category = current
        else:
            category = _keyword_category(label)
        keep_rows.append(idx)
        categories.append(category)

    out = df.loc[keep_rows].copy()
    out["category"] = categories
    out["line_item"] = out["line_item"].apply(clean_line_item)

    for c in amount_cols:
        out[c] = out[c].apply(_to_number)

    # A grand Total column alongside real month columns would double count.
    month_like = [c for c in amount_cols if str(c).strip().lower() not in _AMOUNT_HEADER_HINTS]
    if month_like and len(month_like) < len(amount_cols):
        out = out.drop(columns=[c for c in amount_cols if c not in month_like])

    return out.reset_index(drop=True)


def read_pnl(uploaded_file) -> pd.DataFrame:
    """Read any P&L a client has: our template, a QuickBooks export, or
    their own spreadsheet. Returns line_item, category, and amount columns,
    with subtotals and section headers already removed."""
    name = getattr(uploaded_file, "name", str(uploaded_file)).lower()

    if name.endswith(".csv"):
        try:
            raw = pd.read_csv(uploaded_file, header=None, dtype=object,
                              skip_blank_lines=False, engine="python")
        except Exception:
            uploaded_file.seek(0)
            raw = pd.read_csv(uploaded_file).T.reset_index().T.reset_index(drop=True)
        table = _extract_table(raw)
    else:
        sheets = pd.read_excel(uploaded_file, sheet_name=None, header=None)
        table = _extract_table(_choose_sheet(sheets))

    cleaned = _classify_and_clean(table)
    if cleaned.empty:
        raise ValueError(
            "No line items with amounts were found in that P&L. Check the file "
            "and try again."
        )
    return cleaned
