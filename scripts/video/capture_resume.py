#!/usr/bin/env python3
"""Resume-friendly frame capture: renders only frames that don't already exist
in outputs/.../frames, then encodes the silent MP4. Lets us recover a stalled
render without redoing completed frames. Cleans the frame dir after encoding."""
import os, subprocess, glob
from playwright.sync_api import sync_playwright

ROOT = "/Users/matthewfitzpatrick-buck/Desktop/matthew-fitzpatrick-aios-main"
DIR = os.path.join(ROOT, "outputs/videos/cool-hollow-brand")
HTML = os.path.join(DIR, "brand-explainer.html")
FRAMES = os.path.join(DIR, "frames")
SILENT = os.path.join(DIR, "silent.mp4")
FPS = 30
W, H = 1920, 1080
os.makedirs(FRAMES, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--force-color-profile=srgb"])
    page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    page.goto("file://" + HTML)
    page.wait_for_function("window.__READY === true", timeout=15000)
    try:
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(400)
    except Exception:
        pass
    total = page.evaluate("window.TOTAL")
    n = int(total * FPS / 1000) + 1
    step = 1000.0 / FPS
    done = 0
    for i in range(n):
        path = os.path.join(FRAMES, f"f{i:05d}.png")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            continue
        page.evaluate(f"window.seek({i*step})")
        page.screenshot(path=path)
        done += 1
        if done % 100 == 0:
            print(f"rendered up to frame {i}/{n}", flush=True)
    browser.close()
print(f"capture complete: rendered {done} new frames")

subprocess.run([
    "ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(FRAMES, "f%05d.png"),
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
    "-movflags", "+faststart", SILENT
], check=True)
print("wrote", SILENT, flush=True)

# clean up frames to save disk (final video is tiny; frames are not)
for f in glob.glob(os.path.join(FRAMES, "*.png")):
    os.remove(f)
try:
    os.rmdir(FRAMES)
except OSError:
    pass
print("cleaned frame dir")
