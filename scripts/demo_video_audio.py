#!/usr/bin/env python3
"""Build the final audio for a demo/explainer video and mux it into a silent render.

Does: ElevenLabs TTS for each spoken cue -> synth music bed (lo-fi or upbeat) ->
music DUCKED under the voice (sidechain) -> optional UI "boops" at each cue start ->
muxed onto the silent video. The TTS is cached by (voice_id, text) hash so re-runs are free.

Usage:
  python scripts/demo_video_audio.py <config.json> [--dry-run]

Config (see .claude/skills/demo-video/reference/audio-config.example.json):
{
  "video": "outputs/videos/aios-demo/aios-demo.mp4",   # silent base render
  "out":   "outputs/videos/aios-demo/aios-demo-narrated.mp4",
  "voice_id": "lcMyyd2HUfFzxdCaC4Ta",
  "model": "eleven_multilingual_v2",
  "voice_settings": {"stability":0.5,"similarity_boost":0.85,"style":0.0,"use_speaker_boost":true},
  "normalise_numbers": true,    # spell out R50,000 / 75% / 1,500 before TTS (research 2026-06-02)
  "music": "upbeat",            # "lofi" | "upbeat" | "none"
  "music_volume": 0.55,
  "duck": true,                 # lower music while a voice is speaking
  "boops": true,                # short blip + (paired with the on-screen mic illuminate)
  "voice_dir": "outputs/videos/aios-demo/voice",
  "cues": [
    {"text": "I just hopped off a call with a client. Now watch what my AIOS does next.", "start_ms": 7800},
    {"text": "First, I tell it to debrief the call ...", "start_ms": 14100}
  ]
}
"""
import json, sys, hashlib, subprocess, tempfile, urllib.request, pathlib, os, re

REPO = pathlib.Path(__file__).resolve().parent.parent

LOFI = ("0.06*( between(mod(t,12),0,3)*(sin(2*PI*174.61*t)+sin(2*PI*220*t)+sin(2*PI*261.63*t)+sin(2*PI*329.63*t)) "
 "+ between(mod(t,12),3,6)*(sin(2*PI*220*t)+sin(2*PI*261.63*t)+sin(2*PI*329.63*t)+sin(2*PI*392*t)) "
 "+ between(mod(t,12),6,9)*(sin(2*PI*146.83*t)+sin(2*PI*174.61*t)+sin(2*PI*220*t)+sin(2*PI*261.63*t)) "
 "+ between(mod(t,12),9,12)*(sin(2*PI*196*t)+sin(2*PI*246.94*t)+sin(2*PI*293.66*t)+sin(2*PI*349.23*t)) ) "
 "+ 0.13*( between(mod(t,12),0,3)*sin(2*PI*87.31*t)+between(mod(t,12),3,6)*sin(2*PI*110*t)+between(mod(t,12),6,9)*sin(2*PI*73.42*t)+between(mod(t,12),9,12)*sin(2*PI*98*t) ) "
 "+ 0.9*exp(-mod(t,0.75)*30)*sin(2*PI*55*t) + 0.30*exp(-mod(t-0.75,1.5)*16)*(2*random(0)-1) + 0.09*exp(-mod(t,0.375)*60)*(2*random(0)-1)")

UPBEAT = ("0.05*( between(mod(t,9),0,2.25)*(sin(2*PI*261.63*t)+sin(2*PI*329.63*t)+sin(2*PI*392*t)+sin(2*PI*523.25*t)) "
 "+ between(mod(t,9),2.25,4.5)*(sin(2*PI*196*t)+sin(2*PI*246.94*t)+sin(2*PI*293.66*t)+sin(2*PI*392*t)) "
 "+ between(mod(t,9),4.5,6.75)*(sin(2*PI*220*t)+sin(2*PI*261.63*t)+sin(2*PI*329.63*t)+sin(2*PI*440*t)) "
 "+ between(mod(t,9),6.75,9)*(sin(2*PI*174.61*t)+sin(2*PI*220*t)+sin(2*PI*261.63*t)+sin(2*PI*349.23*t)) ) "
 "+ 0.13*( between(mod(t,9),0,2.25)*sin(2*PI*130.81*t)+between(mod(t,9),2.25,4.5)*sin(2*PI*98*t)+between(mod(t,9),4.5,6.75)*sin(2*PI*110*t)+between(mod(t,9),6.75,9)*sin(2*PI*87.31*t) ) "
 "+ 0.95*exp(-mod(t,0.5625)*32)*sin(2*PI*60*t) + 0.34*exp(-mod(t-0.5625,1.125)*17)*(2*random(0)-1) + 0.11*exp(-mod(t,0.28125)*55)*(2*random(0)-1)")

MUSIC_AF = {
 "lofi":   "highpass=f=35,lowpass=f=3300,aecho=0.85:0.88:38:0.12,volume={vol},afade=t=in:st=0:d=2,afade=t=out:st={fo}:d=3.5",
 "upbeat": "highpass=f=35,lowpass=f=4800,volume={vol},afade=t=in:st=0:d=2,afade=t=out:st={fo}:d=3.5",
}
MUSIC_EXPR = {"lofi": LOFI, "upbeat": UPBEAT}
BOOP = "exp(-t*13)*(0.5*sin(2*PI*760*t)+0.28*sin(2*PI*1520*t))"
# SFX: short cues placed at an absolute ms in the final mix (added post-duck, so they sit
# over the music like the boops). Config: "sfx":[{"file":"path.wav","ms":9800,"gain":1.0},
# {"type":"swoosh","ms":35400,"gain":0.6}]. file-based = use a real sample (e.g. the FaceTime
# end chime); type "swoosh" = synthesised Mac-Mail-style send whoosh (pink-noise + flanger).
SWOOSH_SRC = "anoisesrc=d=0.5:c=pink:a=0.85"
SWOOSH_AF  = "highpass=f=420,lowpass=f=7200,flanger=delay=3:depth=5:speed=3,afade=t=in:st=0:d=0.05,afade=t=out:st=0.2:d=0.28,volume=1.6"

# Docs-backed default voice settings (research 2026-06-02): style MUST be 0 for clean
# narration (ElevenLabs docs: "keep this setting at 0 at all times"); speaker_boost on;
# stability ~0.5 baseline (audition 0.50 vs 0.60 on the real script). model eleven_multilingual_v2.
DEFAULT_VOICE_SETTINGS = {"stability": 0.5, "similarity_boost": 0.85, "style": 0.0, "use_speaker_boost": True}

# --- Number/currency normalisation (research 2026-06-02) -----------------------------
# Spell out currency, percentages and comma-grouped numbers BEFORE TTS so the model reads
# pricing/stats cues cleanly ("R50,000" -> "fifty thousand rand"). Small bare integers
# (e.g. "2 hours") are left alone — eleven_multilingual_v2 handles those well.
_ONES = ["zero","one","two","three","four","five","six","seven","eight","nine","ten","eleven",
         "twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen"]
_TENS = ["","","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]
_CUR  = {"R":"rand","$":"dollars","£":"pounds","€":"euros"}
_CENT = {"rand":"cents","dollars":"cents","pounds":"pence","euros":"cents"}

def _under_1000(n):
    if n < 20: return _ONES[n]
    if n < 100: return _TENS[n//10] + ("-"+_ONES[n%10] if n%10 else "")
    return _ONES[n//100] + " hundred" + (" and "+_under_1000(n%100) if n%100 else "")

def _int_words(n):
    if n == 0: return "zero"
    parts=[]
    for div,name in [(1_000_000_000,"billion"),(1_000_000,"million"),(1000,"thousand")]:
        if n>=div: parts.append(_under_1000(n//div)+" "+name); n%=div
    if n: parts.append(_under_1000(n))
    return " ".join(parts)

def _frac_words(frac):  # read digits after a decimal point one by one ("point five")
    return "point " + " ".join(_ONES[int(d)] for d in frac)

def normalise_for_speech(text):
    def _cur(m):
        unit=_CUR[m.group(1)]; num=m.group(2).replace(",","")
        whole,_,cents = num.partition(".")
        out=_int_words(int(whole or 0))+" "+unit
        if cents:
            out += " and "+_int_words(int(cents.ljust(2,"0")[:2]))+" "+_CENT[unit]
        return out
    def _pct(m):
        num=m.group(1).replace(",",""); whole,_,frac = num.partition(".")
        w=_int_words(int(whole or 0))
        return (w+" "+_frac_words(frac) if frac else w)+" percent"
    def _grouped(m):
        num=m.group(0).replace(",",""); whole,_,frac = num.partition(".")
        w=_int_words(int(whole or 0))
        return w+" "+_frac_words(frac) if frac else w
    text=re.sub(r"([R$£€])\s?([\d,]+(?:\.\d+)?)", _cur, text)          # currency
    text=re.sub(r"\b(\d[\d,]*(?:\.\d+)?)\s?%", _pct, text)             # percentages
    text=re.sub(r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b", _grouped, text)   # comma-grouped numbers
    return text

def env(key):
    for line in open(REPO/".env"):
        s=line.strip()
        if s.startswith(key+"=") and not s.startswith("#"):
            return s.split("=",1)[1].strip().strip('"').strip("'")
    return None

def rp(p):
    p=pathlib.Path(p); return p if p.is_absolute() else REPO/p

def dur(path):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(path)],capture_output=True,text=True).stdout.strip())

def tts(text, cfg, mp3, key):
    body=json.dumps({"text":text,"model_id":cfg.get("model","eleven_multilingual_v2"),
        "voice_settings":cfg.get("voice_settings",DEFAULT_VOICE_SETTINGS)}).encode()
    req=urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{cfg['voice_id']}?output_format=mp3_44100_128",
        data=body, headers={"xi-api-key":key,"Content-Type":"application/json","Accept":"audio/mpeg"})
    mp3.write_bytes(urllib.request.urlopen(req,timeout=90).read())

def main():
    args=[a for a in sys.argv[1:]]
    dry = "--dry-run" in args
    cfg_path = next(a for a in args if not a.startswith("--"))
    cfg=json.load(open(rp(cfg_path)))
    # resolve a named voice preset (reference/voice-presets.json): fills voice_id/model/
    # voice_settings unless the config sets them inline. "voice_preset":"default" uses the file's default.
    pname=cfg.get("voice_preset")
    if pname:
        pf=json.load(open(REPO/".claude/skills/demo-video/reference/voice-presets.json"))
        if pname=="default": pname=pf.get("default")
        p=pf["presets"][pname]
        cfg.setdefault("voice_id",p["voice_id"])
        cfg.setdefault("model",p.get("model","eleven_multilingual_v2"))
        cfg.setdefault("voice_settings",p.get("voice_settings"))
        print(f"  voice preset: {pname} ({p.get('elevenlabs_name','?')})")
    video=rp(cfg["video"]); out=rp(cfg["out"]); vlen=dur(video)
    music=cfg.get("music","none"); duck=cfg.get("duck",True) and music!="none"; boops=cfg.get("boops",True)
    vdir=rp(cfg.get("voice_dir", video.parent/"voice")); vdir.mkdir(parents=True,exist_ok=True)

    key=env("ELEVENLABS_API_KEY")
    if not key and not dry: sys.exit("No ELEVENLABS_API_KEY in .env")
    norm=cfg.get("normalise_numbers",True)
    # cache key includes model + voice_settings so changing speed/stability/etc. regenerates
    sig=json.dumps([cfg.get("model"),cfg.get("voice_settings")],sort_keys=True)
    cues=[]
    for c in cfg["cues"]:
        spoken=normalise_for_speech(c["text"]) if norm else c["text"]
        h=hashlib.md5((cfg["voice_id"]+"|"+spoken+"|"+sig).encode()).hexdigest()[:10]
        mp3=vdir/f"tts_{h}.mp3"
        if not mp3.exists() and not dry:
            if spoken!=c["text"]: print(f"  norm: \"{c['text'][:40]}...\" -> \"{spoken[:48]}...\"")
            print(f"  TTS: \"{spoken[:50]}...\""); tts(spoken,cfg,mp3,key)
        # per-cue boop: default to global `boops`, but a cue can set "boop": false
        # (e.g. an automatic/triggered beat with no spoken command should not blip).
        # "boop_ms" places the blip independently of the narration start — use it when the
        # on-screen voice-note pill appears later than the narration (e.g. a mid-slide confirm).
        cues.append((mp3, int(c["start_ms"]), c.get("boop", True), c.get("boop_ms")))

    # boop wav (temp)
    boop=None
    if boops and not dry:
        boop=pathlib.Path(tempfile.mkstemp(suffix=".wav")[1])
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i",f"aevalsrc='{BOOP}':d=0.22:s=44100",
            "-af","highpass=f=200,volume=0.72,afade=t=out:st=0.16:d=0.06",str(boop)],
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

    # sfx: synth the swoosh once if any sfx entry needs it
    sfx_list=cfg.get("sfx",[])
    swoosh=None
    if any(s.get("type")=="swoosh" for s in sfx_list) and not dry:
        swoosh=pathlib.Path(tempfile.mkstemp(suffix=".wav")[1])
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i",SWOOSH_SRC,"-af",SWOOSH_AF,str(swoosh)],
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

    # assemble ffmpeg inputs
    inputs=["-i",str(video)]; idx=1; fc=[]
    bed_in=None
    if music!="none":
        inputs+=["-f","lavfi","-i",f"aevalsrc='{MUSIC_EXPR[music]}':d={vlen+0.5:.2f}:s=44100"]
        af=MUSIC_AF[music].format(vol=cfg.get("music_volume",0.55), fo=max(0.0,vlen-3.4))
        fc.append(f"[{idx}]{af}[bed]"); bed_in="[bed]"; idx+=1
    vlabels=[]
    for i,(mp3,start,_bp,_bm) in enumerate(cues):
        inputs+=["-i",str(mp3)]; fc.append(f"[{idx}]adelay={start}:all=1[v{i}]"); vlabels.append(f"[v{i}]"); idx+=1
    fc.append("".join(vlabels)+f"amix=inputs={len(vlabels)}:duration=longest:normalize=0,apad=whole_dur={vlen+0.5:.2f}[voc]")
    music_lab=bed_in; voice_lab="[voc]"
    if duck:
        fc.append("[voc]asplit=2[vk][vm]")
        fc.append(f"{bed_in}[vk]sidechaincompress=threshold=0.03:ratio=12:attack=12:release=350[bedd]")
        music_lab="[bedd]"; voice_lab="[vm]"
    boop_labs=[]
    if boop:
        for i,(_,start,bp,bm) in enumerate(cues):
            if not bp: continue
            bstart=int(bm) if bm is not None else max(0,start-200)
            inputs+=["-i",str(boop)]; fc.append(f"[{idx}]adelay={max(0,bstart)}:all=1[bp{i}]"); boop_labs.append(f"[bp{i}]"); idx+=1
    sfx_labs=[]
    for j,s in enumerate(sfx_list):
        src = rp(s["file"]) if s.get("file") else swoosh
        if src is None: continue
        if not dry and not pathlib.Path(src).exists():
            print(f"  WARN sfx source missing, skipping: {src}"); continue
        inputs+=["-i",str(src)]
        fc.append(f"[{idx}]adelay={max(0,int(s.get('ms',0)))}:all=1,volume={s.get('gain',1.0)}[sfx{j}]")
        sfx_labs.append(f"[sfx{j}]"); idx+=1
    mixparts=([music_lab] if music_lab else [])+[voice_lab]+boop_labs+sfx_labs
    fc.append("".join(mixparts)+f"amix=inputs={len(mixparts)}:duration=longest:normalize=0[mx]")
    fc.append("[mx]alimiter=limit=0.95[aout]")

    cmd=["ffmpeg","-y"]+inputs+["-filter_complex",";".join(fc),"-map","0:v:0","-map","[aout]",
         "-c:v","copy","-c:a","aac","-b:a","192k","-shortest",str(out)]
    if dry:
        print("DRY RUN — ffmpeg command:\n"," ".join(f'"{a}"' if " " in a else a for a in cmd)); return
    print("Muxing audio ->", out)
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if boop: boop.unlink(missing_ok=True)
    if swoosh: swoosh.unlink(missing_ok=True)
    print(f"Done: {out}  ({dur(out):.1f}s)")

if __name__=="__main__":
    main()
