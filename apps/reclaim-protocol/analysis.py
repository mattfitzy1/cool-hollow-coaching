"""
Core scoring logic for the Business Without You 15-Hour Reclaim Protocol.

This is Milestone 1's model. The owner runs the Liberation Audit exercise
first: a one-week time log where every task gets sorted into one of four
categories (owner_only, delegate, automate, eliminate), plus a short
Constraint Diagnosis on each delegate/automate/eliminate candidate (is it
documented, is there a trained replacement, what's the risk if it's handed
off and something goes wrong).

This module takes that time log, scores every non-owner-only task on how
much weekly time it costs and how ready it is to move, and outputs a named,
deadlined list: the 15-Hour Reclaim Protocol.
"""

import pandas as pd

VALID_CATEGORIES = {"owner_only", "delegate", "automate", "eliminate"}
VALID_RISK = {"low", "medium", "high"}

ACTION_LABELS = {
    "delegate": "Delegate",
    "automate": "Automate",
    "eliminate": "Eliminate",
}

RISK_PENALTY = {"low": 0, "medium": 1, "high": 2}


def load_time_log(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the uploaded Liberation Audit sheet."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    required = {"task", "hours_per_week", "category"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Time log is missing column(s): {', '.join(sorted(missing))}. "
            f"Expected: task, hours_per_week, category, and optionally "
            f"documented, trained_replacement, risk."
        )

    df["task"] = df["task"].astype(str)
    df["hours_per_week"] = pd.to_numeric(df["hours_per_week"], errors="coerce").fillna(0)
    df["category"] = df["category"].astype(str).str.strip().str.lower()

    bad_categories = set(df["category"]) - VALID_CATEGORIES
    if bad_categories:
        raise ValueError(
            f"Found category value(s) not recognized: {', '.join(sorted(bad_categories))}. "
            f"Each row's category must be one of: owner_only, delegate, automate, eliminate."
        )

    for col in ("documented", "trained_replacement"):
        if col not in df.columns:
            df[col] = "no"
        df[col] = df[col].astype(str).str.strip().str.lower().replace({"": "no"})

    if "risk" not in df.columns:
        df["risk"] = "medium"
    df["risk"] = df["risk"].astype(str).str.strip().str.lower().replace({"": "medium"})
    df.loc[~df["risk"].isin(VALID_RISK), "risk"] = "medium"

    return df[["task", "hours_per_week", "category", "documented", "trained_replacement", "risk"]]


def _urgency(row: pd.Series) -> float:
    readiness = (2 if row["documented"] == "yes" else 0) + (2 if row["trained_replacement"] == "yes" else 0)
    risk_penalty = RISK_PENALTY.get(row["risk"], 1)
    return row["hours_per_week"] + readiness - risk_penalty


def _deadline_for_rank(rank: int, total: int) -> str:
    if total <= 1:
        return "This week"
    position = rank / (total - 1) if total > 1 else 0
    if position <= 1 / 3:
        return "This week"
    if position <= 2 / 3:
        return "Within 2 weeks"
    return "Within 30 days"


def build_protocol(df: pd.DataFrame) -> dict:
    """Score the time log and build the 15-Hour Reclaim Protocol."""
    owner_only = df[df["category"] == "owner_only"]
    candidates = df[df["category"] != "owner_only"].copy()

    owner_only_hours = round(owner_only["hours_per_week"].sum(), 1)

    if candidates.empty:
        return {
            "owner_only_hours": owner_only_hours,
            "reclaimable_hours": 0.0,
            "items": [],
        }

    candidates["urgency"] = candidates.apply(_urgency, axis=1)
    candidates = candidates.sort_values("urgency", ascending=False).reset_index(drop=True)

    total = len(candidates)
    items = []
    for rank, row in candidates.iterrows():
        deadline = _deadline_for_rank(rank, total)
        action = ACTION_LABELS[row["category"]]

        reasons = []
        if row["documented"] == "yes" and row["trained_replacement"] == "yes":
            reasons.append("already documented with a trained replacement ready, no reason to wait")
        elif row["documented"] == "yes":
            reasons.append("documented but no trained replacement yet, train someone on this first")
        elif row["trained_replacement"] == "yes":
            reasons.append("a trained replacement exists but the process isn't written down, document it as you hand it off")
        else:
            reasons.append("not documented and no replacement trained yet, this needs prep before it moves")

        if row["risk"] == "high":
            reasons.append("flagged high risk if it's dropped, hand off with a check-in built in, not a clean cutover")
        elif row["risk"] == "low":
            reasons.append("low risk if it's dropped, safe to hand off cleanly")

        items.append({
            "task": row["task"],
            "action": action,
            "hours_per_week": round(row["hours_per_week"], 1),
            "deadline": deadline,
            "reasoning": "; ".join(reasons).capitalize() + ".",
        })

    reclaimable_hours = round(candidates["hours_per_week"].sum(), 1)

    return {
        "owner_only_hours": owner_only_hours,
        "reclaimable_hours": reclaimable_hours,
        "items": items,
    }
