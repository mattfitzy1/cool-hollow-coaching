---
name: watch
description: "Watch a video (YouTube, Instagram, TikTok, Loom, X, Vimeo, or a local file) and answer questions about it. Downloads with yt-dlp, extracts frames with ffmpeg, pulls the transcript from captions (or Whisper API fallback), and hands frames plus transcript to Claude so it can actually see what is on screen, not just read the words. Use when the user pastes a video URL or local path and wants it watched, summarised, or queried. Trigger words: watch this video, what happens in this clip, analyse this reel, break down this hook, look at this screen recording."
argument-hint: "<video-url-or-path> [question]"
allowed-tools: Bash, Read, AskUserQuestion
user-invocable: true
---

# /watch — Claude watches a video

You do not have a native video input. This skill gives you one. A Python script downloads the video, extracts frames as JPEGs, gets a timestamped transcript (native captions first, then Whisper API as fallback), and prints frame paths. You then Read each frame to see the images and combine them with the transcript to answer the user.

This is the layer above `/assess-video`. `/assess-video` reads the transcript only and scores it against priorities. `/watch` actually sees the screen, which matters for graphs, demos, UI walkthroughs, and reels where half the meaning is visual and never spoken.

> Vendored from `github.com/bradautomates/claude-video` (MIT, by Bradley Bonanno) on 1 June 2026. Pure Python stdlib. The upstream SessionStart hook and plugin wrapper were dropped; this runs only when invoked. Scripts reviewed before vendoring: no shell injection (all subprocess calls are list-form), only extracted audio leaves the machine (to Groq/OpenAI, captions-missing case only), no key logging.

## Conventions for this workspace

- Python interpreter: `.venv-command/bin/python3` (stdlib only, so the version does not matter, but stay consistent with the rest of the workspace).
- Run all commands from the workspace root. Script paths are `.claude/skills/watch/scripts/...`.
- API key for the Whisper fallback lives in `~/.config/watch/.env` OR the workspace `.env` (the script checks both). Most YouTube videos have free captions and need no key at all.

## Step 0 — Setup preflight (run once per session, silent on success)

```bash
.venv-command/bin/python3 .claude/skills/watch/scripts/setup.py --check
```

This is a sub-100ms lookup. On exit 0 it prints nothing — proceed to Step 1 without comment. Do not announce "setup is complete".

On non-zero exit:

| Exit | Meaning | Action |
|------|---------|--------|
| 2 | Missing binaries (ffmpeg / ffprobe / yt-dlp) | Run the installer (below) |
| 3 | No Whisper API key | Captions still work. Only set up a key if a video lacks captions. |
| 4 | Both missing | Run the installer, then handle the key as in row 3 |

Installer (idempotent, auto-installs ffmpeg and yt-dlp via brew on macOS):

```bash
.venv-command/bin/python3 .claude/skills/watch/scripts/setup.py
```

If a key is needed (only when a target video has no captions): ask the user via AskUserQuestion whether he has a Groq key (preferred, free tier, faster) or an OpenAI key, then write the matching `GROQ_API_KEY=...` or `OPENAI_API_KEY=...` line into `~/.config/watch/.env`. Never paste the key into chat. If he does not want Whisper, run with `--no-whisper` and tell him captionless videos come back frames-only.

Within one session, skip Step 0 on follow-up `/watch` calls once `--check` returned 0.

## When to use

- the user pastes a video URL (YouTube, Vimeo, X, TikTok, Instagram, Twitch clip, Loom, most of the 1000-plus yt-dlp sites) and asks about it.
- He points at a local file (`.mp4`, `.mov`, `.mkv`, `.webm`) and asks about it.
- He types `/watch <url-or-path> [question]`.

Note on Instagram: yt-dlp supports it but IG is the flakiest source and sometimes needs login cookies. If an IG reel fails to download, say so plainly rather than retrying in a loop.

## Recommended limits

- Best accuracy on videos under 10 minutes. Frame coverage scales inversely with length.
- Hard caps: 100 frames total, 2 fps. The script targets a frame budget by duration:
  - 30s and under: up to ~30 frames
  - 30s to 1min: ~40 frames
  - 1 to 3min: ~60 frames
  - 3 to 10min: ~80 frames
  - over 10min: 100 frames, sparsely spaced (a warning is printed)
- For a long video, prefer asking which section he cares about, then run focused (see below) rather than burning tokens on a sparse full scan.

## How to invoke

Step 1 — parse the input. Separate the video source from any question.
`/watch https://youtu.be/abc what language is this in?` becomes source `https://youtu.be/abc`, question `what language is this in?`.

Step 2 — run the watch script. Pass the source verbatim inside quotes:

```bash
.venv-command/bin/python3 .claude/skills/watch/scripts/watch.py "<source>"
```

Optional flags:
- `--start T` / `--end T` — focus on a section. Accepts `SS`, `MM:SS`, or `HH:MM:SS`. Denser frame budget when set.
- `--max-frames N` — lower the cap for a tighter token budget (e.g. `--max-frames 40`).
- `--resolution W` — frame width in px (default 512; bump to 1024 only when on-screen text must be read).
- `--fps F` — override auto-fps (clamped to 2 fps).
- `--whisper groq|openai` — force a backend.
- `--no-whisper` — disable the Whisper fallback (frames-only if no captions).
- `--out-dir DIR` — keep working files somewhere specific.

### Focusing on a section

When the question is about a specific moment ("what happens at 2:30?", "the first 10 seconds", "the last 30 seconds"), pass `--start` and `--end`. Focused mode uses a denser budget and auto-filters the transcript to the same window. Frame timestamps stay absolute (real video timeline). This is the right call for any named moment, and for any video over ~10 minutes where the question is about one part.

```bash
# Last 10 seconds of a 1 minute clip
.venv-command/bin/python3 .claude/skills/watch/scripts/watch.py video.mp4 --start 50 --end 60

# Zoom into 2:15 to 2:45
.venv-command/bin/python3 .claude/skills/watch/scripts/watch.py "$URL" --start 2:15 --end 2:45
```

Step 3 — Read every frame path the script lists. The Read tool renders JPEGs as images. Read all frames in a single message (parallel Read calls) so you see them together. Frames are chronological with a `t=MM:SS` absolute timestamp.

Step 4 — answer. You now have two evidence streams: frames (what is on screen at each timestamp) and transcript (what is said). The report header shows the transcript source (`captions`, or `whisper (groq)` / `whisper (openai)`). Answer the question directly, citing timestamps. If no question was asked, summarise structure, key moments, notable visuals, and spoken content.

Step 5 — clean up. The script prints a working directory. If the user is unlikely to ask follow-ups, delete it with `rm -rf <dir>`. If he might, leave it so you can answer without re-running.

## Transcription strategy

1. Native captions (free, preferred) — yt-dlp pulls manual or auto subtitles when the source has them. Covers most public YouTube.
2. Whisper fallback (only when captions are missing) — extracts mono 16kHz audio and uploads to Groq `whisper-large-v3` (preferred, cheaper, faster) or OpenAI `whisper-1`. Note: Groq is groq.com, a different service from xAI's Grok. The 25 MB upload limit means very long captionless videos need a `--start`/`--end` window.

## Token efficiency

Tokens go mostly on frames. Roughly 80 frames at 512px is 50 to 80k image tokens; the transcript is cheap. `--resolution 1024` roughly quadruples image tokens per frame, so only use it when text must be read. If you already watched a video this session, do not re-run for a follow-up — answer from what is in context.

## Failure modes

- Preflight failed: run the installer command above.
- No transcript: captions missing and no Whisper key (or `--no-whisper`). Proceed frames-only and say so.
- Long-video warning printed: acknowledge it and offer a focused re-run.
- Download fails (login-required or region-locked): tell the user plainly, do not retry in a loop.
- Whisper fails: error goes to stderr (bad key, rate limit, or 25 MB cap). Retry with the other backend if one key is set.

## Bundled scripts

`watch.py` (entry point), `download.py` (yt-dlp wrapper), `frames.py` (ffmpeg frame extraction), `transcribe.py` (caption parsing), `whisper.py` (Groq/OpenAI clients), `setup.py` (preflight plus installer). LICENSE is the upstream MIT licence.
