#!/usr/bin/env python3
"""doctor.py - Cool Hollow Coaching AIOS connection check (read-only).

Prints a green/amber/red table, one row per external tool, grouped by
bundle in cost order (Content, Creative, App, Business). For each tool it
shows the account name, the software-and-credential state, and a one-line
next step for anything that is not connected yet.

This is deliberately read-only: it never writes a file, never installs
anything, never commits, never touches her .env beyond reading it. It only
reports. The /setup wizard is the thing that actually connects tools.

Every row is generated from data/skill_registry.json, which is built from
the SKILL.md `requires:` manifests by build_registry.py. Nothing here is
hand-maintained, so adding a new external skill makes it appear here
automatically.

Tone rule (matters for a non-technical user with admin anxiety): amber and
red mean "not connected yet", never "you did something wrong". The closing
line always reassures.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
# scripts/doctor.py -> repo root is one level up.
ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "skill_registry.json"
ENV_FILE = ROOT / ".env"

# ── Display ────────────────────────────────────────────────────────────
GREEN = "🟢"
AMBER = "🟡"
RED = "🔴"

# Bundles shown in cost order (cheapest / highest day-one value first).
BUNDLE_ORDER = ["content", "creative", "app", "business"]
BUNDLE_TITLES = {
    "content": "CONTENT & SOCIAL",
    "creative": "CREATIVE STUDIO",
    "app": "APP & WEB",
    "business": "BUSINESS",
}


# ── .env reading (no shell-out, no secret echo) ────────────────────────
def read_env() -> dict[str, str]:
    """Read .env into a dict. Values are never printed back."""
    values: dict[str, str] = {}
    if not ENV_FILE.exists():
        return values
    for raw in ENV_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip().strip('"').strip("'")
    return values


# ── Registry loading ───────────────────────────────────────────────────
def load_registry() -> list[dict] | None:
    """Load the generated registry. Returns None if it has not been built yet.

    build_registry.py emits an object keyed by tool name. We also tolerate a
    plain list, or an object with a "tools" key, so a schema tweak upstream
    does not silently break the health check.
    """
    if not REGISTRY.exists():
        return None
    try:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "tools" in data and isinstance(data["tools"], list):
            return data["tools"]
        # Dict keyed by tool name -> flatten to a list of entries, making sure
        # each entry carries its own "tool" name even if the value omitted it.
        entries: list[dict] = []
        for key, val in data.items():
            if isinstance(val, dict):
                val.setdefault("tool", key)
                entries.append(val)
        return entries
    return []


# ── Prerequisite (software) check - Layer 0 ────────────────────────────
def bins_present(entry: dict) -> tuple[bool, list[str]]:
    """Are all required binaries on PATH? Returns (ok, missing_list)."""
    needed = list(entry.get("requires_bin") or []) + list(
        entry.get("requires_runtime") or []
    )
    missing = [b for b in needed if shutil.which(b) is None]
    return (not missing, missing)


# ── Credential check ───────────────────────────────────────────────────
def env_slots(entry: dict) -> list[str]:
    """The .env slot name(s) a key tool needs.

    The registry names the primary slot in `env` (a string) or `env_keys`
    (a list). If neither is present, fall back to the {TOOL}_API_KEY
    convention. Cloudflare needs its account ID too, so we add the matching
    *_ACCOUNT_ID slot whenever a *_API_TOKEN slot is required.
    """
    slots: list[str] = []
    raw = entry.get("env_keys") or entry.get("env")
    if isinstance(raw, str):
        slots = [raw]
    elif isinstance(raw, list):
        slots = list(raw)
    # Otherwise, sniff the named slot out of the "where" instruction
    # (e.g. "Paste into GEMINI_API_KEY in .env" -> GEMINI_API_KEY).
    if not slots:
        where = entry.get("where") or ""
        found = re.findall(r"\b([A-Z][A-Z0-9]+_(?:API_KEY|API_TOKEN|ACCOUNT_ID|KEY|TOKEN))\b", where)
        slots = list(dict.fromkeys(found))  # de-dupe, keep order
    if not slots:
        tool = (entry.get("tool") or "").upper().replace("-", "_")
        if tool:
            slots = [f"{tool}_API_TOKEN" if tool == "CLOUDFLARE" else f"{tool}_API_KEY"]
    # Cloudflare's deploy path also needs the account ID.
    extra = []
    for s in slots:
        if s.endswith("_API_TOKEN"):
            extra.append(s.replace("_API_TOKEN", "_ACCOUNT_ID"))
    return slots + extra


def env_slot_filled(entry: dict, env: dict[str, str]) -> bool:
    """For key tools: is every required .env slot non-empty?"""
    slots = env_slots(entry)
    if not slots:
        return False
    return all(env.get(s, "").strip() for s in slots)


# A verify is only run if it looks like an actual command. Some manifests
# carry a human-readable description ("Publer API: list workspaces/accounts")
# instead of a runnable command; those must NOT be shelled out.
_RUNNABLE_PREFIXES = ("python", "python3", "higgsfield", "wrangler", "node", "npx", "./", "bash", "sh ")


def is_runnable(cmd: str | list[str]) -> bool:
    if isinstance(cmd, list):
        return bool(cmd)
    if not isinstance(cmd, str) or not cmd.strip():
        return False
    first = cmd.strip()
    return first.startswith(_RUNNABLE_PREFIXES)


def run_verify(cmd: str | list[str]) -> bool:
    """Run a verify command quietly. True iff exit 0.

    Never prints stdout/stderr (could contain account detail). Times out
    fast so /doctor stays snappy and never hangs a non-technical user.
    Only runs commands that look runnable; descriptive verify strings
    return False here so the caller falls back to the env-slot signal.
    """
    if not is_runnable(cmd):
        return False
    try:
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            cwd=ROOT,
            capture_output=True,
            timeout=20,
            env={**os.environ},
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return False


# ── Status resolution per tool ─────────────────────────────────────────
def resolve(entry: dict, env: dict[str, str]) -> dict:
    """Resolve one tool to a coloured row.

    State machine:
      - software missing  -> amber "needs install"
      - credential missing:
            optional tool  -> amber "set up when you want it"
            required tool  -> red   "needs connecting"
      - credential present but live verify fails -> amber "almost there"
      - everything verifies -> green
    """
    account = entry.get("account") or entry.get("tool") or "tool"
    # Normalise type: the registry sometimes carries a trailing "# key|auth|mcp"
    # comment after the value, so take the first token only.
    ttype = (entry.get("type") or "key").split()[0].split("#")[0].strip().lower()
    optional = bool(entry.get("optional"))
    bundle = (entry.get("bundle") or "business").lower()

    # Layer 0 - software first.
    soft_ok, missing_bins = bins_present(entry)
    if not soft_ok:
        nxt = entry.get("setup_hint") or (
            f"run /setup {bundle} to install {', '.join(missing_bins)}"
        )
        return {
            "icon": AMBER,
            "account": account,
            "state": "needs install",
            "next": nxt,
            "ready": False,
        }

    # Credential layer, by type.
    if ttype == "key":
        if not env_slot_filled(entry, env):
            if optional:
                return {
                    "icon": AMBER,
                    "account": account,
                    "state": "set up when you want it",
                    "next": entry.get("setup_hint")
                    or f"run /setup {bundle} to connect it",
                    "ready": False,
                }
            return {
                "icon": RED,
                "account": account,
                "state": "not connected yet",
                "next": entry.get("setup_hint")
                or f"run /setup {bundle} to connect it",
                "ready": False,
            }
        # Slot filled. Try the live verify if it's a runnable command.
        verify = entry.get("verify", "")
        if is_runnable(verify):
            if run_verify(verify):
                return {
                    "icon": GREEN,
                    "account": account,
                    "state": entry.get("connected_note") or "connected",
                    "next": "",
                    "ready": True,
                }
            return {
                "icon": AMBER,
                "account": account,
                "state": "almost there",
                "next": "key is in, but the check did not pass yet - run /doctor again or /setup "
                + bundle,
                "ready": False,
            }
        # No runnable live check (descriptive verify). The key is present, so
        # treat it as connected; the skill's own ensure_ready does the live
        # check when she actually uses it.
        return {
            "icon": GREEN,
            "account": account,
            "state": entry.get("connected_note") or "connected",
            "next": "",
            "ready": True,
        }

    if ttype == "auth":
        # Login tools (e.g. Higgsfield). Honour a dormant-until-paid flag:
        # the manifest may name one (enable_flag), else fall back to the
        # conventional {TOOL}_ENABLED slot. Higgsfield ships
        # HIGGSFIELD_ENABLED=false so she is never pushed into a paid bill.
        tool_up = (entry.get("tool") or "").upper().replace("-", "_")
        enable_flag = entry.get("enable_flag") or (f"{tool_up}_ENABLED" if tool_up else "")
        if enable_flag and enable_flag in env and env.get(
            enable_flag, ""
        ).lower() not in ("true", "1", "yes"):
            return {
                "icon": AMBER,
                "account": account,
                "state": "needs install",
                "next": entry.get("setup_hint")
                or f"run /setup {bundle} when you want it (paid plan first)",
                "ready": False,
            }
        if run_verify(entry.get("verify", "")):
            return {
                "icon": GREEN,
                "account": account,
                "state": entry.get("connected_note") or "connected",
                "next": "",
                "ready": True,
            }
        icon = AMBER if optional else RED
        return {
            "icon": icon,
            "account": account,
            "state": "needs install" if optional else "not connected yet",
            "next": entry.get("setup_hint") or f"run /setup {bundle} to log in",
            "ready": False,
        }

    if ttype == "mcp":
        # MCP tools (e.g. nano-banana). The verify is the MCP's own status
        # tool, which we cannot call from a plain subprocess. If the manifest
        # gives a CLI proxy verify, use it; otherwise gate on the env key the
        # MCP reads, and let the skill's own ensure_ready do the live check.
        if entry.get("verify") and run_verify(entry["verify"]):
            return {
                "icon": GREEN,
                "account": account,
                "state": entry.get("connected_note") or "connected",
                "next": "",
                "ready": True,
            }
        if env_slot_filled(entry, env):
            return {
                "icon": GREEN,
                "account": account,
                "state": entry.get("connected_note") or "connected",
                "next": "",
                "ready": True,
            }
        icon = AMBER if optional else RED
        return {
            "icon": icon,
            "account": account,
            "state": "not connected yet",
            "next": entry.get("setup_hint") or f"run /setup {bundle} to connect it",
            "ready": False,
        }

    # Unknown type - be honest, don't pretend green.
    return {
        "icon": AMBER,
        "account": account,
        "state": "unknown setup type",
        "next": "ask your builder - this tool's manifest looks off",
        "ready": False,
    }


# ── Rendering ──────────────────────────────────────────────────────────
def render(rows_by_bundle: dict[str, list[dict]]) -> str:
    out: list[str] = []
    out.append("Cool Hollow Coaching AIOS - connection check")
    out.append("")

    total = 0
    connected = 0
    needs = 0

    any_rows = False
    for bundle in BUNDLE_ORDER:
        rows = rows_by_bundle.get(bundle, [])
        if not rows:
            continue
        any_rows = True
        out.append(BUNDLE_TITLES[bundle])
        # Column widths sized to the longest account name in this group.
        width = max((len(r["account"]) for r in rows), default=10)
        for r in rows:
            total += 1
            if r["ready"]:
                connected += 1
            else:
                needs += 1
            line = f"  {r['icon']} {r['account'].ljust(width)}  {r['state']}"
            if r["next"]:
                line += f"  → {r['next']}"
            out.append(line)
    out.append("")

    if not any_rows:
        out.append("No external tools are registered yet.")
        out.append("Run /setup and I'll walk you through connecting them one at a time.")
        return "\n".join(out)

    # Summary line.
    plural = "tool is" if connected == 1 else "tools are"
    summary = f"{connected} connected"
    if needs:
        summary += f" · {needs} {'needs' if needs == 1 else 'need'} setup"
    out.append(summary)

    # Closing reassurance - always present, tone-checked for an anxious user.
    if needs == 0:
        out.append("Everything's connected. You're all set.")
    else:
        out.append(
            "Nothing is broken - the ones that aren't green just aren't connected yet. "
            "Run /setup whenever you're ready, or send your builder this output and "
            "they'll point you to the exact step."
        )
    return "\n".join(out)


def main() -> int:
    tools = load_registry()
    if tools is None:
        print("Your AIOS - connection check")
        print("")
        print(
            "I can't find your tool registry yet (data/skill_registry.json)."
        )
        print(
            "That's a setup step, not a problem on your side. Ask your builder to run "
            "build_registry.py, or run /setup and I'll sort it as we go."
        )
        return 0

    env = read_env()
    rows_by_bundle: dict[str, list[dict]] = {b: [] for b in BUNDLE_ORDER}

    for entry in tools:
        # Only external tools belong in /doctor. A skill with no requirement
        # (type none / no tool) is purely local and never shown.
        if not entry.get("tool"):
            continue
        ttype = (entry.get("type") or "").lower()
        if ttype in ("", "none", "local"):
            continue
        # Gmail / Calendar never get a permanent amber row here:
        # there is no self-serve connect path, so they live in the separate
        # Phase-2 MCP capability, not in the health check.
        tool_l = (entry.get("tool") or "").lower()
        if any(x in tool_l for x in ("gmail", "calendar")):
            continue
        bundle = (entry.get("bundle") or "business").lower()
        if bundle not in rows_by_bundle:
            rows_by_bundle[bundle] = []
        rows_by_bundle[bundle].append(resolve(entry, env))

    print(render(rows_by_bundle))
    return 0


if __name__ == "__main__":
    sys.exit(main())
