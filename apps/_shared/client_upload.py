"""
Shared reader for client-uploaded files across the milestone tools.

The branded Excel templates have an Instructions tab, an Examples tab, and
one or more data tabs with a title block above the header row. A naive
pd.read_excel() reads the first sheet with row 1 as the header, which is
wrong on every count. This reader:

- reads CSVs directly,
- for Excel, skips the Instructions/Examples tabs,
- finds the sheet and header row that actually contain the columns the
  tool needs (scanning the first rows, so the title block is harmless),
- drops fully empty rows so blank styled template rows never parse as data.

Because each upload slot searches by its own required columns, a client
can upload the same filled template workbook into every slot of a
multi-file tool and each slot finds its own tab.
"""

import pandas as pd

_SKIP_SHEETS = {"instructions", "examples", "example", "starter ideas"}
_HEADER_SCAN_ROWS = 12


def _norm(value) -> str:
    return str(value).strip().lower().replace(" ", "_")


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="all")
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")] if hasattr(df.columns, "str") else df
    return df.reset_index(drop=True)


def _extract_table(raw: pd.DataFrame, required: set):
    """Scan the first rows of a header-less sheet for the row that contains
    every required column, then return the table below it."""
    limit = min(_HEADER_SCAN_ROWS, len(raw))
    for i in range(limit):
        row = raw.iloc[i]
        normalized = {_norm(v) for v in row if pd.notna(v)}
        if required <= normalized:
            df = raw.iloc[i + 1:].copy()
            df.columns = [str(v) if pd.notna(v) else "" for v in raw.iloc[i]]
            df = df.loc[:, [c for c in df.columns if c]]
            df = df.dropna(how="all")
            return df.reset_index(drop=True)
    return None


def read_upload(uploaded_file, required_columns) -> pd.DataFrame:
    """Read a client upload (CSV or Excel) and return the data table.

    required_columns: the normalized (lowercase_underscore) column names this
    tool needs. Used to locate the right sheet and header row in Excel files.
    Raises ValueError with a plain-English message when nothing matches.
    """
    required = {_norm(c) for c in required_columns}
    name = getattr(uploaded_file, "name", str(uploaded_file)).lower()

    if name.endswith(".csv"):
        return _clean(pd.read_csv(uploaded_file))

    sheets = pd.read_excel(uploaded_file, sheet_name=None, header=None)

    data_sheets = {
        sheet: raw for sheet, raw in sheets.items()
        if sheet.strip().lower() not in _SKIP_SHEETS
    }

    for raw in data_sheets.values():
        table = _extract_table(raw, required)
        if table is not None:
            return table

    # Nothing matched. Fall back to a naive read of the first data sheet so
    # the tool's own loader can raise its usual, specific missing-column
    # message (this covers a client's own spreadsheet with renamed headers).
    if data_sheets:
        first = next(iter(data_sheets.values()))
        df = first.copy()
        if len(df) > 0:
            df.columns = [str(v) if pd.notna(v) else "" for v in df.iloc[0]]
            df = df.iloc[1:]
        return _clean(df)

    raise ValueError(
        "That workbook only contains Instructions/Examples tabs. "
        "Fill in the data tab and upload the file again."
    )
