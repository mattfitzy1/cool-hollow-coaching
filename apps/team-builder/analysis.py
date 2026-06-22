"""
Core scoring and templating logic for Business Without You Build the Team.

This is Milestone 7's model, the last of the seven. The owner runs the
exercise first: a role inventory with current job descriptions, a
delegation map draft showing how much of each role the owner still holds,
and (where hiring is live) a list of candidates being considered.

This module takes that role inventory and produces:
1. A delegation-level score per role, ranking roles by how far they sit
   from where they need to be, so the owner knows which role to fix first.
2. An outcome-based hiring template per role, built from the role's own
   key outcomes, decision rights, and success metric, ready to use instead
   of a generic job description.
3. A leadership-trait scorecard for any candidates uploaded against a
   role, ranking them and naming the top candidate per role.
"""

import pandas as pd

TRAIT_COLUMNS = ["ownership", "communication", "judgment", "coachability", "results_track_record"]


def load_roles(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the uploaded role inventory and delegation map."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    required = {
        "role_name", "current_delegation_level", "target_delegation_level",
        "key_outcome_1", "key_outcome_2", "key_outcome_3",
        "decision_rights", "success_metric",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Role list is missing column(s): {', '.join(sorted(missing))}. "
            f"Expected: role_name, current_delegation_level (1-5), "
            f"target_delegation_level (1-5), key_outcome_1, key_outcome_2, "
            f"key_outcome_3, decision_rights, success_metric."
        )

    df["role_name"] = df["role_name"].astype(str)
    df["current_delegation_level"] = pd.to_numeric(df["current_delegation_level"], errors="coerce").fillna(0).clip(0, 5)
    df["target_delegation_level"] = pd.to_numeric(df["target_delegation_level"], errors="coerce").fillna(0).clip(0, 5)
    for col in ("key_outcome_1", "key_outcome_2", "key_outcome_3", "decision_rights", "success_metric"):
        df[col] = df[col].astype(str)

    return df[[
        "role_name", "current_delegation_level", "target_delegation_level",
        "key_outcome_1", "key_outcome_2", "key_outcome_3",
        "decision_rights", "success_metric",
    ]]


def load_candidates(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the uploaded candidate list with leadership-trait ratings."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    required = {"candidate_name", "role_name"} | set(TRAIT_COLUMNS)
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Candidate list is missing column(s): {', '.join(sorted(missing))}. "
            f"Expected: candidate_name, role_name, and five 1-5 ratings: "
            f"{', '.join(TRAIT_COLUMNS)}."
        )

    df["candidate_name"] = df["candidate_name"].astype(str)
    df["role_name"] = df["role_name"].astype(str)
    for col in TRAIT_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).clip(0, 5)

    return df[["candidate_name", "role_name"] + TRAIT_COLUMNS]


def build_delegation_scores(roles: pd.DataFrame) -> list:
    """Score and rank every role by how far it sits from its target delegation level."""
    if roles.empty:
        return []

    df = roles.copy()
    df["delegation_gap"] = df["target_delegation_level"] - df["current_delegation_level"]
    df = df.sort_values("delegation_gap", ascending=False)

    scores = []
    for rank, (_, row) in enumerate(df.iterrows(), start=1):
        scores.append({
            "rank": rank,
            "role_name": row["role_name"],
            "current_delegation_level": int(row["current_delegation_level"]),
            "target_delegation_level": int(row["target_delegation_level"]),
            "delegation_gap": round(row["delegation_gap"], 1),
        })
    return scores


def build_hiring_template(row: pd.Series) -> str:
    outcomes = [row["key_outcome_1"], row["key_outcome_2"], row["key_outcome_3"]]
    outcomes = [o for o in outcomes if o and o.lower() != "nan"]
    outcome_lines = "\n".join(f"  {i+1}. {o}" for i, o in enumerate(outcomes))
    return (
        f"Role: {row['role_name']}\n"
        f"Key outcomes (what this role owns, not just what it does):\n{outcome_lines}\n"
        f"Decision rights: {row['decision_rights']}\n"
        f"Success metric: {row['success_metric']}\n"
    )


def build_hiring_templates(roles: pd.DataFrame) -> list:
    """Build an outcome-based hiring template for every role."""
    templates = []
    for _, row in roles.iterrows():
        templates.append({
            "role_name": row["role_name"],
            "template": build_hiring_template(row),
        })
    return templates


def build_leadership_scorecard(candidates: pd.DataFrame) -> dict:
    """Score and rank candidates per role, flagging the top candidate."""
    if candidates.empty:
        return {}

    df = candidates.copy()
    df["composite"] = df[TRAIT_COLUMNS].mean(axis=1)

    scorecard = {}
    for role_name, group in df.groupby("role_name"):
        ranked = group.sort_values("composite", ascending=False)
        candidates_for_role = []
        for rank, (_, row) in enumerate(ranked.iterrows(), start=1):
            candidates_for_role.append({
                "rank": rank,
                "candidate_name": row["candidate_name"],
                "composite": round(row["composite"], 1),
                "is_top_candidate": rank == 1,
                "traits": {t: round(row[t], 1) for t in TRAIT_COLUMNS},
            })
        scorecard[role_name] = candidates_for_role
    return scorecard


def run_team_builder(roles_raw: pd.DataFrame, candidates_raw: pd.DataFrame = None) -> dict:
    roles = load_roles(roles_raw)
    delegation_scores = build_delegation_scores(roles)
    hiring_templates = build_hiring_templates(roles)

    scorecard = {}
    unmatched_roles = []
    if candidates_raw is not None and not candidates_raw.empty:
        candidates = load_candidates(candidates_raw)
        scorecard = build_leadership_scorecard(candidates)

        known_roles = set(roles["role_name"])
        unmatched_roles = sorted(set(candidates["role_name"]) - known_roles)

    return {
        "delegation_scores": delegation_scores,
        "hiring_templates": hiring_templates,
        "leadership_scorecard": scorecard,
        "unmatched_roles": unmatched_roles,
    }
