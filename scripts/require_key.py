#!/usr/bin/env python3
"""
require_key.py - the "no dead skills" engine for your AIOS.

Every external-tool skill calls one line before it does any work:

    from require_key import ensure_ready
    ensure_ready("higgsfield")

`ensure_ready(tool)` makes sure the tool is genuinely usable, and if it is not,
it prints a calm, plain-English walkthrough instead of crashing. The promise is:
you never hit a cryptic failure. A skill you have not connected yet turns
itself into a friendly setup guide.

What it checks, in order (plan section 4):

  Layer 0  software first - the binaries and runtimes the tool needs
           (Homebrew, Node, ffmpeg, the higgsfield CLI, wrangler). On a fresh
           Mac these are absent, and a tool with a valid key but no binary is
           still a dead skill, so this runs BEFORE any key check.

  Then by type:
    key   - the .env slot is non-empty AND a live verify passes
    auth  - a CLI status check passes (interactive login, no key to paste)
    mcp   - the MCP's own status tool reports connected

If everything is ready it returns silently and the skill carries on. If not, it
prints the standard walkthrough (what to sign up for, the exact link + click
path, where the key goes in .env, then verify) and returns False so the caller
stops. The key is NEVER echoed back to the chat: you paste it into .env, the
helper reads the file, never the conversation.

Spend cap: for Higgsfield, ensure_spend(tool, projected_credits) keeps a running
monthly tally in data/hf_spend.json, adds the projected cost of the next call,
and HARD-REFUSES if it would push past HF_MONTHLY_CAP. A convention is not a cap
for a non-technical user on bypass, so the cap is load-bearing here.

Stdlib only. No third-party imports.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "data" / "skill_registry.json"
ENV_PATH = ROOT / ".env"
HF_SPEND_PATH = ROOT / "data" / "hf_spend.json"
SETUP_STATE_PATH = ROOT / "data" / "setup_state.json"  # records what was skipped


# ---------------------------------------------------------------------------
# .env loading (same minimal loader the other scripts use - stdlib only)
# ---------------------------------------------------------------------------

def _load_dotenv(path: Path | None = None) -> None:
    """Read KEY=VALUE lines from .env into os.environ. Skips comments/blanks.
    Does not override values already set in the environment."""
    p = path or ENV_PATH
    if not p.exists():
        return
    for raw in p.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


_load_dotenv()


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _c(text: str, code: str) -> str:
    """Colour text only when stdout is a real terminal (so logs stay clean)."""
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def green(t: str) -> str:
    return _c(t, "32")


def amber(t: str) -> str:
    return _c(t, "33")


def red(t: str) -> str:
    return _c(t, "31")


def bold(t: str) -> str:
    return _c(t, "1")


def _load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {}
    try:
        return json.loads(REGISTRY_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


# A few tools name their .env slot off the {TOOL}_API_KEY convention. Cloudflare
# uses a *token* (and a second account-ID var); Gemini's slot is GEMINI_API_KEY
# which the convention already produces. Listed here so a missing `env:` in a
# manifest still resolves to the right slot.
_ENV_SLOT_ALIASES = {
    "cloudflare": "CLOUDFLARE_API_TOKEN",
}


def _env_slot_for(entry: dict) -> str | None:
    """Work out which .env variable holds this tool's key.

    Preference order: an explicit `env:` field in the manifest; then a known
    alias (e.g. cloudflare -> CLOUDFLARE_API_TOKEN); else the convention
    {TOOL}_API_KEY. Login (auth) and mcp tools have no key slot.
    """
    if entry.get("type") not in ("key",):
        return None
    explicit = entry.get("env")
    if explicit:
        return explicit
    tool = entry.get("tool", "")
    if not tool:
        return None
    if tool in _ENV_SLOT_ALIASES:
        return _ENV_SLOT_ALIASES[tool]
    return f"{tool.upper()}_API_KEY"


def _env_value(name: str) -> str:
    """Read a value, re-loading .env each call so a key pasted mid-session is
    seen without restarting."""
    _load_dotenv()
    return (os.environ.get(name) or "").strip()


# ---------------------------------------------------------------------------
# Setup state (skip-awareness)
# ---------------------------------------------------------------------------

def _load_setup_state() -> dict:
    if not SETUP_STATE_PATH.exists():
        return {}
    try:
        return json.loads(SETUP_STATE_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _was_skipped(tool: str) -> bool:
    return _load_setup_state().get(tool, {}).get("status") == "skipped"


def mark_skipped(tool: str) -> None:
    """Record that you chose to skip a tool, so the next time the walkthrough
    can tie back to that instead of acting like it forgot."""
    state = _load_setup_state()
    state[tool] = {"status": "skipped", "when": date.today().isoformat()}
    SETUP_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETUP_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def mark_connected(tool: str) -> None:
    state = _load_setup_state()
    state[tool] = {"status": "connected", "when": date.today().isoformat()}
    SETUP_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETUP_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


# ---------------------------------------------------------------------------
# Layer 0 - software prerequisites (binaries + runtimes)
# ---------------------------------------------------------------------------

# How to install each piece of software you might be missing. Keyed by the
# binary name. Homebrew is the foundation everything else installs through; Node
# goes via Homebrew (not nvm) deliberately, because nvm is per-user shell config
# a non-technical user will fumble.
SOFTWARE_HELP = {
    "brew": {
        "label": "Homebrew (the Mac software installer)",
        "how": (
            'Paste this one line into Terminal and press return:\n'
            '    /bin/bash -c "$(curl -fsSL '
            'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"\n'
            "Follow its prompts. This is the official installer."
        ),
    },
    "node": {
        "label": "Node (runs nano-banana and wrangler)",
        "how": "Once Homebrew is in, run:\n    brew install node",
    },
    "ffmpeg": {
        "label": "ffmpeg (stitches video clips together)",
        "how": "    brew install ffmpeg",
    },
    "wrangler": {
        "label": "wrangler (deploys your app to Cloudflare)",
        "how": "    npm i -g wrangler",
    },
    "higgsfield": {
        "label": "the Higgsfield CLI (the paid AI image/video engine)",
        "how": (
            "Install the Higgsfield CLI per its docs, then fetch its global\n"
            "skills folder into ~/.claude/higgsfield-skills/. The /setup wizard\n"
            "does this for you when you choose to turn Higgsfield on."
        ),
    },
}

# Ordering so the walkthrough always installs foundations first.
_SOFTWARE_ORDER = ["brew", "node", "ffmpeg", "wrangler", "higgsfield"]


def _have_bin(name: str) -> bool:
    return shutil.which(name) is not None


def _missing_software(entry: dict) -> list[str]:
    """Return the list of required binaries/runtimes that are not installed,
    in install order (foundations first)."""
    needed: list[str] = []
    for b in (entry.get("requires_bin") or []):
        if b and b not in needed:
            needed.append(b)
    for r in (entry.get("requires_runtime") or []):
        if r and r not in needed:
            needed.append(r)
    missing = [b for b in needed if not _have_bin(b)]
    # If anything is missing and brew is also missing, surface brew first.
    if missing and not _have_bin("brew") and "brew" not in missing:
        missing.insert(0, "brew")
    # Sort by the known install order; unknowns go last in their original order.
    def sort_key(name: str) -> int:
        return _SOFTWARE_ORDER.index(name) if name in _SOFTWARE_ORDER else 99
    return sorted(missing, key=sort_key)


def _print_software_walkthrough(tool: str, missing: list[str]) -> None:
    print()
    print(amber(f"Before {tool} can run, a couple of pieces of software need "
                "installing on this Mac."))
    print("This is a one-time thing. I'll list exactly what to paste; nothing "
          "here costs money.")
    print()
    for i, b in enumerate(missing, 1):
        info = SOFTWARE_HELP.get(b, {"label": b, "how": f"Install {b}."})
        print(bold(f"  {i}. {info['label']}"))
        for ln in info["how"].splitlines():
            print(f"     {ln}")
        print()
    print("Once those are installed, ask me again and we'll carry on with the "
          "key step.")
    print(amber("Stuck? Send your builder the output of /doctor and they'll point "
                "you to the exact step."))
    print()


# ---------------------------------------------------------------------------
# Verification per type
# ---------------------------------------------------------------------------

def _run_verify_command(cmd: str) -> bool:
    """Run a verify command string and return True on exit 0.

    Some manifests carry a runnable shell command (e.g. the cloudflare verify
    'python scripts/cloudflare_pages.py verify'); others carry a human
    description (e.g. 'Publer API: list workspaces/accounts'). We only execute
    things that look like a real command (start with python / a script path /
    a known binary). Descriptive strings are treated as "can't auto-verify",
    in which case a non-empty key is accepted as best-effort and the skill's own
    call will surface a real failure honestly.
    """
    cmd = (cmd or "").strip()
    if not cmd:
        return True  # nothing to run; treat slot-non-empty as good enough
    first = cmd.split()[0].lower()
    runnable = (
        first in ("python", "python3", "node", "wrangler", "higgsfield")
        or first.endswith(".py")
        or first.startswith("scripts/")
        or _have_bin(first)
    )
    if not runnable:
        return True  # descriptive verify; defer to the skill's own real call
    try:
        proc = subprocess.run(
            cmd, shell=True, cwd=str(ROOT),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=60,
        )
        return proc.returncode == 0
    except (subprocess.SubprocessError, OSError):
        return False


def _verify_auth(entry: dict) -> bool:
    """Login tools: run the CLI status check (e.g. 'higgsfield account status')."""
    cmd = (entry.get("auth") or entry.get("verify") or "").strip()
    if not cmd:
        return False
    first = cmd.split()[0]
    if not _have_bin(first):
        return False
    try:
        proc = subprocess.run(
            cmd, shell=True, cwd=str(ROOT),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=60,
        )
        return proc.returncode == 0
    except (subprocess.SubprocessError, OSError):
        return False


# ---------------------------------------------------------------------------
# Walkthroughs
# ---------------------------------------------------------------------------

def _skip_preamble(tool: str, entry: dict) -> None:
    """If you skipped this tool earlier, open by tying back to that so it
    feels continuous, not like the system forgot."""
    if _was_skipped(tool):
        reason = entry.get("plan", "")
        cost = f" ({reason})" if reason else ""
        print(amber(f"You skipped {entry.get('account', tool)} earlier, that's "
                    f"fine. You only need it now because you've asked for "
                    f"something it powers."))
        print(f"Connect it{cost} now, or skip again and I'll do what I can "
              "without it.")
        print()


def _print_key_walkthrough(tool: str, entry: dict, slot: str) -> None:
    _skip_preamble(tool, entry)
    print(amber(f"{entry.get('account', tool)} isn't connected yet. Here's how, "
                "it takes a minute:"))
    print()
    if entry.get("plan"):
        print(f"  What it is: {entry.get('account', tool)} - {entry['plan']}")
    if entry.get("signup"):
        print(f"  1. Sign up / open: {entry['signup']}")
    where = entry.get("where") or f"paste the key into {slot} in your .env file"
    print(f"  2. {where}")
    print(f"  3. Paste it into {bold(slot)}= in your {bold('.env')} file (in this "
          "folder), then save.")
    print(f"  4. Tell me 'done' and I'll check it.")
    print()
    if entry.get("spend"):
        print(f"  Cost note: {entry['spend']}")
    print("  Your key stays in .env. I read it from the file, never from the "
          "chat, and I never print it back.")
    print(amber("  Stuck? Send your builder the output of /doctor and they'll "
                "point you to the exact step."))
    print()


def _print_auth_walkthrough(tool: str, entry: dict) -> None:
    _skip_preamble(tool, entry)
    print(amber(f"{entry.get('account', tool)} isn't connected yet."))
    print()
    if entry.get("plan"):
        print(f"  What it is: {entry.get('account', tool)} - {entry['plan']}")
    if entry.get("spend"):
        print(f"  {entry['spend']}")
    if entry.get("signup"):
        print(f"  1. {entry['signup']}")
    login_cmd = entry.get("auth") or "log in via its CLI"
    print(f"  2. This one is a login, not a key to paste. Run: {bold(login_cmd)}")
    print(f"  3. Tell me 'done' and I'll check it.")
    print()
    print(amber("  Stuck? Send your builder the output of /doctor and they'll "
                "point you to the exact step."))
    print()


def _print_mcp_walkthrough(tool: str, entry: dict) -> None:
    _skip_preamble(tool, entry)
    print(amber(f"{entry.get('account', tool)} (an MCP tool) isn't connected "
                "yet."))
    print()
    if entry.get("signup"):
        print(f"  1. {entry['signup']}")
    slot = entry.get("env") or "GEMINI_API_KEY"
    print(f"  2. Paste your key into {bold(slot)}= in {bold('.env')}, then save.")
    print(f"  3. Tell me 'done'. I'll confirm the MCP reports connected via its "
          "own status check before using it.")
    print()
    print(amber("  Stuck? Send your builder the output of /doctor and they'll "
                "point you to the exact step."))
    print()


# ---------------------------------------------------------------------------
# The main entry point
# ---------------------------------------------------------------------------

def ensure_ready(tool: str, *, quiet: bool = False) -> bool:
    """Make sure `tool` is usable. Returns True if ready (caller proceeds),
    False if not (caller stops; a walkthrough has been printed).

    Order: registry lookup -> Layer 0 software -> credential/login/mcp + verify.
    Never raises for the "not set up" case; it guides instead.
    """
    registry = _load_registry()
    entry = registry.get(tool)

    if entry is None:
        # Unknown tool. Don't block work over a registry gap; warn quietly.
        if not quiet:
            print(amber(f"(heads up: '{tool}' isn't in the skill registry yet; "
                        "run scripts/build_registry.py. Carrying on.)"))
        return True

    # --- Layer 0: software first -------------------------------------------
    missing = _missing_software(entry)
    if missing:
        if not quiet:
            _print_software_walkthrough(tool, missing)
        return False

    ttype = entry.get("type", "key")

    # --- key tools ----------------------------------------------------------
    if ttype == "key":
        slot = _env_slot_for(entry) or f"{tool.upper()}_API_KEY"
        if not _env_value(slot):
            if not quiet:
                _print_key_walkthrough(tool, entry, slot)
            return False
        if not _run_verify_command(entry.get("verify", "")):
            if not quiet:
                print(amber(f"{entry.get('account', tool)}: I found a key in "
                            f"{slot} but it didn't verify. Double-check it's the "
                            "right key (no spaces), then tell me 'done'."))
                _print_key_walkthrough(tool, entry, slot)
            return False
        mark_connected(tool)
        return True

    # --- login (auth) tools -------------------------------------------------
    if ttype == "auth":
        if not _verify_auth(entry):
            if not quiet:
                _print_auth_walkthrough(tool, entry)
            return False
        mark_connected(tool)
        return True

    # --- mcp tools ----------------------------------------------------------
    if ttype == "mcp":
        # The MCP status tool (e.g. nano-banana's get_configuration_status) is
        # only callable by Claude, not from this Python process. We do the part
        # we can check from here - that the underlying key slot is present - and
        # hand the connected-check to the skill via its MCP status call.
        slot = entry.get("env") or "GEMINI_API_KEY"
        if not _env_value(slot):
            if not quiet:
                _print_mcp_walkthrough(tool, entry)
            return False
        # Key present; the skill confirms the MCP itself reports connected.
        return True

    # Unknown type - be permissive rather than block real work.
    return True


# ---------------------------------------------------------------------------
# Higgsfield spend cap (load-bearing, not a reminder)
# ---------------------------------------------------------------------------

def _current_month() -> str:
    return date.today().strftime("%Y-%m")


def _load_spend() -> dict:
    if not HF_SPEND_PATH.exists():
        return {"month": _current_month(), "credits": 0.0}
    try:
        data = json.loads(HF_SPEND_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {"month": _current_month(), "credits": 0.0}
    # Roll the tally over at the start of a new month.
    if data.get("month") != _current_month():
        return {"month": _current_month(), "credits": 0.0}
    return data


def _save_spend(data: dict) -> None:
    HF_SPEND_PATH.parent.mkdir(parents=True, exist_ok=True)
    HF_SPEND_PATH.write_text(json.dumps(data, indent=2) + "\n")


def _hf_cap() -> float:
    raw = _env_value("HF_MONTHLY_CAP")
    try:
        return float(raw) if raw else 30.0
    except ValueError:
        return 30.0


def current_spend() -> float:
    """This month's Higgsfield credit tally so far."""
    return float(_load_spend().get("credits", 0.0))


def ensure_spend(projected_credits: float, *, tool: str = "higgsfield",
                 quiet: bool = False) -> bool:
    """Hard spend-cap gate. Call BEFORE spending Higgsfield credits.

    Adds `projected_credits` to this month's running tally and refuses if the
    total would exceed HF_MONTHLY_CAP. Returns True if the call is allowed
    (and the caller should then record it with record_spend), False if it would
    breach the cap (a refusal message has been printed).
    """
    spent = current_spend()
    cap = _hf_cap()
    projected = float(projected_credits or 0)
    if spent + projected > cap:
        if not quiet:
            print()
            print(red(f"Holding off: this would spend about {projected:g} "
                      f"credits and push this month's Higgsfield total to "
                      f"{spent + projected:g}, over your cap of {cap:g}."))
            print(f"You've used {spent:g} of {cap:g} credits so far this month.")
            print("Nothing has been spent. If you want to go ahead, raise "
                  f"{bold('HF_MONTHLY_CAP')} in your .env and ask me again.")
            print()
        return False
    return True


def record_spend(credits: float, *, note: str = "") -> float:
    """Add credits actually spent to the running monthly tally. Returns the new
    total. Call this AFTER a Higgsfield call succeeds."""
    data = _load_spend()
    data["credits"] = round(float(data.get("credits", 0.0)) + float(credits or 0), 2)
    data["month"] = _current_month()
    log = data.setdefault("log", [])
    log.append({"when": date.today().isoformat(), "credits": float(credits or 0),
                "note": note})
    _save_spend(data)
    return data["credits"]


# ---------------------------------------------------------------------------
# CLI (handy for testing / for /doctor to call)
# ---------------------------------------------------------------------------

def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: require_key.py <tool> | spend [projected] | tally")
        return 2
    cmd = argv[1]
    if cmd == "spend":
        projected = float(argv[2]) if len(argv) > 2 else 0.0
        ok = ensure_spend(projected)
        print(f"allowed={ok} (spent {current_spend():g} / cap {_hf_cap():g})")
        return 0 if ok else 1
    if cmd == "tally":
        print(f"{current_spend():g} credits used this month "
              f"(cap {_hf_cap():g})")
        return 0
    ready = ensure_ready(cmd)
    print(f"\n{green('ready') if ready else amber('needs setup')}: {cmd}")
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
