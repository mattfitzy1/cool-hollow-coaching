#!/usr/bin/env python3
"""Render branded social posters/carousels to PNG (1080x1350, 4:5).

Builds branded posters to a clean editorial design system (neutral placeholder theme,
deep ink anchor, soft-blue and beige supporting tones, a serif display +
sans body. Architectural restraint, generous whitespace. Each "card" renders
to one PNG at 2x for crispness. Adjust the palette, fonts and BRAND wordmark
below to match your brand (see context/brand.md).

Posts are defined in the POSTS array below, which ships EMPTY. Add your own
cards there (a small helper set is provided) and run this script to render them.
Renders via Playwright (headless Chromium, full font loading from Google Fonts
with Georgia/Arial fallback).

Usage:
    python3 scripts/social/render_posters.py [out_dir]
Default out_dir: outputs/social/rendered/
"""
from __future__ import annotations
import sys, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

W, H = 1080, 1350
ROOT = Path(__file__).resolve().parents[2]

# Brand wordmark shown on each card. Set this to your brand name.
BRAND = "Your Brand"

# Palette (clean editorial default; adjust to match context/brand.md)
CREAM = "#F7F7F5"      # placeholder base; reskin from context/brand.md
CREAM_LIGHT = "#FFFFFF"
CARD = "#ECEEF1"       # beige card
CARD_DEEP = "#DCE0E5"
INK = "#1F2933"        # dark ink anchor (typography + key UI)
BROWN = "#334155"      # slate accent
BLUE = "#3B6EA5"       # supporting blue
BLUE_DEEP = "#2C5680"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Manrope:wght@200;300;400;500&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
.poster{width:1080px;height:1350px;position:relative;overflow:hidden;
  font-family:'Manrope',Arial,sans-serif;font-weight:300;-webkit-font-smoothing:antialiased}
.bg-cream{background:#F7F7F5;color:#1F2933}
.bg-card{background:#ECEEF1;color:#1F2933}
.bg-ink{background:#1F2933;color:#FFFFFF}
.pad{position:absolute;inset:88px}
.eyebrow{font-size:22px;font-weight:500;letter-spacing:.26em;text-transform:uppercase}
.display{font-family:'Cormorant Garamond',Georgia,serif;font-weight:500;font-size:108px;line-height:1.02;letter-spacing:-0.005em}
.display-sm{font-family:'Cormorant Garamond',Georgia,serif;font-weight:500;font-size:84px;line-height:1.06}
.display-i{font-family:'Cormorant Garamond',Georgia,serif;font-weight:500;font-style:italic;font-size:84px;line-height:1.06}
.h1{font-family:'Cormorant Garamond',Georgia,serif;font-weight:500;font-size:66px;line-height:1.08}
.body{font-size:37px;line-height:1.5;font-weight:300}
.caption{font-size:26px;line-height:1.5;font-weight:300}
.rule{width:108px;height:2px;background:#334155;border:0}
.col{display:flex;flex-direction:column;height:100%}
.spacer{flex:1}
.ink{color:#1F2933}.brown{color:#334155}.blue{color:#3B6EA5}.cream{color:#FFFFFF}.muted{color:#2C5680}
.swipe{position:absolute;right:88px;bottom:88px;font-size:24px;color:#2C5680;letter-spacing:.04em}
.slidenum{position:absolute;right:88px;bottom:88px;font-size:22px;color:#2C5680;letter-spacing:.05em}
.wordmark{position:absolute;left:88px;bottom:88px;font-family:'Cormorant Garamond',Georgia,serif;
  font-size:30px;font-weight:500;letter-spacing:.04em;color:#334155}
.quote{font-family:'Cormorant Garamond',Georgia,serif;font-weight:500;font-size:180px;line-height:.55;color:#3B6EA5;height:84px;display:block}
"""


# ---- Card helpers --------------------------------------------------------
# Each helper returns (bg-class, inner-HTML). Build your cards from these in
# the POSTS array below. The wordmark is plain text (the BRAND constant);
# there is no logo mark dependency, so these render anywhere.

def hook_poster(eyebrow, line, sub=None):
    """A bold opening still: small eyebrow, a large serif line, optional sub."""
    subhtml = f'<div class="body muted" style="margin-top:28px;max-width:820px">{sub}</div>' if sub else ""
    return ("bg-cream", f"""
      <div class="pad col">
        <div class="eyebrow brown">{eyebrow}</div>
        <div class="spacer"></div>
        <div class="display ink">{line}</div>
        <hr class="rule" style="margin-top:40px">
        {subhtml}
        <div class="spacer"></div>
      </div>
      <div class="wordmark">{BRAND}</div>""")


def carousel_cover(eyebrow, line, sub):
    """First slide of a carousel: sets up the topic, invites a swipe."""
    return ("bg-cream", f"""
      <div class="pad col">
        <div class="eyebrow brown">{eyebrow}</div>
        <div class="spacer"></div>
        <div class="display-sm ink">{line}</div>
        <hr class="rule" style="margin-top:40px">
        <div class="body muted" style="margin-top:28px;max-width:840px">{sub}</div>
        <div class="spacer"></div>
      </div>
      <div class="swipe">Swipe &rarr;</div>""")


def carousel_body(kicker, title, body, num):
    """A middle slide on a beige card: one idea, calmly stated."""
    return ("bg-card", f"""
      <div class="pad col" style="justify-content:center">
        <div class="eyebrow brown">{kicker}</div>
        <div class="h1 ink" style="margin-top:16px">{title}</div>
        <div class="body" style="margin-top:28px;max-width:830px">{body}</div>
      </div>
      <div class="slidenum">{num}</div>""")


def carousel_cta(line, sub, prompt):
    """Closing slide: the invitation, on the dark ink field."""
    return ("bg-ink", f"""
      <div class="pad col">
        <div class="spacer"></div>
        <div class="display-sm cream">{line}</div>
        <div class="body" style="margin-top:32px;max-width:840px;color:#DCE0E5">{sub}</div>
        <hr class="rule" style="margin-top:36px;background:#3B6EA5">
        <div class="caption" style="margin-top:28px;color:#FFFFFF">{prompt}</div>
        <div class="spacer"></div>
      </div>
      <div class="wordmark" style="color:#DCE0E5">{BRAND}</div>""")


def quote_poster(line, attrib):
    """A method note or journal line, set as a quiet quote."""
    return ("bg-cream", f"""
      <div class="pad col">
        <div class="spacer"></div>
        <span class="quote">&ldquo;</span>
        <div class="display ink" style="margin-top:30px;max-width:880px">{line}</div>
        <div class="spacer"></div>
        <div class="caption muted">{attrib}</div>
      </div>
      <div class="wordmark">{BRAND}</div>""")


# ---- POST DEFINITIONS ----------------------------------------------------
# Empty by design. Add entries as (name, (bg-class, inner-HTML)) tuples, e.g.
#
#   POSTS.append(("01-hook-clarity", hook_poster(
#       "The method",
#       "Your business<br>should run<br>without you.",
#       "A short note on why owner-dependence is the real bottleneck.")))
#
# Then run this script to render them into the output folder.
POSTS: list[tuple[str, tuple[str, str]]] = []


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "outputs/social/rendered"
    out.mkdir(parents=True, exist_ok=True)

    if not POSTS:
        print("No posts defined yet. Add cards to the POSTS array in this file,")
        print("then run it again. (Helpers: hook_poster, carousel_cover,")
        print("carousel_body, carousel_cta, quote_poster.)")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=2)
        page = ctx.new_page()
        for name, (bgclass, inner) in POSTS:
            html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
              <body><div class="poster {bgclass}">{inner}</div></body></html>"""
            tmp = Path(tempfile.mkdtemp()) / "p.html"
            tmp.write_text(html)
            page.goto(tmp.as_uri())
            page.wait_for_timeout(400)
            try:
                page.evaluate("document.fonts.ready")
            except Exception:
                pass
            page.wait_for_timeout(300)
            el = page.query_selector(".poster")
            el.screenshot(path=str(out / f"{name}.png"))
            print("rendered", name)
        browser.close()
    print("\nDONE ->", out)


if __name__ == "__main__":
    main()
