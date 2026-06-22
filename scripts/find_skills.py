#!/usr/bin/env python3
"""Skill finder MVP — surface high-signal community Claude Code skills.

Operationalises the "Borrow Before You Build" AIOS principle. Searches a
small set of GitHub topic queries via the `gh` CLI, filters out junk,
scores each candidate against the workspace fingerprint, and writes a
markdown digest under outputs/skill-finder/.

Usage:
    python3 scripts/find_skills.py                  # writes today's digest
    python3 scripts/find_skills.py --limit 10       # change top-N
    python3 scripts/find_skills.py --print          # also print digest to stdout
    python3 scripts/find_skills.py --since 90       # exclude commits older than 90 days

Trust model: advisory only. The digest never installs anything. Every
candidate must be reviewed manually before adoption — community skills
run arbitrary code.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
DOCS_INDEX = REPO_ROOT / "docs" / "_index.md"
OUTPUT_DIR = REPO_ROOT / "outputs" / "skill-finder"
TASK_AUDIT_PATH = REPO_ROOT / "context" / "task-audit.md"
NEXT_ACTIONS_PATH = REPO_ROOT / "gtd" / "next-actions.md"

QUERIES = [
    "topic:claude-code-skills stars:>10 archived:false",
    "topic:claude-skills stars:>10 archived:false",
    "topic:claude-code-plugins stars:>10 archived:false",
]

PERMISSIVE_LICENSES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD", "Unlicense"}

MIN_STARS = 50
DEFAULT_TOP_N = 5
DEFAULT_RECENCY_DAYS = 180  # skip repos untouched for 6 months
README_PREVIEW_CHARS = 1200


@dataclass
class Candidate:
    full_name: str
    description: str
    stars: int
    pushed_at: str
    license: str
    html_url: str
    topics: list[str] = field(default_factory=list)
    readme_preview: str = ""
    score: int = 0
    score_reasons: list[str] = field(default_factory=list)
    overlap: list[str] = field(default_factory=list)
    matches: list["TaskMatch"] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return self.full_name.split("/")[-1].lower()

    @property
    def pushed_age_days(self) -> int:
        try:
            ts = datetime.fromisoformat(self.pushed_at.replace("Z", "+00:00"))
        except ValueError:
            return 9999
        return (datetime.now(timezone.utc) - ts).days


@dataclass
class TaskMatch:
    """A task-audit row or next-action that overlaps with a candidate."""
    source: str          # "task-audit" or "next-actions"
    identifier: str      # task-audit row ID (e.g. "24") or short next-action slug
    snippet: str         # one-line human-readable summary
    overlap_terms: list[str] = field(default_factory=list)


def run_gh(args: list[str], raw: bool = False) -> dict | list | str:
    """Run `gh api` and return JSON (default) or raw text. Raises CalledProcessError on failure."""
    cmd = ["gh", "api"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    if raw:
        return result.stdout or ""
    if not result.stdout:
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        # Some endpoints (e.g. /readme with Accept: raw) return non-JSON. Return as text.
        return result.stdout


def search_repos(query: str) -> list[dict]:
    args = [
        "-X", "GET", "search/repositories",
        "-f", f"q={query}",
        "-f", "sort=stars",
        "-f", "order=desc",
        "-f", "per_page=30",
    ]
    payload = run_gh(args)
    return payload.get("items", []) if isinstance(payload, dict) else []


def fetch_readme(full_name: str) -> str:
    try:
        payload = run_gh(["-X", "GET", f"repos/{full_name}/readme",
                          "-H", "Accept: application/vnd.github.raw"], raw=True)
    except subprocess.CalledProcessError:
        return ""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        # Fallback if accept header wasn't honoured: payload has base64 content.
        import base64
        content = payload.get("content", "")
        encoding = payload.get("encoding", "")
        if encoding == "base64" and content:
            try:
                return base64.b64decode(content).decode("utf-8", errors="ignore")
            except Exception:
                return ""
    return ""


def workspace_fingerprint() -> tuple[set[str], str]:
    """Return (installed_skill_slugs, docs_index_text) — used for overlap detection."""
    slugs: set[str] = set()
    if SKILLS_DIR.exists():
        slugs = {p.name.lower() for p in SKILLS_DIR.iterdir() if p.is_dir()}
    docs_text = DOCS_INDEX.read_text(encoding="utf-8") if DOCS_INDEX.exists() else ""
    return slugs, docs_text


def detect_overlap(candidate: Candidate, installed: set[str], docs_text: str) -> list[str]:
    overlaps: list[str] = []
    blob = " ".join([candidate.full_name, candidate.description or "",
                     candidate.readme_preview[:400], " ".join(candidate.topics)]).lower()
    # 1) Direct slug match in installed skills
    if candidate.slug in installed:
        overlaps.append(f"installed skill `{candidate.slug}` already exists")
    # 2) Keyword overlap with installed skills
    keyword_hits = [s for s in installed if len(s) > 3 and s in blob]
    for hit in keyword_hits[:3]:
        if hit != candidate.slug:
            overlaps.append(f"keyword overlap with installed skill `{hit}`")
    # 3) docs/_index.md mentions
    if candidate.slug and candidate.slug in docs_text.lower():
        overlaps.append(f"`{candidate.slug}` appears in docs/_index.md")
    return overlaps


STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "for", "by",
    "with", "from", "as", "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "its", "their", "them", "they",
    "we", "you", "your", "our", "i", "me", "my",
    "do", "does", "did", "doing", "done", "have", "has", "had", "having",
    "can", "will", "would", "should", "could", "may", "might", "must",
    "not", "no", "yes", "only", "also", "more", "less", "than", "then",
    "into", "out", "up", "down", "over", "under", "off", "again",
    "via", "vs", "etc", "eg", "ie",
    # very generic words that produce false matches
    "task", "tasks", "action", "actions", "work", "works", "working", "worked",
    "system", "use", "used", "using",
    "manual", "auto", "ongoing", "daily", "weekly", "monthly", "per", "each",
    "min", "mins", "minute", "minutes", "hr", "hrs", "hour", "hours",
    "setup", "setting", "settings", "thing", "things",
    "client", "clients",
    # Universal AI-tooling terms — these appear in every candidate AND many tasks,
    # so they produce noise rather than signal in the cross-reference.
    "claude", "code", "ai", "llm", "agent", "agents", "agentic",
    "skill", "skills", "plugin", "plugins", "anthropic", "mcp", "model", "models",
    "prompt", "prompts", "openai", "cursor", "codex", "tool", "tools",
    # Generic verbs/nouns from task lists that don't distinguish.
    "run", "runs", "ran", "running", "build", "builds", "building", "built",
    "find", "found", "make", "made", "save", "saved", "saving", "send", "sent",
    "get", "gets", "got", "see", "saw", "look", "looking",
    "add", "added", "adding", "create", "created", "creating", "set", "sets",
    "one", "two", "three", "first", "second", "next", "last", "previous",
    "what", "who", "when", "where", "why", "how", "any", "all", "every",
    "full", "front", "back", "long", "short", "new", "old",
    "time", "today", "yesterday", "tomorrow", "yet", "still", "soon",
    "list", "lists", "doc", "docs", "file", "files", "folder", "page", "pages",
    "ground", "open", "close",
}

PRIORITY_TERMS = [
    # Active 2026-Q2 priorities — keep this list short and edit it as priorities shift.
    "aios", "ai partner", "ai agency", "agency",
    "outlook", "microsoft 365", "msgraph", "graph api",
    "linkedin", "outreach", "sales",
    "cloudflare", "pages", "dns", "ionos",
    "telegram", "bot",
    "ghl", "gohighlevel", "hubspot",
    "notion", "tasks", "gtd",
    "n8n", "workflow", "automation",
    "stripe", "finance", "invoice",
    "supabase", "sqlite", "claude code",
    "deep research", "research", "scrape", "firecrawl",
    "memory", "context", "hooks", "subagent", "skill",
]


TOKEN_RE = re.compile(r"[a-z][a-z0-9\-]{2,}")  # 3+ chars, leading letter


def _tokenise(text: str) -> set[str]:
    """Lowercase, extract content tokens, drop stopwords."""
    text = (text or "").lower()
    raw = TOKEN_RE.findall(text)
    return {t for t in raw if t not in STOPWORDS and len(t) >= 3}


# Match task-audit rows: | [ ] | id | description | category | freq | time-cost | priority | note |
# Done rows ([x]) are skipped — they don't need automation.
_TASK_AUDIT_RE = re.compile(
    r"^\|\s*\[\s\]\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|",
    re.MULTILINE,
)
# Next-action bullets: open `- [ ] ...` items. Strip bold prefixes for the snippet.
_NEXT_ACTION_RE = re.compile(r"^-\s*\[\s\]\s*(.+)$", re.MULTILINE)
_BOLD_PREFIX_RE = re.compile(r"^\*\*([^*]+?)\*\*:?\s*")


def parse_task_audit(path: Path = TASK_AUDIT_PATH) -> list[TaskMatch]:
    """Return one TaskMatch stub per open task-audit row."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    out: list[TaskMatch] = []
    for m in _TASK_AUDIT_RE.finditer(text):
        row_id, description, category = m.group(1), m.group(2).strip(), m.group(3).strip()
        # Trim "Quick Wins" header rows etc. — these have empty IDs or non-numeric ones.
        if not row_id.isdigit():
            continue
        snippet = description if not category else f"[{category}] {description}"
        out.append(TaskMatch(
            source="task-audit",
            identifier=row_id,
            snippet=snippet[:160],
            overlap_terms=[],
        ))
    return out


def parse_next_actions(path: Path = NEXT_ACTIONS_PATH) -> list[TaskMatch]:
    """Return one TaskMatch stub per open next-action bullet."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    out: list[TaskMatch] = []
    seen: set[str] = set()
    for i, m in enumerate(_NEXT_ACTION_RE.finditer(text)):
        raw = m.group(1).strip()
        # Strip leading bold prefix like "**Action 5 (accelerator research):**"
        # so the matcher and snippet focus on the actual action text.
        body = _BOLD_PREFIX_RE.sub("", raw)
        snippet = body[:160]
        if snippet.lower() in seen:
            continue
        seen.add(snippet.lower())
        # Identifier: short slug for digest readability.
        ident = re.sub(r"[^a-z0-9]+", "-", body.lower()).strip("-")[:30] or f"na-{i}"
        out.append(TaskMatch(
            source="next-actions",
            identifier=ident,
            snippet=snippet,
            overlap_terms=[],
        ))
    return out


MIN_OVERLAP_TERMS = 2          # minimum shared content tokens to call it a match
MAX_MATCHES_PER_CANDIDATE = 3  # cap the digest noise
PHASE3_SCORE_PER_MATCH = 3
PHASE3_BOOST_CAP = 6           # +6 max from cross-reference, regardless of match count


def match_candidate_to_tasks(candidate: Candidate, tasks: list[TaskMatch]) -> list[TaskMatch]:
    """Find which tasks a candidate could plausibly unblock. Returns ranked matches."""
    cand_blob = " ".join([
        candidate.description or "",
        candidate.readme_preview or "",
        " ".join(candidate.topics),
        candidate.full_name.replace("/", " "),
    ])
    cand_terms = _tokenise(cand_blob)
    if not cand_terms:
        return []

    scored: list[tuple[int, TaskMatch]] = []
    for t in tasks:
        task_terms = _tokenise(t.snippet)
        if not task_terms:
            continue
        shared = cand_terms & task_terms
        if len(shared) < MIN_OVERLAP_TERMS:
            continue
        # Copy so we don't mutate the shared task stub.
        match = TaskMatch(
            source=t.source,
            identifier=t.identifier,
            snippet=t.snippet,
            overlap_terms=sorted(shared)[:6],
        )
        scored.append((len(shared), match))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [m for _, m in scored[:MAX_MATCHES_PER_CANDIDATE]]


def score_candidate(candidate: Candidate, installed: set[str], docs_text: str,
                    tasks: list[TaskMatch] | None = None) -> None:
    """Mutate candidate with a crude fit score and reasons.

    If `tasks` is provided, Phase 3 cross-reference fires: candidates that
    overlap (≥MIN_OVERLAP_TERMS shared content tokens) with open task-audit rows
    or next-actions get a score boost (capped at PHASE3_BOOST_CAP) and the
    matched tasks are recorded on the candidate.
    """
    score = 0
    reasons: list[str] = []
    blob = " ".join([candidate.description or "", candidate.readme_preview,
                     " ".join(candidate.topics)]).lower()

    # +stars (capped)
    if candidate.stars >= 1000:
        score += 4
        reasons.append(f"{candidate.stars:,} stars (>1k)")
    elif candidate.stars >= 200:
        score += 3
        reasons.append(f"{candidate.stars:,} stars (>200)")
    elif candidate.stars >= MIN_STARS:
        score += 2
        reasons.append(f"{candidate.stars:,} stars (>{MIN_STARS})")

    # +recency
    age = candidate.pushed_age_days
    if age <= 14:
        score += 3
        reasons.append(f"pushed {age}d ago")
    elif age <= 60:
        score += 2
        reasons.append(f"pushed {age}d ago")
    elif age <= 180:
        score += 1
        reasons.append(f"pushed {age}d ago")

    # +license
    if candidate.license in PERMISSIVE_LICENSES:
        score += 1
        reasons.append(f"{candidate.license} licensed")

    # +priority term match (workspace fit)
    matched_terms = [t for t in PRIORITY_TERMS if t in blob]
    if matched_terms:
        bonus = min(len(matched_terms), 4)
        score += bonus
        reasons.append(f"matches: {', '.join(matched_terms[:5])}")

    # -overlap
    overlaps = detect_overlap(candidate, installed, docs_text)
    if overlaps:
        score -= 2 * len(overlaps)
        reasons.append(f"overlap penalty ({len(overlaps)})")
    candidate.overlap = overlaps

    # +task-audit / next-actions cross-reference (Phase 3)
    if tasks:
        matches = match_candidate_to_tasks(candidate, tasks)
        candidate.matches = matches
        if matches:
            boost = min(PHASE3_SCORE_PER_MATCH * len(matches), PHASE3_BOOST_CAP)
            score += boost
            ta_count = sum(1 for m in matches if m.source == "task-audit")
            na_count = sum(1 for m in matches if m.source == "next-actions")
            parts: list[str] = []
            if ta_count:
                parts.append(f"{ta_count} task-audit row(s)")
            if na_count:
                parts.append(f"{na_count} next-action(s)")
            reasons.append(f"could unblock {' + '.join(parts)} (+{boost})")

    candidate.score = score
    candidate.score_reasons = reasons


def parse_candidate(item: dict) -> Candidate | None:
    full_name = item.get("full_name") or ""
    if not full_name:
        return None
    license_obj = item.get("license") or {}
    license_id = (license_obj.get("spdx_id") or "").strip() if isinstance(license_obj, dict) else ""
    return Candidate(
        full_name=full_name,
        description=(item.get("description") or "").strip(),
        stars=item.get("stargazers_count", 0),
        pushed_at=item.get("pushed_at") or "",
        license=license_id or "NOASSERTION",
        html_url=item.get("html_url") or f"https://github.com/{full_name}",
        topics=item.get("topics") or [],
    )


def apply_filters(candidates: list[Candidate], min_stars: int, max_age_days: int) -> list[Candidate]:
    out: list[Candidate] = []
    for c in candidates:
        if c.stars < min_stars:
            continue
        if c.pushed_age_days > max_age_days:
            continue
        if c.license not in PERMISSIVE_LICENSES and c.license != "NOASSERTION":
            # NOASSERTION = no LICENSE file detected; allow but flag in digest.
            continue
        out.append(c)
    return out


CLEAN_RE = re.compile(r"<!--.*?-->", re.DOTALL)
BADGE_PREFIXES = ("![", "[![", "<img", "<a href", "<div", "</div>", "<kbd>", "</kbd>",
                  "<p align", "</p>", "<picture", "</picture>", "<source", "<h1", "<h2",
                  "<h3", "</h1>", "</h2>", "</h3>")


def clean_readme(text: str) -> str:
    text = CLEAN_RE.sub("", text)
    out: list[str] = []
    blank_streak = 0
    for ln in text.splitlines():
        stripped = ln.strip()
        if any(stripped.startswith(p) for p in BADGE_PREFIXES):
            continue
        # collapse runs of blank lines
        if not stripped:
            blank_streak += 1
            if blank_streak > 1:
                continue
        else:
            blank_streak = 0
        out.append(ln)
    cleaned = "\n".join(out).strip()
    return cleaned[:README_PREVIEW_CHARS]


def deduplicate(candidates: list[Candidate]) -> list[Candidate]:
    seen: dict[str, Candidate] = {}
    for c in candidates:
        key = c.full_name.lower()
        if key in seen:
            # keep the one with higher star count (gh occasionally returns dupes)
            if c.stars > seen[key].stars:
                seen[key] = c
        else:
            seen[key] = c
    return list(seen.values())


def write_digest(top: list[Candidate], all_kept: list[Candidate], today: str, queries: list[str]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{today}.md"
    lines: list[str] = []
    lines.append(f"# Skill Finder Digest — {today}\n")
    lines.append("> Advisory only. Never auto-install. Review each candidate manually before adopting.\n")
    lines.append(f"**Sources scanned:** {len(queries)} GitHub topic queries via `gh` CLI.")
    lines.append(f"**Candidates after filtering:** {len(all_kept)} (min {MIN_STARS} stars, "
                 f"≤{DEFAULT_RECENCY_DAYS}d since last push, permissive licence).")
    lines.append(f"**Top {len(top)} surfaced below.**\n")

    lines.append("## Top candidates\n")
    if not top:
        lines.append("_No candidates passed the filters today._\n")
    for i, c in enumerate(top, start=1):
        lines.append(f"### {i}. {c.full_name}  ·  score {c.score}")
        lines.append("")
        lines.append(f"- **Repo:** {c.html_url}")
        lines.append(f"- **Stars:** {c.stars:,}  ·  **License:** {c.license}  ·  **Last push:** "
                     f"{c.pushed_at} ({c.pushed_age_days}d ago)")
        if c.topics:
            lines.append(f"- **Topics:** {', '.join(c.topics[:8])}")
        if c.description:
            lines.append(f"- **Description:** {c.description}")
        if c.score_reasons:
            lines.append(f"- **Why surfaced:** {'; '.join(c.score_reasons)}")
        if c.overlap:
            lines.append(f"- **Overlap flags:** {'; '.join(c.overlap)}")
        if c.matches:
            lines.append(f"- **Could unblock ({len(c.matches)}):**")
            for m in c.matches:
                if m.source == "task-audit":
                    label = f"task-audit row #{m.identifier}"
                else:
                    label = "next-action"
                shared = f" [shared: {', '.join(m.overlap_terms[:4])}]" if m.overlap_terms else ""
                lines.append(f"    - {label}: {m.snippet}{shared}")
        lines.append("")
        lines.append("**Install (manual review required):**")
        lines.append("")
        lines.append("```")
        lines.append(f"# Inspect first:")
        lines.append(f"gh repo view {c.full_name} --web")
        lines.append(f"# If approved, /plugin install (or manual clone into .claude/skills/):")
        lines.append(f"# /plugin install {c.full_name}")
        lines.append("```")
        lines.append("")
        if c.readme_preview:
            preview = c.readme_preview.strip()
            preview = preview[:800] + ("…" if len(preview) > 800 else "")
            lines.append("**README preview:**")
            lines.append("")
            lines.append("> " + preview.replace("\n", "\n> "))
            lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## All kept (after filtering)\n")
    lines.append("| Rank | Repo | Stars | Pushed | Licence | Score |")
    lines.append("|------|------|-------|--------|---------|-------|")
    for i, c in enumerate(sorted(all_kept, key=lambda x: x.score, reverse=True), start=1):
        lines.append(f"| {i} | [{c.full_name}]({c.html_url}) | {c.stars:,} | "
                     f"{c.pushed_age_days}d | {c.license} | {c.score} |")
    lines.append("")

    lines.append("## Queries used\n")
    for q in queries:
        lines.append(f"- `{q}`")
    lines.append("")
    lines.append("---")
    lines.append(f"_Generated by `scripts/find_skills.py` on {datetime.now(timezone.utc).isoformat()}._")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Find high-signal Claude Code skills on GitHub.")
    parser.add_argument("--limit", type=int, default=DEFAULT_TOP_N, help="Top N candidates to detail")
    parser.add_argument("--since", type=int, default=DEFAULT_RECENCY_DAYS,
                        help="Skip repos with no push in N days")
    parser.add_argument("--min-stars", type=int, default=MIN_STARS, help="Minimum star count")
    parser.add_argument("--print", action="store_true", help="Also print digest to stdout")
    parser.add_argument("--no-readme", action="store_true",
                        help="Skip README fetch for top candidates (faster, but less context)")
    parser.add_argument("--notify", action="store_true",
                        help="Send a Telegram notification when the digest is written "
                             "(uses scripts/notify.py). Used by the weekly launchd agent.")
    parser.add_argument("--no-task-match", action="store_true",
                        help="Skip the task-audit and next-actions cross-reference (Phase 3).")
    args = parser.parse_args()

    if shutil.which("gh") is None:
        print("ERROR: `gh` CLI is not on PATH. Install gh first (`brew install gh && gh auth login`).",
              file=sys.stderr)
        return 2

    raw: list[Candidate] = []
    for q in QUERIES:
        try:
            items = search_repos(q)
        except subprocess.CalledProcessError as e:
            print(f"WARN: query failed -> {q}\n  {e.stderr.strip() if e.stderr else e}", file=sys.stderr)
            continue
        for item in items:
            c = parse_candidate(item)
            if c:
                raw.append(c)

    deduped = deduplicate(raw)
    kept = apply_filters(deduped, args.min_stars, args.since)

    if not kept:
        print("No candidates passed filters. Loosen --min-stars or --since to widen the net.")
    installed, docs_text = workspace_fingerprint()

    # Phase 3: parse open task-audit rows + next-actions for cross-reference.
    if args.no_task_match:
        tasks: list[TaskMatch] = []
    else:
        tasks = parse_task_audit() + parse_next_actions()
        if tasks:
            print(f"Loaded {len(tasks)} open tasks for cross-reference "
                  f"({sum(1 for t in tasks if t.source == 'task-audit')} task-audit, "
                  f"{sum(1 for t in tasks if t.source == 'next-actions')} next-actions).")

    # Score first using only metadata (skip README) so we can pick top-N cheaply.
    for c in kept:
        score_candidate(c, installed, docs_text, tasks)

    kept.sort(key=lambda x: x.score, reverse=True)
    top = kept[: args.limit]

    if not args.no_readme:
        for c in top:
            readme = fetch_readme(c.full_name)
            c.readme_preview = clean_readme(readme) if readme else ""
            # rescore now that we have README context
            score_candidate(c, installed, docs_text, tasks)
        top.sort(key=lambda x: x.score, reverse=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = write_digest(top, kept, today, QUERIES)
    print(f"Wrote digest → {out_path.relative_to(REPO_ROOT)}")
    print(f"Top {len(top)} of {len(kept)} kept candidates ({len(deduped)} unique pre-filter).")
    for i, c in enumerate(top, start=1):
        print(f"  {i}. {c.full_name}  ·  {c.stars:,}★  ·  score {c.score}")

    if args.print:
        print()
        print(out_path.read_text(encoding="utf-8"))

    if args.notify:
        try:
            sys.path.insert(0, str(REPO_ROOT))
            from scripts.notify import notify  # noqa: WPS433 (local import by design)
            lines: list[str] = []
            lines.append(f"{len(kept)} candidates kept, top {len(top)} detailed.")
            for i, c in enumerate(top[:3], start=1):
                lines.append(f"  {i}. {c.full_name} ({c.stars:,}★, score {c.score})")
            lines.append(f"Digest: {out_path.relative_to(REPO_ROOT)}")
            notify("Skill Finder", lines, status="success")
        except Exception as exc:  # noqa: BLE001 (best-effort notification)
            print(f"WARN: notify failed: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
