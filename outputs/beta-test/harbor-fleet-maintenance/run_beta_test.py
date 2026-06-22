"""
Runs Harbor Fleet Maintenance's data through all seven Business Without You
milestone tools and prints every result, so the framework can be checked
end to end before it goes in front of a paying client.
"""
import importlib.util
import json
import pandas as pd

ROOT = "/Users/matthewfitzpatrick-buck/Desktop/matthew-fitzpatrick-aios-main"
DATA = f"{ROOT}/outputs/beta-test/harbor-fleet-maintenance"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m1 = load_module("m1_analysis", f"{ROOT}/apps/reclaim-protocol/analysis.py")
m2 = load_module("m2_analysis", f"{ROOT}/apps/impact-map/analysis.py")
m3 = load_module("m3_analysis", f"{ROOT}/apps/dashboard-selector/analysis.py")
m4 = load_module("m4_analysis", f"{ROOT}/apps/profit-discovery-audit/analysis.py")
m5 = load_module("m5_analysis", f"{ROOT}/apps/cash-confidence/analysis.py")
m6 = load_module("m6_analysis", f"{ROOT}/apps/bottleneck-breakthrough/analysis.py")
m7 = load_module("m7_analysis", f"{ROOT}/apps/team-builder/analysis.py")


def section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def dump(result):
    print(json.dumps(result, indent=2, default=str))


# Milestone 1
section("MILESTONE 1 — Reclaim the Owner's Time and Identity")
df = m1.load_time_log(pd.read_csv(f"{DATA}/m1_time_log.csv"))
dump(m1.build_protocol(df))

# Milestone 2
section("MILESTONE 2 — Define the Destination with Precision")
df = m2.load_initiatives(pd.read_csv(f"{DATA}/m2_initiatives.csv"))
dump(m2.build_impact_map(df))

# Milestone 3
section("MILESTONE 3 — Install the Dashboard That Tells the Truth")
df = m3.load_metrics(pd.read_csv(f"{DATA}/m3_metrics.csv"))
dump(m3.build_dashboard(df))

# Milestone 4
section("MILESTONE 4 — Discover the Hidden Profit")
pnl_raw = pd.read_csv(f"{DATA}/m4_pnl.csv")
breakdown_raw = pd.read_csv(f"{DATA}/m4_breakdown.csv")
dump(m4.run_full_audit(pnl_raw, breakdown_raw,
                        business_type="Trades, field service, or repair", period_months=3))

# Milestone 5
section("MILESTONE 5 — Build Cash Confidence")
cash_raw = pd.read_csv(f"{DATA}/m5_cash_items.csv")
exp_raw = pd.read_csv(f"{DATA}/m5_recurring_expenses.csv")
dump(m5.run_cash_confidence(cash_raw, exp_raw, starting_balance=15000))

# Milestone 6
section("MILESTONE 6 — Break the Binding Constraint")
df = m6.load_constraints(pd.read_csv(f"{DATA}/m6_constraints.csv"))
dump(m6.build_breakthrough_plan(df))

# Milestone 7
section("MILESTONE 7 — Build the Team That Builds the Business")
roles_raw = pd.read_csv(f"{DATA}/m7_roles.csv")
candidates_raw = pd.read_csv(f"{DATA}/m7_candidates.csv")
dump(m7.run_team_builder(roles_raw, candidates_raw))
