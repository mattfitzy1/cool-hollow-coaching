#!/usr/bin/env python3
"""
Creative generation pipeline (Creative Department, C1).

Thin, deterministic wrapper over the `hf` (Higgsfield) CLI that generates and
downloads on-brand assets into a brand folder. Reads models + style block from
brand.json. The /creative skill (Claude) decides WHAT to generate (the shot
list); this just executes and downloads.

Subcommands:
  scene  --brand-dir D --name s1 --prompt "..."            (gpt_image_2 + style block)
  hero   --brand-dir D --name hero-acv --ref refs/x.png --prompt "..."  (nano_banana_2 ref)
  reel   --brand-dir D --name reel --start images/x.png --prompt "..."  (seedance_2_0 i2v)
  batch  --brand-dir D --jobs jobs.json                    (runs many, see schema below)

jobs.json:
  { "scenes": [ {"name":"s1","prompt":"...","aspect":"4:5"}, ... ],
    "heroes": [ {"name":"hero-1","ref":"refs/mat.png","prompt":"...","aspect":"4:5"} ],
    "reels":  [ {"name":"reel","start":"images/hero-1.png","prompt":"...","aspect":"9:16","duration":5} ] }

Each generated asset is logged to data/content.db creative_assets.
"""
import os, json, argparse, subprocess, sqlite3, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data", "content.db")
UA = {"User-Agent": "Mozilla/5.0"}

def load_brand(bd):
    with open(os.path.join(bd, "brand.json")) as f:
        return json.load(f)

def rel(bd, p):
    return p if os.path.isabs(p) else os.path.join(bd, p)

def hf_create(model, args):
    """Run hf generate create ... --wait --json, return (result_url, credits)."""
    cmd = ["hf", "generate", "create", model, "--wait", "--json"] + args
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        raise RuntimeError(f"hf failed: {r.stderr.strip()[:400]}")
    out = r.stdout.strip()
    # tolerate any leading log lines before JSON
    start = out.find("[") if out.find("[") != -1 else out.find("{")
    data = json.loads(out[start:])
    j = data[0] if isinstance(data, list) else data
    if j.get("status") != "completed":
        raise RuntimeError(f"job status {j.get('status')}: {str(j)[:300]}")
    return j.get("result_url"), j.get("params", {}).get("credits")

def download(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest

def log_asset(brand, asset_type, path, prompt, model, title=None, product=None, batch=None):
    try:
        con = sqlite3.connect(DB)
        con.execute("""INSERT INTO creative_assets
            (brand, asset_type, path, title, product, prompt, model, status, batch)
            VALUES (?,?,?,?,?,?,?, 'draft', ?)""",
            (brand, asset_type, os.path.relpath(path, ROOT), title, product, prompt, model, batch))
        con.commit(); con.close()
    except Exception as e:
        print("  ! db log skipped:", e)

# ---- single-asset ops ----
def gen_scene(bd, cfg, name, prompt, aspect="3:4", batch=None):
    model = cfg.get("image_model", "gpt_image_2")
    style = cfg.get("style_block", "")
    full = f"{prompt} {style}".strip()
    url, cr = hf_create(model, ["--prompt", full, "--aspect_ratio", aspect])
    dest = download(url, os.path.join(bd, "images", f"{name}-bg.png"))
    log_asset(cfg["brand"], "scene", dest, full, model, title=name, batch=batch)
    print(f"scene  {name} -> {os.path.relpath(dest, ROOT)}")
    return dest

def gen_hero(bd, cfg, name, ref, prompt, aspect="3:4", batch=None):
    model = cfg.get("hero_model", "nano_banana_2")
    url, cr = hf_create(model, ["--image", rel(bd, ref), "--prompt", prompt, "--aspect_ratio", aspect])
    dest = download(url, os.path.join(bd, "images", f"{name}.png"))
    log_asset(cfg["brand"], "hero", dest, prompt, model, title=name, batch=batch)
    print(f"hero   {name} -> {os.path.relpath(dest, ROOT)}")
    return dest

def gen_reel(bd, cfg, name, start, prompt, aspect="9:16", duration=5, batch=None, resolution=None):
    model = cfg.get("video_model", "seedance_2_0")
    resolution = resolution or cfg.get("film", {}).get("resolution", "1080p")
    url, cr = hf_create(model, ["--start-image", rel(bd, start), "--prompt", prompt,
                                "--aspect_ratio", aspect, "--duration", str(duration),
                                "--resolution", resolution])
    dest = download(url, os.path.join(bd, "video", f"{name}.mp4"))
    log_asset(cfg["brand"], "reel", dest, prompt, model, title=name, batch=batch)
    print(f"reel   {name} -> {os.path.relpath(dest, ROOT)}")
    return dest

def mode_resolution(draft, final):
    """Draft = cheap 480p preview, Final = 1080p. Same model + start image + prompt,
    so a 480p draft upgrades to 1080p with no rework (just the resolution changes)."""
    if final: return "1080p"
    if draft: return "480p"
    return None  # fall back to per-reel resolution, then brand.json film.resolution

def run_batch(bd, cfg, jobs, batch="batch1", draft=False, final=False):
    made = {"scenes": [], "heroes": [], "reels": []}
    mres = mode_resolution(draft, final)
    for s in jobs.get("scenes", []):
        try: made["scenes"].append(gen_scene(bd, cfg, s["name"], s["prompt"], s.get("aspect", "3:4"), batch))
        except Exception as e: print("  ! scene", s.get("name"), "failed:", e)
    for h in jobs.get("heroes", []):
        try: made["heroes"].append(gen_hero(bd, cfg, h["name"], h["ref"], h["prompt"], h.get("aspect", "3:4"), batch))
        except Exception as e: print("  ! hero", h.get("name"), "failed:", e)
    for v in jobs.get("reels", []):
        try: made["reels"].append(gen_reel(bd, cfg, v["name"], v["start"], v["prompt"],
                                            v.get("aspect", "9:16"), v.get("duration", 5), batch,
                                            v.get("resolution") or mres))
        except Exception as e: print("  ! reel", v.get("name"), "failed:", e)
    return made

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd")
    for c in ("scene", "hero", "reel", "batch"):
        s = sub.add_parser(c); s.add_argument("--brand-dir", required=True)
        if c == "batch":
            s.add_argument("--jobs", required=True); s.add_argument("--batch", default="batch1")
        else:
            s.add_argument("--name", required=True); s.add_argument("--prompt", required=(c != "reel") )
            s.add_argument("--aspect", default="3:4" if c != "reel" else "9:16")
            s.add_argument("--batch", default="batch1")
            if c == "hero": s.add_argument("--ref", required=True)
            if c == "reel": s.add_argument("--start", required=True); s.add_argument("--duration", type=int, default=5); s.add_argument("--resolution", default=None)
        if c in ("reel", "batch"):
            # cheap-iteration controls (video only): --draft 480p preview, --final 1080p
            s.add_argument("--draft", action="store_true", help="cheap 480p preview")
            s.add_argument("--final", action="store_true", help="1080p final")
    a = ap.parse_args()
    if not a.cmd: ap.print_help(); return
    bd = a.brand_dir; cfg = load_brand(bd)
    if a.cmd == "scene": gen_scene(bd, cfg, a.name, a.prompt, a.aspect, a.batch)
    elif a.cmd == "hero": gen_hero(bd, cfg, a.name, a.ref, a.prompt, a.aspect, a.batch)
    elif a.cmd == "reel":
        res = a.resolution or mode_resolution(a.draft, a.final)
        gen_reel(bd, cfg, a.name, a.start, a.prompt, a.aspect, a.duration, a.batch, res)
    elif a.cmd == "batch":
        with open(a.jobs) as f: jobs = json.load(f)
        run_batch(bd, cfg, jobs, a.batch, draft=a.draft, final=a.final)

if __name__ == "__main__":
    main()
