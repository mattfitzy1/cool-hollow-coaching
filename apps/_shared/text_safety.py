"""
Shared text-safety helpers for displaying generated findings in Streamlit.

Streamlit's markdown renderer treats a pair of literal "$" characters as
inline LaTeX math (this is on by default, not opt-in). Every dollar-amount
finding these tools generate contains a literal "$", and a bullet or
paragraph with two or more dollar amounts in it (extremely common: "X grew
from $46,731 to $44,573") gets its text between them silently swallowed
into a broken math render: hyphens become minus signs, spaces collapse,
and the actual numbers vanish. escape_dollars() neutralizes this everywhere
generated text reaches st.write/st.markdown, without touching the PDF
export (reportlab has no such behavior, so PDF text stays unescaped).

clean_line_item() strips the raw account-number prefixes real accounting
exports (QuickBooks in particular) put in front of every line item, e.g.
"66026 66026-Payroll Expense-Executive Salaries-NH" becomes "Payroll
Expense - Executive Salaries - NH", the label an owner actually reads.
"""

import re


def escape_dollars(text: str) -> str:
    """Escapes literal $ so Streamlit never mistakes a dollar figure for the
    start of a LaTeX math block. Call this on any generated string right
    before it reaches st.write / st.markdown / st.caption / st.error, etc."""
    if text is None:
        return text
    return str(text).replace("$", "\\$")


_LEADING_CODE = re.compile(r"^(?:\d[\d\-]*\s+)+")
_INLINE_CODE = re.compile(r"^\d{3,}\s*-?\s*")


def clean_line_item(label: str) -> str:
    """Strips a leading QuickBooks-style account-number prefix from a line
    item label, then normalizes internal hyphens to ' - ' with even
    spacing so 'Payroll Expense-Executive Salaries-NH' reads cleanly.
    Leaves already-clean labels (no numeric prefix) untouched."""
    text = str(label).strip()
    text = _LEADING_CODE.sub("", text)
    text = _INLINE_CODE.sub("", text)
    text = re.sub(r"\s*-\s*", " - ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or str(label).strip()
