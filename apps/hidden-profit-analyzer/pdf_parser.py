"""
PDF P&L parsing for the hidden-profit analyzer.

P&L PDFs vary a lot in layout, so this takes two passes:
1. Try pdfplumber's table extraction first (works for clean exports from
   QuickBooks, Xero, and similar tools).
2. Fall back to line-by-line text parsing, matching a line item name followed
   by one or more dollar amounts (works for simpler, less structured PDFs).

Either path produces a plain DataFrame with a line_item column plus one or
more amount columns, the same shape a CSV/Excel upload would produce, so it
can be handed straight to analysis.load_pnl().
"""

from __future__ import annotations

import re

import pandas as pd
import pdfplumber

AMOUNT_PATTERN = re.compile(r"\(?-?\$?\s?[\d,]+(?:\.\d{2})?\)?")


def _clean_amount(text: str) -> float:
    negative = text.strip().startswith("(") and text.strip().endswith(")")
    cleaned = re.sub(r"[()$,\s]", "", text)
    if not cleaned or cleaned in ("-",):
        return 0.0
    value = float(cleaned)
    return -value if negative else value


def _try_table_extraction(pdf) -> pd.DataFrame | None:
    rows = []
    header = None

    for page in pdf.pages:
        for table in page.extract_tables() or []:
            if not table or len(table) < 2:
                continue
            for row in table:
                if row is None or not row[0]:
                    continue
                label = str(row[0]).strip()
                amounts = [c for c in row[1:] if c is not None and str(c).strip()]
                if not amounts:
                    continue
                if header is None:
                    header = [str(c).strip() if c else f"col_{i}" for i, c in enumerate(row)]
                    continue
                rows.append([label] + amounts)

    if not rows:
        return None

    max_cols = max(len(r) for r in rows)
    columns = ["line_item"] + [f"month_{i}" for i in range(max_cols - 1)]
    padded = [r + [None] * (max_cols - len(r)) for r in rows]
    return pd.DataFrame(padded, columns=columns)


def _try_text_extraction(pdf) -> pd.DataFrame | None:
    rows = []

    for page in pdf.pages:
        text = page.extract_text() or ""
        for line in text.split("\n"):
            amounts = AMOUNT_PATTERN.findall(line)
            amounts = [a for a in amounts if a.strip() not in ("", "-")]
            if not amounts:
                continue
            label = AMOUNT_PATTERN.sub("", line).strip(" .:-\t")
            if not label or len(label) < 2:
                continue
            rows.append([label] + amounts)

    if not rows:
        return None

    max_cols = max(len(r) for r in rows)
    columns = ["line_item"] + [f"month_{i}" for i in range(max_cols - 1)]
    padded = [r + [None] * (max_cols - len(r)) for r in rows]
    return pd.DataFrame(padded, columns=columns)


def parse_pdf(file) -> pd.DataFrame:
    """Extract a P&L-shaped DataFrame from an uploaded PDF file object."""
    with pdfplumber.open(file) as pdf:
        df = _try_table_extraction(pdf)
        if df is None or df.empty:
            file.seek(0)
            with pdfplumber.open(file) as pdf2:
                df = _try_text_extraction(pdf2)

    if df is None or df.empty:
        raise ValueError(
            "Could not find any line items with dollar amounts in this PDF. "
            "Try a cleaner export, or upload a CSV/Excel version instead."
        )

    for col in df.columns[1:]:
        df[col] = df[col].apply(lambda v: _clean_amount(str(v)) if v is not None else None)

    return df
