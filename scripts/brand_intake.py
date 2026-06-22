#!/usr/bin/env python3
"""
Brand intake (Creative Department, B1).

Deterministic first pass for /brand-pack: scrape a brand's website for its logo,
product images and copy, sample a palette, ingest any dropped screenshots, and
emit a STARTER brand.json + intake-notes.md into outputs/creative/{brand}/.

Web research, voice, and final brand.json/brand-pack.md curation are the skill's
job (Claude) on top of this. This just gathers the raw, repeatable material.

Usage:
  python scripts/brand_intake.py --brand example-brand --url https://example.com \
      --screenshots ~/Downloads/shots
"""
import os, re, json, argparse, urllib.request, urllib.parse, shutil
from collections import Counter
from PIL import Image

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
IMG_RE = re.compile(r'https?://[^"\'\s)]+\.(?:png|jpg|jpeg|webp)', re.I)

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def fetch_text(url):
    try: return fetch(url).decode("utf-8", "ignore")
    except Exception as e: print("  ! fetch failed:", e); return ""

def download(url, dest):
    try:
        data = fetch(url)
        with open(dest, "wb") as f: f.write(data)
        return True
    except Exception as e:
        print("  ! dl failed", url, e); return False

# filenames that are never the brand's own product/logo
NOISE = ("icon", "favicon", "sprite", "placeholder", "avatar", "-bg", "bg-", "/bg",
         "hero", "header", "banner", "background", "pattern", "texture", "sun",
         "facebook", "instagram", "twitter", "youtube", "tiktok")
PARTNER = ("libstar", "cecil", "partner", "client", "sponsor", "powered")

def _logo_rank(brand, u):
    lu = u.lower()
    score = 0
    if lu.endswith(".png"): score -= 2          # prefer transparent PNG logos
    if brand and brand.lower() in lu: score -= 3 # brand's own name in filename
    if any(c in lu for c in ("yellow", "white", "primary", "main", "header")): score -= 1
    if any(p in lu for p in PARTNER): score += 5 # demote manufacturer/partner logos
    return score

def classify(urls, brand=""):
    """Split image URLs into logo candidates, products, and other."""
    logos, products, other = [], [], []
    for u in urls:
        lu = u.lower()
        if any(k in lu for k in ("logo", "brandmark", "wordmark")):
            logos.append(u)
        elif any(k in lu for k in NOISE):
            other.append(u)
        elif any(p in lu for p in PARTNER):
            other.append(u)
        elif any(k in lu for k in ("product", "bottle", "pack", "/uploads/", "wp-content")):
            products.append(u)
        else:
            other.append(u)
    logos.sort(key=lambda u: _logo_rank(brand, u))
    return logos, products, other

def sample_accent(path):
    """Most common saturated, non-neutral colour in an image (the brand accent)."""
    try:
        im = Image.open(path).convert("RGBA"); w, h = im.size
        c = Counter()
        for x in range(0, w, max(1, w // 80)):
            for y in range(0, h, max(1, h // 80)):
                r, g, b, a = im.getpixel((x, y))
                if a < 180: continue
                mx, mn = max(r, g, b), min(r, g, b)
                if mx - mn < 50 or mx < 60: continue   # skip greys/near-black
                c[(r // 16 * 16, g // 16 * 16, b // 16 * 16)] += 1
        if not c: return None
        (r, g, b), _ = c.most_common(1)[0]
        return "#%02X%02X%02X" % (r, g, b)
    except Exception:
        return None

def text_snippets(html):
    """Crude copy harvest: title, meta description, h1/h2."""
    out = {}
    m = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    if m: out["title"] = re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html, re.I)
    if m: out["description"] = m.group(1).strip()
    heads = re.findall(r"<h[12][^>]*>(.*?)</h[12]>", html, re.I | re.S)
    out["headings"] = [re.sub(r"<[^>]+>", "", h).strip() for h in heads if h.strip()][:12]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--instagram", default="")
    ap.add_argument("--screenshots", default="")
    ap.add_argument("--max-products", type=int, default=14)
    ap.add_argument("--out-root", default="outputs/creative")
    a = ap.parse_args()

    base = os.path.join(a.out_root, a.brand)
    refs = os.path.join(base, "refs"); shots = os.path.join(refs, "screenshots")
    os.makedirs(refs, exist_ok=True); os.makedirs(shots, exist_ok=True)
    notes = [f"# Intake notes - {a.brand}", "", f"Source: {a.url}", ""]

    # crawl home + likely product/about pages
    pages = [a.url.rstrip("/")]
    for sub in ("products", "our-products", "about", "shop", "range"):
        pages.append(a.url.rstrip("/") + "/" + sub + "/")
    seen_imgs, copy = set(), {}
    for pg in pages:
        html = fetch_text(pg)
        if not html: continue
        print("scanned", pg)
        for u in IMG_RE.findall(html):
            seen_imgs.add(u.split("?")[0])
        if pg == pages[0]:
            copy = text_snippets(html)

    logos, products, other = classify(sorted(seen_imgs), a.brand)
    notes += [f"Images found: {len(seen_imgs)} (logos {len(logos)}, products {len(products)}, other {len(other)})", ""]

    # download logo(s) in ranked order; remember locals for accent sampling
    logo_locals = []
    for i, u in enumerate(logos[:3]):
        ext = os.path.splitext(u)[1].split("?")[0] or ".png"
        dest = os.path.join(refs, f"logo-{i}{ext}")
        if download(u, dest):
            logo_locals.append(os.path.relpath(dest, base))
            notes.append(f"- logo: {u}")
    logo_local = logo_locals[0] if logo_locals else None

    # download products (skip tiny thumbnails by filename hints)
    prod_entries = []
    skip_thumb = re.compile(r"-\d+x\d+\.", re.I)
    picked = [u for u in products if not skip_thumb.search(u)][: a.max_products]
    for u in picked:
        name = os.path.basename(urllib.parse.urlparse(u).path)
        dest = os.path.join(refs, name)
        if download(u, dest):
            prod_entries.append({"name": os.path.splitext(name)[0].replace("-", " ").title(),
                                 "ref": os.path.relpath(dest, base)})
            notes.append(f"- product: {name}")

    # ingest screenshots
    n_shots = 0
    if a.screenshots and os.path.isdir(os.path.expanduser(a.screenshots)):
        for fn in sorted(os.listdir(os.path.expanduser(a.screenshots))):
            if fn.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                shutil.copy2(os.path.join(os.path.expanduser(a.screenshots), fn), os.path.join(shots, fn))
                n_shots += 1
    notes += ["", f"Screenshots ingested: {n_shots}"]

    # palette guess: try each logo candidate, then products, until one yields an accent
    accent = None
    for rel in logo_locals + [pe["ref"] for pe in prod_entries]:
        accent = sample_accent(os.path.join(base, rel))
        if accent:
            notes += ["", f"Sampled accent {accent} from {rel}"]
            break
    if not accent:
        notes += ["", "Sampled accent: n/a (Claude to set from screenshots)"]

    # starter brand.json (Claude refines)
    brand_json = {
        "brand": a.brand,
        "display_name": copy.get("title", a.brand.title()).split("|")[0].strip(),
        "website": a.url,
        "instagram": a.instagram,
        "canvas": [1080, 1350],
        "palette": {
            "accent": accent or "#F0C800",
            "accent2": "#4AA0D6",
            "ink": "#0E0E0C",
            "paper": "#F6F1E7"
        },
        "fonts": {"headline": "HelveticaNeue.ttc#1", "display": "HelveticaNeue.ttc#9"},
        "logo": logo_local,
        "devices": {"spark": True, "tick": True},
        "campaign": {"formula": ["Add a little {quality}", "to your {thing}."],
                     "endcard": ["", copy.get("title", a.brand).split("|")[0].strip().upper(), ""]},
        "style_block": "TODO: Claude fills the look (e.g. dark moody food photography, one accent colour) from research + screenshots.",
        "image_model": "gpt_image_2", "hero_model": "nano_banana_2", "video_model": "seedance_2_0",
        "products": prod_entries,
        "_intake": {"copy": copy}
    }
    with open(os.path.join(base, "brand.json"), "w") as f:
        json.dump(brand_json, f, indent=2)
    with open(os.path.join(base, "intake-notes.md"), "w") as f:
        f.write("\n".join(notes) + "\n")

    print(f"\nINTAKE COMPLETE -> {base}")
    print(f"  logo: {logo_local}  | products: {len(prod_entries)}  | screenshots: {n_shots}  | accent: {accent}")
    print("  wrote brand.json (STARTER) + intake-notes.md. Claude now refines + writes brand-pack.md.")

if __name__ == "__main__":
    main()
