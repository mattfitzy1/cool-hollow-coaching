#!/usr/bin/env python3
"""
Sign a PDF document by overlaying the user's signature image.

Configuration is read from environment variables:
  SIGNER_NAME       — name printed below the signature (required)
  SIGNATURE_PATH    — path to a transparent PNG of the signature
                      (default: reference/signature.png in the workspace root)

Usage: python3 sign_pdf.py <input.pdf> [--page N] [--position bottom-left|bottom-right|custom] [--x X] [--y Y]
"""

import sys
import os
import fitz  # PyMuPDF
from datetime import datetime

DEFAULT_SIGNATURE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "reference",
    "signature.png",
)
SIGNATURE_PATH = os.environ.get("SIGNATURE_PATH", DEFAULT_SIGNATURE_PATH)
SIGNER_NAME = os.environ.get("SIGNER_NAME", "")

def find_signature_area(page):
    """Try to find a signature line or 'Sign here' text on the page."""
    text = page.get_text()
    signature_markers = ["signature", "sign here", "signed by", "authorized signature", "signatory"]

    for marker in signature_markers:
        areas = page.search_for(marker, quads=False)
        if areas:
            # Return the area just to the right of or below the marker
            rect = areas[0]
            return fitz.Rect(rect.x0, rect.y0 - 60, rect.x0 + 200, rect.y0)

    return None

def sign_pdf(input_path, output_path=None, page_num=None, x=None, y=None, position="bottom-left"):
    """
    Sign a PDF by overlaying the signature image.

    Args:
        input_path: Path to the PDF to sign
        output_path: Path for signed PDF (default: input_signed.pdf)
        page_num: Page number to sign (default: last page)
        x, y: Custom position coordinates (bottom-left origin)
        position: Preset position if x/y not given
    """
    if not SIGNER_NAME:
        print("ERROR: SIGNER_NAME environment variable not set.")
        print('  e.g. export SIGNER_NAME="Your Name"')
        sys.exit(1)

    if not os.path.exists(SIGNATURE_PATH):
        print(f"ERROR: Signature image not found at {SIGNATURE_PATH}")
        print("  Set SIGNATURE_PATH or place a transparent PNG at reference/signature.png.")
        sys.exit(1)

    if not os.path.exists(input_path):
        print(f"ERROR: PDF not found at {input_path}")
        sys.exit(1)

    # Generate output path
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_signed{ext}"

    doc = fitz.open(input_path)

    # Default to last page
    if page_num is None:
        page_num = len(doc) - 1
    else:
        page_num = page_num - 1  # Convert to 0-indexed

    page = doc[page_num]
    page_rect = page.rect

    # Signature size (width 150pt, maintain aspect ratio)
    sig_width = 150
    sig_img = fitz.Pixmap(SIGNATURE_PATH)
    aspect = sig_img.height / sig_img.width
    sig_height = sig_width * aspect

    # Determine position
    if x is not None and y is not None:
        sig_rect = fitz.Rect(x, y - sig_height, x + sig_width, y)
    else:
        # Try to auto-detect signature area
        auto_area = find_signature_area(page)
        if auto_area:
            sig_rect = auto_area
            # Resize to fit the detected area
            sig_rect = fitz.Rect(
                auto_area.x0,
                auto_area.y1 - sig_height,
                auto_area.x0 + sig_width,
                auto_area.y1
            )
        elif position == "bottom-left":
            margin_x = 72  # 1 inch
            margin_y = 100
            sig_rect = fitz.Rect(
                margin_x,
                page_rect.height - margin_y - sig_height,
                margin_x + sig_width,
                page_rect.height - margin_y
            )
        elif position == "bottom-right":
            margin_x = 72
            margin_y = 100
            sig_rect = fitz.Rect(
                page_rect.width - margin_x - sig_width,
                page_rect.height - margin_y - sig_height,
                page_rect.width - margin_x,
                page_rect.height - margin_y
            )
        elif position == "bottom-center":
            margin_y = 100
            center_x = (page_rect.width - sig_width) / 2
            sig_rect = fitz.Rect(
                center_x,
                page_rect.height - margin_y - sig_height,
                center_x + sig_width,
                page_rect.height - margin_y
            )

    # Insert signature image
    page.insert_image(sig_rect, filename=SIGNATURE_PATH)

    # Add date below signature
    date_str = datetime.now().strftime("%d %B %Y")
    date_point = fitz.Point(sig_rect.x0, sig_rect.y1 + 14)
    page.insert_text(date_point, date_str, fontsize=9, color=(0, 0, 0))

    # Add name below date
    name_point = fitz.Point(sig_rect.x0, sig_rect.y1 + 26)
    page.insert_text(name_point, SIGNER_NAME, fontsize=9, color=(0, 0, 0))

    doc.save(output_path)
    doc.close()

    print(f"Signed: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 sign_pdf.py <input.pdf> [--page N] [--position bottom-left|bottom-right|bottom-center] [--x X] [--y Y]")
        sys.exit(1)

    input_path = sys.argv[1]
    page_num = None
    x = None
    y = None
    position = "bottom-left"

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--page" and i + 1 < len(sys.argv):
            page_num = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--position" and i + 1 < len(sys.argv):
            position = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--x" and i + 1 < len(sys.argv):
            x = float(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--y" and i + 1 < len(sys.argv):
            y = float(sys.argv[i + 1])
            i += 2
        else:
            i += 1

    sign_pdf(input_path, page_num=page_num, x=x, y=y, position=position)
