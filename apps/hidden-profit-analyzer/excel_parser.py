"""
Excel P&L parsing for the hidden-profit analyzer.

Real Excel P&Ls are messy at the top: a company name, a date range, and a blank row
before the actual table, and the amount column is often headed "Total" or by month
names rather than sitting in row 1. A naive pd.read_excel() treats the first title row
as the header and mangles everything.

This reads the sheet with no assumed header, drops empty rows and columns, finds the
real header row (the one labeling the amount columns), drops the title rows above it,
and returns a clean DataFrame: line_item plus one or more amount columns, in document
order. Same shape the PDF and CSV paths produce, so analysis.load_pnl reads it the same.
"""

from __future__ import annotations

import pandas as pd

_MONTHS = {
    "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
    "january", "february", "march", "april", "june", "july", "august", "september",
    "october", "november", "december",
}
_AMOUNT_HEADER_HINTS = {"total", "amount", "balance", "ytd", "year to date"}


def _looks_like_amount_header(value) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    text = str(value).strip().lower()
    if not text:
        return False
    if text in _AMOUNT_HEADER_HINTS:
        return True
    first = text.replace(",", " ").split()[0] if text.split() else ""
    return first in _MONTHS


def _choose_sheet(xls: pd.ExcelFile) -> str:
    best, best_score = xls.sheet_names[0], -1
    for sheet in xls.sheet_names:
        frame = xls.parse(sheet, header=None)
        score = int(frame.notna().sum().sum())
        if "profit" in sheet.lower() or "loss" in sheet.lower() or "p&l" in sheet.lower():
            score += 100000
        if score > best_score:
            best, best_score = sheet, score
    return best


def parse_excel(file) -> pd.DataFrame:
    xls = pd.ExcelFile(file)
    raw = xls.parse(_choose_sheet(xls), header=None)
    raw = raw.dropna(axis=1, how="all").dropna(axis=0, how="all")
    if raw.empty or raw.shape[1] < 2:
        raise ValueError("This sheet does not look like a P&L (need a label column and an "
                         "amount column). Try a CSV export instead.")

    raw = raw.reset_index(drop=True)
    label_col = raw.columns[0]
    amount_cols = list(raw.columns[1:])

    # Find the header row: the first row whose amount cells read like column headers.
    header_idx = None
    for i in raw.index[:8]:
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
    if len(amount_cols) == 1:
        out["amount"] = body[amount_cols[0]].values
    else:
        for h, c in zip(headers, amount_cols):
            out[h] = body[c].values
    return out
