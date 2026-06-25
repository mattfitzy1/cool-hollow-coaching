#!/usr/bin/env python3
"""Render a local HTML file to a clean Letter-size PDF using Playwright.
Used to turn AIOS strategy/roadmap docs into something easy to email."""
import sys, pathlib
from playwright.sync_api import sync_playwright

src = pathlib.Path(sys.argv[1]).resolve()
dst = src.with_suffix(".pdf")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(src.as_uri())
    page.pdf(
        path=str(dst),
        format="Letter",
        print_background=True,
        margin={"top": "0.4in", "bottom": "0.4in", "left": "0.4in", "right": "0.4in"},
    )
    browser.close()

print(dst)
