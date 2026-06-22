#!/usr/bin/env python3
"""
build_registry.py - generate data/skill_registry.json for your AIOS.

This is the single source of truth that require_key.py (ensure_ready), /setup,
and /doctor all read, so they can never drift from the skills themselves. Same
discipline as the projects index: the map is GENERATED from the files, so it
cannot rot.

It scans two places and merges their `requires:` declarations:

  1. every .claude/skills/*/SKILL.md frontmatter
  2. every module-installs/*/INSTALL.md frontmatter

so MCP/OAuth tools that live as install modules (nano-banana, canva) appear in
the registry alongside the skill-declared ones (cloudflare, publer, higgsfield).

The output is a JSON object keyed by tool name. Each value is the tool's
manifest plus a `sources` list naming every SKILL.md / INSTALL.md that declared
it (so two skills can share one tool - e.g. creative + product-photoshoot both
needing higgsfield - and we keep one merged entry).

Run it after adding or editing any skill's `requires:` block:

    python3 scripts/build_registry.py

Stdlib only - it parses just the narrow `requires:` YAML shape these manifests
use (a list of flat dicts under a `requires:` key inside `--- ... ---`
frontmatter), not arbitrary YAML.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".claude" / "skills"
MODULES_DIR = ROOT / "module-installs"
OUT_PATH = ROOT / "data" / "skill_registry.json"


# ---------------------------------------------------------------------------
# Frontmatter + narrow YAML parsing (stdlib only)
# ---------------------------------------------------------------------------

def _extract_frontmatter(text: str) -> str | None:
    """Return the YAML frontmatter block (between the first two '---' lines),
    or None if the file has no frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i])
    return None


def _strip_inline_comment(v: str) -> str:
    """Drop a trailing YAML '# comment' from an UNQUOTED scalar. A comment only
    starts at a '#' that follows whitespace (so 'https://x#frag' and '#hashtag'
    inside a value survive). Quoted scalars are handled before this is called."""
    out = []
    prev_ws = True  # treat start-of-string as preceded by whitespace
    for ch in v:
        if ch == "#" and prev_ws:
            break
        out.append(ch)
        prev_ws = ch in " \t"
    return "".join(out).strip()


def _coerce(value: str):
    """Turn a scalar string into bool / int / float / str, stripping quotes and
    any trailing inline '# comment' on unquoted values."""
    v = value.strip()
    if (len(v) >= 2) and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
        return v[1:-1]
    v = _strip_inline_comment(v)
    low = v.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~", "none", ""):
        return None
    # inline list e.g. [higgsfield]  or  [node, npx]
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [_coerce(x) for x in inner.split(",")]
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def _parse_requires(frontmatter: str) -> list[dict]:
    """Parse the `requires:` section of a frontmatter block into a list of
    dicts. Handles the exact shape these manifests use:

        requires:
          - tool: higgsfield
            type: auth
            requires_bin: [higgsfield]
            requires_runtime: []
            optional: true

    Each list item begins with '- key: value' at some indent; subsequent
    'key: value' lines at a deeper indent belong to that item. Parsing stops at
    the next top-level (zero-or-base-indent) key after `requires:`.
    """
    lines = frontmatter.splitlines()

    # Find the `requires:` line and its indent.
    start = None
    base_indent = 0
    for idx, raw in enumerate(lines):
        stripped = raw.strip()
        if stripped == "requires:" or stripped.startswith("requires:"):
            # only treat as the block opener if there's nothing inline after it
            if stripped.replace("requires:", "").strip() == "":
                start = idx + 1
                base_indent = len(raw) - len(raw.lstrip())
                break
    if start is None:
        return []

    items: list[dict] = []
    current: dict | None = None

    for raw in lines[start:]:
        if raw.strip() == "":
            continue
        indent = len(raw) - len(raw.lstrip())
        stripped = raw.strip()

        # A line at or below the base indent that is not a list item ends the
        # block (the next top-level frontmatter key).
        if indent <= base_indent and not stripped.startswith("- "):
            break

        if stripped.startswith("- "):
            # New list item. The remainder after '- ' is the first key:value.
            if current is not None:
                items.append(current)
            current = {}
            stripped = stripped[2:].strip()
            if not stripped:
                continue
            # fall through to parse the inline key:value below

        if current is None:
            # Defensive: a stray line before any '- '; skip it.
            continue

        if ":" in stripped:
            key, _, val = stripped.partition(":")
            current[key.strip()] = _coerce(val)

    if current is not None:
        items.append(current)

    # Keep only items that actually name a tool.
    return [it for it in items if it.get("tool")]


# ---------------------------------------------------------------------------
# Scanning + merging
# ---------------------------------------------------------------------------

def _scan_manifests() -> list[tuple[str, dict]]:
    """Return (source_label, requirement_dict) pairs from every SKILL.md and
    every INSTALL.md that declares `requires:`."""
    found: list[tuple[str, dict]] = []

    if SKILLS_DIR.is_dir():
        for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
            text = skill_md.read_text(errors="replace")
            fm = _extract_frontmatter(text)
            if not fm:
                continue
            label = f"skills/{skill_md.parent.name}/SKILL.md"
            for req in _parse_requires(fm):
                found.append((label, req))

    if MODULES_DIR.is_dir():
        for install_md in sorted(MODULES_DIR.glob("*/INSTALL.md")):
            text = install_md.read_text(errors="replace")
            fm = _extract_frontmatter(text)
            if not fm:
                continue
            label = f"module-installs/{install_md.parent.name}/INSTALL.md"
            for req in _parse_requires(fm):
                found.append((label, req))

    return found


def _merge(found: list[tuple[str, dict]]) -> dict:
    """Merge requirement dicts by tool name. Later non-empty fields fill gaps;
    every declaring source is recorded under `sources`."""
    registry: dict[str, dict] = {}
    for source, req in found:
        tool = req["tool"]
        entry = registry.setdefault(tool, {"sources": []})
        if source not in entry["sources"]:
            entry["sources"].append(source)
        for k, v in req.items():
            if k == "sources":
                continue
            # First non-empty value wins; don't overwrite a populated field with
            # an empty one from a sparser declaration.
            existing = entry.get(k)
            if existing in (None, "", []) or k not in entry:
                if v not in (None, "") or k not in entry:
                    entry[k] = v
    # Normalise: ensure a few expected fields always exist.
    for tool, entry in registry.items():
        entry.setdefault("tool", tool)
        entry.setdefault("type", "key")
        entry.setdefault("requires_bin", [])
        entry.setdefault("requires_runtime", [])
        entry.setdefault("optional", False)
        # sources at the end for readability
        srcs = entry.pop("sources")
        entry["sources"] = srcs
    return registry


def build(write: bool = True) -> dict:
    found = _scan_manifests()
    registry = _merge(found)
    if write:
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(
            json.dumps(registry, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        )
    return registry


def _main(argv: list[str]) -> int:
    registry = build(write=True)
    n = len(registry)
    print(f"Wrote {OUT_PATH.relative_to(ROOT)} - {n} external "
          f"tool{'s' if n != 1 else ''} found:")
    for tool in sorted(registry):
        e = registry[tool]
        bins = ", ".join(e.get("requires_bin") or []) or "-"
        opt = " (optional)" if e.get("optional") else ""
        print(f"  - {tool}  [{e.get('type')}]  bundle={e.get('bundle', '?')}  "
              f"bin={bins}{opt}")
    if n == 0:
        print("  (no skills declare `requires:` yet - that's fine; this file "
              "regenerates whenever one does.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
