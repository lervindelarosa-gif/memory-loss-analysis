"""Small, ready-to-plot tables for the Tableau dashboard (BRFSS 2023 + 2024, people 45+).

Each table feeds one chart, so Tableau needs no filters or calculations.
Percentages use the survey weights. Group totals only; groups with fewer than 50 people are hidden.

Usage:  python src/make_dashboard_tables.py   (run build_table.py and ml_model.py first)
Output: tableau/dash_groups.csv, dash_age.csv, dash_income.csv, dash_education.csv,
        dash_health.csv, dash_model.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tableau"
MIN_GROUP = 50

df = pd.read_csv(ROOT / "data" / "processed" / "brfss_2023_2024.csv")
df["group"] = df["age_band"].map({"45-64": "Younger (45-64)", "65+": "Older (65+)"})


def summary(d, by):
    d = d.dropna(subset=by)
    t = d.groupby(by).apply(lambda g: pd.Series({
        "people": len(g),
        "with_memory_loss": int(g["memory_loss"].sum()),
        "memory_loss_pct": round(100 * (g["memory_loss"] * g["weight"]).sum() / g["weight"].sum(), 1)}),
        include_groups=False)
    t = t.reset_index()
    t[["people", "with_memory_loss"]] = t[["people", "with_memory_loss"]].astype(int)
    return t[t["people"] >= MIN_GROUP]


groups = pd.concat([summary(df, ["group"]),
                    summary(df.assign(group="Everyone (45+)"), ["group"])], ignore_index=True)

health_names = {"depression": "Depression", "deaf": "Deaf / hearing problem", "stroke": "Stroke",
                "copd": "COPD", "heart_disease": "Heart disease", "diabetes": "Diabetes",
                "no_exercise": "No exercise", "current_smoker": "Current smoker", "obese": "Obese"}
health = []
for col, name in health_names.items():
    t = summary(df[df[col] == 1], ["group"])
    t.insert(0, "factor", name)
    health.append(t)
no_factor = summary(df[df[list(health_names)].fillna(0).sum(axis=1) == 0], ["group"])
no_factor.insert(0, "factor", "None of these")
health = pd.concat(health + [no_factor], ignore_index=True)

tables = {
    "dash_groups.csv": groups,
    "dash_age.csv": summary(df, ["age_group"]),
    "dash_income.csv": summary(df, ["group", "income"]),
    "dash_education.csv": summary(df, ["group", "education"]),
    "dash_health.csv": health,
    "dash_model.csv": pd.read_csv(OUT / "ml_importance.csv"),
}
for name, t in tables.items():
    if "memory_loss_pct" in t:  # text labels with words, so Tableau keeps them as text (no number formatting)
        t["pct_label"] = t["memory_loss_pct"].map("{:.1f}% memory loss".format)
        t["people_label"] = t["people"].map("{:,} people".format)
        t["with_label"] = t["with_memory_loss"].map("{:,} with memory loss".format)
    t.to_csv(OUT / name, index=False)
    print(f"{name:20s} {len(t):3d} rows")

# ---- BRFSS vs NHANES: same groups side by side (needs src/nhanes_analysis.py first) ----
# BRFSS = people SAY their memory is getting worse; NHANES = people SCORE LOW on memory tests
nh = pd.read_csv(OUT / "nhanes_groups.csv")
inc, edu = tables["dash_income.csv"], tables["dash_education.csv"]
ITEMS = [  # (label, BRFSS rows, NHANES category)
    ("1 Everyone", groups[groups["group"] != "Everyone (45+)"], "Everyone"),
    ("2 Lowest income", inc[inc["income"] == "1 Under $15k"], "Under $25k"),
    ("3 Highest income", inc[inc["income"] == "7 $200k+"], "$100k+"),
    ("4 Less than high school", edu[edu["education"] == "1 Less than high school"], "Less than high school"),
    ("5 College graduate", edu[edu["education"] == "4 College graduate"], "College graduate"),
    ("6 Depression", health[health["factor"] == "Depression"], "Depression"),
    ("7 Hearing problem", health[health["factor"] == "Deaf / hearing problem"], "Hearing problem"),
    ("8 Stroke", health[health["factor"] == "Stroke"], "Stroke"),
    ("9 No exercise", health[health["factor"] == "No exercise"], "No exercise"),
]
rows = []
for label, b, cat in ITEMS:
    for _, r in b.iterrows():
        rows.append({"item": label, "group": "1 Younger" if "Younger" in r["group"] else "2 Older",
                     "measure": "BRFSS: say memory is worse", "pct": r["memory_loss_pct"], "people": r["people"]})
    for _, r in nh[nh["category"] == cat].iterrows():
        rows.append({"item": label, "group": "1 Younger" if "Younger" in r["group"] else "2 Older",
                     "measure": "NHANES: low memory test score", "pct": r["low_test_score_pct"],
                     "people": r["people"]})
compare = pd.DataFrame(rows)
compare["pct_label"] = compare["pct"].map("{:.1f}%".format)
compare.to_csv(OUT / "dash_compare.csv", index=False)
print(f"{'dash_compare.csv':20s} {len(compare):3d} rows")
