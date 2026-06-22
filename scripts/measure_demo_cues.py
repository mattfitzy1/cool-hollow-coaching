#!/usr/bin/env python3
"""Measure each narration cue's real duration for a /demo-video config, and print a
non-overlapping timeline suggestion. Run this BEFORE setting start_ms / the HTML timeline —
it's the step that prevents lines overlapping each other (the #1 timing bug).

It generates+caches each cue's TTS using the SAME cache key as scripts/demo_video_audio.py,
so the later mux reuses these clips (no double ElevenLabs spend).

Usage:
  python scripts/measure_demo_cues.py outputs/videos/<slug>/<config>.json [--gap 1500] [--start 1500]

--gap   ms of silence to leave between the end of one cue and the start of the next (default 1500)
--start ms for the first cue (default = the config's first cue start_ms, else 1500)
"""
import sys, json, hashlib, subprocess, pathlib, importlib.util

REPO = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("dva", REPO/"scripts/demo_video_audio.py")
dva = importlib.util.module_from_spec(spec); spec.loader.exec_module(dva)

def main():
    args = sys.argv[1:]
    cfg_path = next(a for a in args if not a.startswith("--"))
    gap = int(args[args.index("--gap")+1]) if "--gap" in args else 1500
    cfg = json.load(open(REPO/cfg_path if not pathlib.Path(cfg_path).is_absolute() else cfg_path))

    # resolve voice preset exactly like demo_video_audio.main()
    pname = cfg.get("voice_preset")
    if pname:
        pf = json.load(open(REPO/".claude/skills/demo-video/reference/voice-presets.json"))
        if pname == "default": pname = pf.get("default")
        p = pf["presets"][pname]
        cfg.setdefault("voice_id", p["voice_id"])
        cfg.setdefault("model", p.get("model", "eleven_multilingual_v2"))
        cfg.setdefault("voice_settings", p.get("voice_settings"))

    key = dva.env("ELEVENLABS_API_KEY")
    vdir = REPO/cfg.get("voice_dir", pathlib.Path(cfg["video"]).parent/"voice")
    vdir.mkdir(parents=True, exist_ok=True)
    norm = cfg.get("normalise_numbers", True)
    sig = json.dumps([cfg.get("model"), cfg.get("voice_settings")], sort_keys=True)

    start = int(args[args.index("--start")+1]) if "--start" in args else int(cfg["cues"][0].get("start_ms", 1500))
    print(f"voice_id={cfg['voice_id']}  gap={gap}ms  (durations are real TTS, cached for the mux)\n")
    cursor = start
    rows = []
    for i, c in enumerate(cfg["cues"]):
        spoken = dva.normalise_for_speech(c["text"]) if norm else c["text"]
        h = hashlib.md5((cfg["voice_id"]+"|"+spoken+"|"+sig).encode()).hexdigest()[:10]
        mp3 = vdir/f"tts_{h}.mp3"
        if not mp3.exists():
            dva.tts(spoken, cfg, mp3, key)
        d = dva.dur(mp3)
        suggested = cursor
        rows.append((i, d, suggested, c["text"]))
        cursor = suggested + int(d*1000) + gap
    print(f"{'#':>2} {'dur':>6} {'suggested_start':>15}  text")
    for i, d, s, t in rows:
        print(f"{i:>2} {d:6.2f} {s:>15}  {t[:64]}")
    print(f"\nlast cue ends ~{rows[-1][2] + int(rows[-1][1]*1000)}ms; +tail -> set video TOTAL accordingly.")
    print("NOTE: 'suggested_start' assumes back-to-back beats. If a cue must align to an on-screen")
    print("event (a step start, a pill), use that event's time instead and keep the gap check.")

if __name__ == "__main__":
    main()
