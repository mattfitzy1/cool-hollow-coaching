"""Context aggregator for content development.

Assembles the recent context window used by /develop to make
informed content decisions. Pulls from the content database only:
  - Recent published content (from the published_content table)
  - Content pipeline state (stubs, developed, scheduled ideas)

Returns a structured dict that can be formatted into a prompt context block.

Usage:
    python scripts/context_aggregator.py              # Print context summary
    python scripts/context_aggregator.py --full       # Print full formatted context

    # In code:
    from scripts.context_aggregator import build_context_window, format_context_for_prompt
    context = build_context_window(days=30)
    prompt_block = format_context_for_prompt(context)
"""

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = WORKSPACE_ROOT / "data" / "content.db"


def build_context_window(days=30):
    """Build the context window from the content database.

    Returns:
        {
            "recent_content": [{"title", "platform", "published_date", "url", "description"}],
            "pipeline_state": {
                "stubs": [{"id", "title", "channel", "format_type", "created_at"}],
                "developed": [{"id", "title", "channel", "format_type"}],
                "scheduled": [{"id", "title", "channel", "film_by_date", "publish_date"}],
            },
            "window_start": "YYYY-MM-DD",
            "window_end": "YYYY-MM-DD",
        }
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    window_end = datetime.now().strftime("%Y-%m-%d")
    window_start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # --- Recent published content (from our table) ---
    recent_content = []
    try:
        rows = conn.execute(
            """SELECT platform, title, published_date, url, description
            FROM published_content
            WHERE published_date >= ?
            ORDER BY published_date DESC""",
            (window_start,),
        ).fetchall()
        for r in rows:
            recent_content.append(
                {
                    "title": r["title"],
                    "platform": r["platform"],
                    "published_date": r["published_date"],
                    "url": r["url"],
                    "description": r["description"],
                }
            )
    except sqlite3.OperationalError:
        pass  # Table doesn't exist yet

    # Sort all content by date
    recent_content.sort(key=lambda x: x.get("published_date", ""), reverse=True)

    # --- Pipeline state (always from content DB) ---
    pipeline_rows = conn.execute(
        """SELECT id, title, channel, format_type, production_status,
                  created_at, film_by_date, publish_date
        FROM content_ideas
        WHERE production_status IN ('stub', 'developed', 'scheduled')
        ORDER BY CASE production_status
            WHEN 'scheduled' THEN 1
            WHEN 'developed' THEN 2
            WHEN 'stub' THEN 3
        END, created_at DESC"""
    ).fetchall()

    pipeline_state = {"stubs": [], "developed": [], "scheduled": []}
    for r in pipeline_rows:
        entry = {
            "id": r["id"],
            "title": r["title"],
            "channel": r["channel"],
            "format_type": r["format_type"],
        }
        status = r["production_status"]
        if status == "stub":
            entry["created_at"] = r["created_at"]
            pipeline_state["stubs"].append(entry)
        elif status == "developed":
            pipeline_state["developed"].append(entry)
        elif status == "scheduled":
            entry["film_by_date"] = r["film_by_date"]
            entry["publish_date"] = r["publish_date"]
            pipeline_state["scheduled"].append(entry)

    conn.close()

    return {
        "recent_content": recent_content,
        "pipeline_state": pipeline_state,
        "window_start": window_start,
        "window_end": window_end,
    }


def format_context_for_prompt(context):
    """Format context dict into a prompt-ready markdown block."""
    sections = []
    sections.append(
        f"## Recent Context Window ({context['window_start']} to {context['window_end']})"
    )

    # Recent content
    content = context["recent_content"]
    sections.append(f"\n### Recent Published Content ({len(content)})")
    if content:
        for c in content:
            platform = c.get("platform", "?")
            sections.append(
                f"\n**{c['title']}** [{platform}] ({c.get('published_date', '?')})"
            )
            desc = c.get("description") or ""
            if desc:
                if len(desc) > 500:
                    desc = desc[:500] + "..."
                sections.append(desc)
    else:
        sections.append("No content published in this window.")

    # Pipeline state
    ps = context["pipeline_state"]
    sections.append("\n### Content Pipeline State")

    scheduled = ps["scheduled"]
    sections.append(f"**Scheduled ({len(scheduled)}):**")
    if scheduled:
        for s in scheduled:
            dates = ""
            if s.get("film_by_date"):
                dates += f" | Prep by: {s['film_by_date']}"
            if s.get("publish_date"):
                dates += f" | Publish: {s['publish_date']}"
            fmt = f" [{s.get('format_type', '?')}]" if s.get("format_type") else ""
            sections.append(f"- #{s['id']} {s['title']}{fmt}{dates}")
    else:
        sections.append("- (none)")

    developed = ps["developed"]
    sections.append(f"**Developed ({len(developed)}):**")
    if developed:
        for d in developed:
            fmt = f" [{d.get('format_type', '?')}]" if d.get("format_type") else ""
            sections.append(f"- #{d['id']} {d['title']}{fmt}")
    else:
        sections.append("- (none)")

    stubs = ps["stubs"]
    sections.append(f"**Stubs ({len(stubs)}):**")
    if stubs:
        for s in stubs:
            fmt = f" [{s.get('format_type', '?')}]" if s.get("format_type") else ""
            sections.append(f"- #{s['id']} {s['title']}{fmt}")
    else:
        sections.append("- (none)")

    return "\n".join(sections)


if __name__ == "__main__":
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        print("Run 'python scripts/content_db.py' first to initialize.")
        sys.exit(1)

    ctx = build_context_window()
    print(f"Recent content: {len(ctx['recent_content'])}")
    print(
        f"Pipeline - Stubs: {len(ctx['pipeline_state']['stubs'])}, "
        f"Developed: {len(ctx['pipeline_state']['developed'])}, "
        f"Scheduled: {len(ctx['pipeline_state']['scheduled'])}"
    )

    if "--full" in sys.argv:
        prompt = format_context_for_prompt(ctx)
        print(f"\nPrompt length: {len(prompt)} chars (~{len(prompt) // 4} tokens)")
        print("\n" + prompt)
    else:
        print("\nRun with --full to see the formatted context block.")
