#!/usr/bin/env python3
"""Capture an animated HTML demo to MP4, deterministically.

Loads the page in Chromium, steps window.seek(ms) frame by frame, screenshots
each frame, then encodes with ffmpeg. The HTML must expose window.seek(t) and
window.TOTAL (ms). Smooth because we drive a virtual clock, not wall time.

Usage:
  .venv-command/bin/python scripts/capture_demo.py outputs/videos/aios-demo/demo.html [--fps 30] [--scale 1.5]
"""
import sys, os, subprocess, shutil, argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--scale", type=float, default=1.5, help="device scale factor (supersampling)")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    html = Path(args.html).resolve()
    if not html.exists():
        sys.exit(f"not found: {html}")
    work = html.parent
    frames = work / "frames"
    if frames.exists():
        shutil.rmtree(frames)
    frames.mkdir(parents=True)
    out = Path(args.out) if args.out else work / (html.stem + ".mp4")

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-color-profile=srgb"])
        page = browser.new_page(viewport={"width": args.width, "height": args.height},
                                device_scale_factor=args.scale)
        page.goto(html.as_uri())
        page.wait_for_function("typeof window.seek === 'function' && typeof window.TOTAL === 'number'")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(400)  # settle fonts/layout

        total = page.evaluate("window.TOTAL")
        n = int(total / 1000 * args.fps) + 1
        print(f"Capturing {n} frames at {args.fps}fps ({total}ms, scale {args.scale}) -> {args.width}x{args.height}")
        for i in range(n):
            t = i / args.fps * 1000.0
            page.evaluate(f"window.seek({t})")
            page.screenshot(path=str(frames / f"{i:04d}.png"), animations="disabled")
            if i % 60 == 0:
                print(f"  frame {i}/{n}")
        browser.close()

    print("Encoding with ffmpeg...")
    cmd = [
        "ffmpeg", "-y", "-framerate", str(args.fps),
        "-i", str(frames / "%04d.png"),
        "-vf", f"scale={args.width}:{args.height}:flags=lanczos,format=yuv420p",
        "-c:v", "libx264", "-crf", "18", "-preset", "slow",
        "-movflags", "+faststart",
        str(out),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.rmtree(frames)

    # also drop a copy on the Desktop for easy sharing
    desktop = Path.home() / "Desktop" / out.name
    try:
        shutil.copy2(out, desktop)
    except Exception as e:
        desktop = None
    size = out.stat().st_size / 1e6
    print(f"\nDone: {out}  ({size:.1f} MB, {n} frames)")
    if desktop:
        print(f"Desktop copy: {desktop}")

if __name__ == "__main__":
    main()
