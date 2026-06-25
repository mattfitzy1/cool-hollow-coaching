#!/usr/bin/env python3
"""Drive window.seek(ms) through Chromium frame by frame, screenshot each,
encode to a silent MP4 with ffmpeg. Deterministic and frame-accurate."""
import os, sys, subprocess, tempfile, shutil
from playwright.sync_api import sync_playwright

ROOT = "/Users/matthewfitzpatrick-buck/Desktop/matthew-fitzpatrick-aios-main"
DIR = os.path.join(ROOT, "outputs/videos/cool-hollow-brand")
HTML = os.path.join(DIR, "brand-explainer.html")
SILENT = os.path.join(DIR, "silent.mp4")
FPS = 30
W, H = 1920, 1080

frames = tempfile.mkdtemp(prefix="chc_frames_")
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-color-profile=srgb"])
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        page.goto("file://" + HTML)
        page.wait_for_function("window.__READY === true", timeout=15000)
        try:
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(400)  # let Poppins paint
        except Exception:
            pass
        total = page.evaluate("window.TOTAL")
        n = int(total * FPS / 1000) + 1
        print(f"capturing {n} frames ({total/1000:.1f}s @ {FPS}fps)")
        step = 1000.0 / FPS
        for i in range(n):
            page.evaluate(f"window.seek({i*step})")
            page.screenshot(path=os.path.join(frames, f"f{i:05d}.png"))
            if i % 120 == 0:
                print(f"  {i}/{n}")
        browser.close()

    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(frames, "f%05d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
        "-movflags", "+faststart", SILENT
    ], check=True)
    print("wrote", SILENT)
finally:
    shutil.rmtree(frames, ignore_errors=True)
