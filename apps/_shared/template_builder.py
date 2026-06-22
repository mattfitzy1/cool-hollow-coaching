"""
Shared styling helper for Business Without You client-input Excel templates.

Every milestone model has a matching branded template: a title block naming
Cool Hollow Coaching and the exact milestone it belongs to, an Instructions
tab explaining every column in plain English, and one or more data tabs
with a styled header row, sized columns, and dropdown or range validation
on every column where a wrong value would break the model upstream.

Column headers use spaces ("Hours Per Week"), not underscores, because the
analysis.py loaders in each app normalize headers to lowercase-with-
underscores before checking them. That normalization is what lets a
client fill in a friendly header and still have it parse correctly.
"""

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

INK = "0E4643"
ACCENT = "589BA8"
ACCENT2 = "B4D351"
PAPER = "FAF8F3"
COMPANY = "Cool Hollow Coaching"
PROGRAM = "Business Without You"

TITLE_FONT = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
SUBTITLE_FONT = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
BODY_FONT = Font(name="Calibri", size=11, color=INK)
NOTE_FONT = Font(name="Calibri", size=10, italic=True, color="5A5A5A")
EXAMPLE_FONT = Font(name="Calibri", size=11, italic=True, color="6B6B6B")

TITLE_FILL = PatternFill("solid", fgColor=INK)
HEADER_FILL = PatternFill("solid", fgColor=ACCENT)
ACCENT_FILL = PatternFill("solid", fgColor=ACCENT2)
EXAMPLE_FILL = PatternFill("solid", fgColor="EFEFEF")

THIN_BORDER = Border(
    left=Side(style="thin", color="CCCCCC"),
    right=Side(style="thin", color="CCCCCC"),
    top=Side(style="thin", color="CCCCCC"),
    bottom=Side(style="thin", color="CCCCCC"),
)


def add_title_block(ws, milestone_label: str, tool_name: str, span: int):
    """Two merged title rows: company/program, then milestone and tool name."""
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=span)
    title_cell = ws.cell(row=1, column=1, value=f"{COMPANY} · {PROGRAM}")
    title_cell.font = TITLE_FONT
    title_cell.fill = TITLE_FILL
    title_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 28

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=span)
    subtitle_cell = ws.cell(row=2, column=1, value=f"{milestone_label}: {tool_name}")
    subtitle_cell.font = SUBTITLE_FONT
    subtitle_cell.fill = TITLE_FILL
    subtitle_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[2].height = 22

    ws.row_dimensions[3].height = 6


def add_header_row(ws, headers: list, row: int = 4, start_col: int = 1):
    for i, header in enumerate(headers):
        cell = ws.cell(row=row, column=start_col + i, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
    ws.row_dimensions[row].height = 32


def add_example_rows(ws, rows: list, start_row: int = 5, start_col: int = 1):
    """Write greyed-out, italic example rows so a client sees the right format
    instead of having to guess what goes in each column. A bold "EXAMPLE,
    replace with your own" label marks the last example row so it's obvious
    where the client's real data should start."""
    last_row = start_row
    for r_offset, row in enumerate(rows):
        last_row = start_row + r_offset
        for c_offset, val in enumerate(row):
            cell = ws.cell(row=last_row, column=start_col + c_offset, value=val)
            cell.font = EXAMPLE_FONT
            cell.fill = EXAMPLE_FILL
            cell.border = THIN_BORDER
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    return last_row


def style_data_rows(ws, start_row: int, end_row: int, start_col: int, end_col: int):
    for r in range(start_row, end_row + 1):
        for c in range(start_col, end_col + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = BODY_FONT
            cell.border = THIN_BORDER
            cell.fill = PatternFill("solid", fgColor=PAPER)


def add_example_label_row(ws, row: int, span: int, start_col: int = 1):
    """A short accent-colored banner row marking where the client's own data
    should start, right below the greyed-out example rows above it."""
    ws.merge_cells(start_row=row, start_column=start_col, end_row=row, end_column=start_col + span - 1)
    cell = ws.cell(row=row, column=start_col, value="Your data starts here, replace or delete the example rows above")
    cell.font = Font(name="Calibri", size=10, bold=True, italic=True, color=INK)
    cell.fill = ACCENT_FILL
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 18


def set_column_widths(ws, widths: list, start_col: int = 1):
    for i, width in enumerate(widths):
        ws.column_dimensions[get_column_letter(start_col + i)].width = width


def add_list_validation(ws, options: list, cell_range: str):
    formula = '"' + ",".join(options) + '"'
    dv = DataValidation(type="list", formula1=formula, allow_blank=True, showDropDown=False)
    dv.error = f"Choose one of: {', '.join(options)}"
    dv.errorTitle = "Invalid entry"
    ws.add_data_validation(dv)
    dv.add(cell_range)
    return dv


def add_range_validation(ws, low: int, high: int, cell_range: str):
    dv = DataValidation(type="whole", operator="between", formula1=low, formula2=high, allow_blank=True)
    dv.error = f"Enter a whole number from {low} to {high}."
    dv.errorTitle = "Out of range"
    ws.add_data_validation(dv)
    dv.add(cell_range)
    return dv


def build_instructions_sheet(wb: Workbook, milestone_label: str, tool_name: str, intro: str, column_notes: list):
    """column_notes: list of (column_name, explanation) tuples."""
    ws = wb.create_sheet("Instructions", 0)
    add_title_block(ws, milestone_label, tool_name, span=2)

    ws.cell(row=5, column=1, value="How to use this template").font = Font(bold=True, size=12, color=INK)
    intro_cell = ws.cell(row=6, column=1, value=intro)
    intro_cell.font = BODY_FONT
    intro_cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=6, start_column=1, end_row=6, end_column=2)
    ws.row_dimensions[6].height = 60

    ws.cell(row=8, column=1, value="Column").font = HEADER_FONT
    ws.cell(row=8, column=1).fill = HEADER_FILL
    ws.cell(row=8, column=2, value="What to put here").font = HEADER_FONT
    ws.cell(row=8, column=2).fill = HEADER_FILL

    row = 9
    for col_name, note in column_notes:
        ws.cell(row=row, column=1, value=col_name).font = Font(bold=True, color=INK)
        note_cell = ws.cell(row=row, column=2, value=note)
        note_cell.alignment = Alignment(wrap_text=True, vertical="top")
        note_cell.font = BODY_FONT
        ws.row_dimensions[row].height = 32
        row += 1

    ws.cell(row=row + 1, column=1, value="Fill in the data tab, save the file, then upload it straight into the tool.").font = NOTE_FONT

    set_column_widths(ws, [32, 70])
    return ws


def new_workbook() -> Workbook:
    wb = Workbook()
    wb.remove(wb.active)
    return wb
