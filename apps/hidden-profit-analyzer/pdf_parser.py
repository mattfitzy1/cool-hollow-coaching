"""
PDF P&L parsing for the hidden-profit analyzer.

Real QuickBooks/Xero P&L PDFs are read line by line as text: a label followed by
one or more dollar amounts at the end of the line. This is deliberately preferred
over table extraction, because table extraction tends to split an account code
("40200 Sales of Product Income") into a separate numeric column and then count
the code as money. Reading the text keeps the account code glued to the label,
where it belongs, and only the trailing formatted amounts are treated as figures.

Output: a DataFrame with a line_item column plus one or more amount columns, in the
original top-to-bottom order (section headers and totals included, so the analysis
layer can read the P&L by its sections). Same shape a CSV/Excel upload produces.
"""

from __future__ import annotations

import re

import pandas as pd
import pdfplumber

# A money amount: has a thousands comma group OR a .dd decimal. A bare integer like
# an account code (40200, 51100) has neither, so it is NOT matched and stays in the label.
AMOUNT_RE = re.compile(
    r"\(?-?\$?\s?(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d{2})\)?"
)


def _clean_amount(text: str) -> float:
    text = text.strip()
    negative = text.startswith("(") and text.endswith(")")
    cleaned = re.sub(r"[()$,\s]", "", text)
    if not cleaned or cleaned in ("-",):
        return 0.0
    try:
        value = float(cleaned)
    except ValueError:
        return 0.0
    return -value if negative else value


def _extract_rows(pdf) -> list:
    """Each row: (label, [amount_str, ...]) in document order."""
    rows = []
    for page in pdf.pages:
        text = page.extract_text() or ""
        for line in text.split("\n"):
            if not line.strip():
                continue
            amounts = AMOUNT_RE.findall(line)
            # Strip the trailing amounts off the end to recover the label, leaving any
            # leading account code in place.
            label = line
            for amt in reversed(amounts):
                idx = label.rfind(amt)
                if idx != -1:
                    label = label[:idx]
            label = label.strip(" .:\t")
            if not label and not amounts:
                continue
            rows.append((label, amounts))
    return rows


def parse_pdf(file) -> pd.DataFrame:
    """Extract a P&L-shaped DataFrame (line_item + amount columns) from a PDF."""
    with pdfplumber.open(file) as pdf:
        rows = _extract_rows(pdf)

    rows = [r for r in rows if r[0] or r[1]]
    if not rows:
        raise ValueError(
            "Could not find any line items with dollar amounts in this PDF. "
            "Try a cleaner export, or upload a CSV/Excel version instead."
        )

    max_amounts = max((len(amts) for _, amts in rows), default=0)
    if max_amounts == 0:
        raise ValueError(
            "Found text but no dollar amounts in this PDF. Try a CSV/Excel export."
        )

    if max_amounts == 1:
        cols = ["line_item", "amount"]
    else:
        cols = ["line_item"] + [f"month_{i}" for i in range(max_amounts)]

    data = []
    for label, amts in rows:
        values = [_clean_amount(a) for a in amts]
        values += [None] * (max_amounts - len(values))
        data.append([label] + values)

    return pd.DataFrame(data, columns=cols)
