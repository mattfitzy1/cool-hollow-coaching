#!/usr/bin/env python3
"""
Creative pack-out (Creative Department, C2).

Builds the review contact sheet, logs composited slides to creative_assets, and
prints a batch summary for the review doc. The /creative skill writes the prose
review doc + captions on top of this.

Subcommands:
  contact  --brand-dir D [--out CONTACT-SHEET.jpg] [--title "Brand - batch"]
           Builds a grid from slides/*.jpg + images/hero-*.png (+ video poster if present).
  log      --brand-dir D --type slide --paths a.jpg b.jpg ...    (record composited assets)
  summary  --brand-dir D                                          (counts + db rows for review)
"""
import os, glob, argparse, sqlite3
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "content.db")
HN = "/System/Library/Fonts/HelveticaNeue.ttc"

def brand_slug(bd):
    import json
    try: return json.load(open(os.path.join(bd, "brand.json")))["brand"]
    except Exception: return os.path.basename(bd.rstrip("/"))

def collect(bd):
    items = []
    for p in sorted(glob.glob(os.path.join(bd, "slides", "*.jpg"))):
        items.append((p, os.path.splitext(os.path.basename(p))[0]))
    for p in sorted(glob.glob(os.path.join(bd, "images", "hero-*.png"))):
        items.append((p, os.path.basename(p).replace(".png", "")))
    return items

def contact(bd, out, title):
    items = collect(bd)
    if not items:
        print("no assets to sheet"); return
    cols, tw, pad, lab = 4, 360, 16, 26
    rows = (len(items) + cols - 1) // cols
    cell_h = int(tw * 1350 / 1080)
    W = cols * tw + (cols + 1) * pad
    H = rows * (cell_h + lab) + (rows + 1) * pad + 40
    sheet = Image.new("RGB", (W, H), (20, 20, 18))
    d = ImageDraw.Draw(sheet)
    ft = ImageFont.truetype(HN, 22, index=1); fl = ImageFont.truetype(HN, 18, index=1)
    d.text((pad, 10), title, font=ft, fill=(240, 235, 220))
    for i, (fp, label) in enumerate(items):
        im = Image.open(fp).convert("RGB")
        im = im.resize((tw, int(im.height * tw / im.width)))
        c = Image.new("RGB", (tw, cell_h), (20, 20, 18))
        c.paste(im, (0, (cell_h - im.height) // 2))
        r, cc = divmod(i, cols)
        x = pad + cc * (tw + pad); y = 40 + pad + r * (cell_h + lab + pad)
        sheet.paste(c, (x, y))
        d.text((x, y + cell_h + 3), label, font=fl, fill=(225, 220, 205))
    o = os.path.join(bd, out)
    sheet.save(o, quality=90)
    print("wrote", os.path.relpath(o, ROOT), sheet.size)

def log(bd, asset_type, paths):
    slug = brand_slug(bd)
    con = sqlite3.connect(DB)
    for p in paths:
        con.execute("""INSERT INTO creative_assets (brand, asset_type, path, title, status, batch)
                       VALUES (?,?,?,?, 'draft', ?)""",
                    (slug, asset_type, os.path.relpath(p, ROOT),
                     os.path.splitext(os.path.basename(p))[0], "batch1"))
    con.commit(); con.close()
    print(f"logged {len(paths)} {asset_type} asset(s)")

def summary(bd):
    slug = brand_slug(bd)
    con = sqlite3.connect(DB)
    rows = con.execute("""SELECT asset_type, COUNT(*), COALESCE(SUM(credits),0)
                          FROM creative_assets WHERE brand=? GROUP BY asset_type""", (slug,)).fetchall()
    total_cr = con.execute("SELECT COALESCE(SUM(credits),0) FROM creative_assets WHERE brand=?", (slug,)).fetchone()[0]
    con.close()
    print(f"=== {slug} creative_assets ===")
    for t, n, cr in rows:
        print(f"  {t:14s} {n:3d}   {cr:.1f} cr")
    print(f"  {'TOTAL credits':14s}       {total_cr:.1f} cr")

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("contact"); c.add_argument("--brand-dir", required=True)
    c.add_argument("--out", default="CONTACT-SHEET.jpg"); c.add_argument("--title", default="Creative batch")
    l = sub.add_parser("log"); l.add_argument("--brand-dir", required=True)
    l.add_argument("--type", required=True); l.add_argument("--paths", nargs="+", required=True)
    s = sub.add_parser("summary"); s.add_argument("--brand-dir", required=True)
    a = ap.parse_args()
    if a.cmd == "contact": contact(a.brand_dir, a.out, a.title)
    elif a.cmd == "log": log(a.brand_dir, a.type, a.paths)
    elif a.cmd == "summary": summary(a.brand_dir)
    else: ap.print_help()

if __name__ == "__main__":
    main()
