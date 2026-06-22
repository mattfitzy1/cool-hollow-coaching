"""
Core scoring logic for the Business Without You 12-Month Impact Map.

This is Milestone 2's model. The owner runs three exercises first: the
Strategy Razor draft (what serves the core customer, what leverages the
unfair advantage), the Core Customer Decree, and the Unfair Advantage list.
Those three turn into a scoring lens applied to a raw list of everything
planned for the next 12 months.

This module takes that raw initiative list, each one rated against the
Strategy Razor (does it serve the core customer, does it leverage the
unfair advantage, how much impact, how much effort), and outputs the
filtered 12-Month Impact Map: the 3-5 initiatives that clear the razor and
rank highest on impact for effort, plus a focus score showing how much of
the original list got cut.
"""

import pandas as pd

RAZOR_PASS_THRESHOLD = 3
MAX_PRIORITIES = 5
MIN_PRIORITIES = 3


def load_initiatives(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the uploaded initiative list."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    required = {"initiative", "core_customer_fit", "unfair_advantage_fit", "impact", "effort"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Initiative list is missing column(s): {', '.join(sorted(missing))}. "
            f"Expected: initiative, core_customer_fit, unfair_advantage_fit, impact, effort "
            f"(each rated 1-5)."
        )

    df["initiative"] = df["initiative"].astype(str)
    for col in ("core_customer_fit", "unfair_advantage_fit", "impact", "effort"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).clip(0, 5)

    return df[["initiative", "core_customer_fit", "unfair_advantage_fit", "impact", "effort"]]


def _passes_razor(row: pd.Series) -> bool:
    return (
        row["core_customer_fit"] >= RAZOR_PASS_THRESHOLD
        and row["unfair_advantage_fit"] >= RAZOR_PASS_THRESHOLD
        and row["impact"] >= RAZOR_PASS_THRESHOLD
    )


def _impact_effort_score(row: pd.Series) -> float:
    effort_drag = row["effort"] / 5
    return row["impact"] - effort_drag


def _reason(row: pd.Series, passed: bool) -> str:
    if passed:
        return (
            f"Serves the core customer ({row['core_customer_fit']:.0f}/5), leverages the unfair "
            f"advantage ({row['unfair_advantage_fit']:.0f}/5), impact {row['impact']:.0f}/5 for "
            f"{row['effort']:.0f}/5 effort."
        )
    gaps = []
    if row["core_customer_fit"] < RAZOR_PASS_THRESHOLD:
        gaps.append(f"core customer fit only {row['core_customer_fit']:.0f}/5")
    if row["unfair_advantage_fit"] < RAZOR_PASS_THRESHOLD:
        gaps.append(f"unfair advantage fit only {row['unfair_advantage_fit']:.0f}/5")
    if row["impact"] < RAZOR_PASS_THRESHOLD:
        gaps.append(f"impact only {row['impact']:.0f}/5")
    return "Cut by the razor: " + ", ".join(gaps) + "."


def build_impact_map(df: pd.DataFrame) -> dict:
    """Apply the Strategy Razor and build the 12-Month Impact Map."""
    if df.empty:
        return {"total_initiatives": 0, "focus_score": 0.0, "kept": [], "cut": []}

    df = df.copy()
    df["passes_razor"] = df.apply(_passes_razor, axis=1)
    df["score"] = df.apply(_impact_effort_score, axis=1)

    passed = df[df["passes_razor"]].sort_values("score", ascending=False)
    failed = df[~df["passes_razor"]].sort_values("score", ascending=False)

    kept_df = passed.head(MAX_PRIORITIES)

    if len(kept_df) < MIN_PRIORITIES:
        fill_needed = MIN_PRIORITIES - len(kept_df)
        kept_df = pd.concat([kept_df, failed.head(fill_needed)])

    # Track by row index, not initiative name, so two initiatives sharing the
    # same name (a real scenario, e.g. the same idea proposed for two teams)
    # don't get conflated when splitting into kept versus cut.
    kept_index = set(kept_df.index)

    kept = []
    for _, row in kept_df.iterrows():
        kept.append({
            "initiative": row["initiative"],
            "impact": int(row["impact"]),
            "effort": int(row["effort"]),
            "reasoning": _reason(row, bool(row["passes_razor"])),
        })

    cut = []
    for _, row in df[~df.index.isin(kept_index)].sort_values("score", ascending=False).iterrows():
        cut.append({
            "initiative": row["initiative"],
            "reasoning": _reason(row, bool(row["passes_razor"])),
        })

    total = len(df)
    focus_score = round((total - len(kept)) / total, 2) if total else 0.0

    return {
        "total_initiatives": total,
        "focus_score": focus_score,
        "kept": kept,
        "cut": cut,
    }
