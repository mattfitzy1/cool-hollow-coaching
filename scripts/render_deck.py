#!/usr/bin/env python3
"""Render an HTML scope/pitch deck into a 16:9 landscape PDF.

The PERMANENT deck-to-PDF tool. Replaces all previous attempts.

How it works
------------
Each `<section class="slide ...">` in the HTML is rendered by Playwright
(headless Chromium with full JS, font, and image loading) at 1920x1080
into a high-resolution PNG. The 16 PNGs are then assembled into a single
lossless PDF via img2pdf. Result is pixel-identical to what the HTML
displays in a browser at 1920x1080. No print CSS reflow, no Chrome CLI
timing tricks.

Usage
-----
    .venv-command/bin/python scripts/render_deck.py <input.html>
    .venv-command/bin/python scripts/render_deck.py <input.html> <output.pdf>

If output is omitted, the PDF is saved next to the HTML with .pdf extension.
Sync to Desktop and Drive happens automatically when output sits inside
this workspace.

Reusable for any HTML deck that follows the convention of one
`<section class="slide ...">` per slide.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import img2pdf
from PIL import Image
from playwright.sync_api import sync_playwright

WIDTH, HEIGHT = 1920, 1080
# Workspace defaults to the directory this script is run from. Set AIOS_WORKSPACE
# in your environment to override (e.g. when running from outside the workspace).
WORKSPACE = Path(os.environ.get("AIOS_WORKSPACE", Path.cwd()))
# Optional sync targets. Leave empty to write only into outputs/decks/.
# Examples:
#   DESKTOP = Path.home() / "Desktop"
#   DRIVE_CLIENTS = Path.home() / "Library/CloudStorage/GoogleDrive-you@example.com/My Drive/Clients"
DESKTOP = None
DRIVE_CLIENTS = None


def count_slides(html: str) -> int:
    return len(re.findall(r'<section class="slide[^"]*"', html))


def build_isolated_html(html_src: str, slide_index: int) -> str:
    """Return a copy of the HTML where only the Nth slide section is visible
    and where scroll-snap is disabled. The slide is forced to exactly
    1920x1080 so capture is consistent."""
    override = f"""
<style>
  html, body {{
    scroll-snap-type: none !important;
    width: {WIDTH}px !important;
    height: {HEIGHT}px !important;
    max-width: {WIDTH}px !important;
    max-height: {HEIGHT}px !important;
    overflow: hidden !important;
    margin: 0 !important; padding: 0 !important;
    background: var(--off-white, #FAF8F3) !important;
  }}
  .slide {{ display: none !important; }}
  .slide:nth-of-type({slide_index}) {{
    display: flex !important;
    width: {WIDTH}px !important; height: {HEIGHT}px !important;
    min-height: {HEIGHT}px !important; max-height: {HEIGHT}px !important;
    scroll-snap-align: none !important;
  }}
</style>
</head>"""
    return html_src.replace("</head>", override, 1)


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    html_src = html_path.read_text()
    n_slides = count_slides(html_src)
    if n_slides == 0:
        sys.exit(f"No <section class=\"slide\"...> elements found in {html_path}")
    print(f"Rendering {n_slides} slides from {html_path.name}")

    with tempfile.TemporaryDirectory() as tmpdir, sync_playwright() as pw:
        tmp = Path(tmpdir)
        browser = pw.chromium.launch()
        context = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=1,
        )

        png_paths: list[Path] = []
        for i in range(1, n_slides + 1):
            slide_html = build_isolated_html(html_src, i)
            slide_html_path = tmp / f"slide_{i:02d}.html"
            slide_html_path.write_text(slide_html)

            page = context.new_page()
            page.goto(slide_html_path.as_uri(), wait_until="networkidle")
            # Wait for web fonts to actually load before screenshotting
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(200)  # final settle for any post-font reflow

            png_path = tmp / f"slide_{i:02d}.png"
            page.screenshot(
                path=str(png_path),
                clip={"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT},
                omit_background=False,
            )
            page.close()

            # Defensive: enforce target size
            with Image.open(png_path) as im:
                if im.size != (WIDTH, HEIGHT):
                    im.convert("RGB").resize((WIDTH, HEIGHT), Image.LANCZOS).save(png_path)
            png_paths.append(png_path)
            print(f"  slide {i:>2}/{n_slides}  ({png_path.stat().st_size // 1024} KB)")

        browser.close()

        # 1920x1080 px at 96 dpi = 20 x 11.25 in landscape
        layout = img2pdf.get_layout_fun(
            pagesize=(img2pdf.in_to_pt(20), img2pdf.in_to_pt(11.25)),
            fit=img2pdf.FitMode.into,
        )
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert([str(p) for p in png_paths], layout_fun=layout))

        size_mb = pdf_path.stat().st_size / 1024 / 1024
        print(f"\n  PDF: {pdf_path}  ({size_mb:.2f} MB, {n_slides} pages, "
              f"20.00 x 11.25 in)")


def sync_outputs(pdf_path: Path) -> list[Path]:
    """Copy the PDF to optional sync targets (Desktop, Drive client folders).
    Both targets are off by default — set DESKTOP and/or DRIVE_CLIENTS at the
    top of this file to enable. Drive routing is based on filename heuristics
    (looks for a client name match)."""
    synced = [pdf_path]
    if DESKTOP is not None:
        desktop_path = DESKTOP / pdf_path.name
        shutil.copy2(pdf_path, desktop_path)
        synced.append(desktop_path)

    if DRIVE_CLIENTS is not None and DRIVE_CLIENTS.exists():
        name_lower = pdf_path.name.lower()
        for client_dir in DRIVE_CLIENTS.iterdir():
            if client_dir.is_dir() and client_dir.name.lower() in name_lower:
                drive_target = client_dir / pdf_path.name
                shutil.copy2(pdf_path, drive_target)
                synced.append(drive_target)
                break

    return synced


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render an HTML deck to a 16:9 landscape PDF (1920x1080 per slide).",
    )
    parser.add_argument("html", type=Path, help="Path to the source HTML deck")
    parser.add_argument(
        "pdf", type=Path, nargs="?",
        help="Output PDF path (defaults to same name with .pdf extension)",
    )
    parser.add_argument(
        "--no-sync", action="store_true",
        help="Skip Desktop/Drive sync; only write to the PDF path.",
    )
    args = parser.parse_args()

    if not args.html.is_file():
        sys.exit(f"Not a file: {args.html}")

    pdf_path = args.pdf or args.html.with_suffix(".pdf")
    pdf_path = pdf_path.expanduser().resolve()

    render_pdf(args.html.expanduser().resolve(), pdf_path)

    if not args.no_sync:
        synced = sync_outputs(pdf_path)
        print("\n  Synced to:")
        for p in synced:
            print(f"    {p}")


if __name__ == "__main__":
    main()
