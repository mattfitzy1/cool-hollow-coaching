"""
Core selection logic for the Business Without You Monday Morning Dashboard.

This is Milestone 3's model. The owner runs the exercise first: list every
metric currently tracked, plus raw candidate metrics across five
categories (cash, sales, delivery, customer, team), each one rated for how
directly it reflects whether the business is actually healthy, and whether
it moves before a problem shows up elsewhere (a leading indicator) or only
after (a lagging one).

This module takes that candidate list and selects exactly one metric per
category (the five-metric dashboard), sets a red/yellow/green threshold for
each based on current value versus target, and flags up to two leading
indicators worth watching first.
"""

import pandas as pd

CATEGORIES = ["cash", "sales", "delivery", "customer", "team"]
VALID_DIRECTIONS = {"higher_better", "lower_better"}
YELLOW_BAND = 0.10
MAX_LEADING_FLAGS = 2


def load_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the uploaded candidate metric list."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    required = {"category", "metric_name", "current_value", "target_value", "direction", "leading", "impact"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Metric list is missing column(s): {', '.join(sorted(missing))}. "
            f"Expected: category, metric_name, current_value, target_value, direction "
            f"(higher_better or lower_better), leading (yes/no), impact (1-5)."
        )

    df["category"] = df["category"].astype(str).str.strip().str.lower()
    df["metric_name"] = df["metric_name"].astype(str)
    df["current_value"] = pd.to_numeric(df["current_value"], errors="coerce").fillna(0)
    df["target_value"] = pd.to_numeric(df["target_value"], errors="coerce").fillna(0)
    df["direction"] = df["direction"].astype(str).str.strip().str.lower()
    df["leading"] = df["leading"].astype(str).str.strip().str.lower().eq("yes")
    df["impact"] = pd.to_numeric(df["impact"], errors="coerce").fillna(0).clip(0, 5)

    bad_categories = set(df["category"]) - set(CATEGORIES)
    if bad_categories:
        raise ValueError(
            f"Found category value(s) not recognized: {', '.join(sorted(bad_categories))}. "
            f"Each row's category must be one of: {', '.join(CATEGORIES)}."
        )

    bad_directions = set(df["direction"]) - VALID_DIRECTIONS
    if bad_directions:
        raise ValueError(
            f"Found direction value(s) not recognized: {', '.join(sorted(bad_directions))}. "
            f"Each row's direction must be higher_better or lower_better."
        )

    return df[["category", "metric_name", "current_value", "target_value", "direction", "leading", "impact"]]


def _status(row: pd.Series) -> str:
    target = row["target_value"]
    current = row["current_value"]

    if target == 0:
        gap = 0 if current == 0 else float("inf")
    else:
        gap = (target - current) / target if row["direction"] == "higher_better" else (current - target) / target

    if gap <= 0:
        return "green"
    if gap <= YELLOW_BAND:
        return "yellow"
    return "red"


def build_dashboard(df: pd.DataFrame) -> dict:
    """Select the five-metric dashboard and flag leading indicators."""
    selected = []
    missing_categories = []

    for category in CATEGORIES:
        candidates = df[df["category"] == category]
        if candidates.empty:
            missing_categories.append(category)
            continue

        candidates = candidates.sort_values(
            ["impact", "leading"], ascending=[False, False]
        )
        best = candidates.iloc[0]
        selected.append({
            "category": category,
            "metric_name": best["metric_name"],
            "current_value": best["current_value"],
            "target_value": best["target_value"],
            "status": _status(best),
            "leading": bool(best["leading"]),
            "impact": float(best["impact"]),
        })

    leading_flags = sorted(
        [m for m in selected if m["leading"]], key=lambda m: m["impact"], reverse=True
    )[:MAX_LEADING_FLAGS]
    leading_names = {m["metric_name"] for m in leading_flags}
    for m in selected:
        m["flagged_leading"] = m["metric_name"] in leading_names

    return {
        "dashboard": selected,
        "missing_categories": missing_categories,
    }
