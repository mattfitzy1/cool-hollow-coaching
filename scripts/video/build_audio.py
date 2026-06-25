#!/usr/bin/env python3
"""Voice each beat with ElevenLabs, measure it, lay out the timeline, build a
soft music bed, and mix the full soundtrack. Writes:
  - voice/cue_N.mp3          (per-line voiceover, cached)
  - timeline.json            (start_ms per beat + TOTAL, for the animation)
  - master.wav               (voice + ducked music bed, full length)
Run with the slide-deck venv python (has numpy)."""
import json, os, sys, subprocess, urllib.request, hashlib, wave, struct
import numpy as np

ROOT = "/Users/matthewfitzpatrick-buck/Desktop/matthew-fitzpatrick-aios-main"
DIR = os.path.join(ROOT, "outputs/videos/cool-hollow-brand")
VOICE_DIR = os.path.join(DIR, "voice")
SR = 44100

def api_key():
    for line in open(os.path.join(ROOT, ".env")):
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no ElevenLabs key")

def tts(text, voice_id, model_id, settings, out_mp3):
    """Generate (cached on text+voice+settings) one cue to mp3."""
    sig = hashlib.sha1((text + voice_id + model_id + json.dumps(settings, sort_keys=True)).encode()).hexdigest()[:10]
    cache = out_mp3.replace(".mp3", f".{sig}.mp3")
    if os.path.exists(cache):
        subprocess.run(["cp", cache, out_mp3], check=True)
        return
    body = json.dumps({"text": text, "model_id": model_id, "voice_settings": settings}).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=body,
        headers={"xi-api-key": api_key(), "Content-Type": "application/json", "Accept": "audio/mpeg"},
        method="POST")
    with urllib.request.urlopen(req) as r:
        data = r.read()
    open(out_mp3, "wb").write(data)
    open(cache, "wb").write(data)

def dur_ms(path):
    out = subprocess.check_output(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", path]).decode().strip()
    return int(float(out) * 1000)

def load_mp3_stereo(path):
    """Decode mp3 to float32 stereo numpy via ffmpeg pipe."""
    raw = subprocess.check_output(["ffmpeg", "-v", "quiet", "-i", path, "-ac", "2", "-ar", str(SR),
                                   "-f", "f32le", "-"])
    a = np.frombuffer(raw, dtype=np.float32)
    return a.reshape(-1, 2).copy()

def warm_pad(total_ms):
    """A soft, slow warm chord bed. Low and unobtrusive, gentle movement."""
    n = int(SR * total_ms / 1000)
    t = np.arange(n) / SR
    # Chord progression (Hz), one chord per ~6s, smooth crossfade.
    chords = [
        [130.81, 164.81, 196.00],   # C
        [146.83, 196.00, 246.94],   # G/D-ish
        [110.00, 164.81, 220.00],   # Am
        [123.47, 155.56, 196.00],   # F-ish
    ]
    seg = SR * 6
    out = np.zeros(n, dtype=np.float64)
    for i in range(0, n, seg):
        ch = chords[(i // seg) % len(chords)]
        sl = slice(i, min(i + seg, n))
        tt = t[sl]
        env = np.ones_like(tt)
        # crossfade edges
        f = int(SR * 1.5)
        L = len(tt)
        if L > 2 * f:
            env[:f] = np.linspace(0, 1, f)
            env[-f:] = np.linspace(1, 0, f)
        wave_seg = np.zeros_like(tt)
        for k, fr in enumerate(ch):
            detune = 1.0 + (0.004 * (k - 1))
            wave_seg += np.sin(2 * np.pi * fr * detune * tt) * (0.6 ** k)
            wave_seg += 0.4 * np.sin(2 * np.pi * fr * 2 * tt)  # soft octave shimmer
        # slow tremolo
        lfo = 0.85 + 0.15 * np.sin(2 * np.pi * 0.12 * tt)
        out[sl] += wave_seg * env * lfo
    # gentle low-pass (moving average) to take the edge off
    k = 24
    out = np.convolve(out, np.ones(k) / k, mode="same")
    out /= (np.max(np.abs(out)) + 1e-9)
    st = np.stack([out, out], axis=1).astype(np.float32)
    return st

def write_wav(path, audio):
    a = np.clip(audio, -1, 1)
    pcm = (a * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())

def main():
    cfg = json.load(open(os.path.join(DIR, "beats.json")))
    beats = cfg["beats"]
    # 1) voice each beat, measure
    starts, cur = [], cfg["lead_in_ms"]
    durs = []
    for i, b in enumerate(beats):
        mp3 = os.path.join(VOICE_DIR, f"cue_{i}.mp3")
        tts(b["vo"], cfg["voice_id"], cfg["model_id"], cfg["voice_settings"], mp3)
        d = dur_ms(mp3)
        durs.append(d)
        starts.append(cur)
        cur += d + cfg["gap_ms"]
        print(f"beat {i}: {d/1000:.1f}s  start {starts[-1]/1000:.1f}s")
    total = cur - cfg["gap_ms"] + cfg["tail_ms"]
    print(f"TOTAL {total/1000:.1f}s")

    # 2) timeline for the animation
    timeline = {"total_ms": total,
                "beats": [{"start_ms": starts[i], "dur_ms": durs[i],
                           "kicker": beats[i].get("kicker", ""),
                           "line": beats[i]["line"], "line2": beats[i].get("line2", ""),
                           "sub": beats[i].get("sub", ""), "brand": beats[i].get("brand", False)}
                          for i in range(len(beats))]}
    json.dump(timeline, open(os.path.join(DIR, "timeline.json"), "w"), indent=2)

    # 3) build master soundtrack
    master = np.zeros((int(SR * total / 1000), 2), dtype=np.float32)
    music = warm_pad(total) * 0.10  # quiet bed
    # duck music under each voice span
    duck = np.ones(master.shape[0], dtype=np.float32)
    for i, b in enumerate(beats):
        s = int(SR * starts[i] / 1000)
        voice = load_mp3_stereo(os.path.join(VOICE_DIR, f"cue_{i}.mp3")) * 1.0
        e = min(s + voice.shape[0], master.shape[0])
        master[s:e] += voice[:e - s]
        # duck a little wider than the voice
        ds = max(0, s - int(SR * 0.2)); de = min(master.shape[0], e + int(SR * 0.3))
        duck[ds:de] = 0.35
    # smooth the duck envelope
    k = int(SR * 0.25)
    duck = np.convolve(duck, np.ones(k) / k, mode="same")
    music[:, 0] *= duck; music[:, 1] *= duck
    master += music
    # soft limit
    peak = np.max(np.abs(master))
    if peak > 0.98:
        master *= 0.98 / peak
    write_wav(os.path.join(DIR, "master.wav"), master)
    print("wrote master.wav and timeline.json")

if __name__ == "__main__":
    main()
