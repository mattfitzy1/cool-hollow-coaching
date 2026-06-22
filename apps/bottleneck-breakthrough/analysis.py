"""
Core ranking logic for the Business Without You Bottleneck Breakthrough Plan.

This is Milestone 6's model. The owner runs the exercise first: the
Constraint Identification worksheet, mapping three core processes and
naming every candidate constraint inside them, how often it bites, how
much time it costs each time, and how much it blocks everything
downstream.

This module takes that candidate list and produces two ranked outputs:
1. The Bottleneck Breakthrough Plan: every constraint ranked by a combined
   impact score (frequency x hours lost x downstream impact), naming the
   single binding constraint to break first.
2. The Automation Hit List: the subset marked automatable, ranked by hours
   saved per week for the effort required, so the easiest wins surface
   first.
"""

import pandas as pd

VALID_YES_NO = {"yes", "no"}


def load_constraints(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the uploaded Constraint Identification worksheet."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    required = {
        "constraint_name", "process", "frequency_per_week",
        "hours_lost_per_occurrence", "downstream_impact",
        "automatable", "automation_effort",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Constraint list is missing column(s): {', '.join(sorted(missing))}. "
            f"Expected: constraint_name, process, frequency_per_week, "
            f"hours_lost_per_occurrence, downstream_impact (1-5), automatable "
            f"(yes/no), automation_effort (1-5, 1 is trivial, 5 is hard)."
        )

    df["constraint_name"] = df["constraint_name"].astype(str)
    df["process"] = df["process"].astype(str)
    df["frequency_per_week"] = pd.to_numeric(df["frequency_per_week"], errors="coerce").fillna(0)
    df["hours_lost_per_occurrence"] = pd.to_numeric(df["hours_lost_per_occurrence"], errors="coerce").fillna(0)
    df["downstream_impact"] = pd.to_numeric(df["downstream_impact"], errors="coerce").fillna(0).clip(0, 5)
    df["automatable"] = df["automatable"].astype(str).str.strip().str.lower()
    df["automation_effort"] = pd.to_numeric(df["automation_effort"], errors="coerce").fillna(5).clip(1, 5)

    bad_values = set(df["automatable"]) - VALID_YES_NO
    if bad_values:
        raise ValueError(
            f"Found automatable value(s) not recognized: {', '.join(sorted(bad_values))}. "
            f"Each row's automatable must be yes or no."
        )

    return df[[
        "constraint_name", "process", "frequency_per_week", "hours_lost_per_occurrence",
        "downstream_impact", "automatable", "automation_effort",
    ]]


def build_breakthrough_plan(df: pd.DataFrame) -> dict:
    """Rank constraints and build the automation hit list."""
    if df.empty:
        return {"binding_constraint": None, "ranked_constraints": [], "automation_hit_list": []}

    df = df.copy()
    df["weekly_hours_lost"] = df["frequency_per_week"] * df["hours_lost_per_occurrence"]
    df["constraint_score"] = df["weekly_hours_lost"] * df["downstream_impact"]

    ranked = df.sort_values("constraint_score", ascending=False).reset_index(drop=True)

    ranked_constraints = []
    for rank, row in ranked.iterrows():
        ranked_constraints.append({
            "rank": rank + 1,
            "constraint_name": row["constraint_name"],
            "process": row["process"],
            "weekly_hours_lost": round(row["weekly_hours_lost"], 1),
            "downstream_impact": int(row["downstream_impact"]),
            "constraint_score": round(row["constraint_score"], 1),
        })

    binding_constraint = ranked_constraints[0] if ranked_constraints else None

    automatable = df[df["automatable"] == "yes"].copy()
    automation_hit_list = []
    if not automatable.empty:
        automatable["automation_roi"] = automatable["weekly_hours_lost"] / automatable["automation_effort"]
        automatable = automatable.sort_values("automation_roi", ascending=False)
        for _, row in automatable.iterrows():
            automation_hit_list.append({
                "constraint_name": row["constraint_name"],
                "weekly_hours_lost": round(row["weekly_hours_lost"], 1),
                "automation_effort": int(row["automation_effort"]),
                "automation_roi": round(row["automation_roi"], 1),
            })

    return {
        "binding_constraint": binding_constraint,
        "ranked_constraints": ranked_constraints,
        "automation_hit_list": automation_hit_list,
    }
