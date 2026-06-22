#!/usr/bin/env python3
"""
Brand-skinned creative template renderer (Creative Department, F3).

Reads a per-brand `brand.json` and renders campaign templates on top of
AI-generated scenes:
  - content_slide  (campaign carousel slide: tick + headline + product + spark)
  - quote_card     (headline-only card on brand background)
  - endcard        (payoff lockup with the real logo)

Everything brand-specific (palette, fonts, logo, graphic devices, canvas)
comes from brand.json so the same code skins any brand. Template #1 is a
generalised "Add a little ___" layout.

Usage as a library (preferred, via the /creative skill) or CLI:
  python scripts/creative_lib/render.py slide   --brand-dir outputs/creative/example-brand \
      --bg images/s1.png --l1 "Build a better" --l2 "business." \
      --product refs/product.png --out slides/01.jpg
  python scripts/creative_lib/render.py endcard --brand-dir outputs/creative/example-brand --out slides/end.jpg
  python scripts/creative_lib/render.py quote   --brand-dir outputs/creative/example-brand \
      --l1 "One method," --l2 "every owner." --out slides/quote.jpg
"""
import os, json, math, argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------- font resolution ----------
FONT_DIRS = [
    "/System/Library/Fonts", "/System/Library/Fonts/Supplemental",
    "/Library/Fonts", os.path.expanduser("~/Library/Fonts"),
]
DEFAULT_FONT = "/System/Library/Fonts/HelveticaNeue.ttc#1"  # Bold

def _resolve_font_file(spec):
    """spec like 'HelveticaNeue.ttc#1' or '/abs/path.ttf' or 'Arial Black.ttf'."""
    path, _, idx = spec.partition("#")
    idx = int(idx) if idx else 0
    if os.path.isabs(path) and os.path.exists(path):
        return path, idx
    for d in FONT_DIRS:
        cand = os.path.join(d, path)
        if os.path.exists(cand):
            return cand, idx
    p, i = DEFAULT_FONT.split("#")
    return p, int(i)

# ---------- brand config ----------
def hexrgba(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

class Brand:
    def __init__(self, brand_dir):
        self.dir = brand_dir
        with open(os.path.join(brand_dir, "brand.json")) as f:
            self.cfg = json.load(f)
        c = self.cfg.get("palette", {})
        self.accent = hexrgba(c.get("accent", "#F0C800"))
        self.accent2 = hexrgba(c.get("accent2", c.get("accent", "#4AA0D6")))
        self.ink    = hexrgba(c.get("ink", "#0E0E0C"))
        self.paper  = hexrgba(c.get("paper", "#F6F1E7"))
        fonts = self.cfg.get("fonts", {})
        self._head = fonts.get("headline", DEFAULT_FONT)
        self._black = fonts.get("display", fonts.get("headline", DEFAULT_FONT))
        canvas = self.cfg.get("canvas", [1080, 1350])
        self.W, self.H = canvas[0], canvas[1]
        dev = self.cfg.get("devices", {})
        self.has_spark = dev.get("spark", True)
        self.has_tick  = dev.get("tick", True)

    def p(self, *a): return os.path.join(self.dir, *a)
    def font(self, size, display=False):
        path, idx = _resolve_font_file(self._black if display else self._head)
        return ImageFont.truetype(path, size, index=idx)
    def logo_path(self):
        lg = self.cfg.get("logo")
        return self.p(lg) if lg else None

# ---------- canvas helpers ----------
def load_bg(b, path):
    im = Image.open(path).convert("RGBA")
    s = max(b.W / im.width, b.H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - b.W) // 2, (im.height - b.H) // 2
    return im.crop((x, y, x + b.W, y + b.H))

def top_vignette(b, base, strength=0.55):
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for yy in range(b.H):
        t = max(0.0, 1 - yy / (b.H * 0.5))
        d.line([(0, yy), (b.W, yy)], fill=(0, 0, 0, int(150 * (t ** 1.4) * strength)))
    return Image.alpha_composite(base, ov)

# ---------- graphic devices ----------
def _star_pts(cx, cy, ro, ri, n=6, rot=-math.pi/2):
    return [(cx + (ro if i % 2 == 0 else ri) * math.cos(rot + i * math.pi / n),
             cy + (ro if i % 2 == 0 else ri) * math.sin(rot + i * math.pi / n))
            for i in range(n * 2)]

def draw_spark(base, cx, cy, r, color):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).polygon(_star_pts(cx, cy, r, r * 0.40, 6), fill=color)
    base.alpha_composite(layer); return base

def draw_tick(base, cx, cy, r, color):
    w = max(6, r // 7)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.arc([cx - r, cy - r, cx + r, cy + r], 300, 270, fill=color, width=w)
    d.line([(cx - r*0.45, cy + r*0.05), (cx - r*0.10, cy + r*0.45), (cx + r*0.55, cy - r*0.40)],
           fill=color, width=w, joint="curve")
    base.alpha_composite(layer); return base

def place_product(b, base, ref_path, target_h=0.62, cx_frac=0.76, bottom_frac=0.97):
    im = Image.open(ref_path).convert("RGBA")
    th = int(b.H * target_h); s = th / im.height
    im = im.resize((round(im.width * s), th), Image.LANCZOS)
    bx = int(b.W * cx_frac) - im.width // 2
    by = int(b.H * bottom_frac) - im.height
    a = im.split()[3]
    sd = Image.new("L", im.size, 0); sd.paste(a, (0, 0))
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 255))
    shadow.putalpha(sd.point(lambda v: int(v * 0.55)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    base.alpha_composite(shadow, (bx + 18, by + 30))
    base.alpha_composite(im, (bx, by))
    return base, (bx, by, im.width, im.height)

def _fit_font(b, d, lines, x, size, display=False):
    max_w = b.W - x - 70
    while size > 50:
        f = b.font(size, display)
        if max(d.textbbox((0, 0), t, font=f)[2] for t in lines) <= max_w:
            return f, size
        size -= 4
    return b.font(size, display), size

def draw_headline(b, base, line1, line2, x=80, y=205, size=86):
    d = ImageDraw.Draw(base)
    f, size = _fit_font(b, d, [line1, line2], x, size)
    lh = int(size * 1.12)
    for txt, yy in ((line1, y), (line2, y + lh)):
        d.text((x + 3, yy + 3), txt, font=f, fill=(0, 0, 0, 170))
        d.text((x, yy), txt, font=f, fill=b.paper)

def _center(b, d, txt, f, cy, fill, shadow=True):
    bb = d.textbbox((0, 0), txt, font=f); w = bb[2] - bb[0]
    x = (b.W - w) // 2 - bb[0]
    if shadow: d.text((x + 3, cy + 3), txt, font=f, fill=(0, 0, 0, 160))
    d.text((x, cy), txt, font=f, fill=fill)

# ---------- templates ----------
def content_slide(brand_dir, bg, line1, line2, product, out,
                  accent="primary", product_h=0.62, product_cx=0.76):
    b = Brand(brand_dir)
    col = b.accent2 if accent == "secondary" else b.accent
    base = top_vignette(b, load_bg(b, b.p(bg) if not os.path.isabs(bg) else bg))
    if b.has_tick:
        draw_tick(base, 112, 118, 40, col)
    draw_headline(b, base, line1, line2)
    pr = b.p(product) if not os.path.isabs(product) else product
    base, (bx, by, bw, bh) = place_product(b, base, pr, product_h, product_cx)
    if b.has_spark:
        draw_spark(base, bx - 30, by + int(bh * 0.30), 78, col)
    o = b.p(out) if not os.path.isabs(out) else out
    os.makedirs(os.path.dirname(o), exist_ok=True)
    base.convert("RGB").save(o, quality=94); print("wrote", o); return o

def quote_card(brand_dir, line1, line2, out, accent="primary", bg=None):
    b = Brand(brand_dir)
    col = b.accent2 if accent == "secondary" else b.accent
    if bg:
        base = top_vignette(b, load_bg(b, b.p(bg) if not os.path.isabs(bg) else bg), 0.9)
    else:
        base = Image.new("RGBA", (b.W, b.H), b.ink)
    d = ImageDraw.Draw(base)
    f, size = _fit_font(b, d, [line1, line2], 90, 104, display=True)
    lh = int(size * 1.1); cy = b.H // 2 - lh
    _center(b, d, line1, f, cy, b.paper, shadow=bool(bg))
    _center(b, d, line2, f, cy + lh, col, shadow=bool(bg))
    if b.has_spark:
        draw_spark(base, b.W // 2, cy - 90, 60, col)
    o = b.p(out) if not os.path.isabs(out) else out
    os.makedirs(os.path.dirname(o), exist_ok=True)
    base.convert("RGB").save(o, quality=94); print("wrote", o); return o

def endcard(brand_dir, out):
    b = Brand(brand_dir)
    lines = b.cfg.get("campaign", {}).get("endcard", ["", b.cfg.get("display_name", ""), ""])
    base = Image.new("RGBA", (b.W, b.H), b.ink)
    d = ImageDraw.Draw(base)
    f = b.font(96, display=True)
    cy = b.H // 2
    logo = b.logo_path()
    if logo and os.path.exists(logo):
        if lines[0]: _center(b, d, lines[0], f, cy - 200, b.paper, shadow=False)
        lg = Image.open(logo).convert("RGBA")
        lw = int(b.W * 0.62); lg = lg.resize((lw, round(lg.height * lw / lg.width)), Image.LANCZOS)
        base.alpha_composite(lg, ((b.W - lw) // 2, cy - 70))
        if len(lines) > 2 and lines[2]:
            _center(b, d, lines[2], f, cy + 120, b.paper, shadow=False)
    else:
        for i, ln in enumerate(lines):
            _center(b, d, ln, f, cy - 150 + i * 150, b.accent if i == 1 else b.paper, shadow=False)
    o = b.p(out) if not os.path.isabs(out) else out
    os.makedirs(os.path.dirname(o), exist_ok=True)
    base.convert("RGB").save(o, quality=95); print("wrote", o); return o

# ---------- CLI ----------
def _letterspace(draw, text, font, cx, cy, fill, tracking):
    ws = [draw.textlength(c, font=font) + tracking for c in text]
    total = sum(ws) - tracking
    x = cx - total / 2
    for c in text:
        draw.text((x, cy), c, font=font, fill=fill); x += draw.textlength(c, font=font) + tracking

def endcard_film(brand_dir, out, bg=None, size=(1920, 1080)):
    """Landscape brand end card for films. Reads brand.json:
       endcard_eyebrow, display_name (or logo), tagline, fonts.endcard (serif).
       Over an optional darkened bg image, else solid ink."""
    b = Brand(brand_dir)
    W, H = size
    if bg:
        base = load_bg_to(b, b.p(bg) if not os.path.isabs(bg) else bg, W, H)
        ov = Image.new("RGB", (W, H), b.ink[:3]); base = Image.blend(base.convert("RGB"), ov, 0.66).convert("RGBA")
    else:
        base = Image.new("RGBA", (W, H), b.ink)
    d = ImageDraw.Draw(base)
    serif = b.cfg.get("fonts", {}).get("endcard", "/System/Library/Fonts/Supplemental/Didot.ttc")
    sp, si = _resolve_font_file(serif)
    def f(sz): return ImageFont.truetype(sp, sz, index=si)
    cy = H // 2
    eyebrow = b.cfg.get("endcard_eyebrow", "")
    if eyebrow:
        _letterspace(d, eyebrow, f(30), W / 2, cy - 180, b.accent, 14)
    logo = b.logo_path()
    if logo and os.path.exists(logo):
        lg = Image.open(logo).convert("RGBA"); lw = int(W * 0.42)
        lg = lg.resize((lw, round(lg.height * lw / lg.width)), Image.LANCZOS)
        base.alpha_composite(lg, ((W - lw) // 2, cy - lg.height // 2 - 10))
    else:
        _letterspace(d, b.cfg.get("display_name", "").upper(), f(150), W / 2, cy - 110, b.paper, 26)
    d.line([(W / 2 - 90, cy + 90), (W / 2 + 90, cy + 90)], fill=b.accent, width=2)
    tag = b.cfg.get("tagline", "")
    if tag:
        _letterspace(d, tag.rstrip(".").upper(), f(40), W / 2, cy + 120, b.paper, 8)
    o = b.p(out) if not os.path.isabs(out) else out
    os.makedirs(os.path.dirname(o), exist_ok=True)
    base.convert("RGB").save(o, quality=95); print("wrote", o); return o

def load_bg_to(b, path, W, H):
    im = Image.open(path).convert("RGBA")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("slide")
    for a in ("--brand-dir", "--bg", "--l1", "--l2", "--product", "--out"): s.add_argument(a, required=True)
    s.add_argument("--accent", default="primary"); s.add_argument("--product-h", type=float, default=0.62)
    s.add_argument("--product-cx", type=float, default=0.76)
    q = sub.add_parser("quote")
    for a in ("--brand-dir", "--l1", "--l2", "--out"): q.add_argument(a, required=True)
    q.add_argument("--accent", default="primary"); q.add_argument("--bg", default=None)
    e = sub.add_parser("endcard")
    for a in ("--brand-dir", "--out"): e.add_argument(a, required=True)
    ef = sub.add_parser("endcard-film")
    for a in ("--brand-dir", "--out"): ef.add_argument(a, required=True)
    ef.add_argument("--bg", default=None)
    a = ap.parse_args()
    if a.cmd == "slide":
        content_slide(a.brand_dir, a.bg, a.l1, a.l2, a.product, a.out, a.accent, a.product_h, a.product_cx)
    elif a.cmd == "quote":
        quote_card(a.brand_dir, a.l1, a.l2, a.out, a.accent, a.bg)
    elif a.cmd == "endcard":
        endcard(a.brand_dir, a.out)
    elif a.cmd == "endcard-film":
        endcard_film(a.brand_dir, a.out, a.bg)
    else:
        ap.print_help()
