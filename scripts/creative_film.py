#!/usr/bin/env python3
"""
Creative film assembler (Creative Department).

Stitches a brand's motion clips into a finished cinematic marketing film, driven
entirely by the `film` block in brand.json so settings are remembered per brand
and improve over time (no per-project bash). Reusable across brands.

Reads brand.json `film`:
  { resolution, aspect, crossfade, slow_factor, voiceover,
    music, music_volume, fade_in, fade_out, endcard_seconds }

Pipeline: per-clip slow + scale/pad -> xfade crossfade chain -> end card clip ->
music bed (from reference/creative/music/) faded in/out -> mux (libx264 crf19).
No voiceover in v1 (film.voiceover is reserved; VO parked until voice quality is good).

Usage:
  python scripts/creative_film.py --brand-dir outputs/creative/example-brand \
      --clips video/v1.mp4 video/v2.mp4 video/v3.mp4 video/v4.mp4 \
      --endcard-bg images/calm-scene-bg.png --out example-brand-film.mp4
  # clips omitted -> auto-discovers video/v*.mp4 sorted
"""
import os, sys, json, glob, argparse, subprocess, datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "creative_lib"))
import render as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSIC_DIR = os.path.join(ROOT, "reference", "creative", "music")
SIZES = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080), "4:3": (1440, 1080)}

def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg/ffprobe failed:\n" + r.stderr[-800:])
    return r.stdout.strip()

def dur(path):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=nk=1:nw=1", path]))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand-dir", required=True)
    ap.add_argument("--clips", nargs="*", default=None, help="ordered clip paths (rel to brand-dir); default auto-discover video/v*.mp4")
    ap.add_argument("--endcard-bg", default=None, help="image (rel to brand-dir) to darken behind the end card")
    ap.add_argument("--out", default=None)
    ap.add_argument("--music", default=None, help="override film.music")
    ap.add_argument("--no-endcard", action="store_true")
    a = ap.parse_args()

    bd = a.brand_dir
    cfg = json.load(open(os.path.join(bd, "brand.json")))
    f = cfg.get("film", {})
    aspect = f.get("aspect", "16:9"); W, H = SIZES.get(aspect, (1920, 1080))
    D = float(f.get("crossfade", 0.8)); SF = float(f.get("slow_factor", 1.15))
    vol = float(f.get("music_volume", 0.9)); fin = float(f.get("fade_in", 2.0)); fout = float(f.get("fade_out", 3.5))
    ec_secs = int(f.get("endcard_seconds", 4))
    rel = lambda p: p if os.path.isabs(p) else os.path.join(bd, p)

    # clips
    clips = a.clips or [os.path.relpath(p, bd) for p in sorted(glob.glob(os.path.join(bd, "video", "v*.mp4")))]
    clips = [rel(c) for c in clips]
    if not clips:
        sys.exit("no clips found")
    print("clips:", [os.path.basename(c) for c in clips])

    # end card -> short clip
    seq = list(clips); sfs = [SF] * len(clips)
    if not a.no_endcard:
        ec_png = os.path.join(bd, "images", "endcard.png")
        R.endcard_film(bd, os.path.relpath(ec_png, bd), bg=a.endcard_bg, size=(W, H))
        ec_mp4 = os.path.join(bd, "video", "endcard.mp4")
        sh(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", str(ec_secs), "-i", ec_png,
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p",
            "-r", "30", ec_mp4])
        seq.append(ec_mp4); sfs.append(1.0)

    # Pass 1: silent stitched video (slow + xfade)
    inputs, filt, sdur = [], "", []
    for i, c in enumerate(seq):
        inputs += ["-i", c]
        sd = dur(c) * sfs[i]; sdur.append(sd)
        filt += (f"[{i}:v]setpts={sfs[i]}*PTS,scale={W}:{H}:force_original_aspect_ratio=decrease,"
                 f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p[v{i}];")
    prev, acc = "v0", sdur[0]
    for j in range(1, len(seq)):
        off = acc - D
        filt += f"[{prev}][v{j}]xfade=transition=fade:duration={D}:offset={off:.3f}[x{j}];"
        acc += sdur[j] - D; prev = f"x{j}"
    filt = filt.rstrip(";")
    VT = round(acc, 2)
    footage = os.path.join(bd, "footage.mp4")
    print(f"pass1: silent video {VT}s @ {W}x{H}")
    sh(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", filt,
        "-map", f"[{prev}]", "-r", "30", "-an", "-pix_fmt", "yuv420p", footage])

    # Pass 2: music bed (no VO)
    music_name = a.music or f.get("music", "reverie")
    music = os.path.join(MUSIC_DIR, f"{music_name}.mp3")
    if not os.path.exists(music):
        sys.exit(f"music not found: {music} (see reference/creative/music/REGISTRY.md)")
    mix = os.path.join(bd, "mix.m4a"); fo = VT - fout
    print(f"pass2: music '{music_name}'")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", music, "-filter_complex",
        f"[0:a]atrim=0:{VT},asetpts=N/SR/TB,volume={vol},afade=t=in:st=0:d={fin},afade=t=out:st={fo:.2f}:d={fout}[aout]",
        "-map", "[aout]", "-t", str(VT), "-c:a", "aac", "-b:a", "192k", mix])

    # Pass 3: mux
    out = a.out or f"{cfg['brand']}-film-{datetime.date.today().isoformat()}.mp4"
    outp = rel(out)
    print("pass3: mux ->", os.path.relpath(outp, ROOT))
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", footage, "-i", mix,
        "-c:v", "libx264", "-crf", "19", "-preset", "slow", "-c:a", "aac",
        "-movflags", "+faststart", "-shortest", outp])
    print(f"DONE: {os.path.relpath(outp, ROOT)}  {dur(outp):.1f}s")

if __name__ == "__main__":
    main()
