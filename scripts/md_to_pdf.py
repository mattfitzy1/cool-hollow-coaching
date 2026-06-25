#!/usr/bin/env python3
"""Convert markdown files to clean, branded PDFs via Chrome headless.

Usage: python md_to_pdf.py file1.md [file2.md ...]
Writes a .pdf next to each .md (same name).
"""
import sys
import os
import subprocess
import tempfile
import markdown

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 20mm 18mm; }
* { box-sizing: border-box; }
body {
  font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
  color: #1A1A1A; font-size: 11pt; line-height: 1.55; max-width: 100%;
}
h1 { font-size: 22pt; color: #1A1A1A; border-bottom: 3px solid #C8A227;
     padding-bottom: 8px; margin: 0 0 18px; }
h2 { font-size: 16pt; color: #1A1A1A; border-bottom: 1px solid #E8C766;
     padding-bottom: 4px; margin: 26px 0 10px; }
h3 { font-size: 13pt; color: #8a6f1a; margin: 18px 0 6px; }
h4 { font-size: 11.5pt; color: #1A1A1A; margin: 14px 0 4px; }
p, li { font-size: 11pt; }
strong { color: #1A1A1A; }
a { color: #8a6f1a; text-decoration: none; word-break: break-all; }
code { background: #f4f1e8; padding: 1px 5px; border-radius: 3px;
       font-family: "SF Mono", Menlo, monospace; font-size: 9.5pt; }
pre { background: #f4f1e8; padding: 12px; border-radius: 6px; overflow-x: auto;
      border-left: 3px solid #C8A227; }
pre code { background: none; padding: 0; }
blockquote { border-left: 3px solid #C8A227; margin: 12px 0; padding: 4px 16px;
             color: #444; background: #faf8f1; }
table { border-collapse: collapse; width: 100%; margin: 14px 0; font-size: 9.5pt; }
th { background: #1A1A1A; color: #fff; text-align: left; padding: 7px 9px; }
td { border: 1px solid #ddd; padding: 6px 9px; vertical-align: top; }
tr:nth-child(even) td { background: #faf8f1; }
hr { border: none; border-top: 1px solid #ddd; margin: 22px 0; }
"""

def convert(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    html_body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "toc", "sane_lists", "nl2br"],
    )
    html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html_body}</body></html>"
    pdf_path = os.path.splitext(md_path)[0] + ".pdf"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(html)
        tmp_html = tmp.name
    try:
        subprocess.run([
            CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}", f"file://{tmp_html}",
        ], check=True, capture_output=True, timeout=120)
        print(f"OK  {os.path.basename(pdf_path)}")
    finally:
        os.unlink(tmp_html)
    return pdf_path

if __name__ == "__main__":
    for p in sys.argv[1:]:
        convert(p)
