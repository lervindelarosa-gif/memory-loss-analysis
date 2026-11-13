"""Small, ready-to-plot tables for the Tableau dashboard (BRFSS 2023 + 2024, people 45+).

Each table feeds one chart, so Tableau needs no filters or calculations.
Percentages use the survey weights. Group totals only; groups with fewer than 50 people are hidden.

Usage:  python src/make_dashboard_tables.py   (run build_table.py and ml_model.py first)
Output: tableau/dash_groups.csv, dash_age.csv, dash_income.csv, dash_education.csv,
        dash_health.csv, dash_model.csv, dash_age_income.csv, dash_state.csv
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

# US state FIPS codes, so Tableau can draw the states on a map
STATES = {1: "Alabama", 2: "Alaska", 4: "Arizona", 5: "Arkansas", 6: "California", 8: "Colorado", 9: "Connecticut",
          10: "Delaware", 11: "District of Columbia", 12: "Florida", 13: "Georgia", 15: "Hawaii", 16: "Idaho",
          17: "Illinois", 18: "Indiana", 19: "Iowa", 20: "Kansas", 21: "Kentucky", 22: "Louisiana", 23: "Maine",
          24: "Maryland", 25: "Massachusetts", 26: "Michigan", 27: "Minnesota", 28: "Mississippi", 29: "Missouri",
          30: "Montana", 31: "Nebraska", 32: "Nevada", 33: "New Hampshire", 34: "New Jersey", 35: "New Mexico",
          36: "New York", 37: "North Carolina", 38: "North Dakota", 39: "Ohio", 40: "Oklahoma", 41: "Oregon",
          42: "Pennsylvania", 44: "Rhode Island", 45: "South Carolina", 46: "South Dakota", 47: "Tennessee",
          48: "Texas", 49: "Utah", 50: "Vermont", 51: "Virginia", 53: "Washington", 54: "West Virginia",
          55: "Wisconsin", 56: "Wyoming", 66: "Guam", 72: "Puerto Rico", 78: "Virgin Islands"}

tables = {
    "dash_groups.csv": groups,
    "dash_age.csv": summary(df, ["age_group"]),
    "dash_income.csv": summary(df, ["group", "income"]),
    "dash_age_income.csv": summary(df, ["age_group", "income"]),
    "dash_state.csv": summary(df.assign(state_name=df["state"].map(STATES)), ["state_name"]),
    "dash_education.csv": summary(df, ["group", "education"]),
    "dash_health.csv": health,
    "dash_model.csv": pd.read_csv(OUT / "ml_importance.csv"),
}
# Age-adjusted state rates: each state's age-group rates, combined using the age mix of all people in the survey
age_mix = df.groupby("age_group")["weight"].sum() / df["weight"].sum()
by_state_age = df.assign(state_name=df["state"].map(STATES), cases=df["memory_loss"] * df["weight"]).groupby(
    ["state_name", "age_group"])[["cases", "weight"]].sum()
state_rates = (by_state_age["cases"] / by_state_age["weight"]).unstack("age_group")
adjusted = 100 * (state_rates * age_mix).sum(axis=1) / state_rates.notna().mul(age_mix).sum(axis=1)
tables["dash_state.csv"]["age_adjusted_pct"] = tables["dash_state.csv"]["state_name"].map(adjusted).round(1)

# Patterns by state, and how much memory loss each state would have from its people's patterns alone.
# Expected = weighted logistic regression on age group, sex, education, income and 9 health factors (no state).
from sklearn.linear_model import LogisticRegression  # noqa: E402

HEALTH = ["stroke", "diabetes", "heart_disease", "copd", "depression", "no_exercise", "current_smoker", "obese", "deaf"]
X = pd.get_dummies(df[["age_group", "education", "income"]].fillna("Unknown"), drop_first=True).astype(float)
X["female"] = df["female"]
for c in HEALTH:
    X[c] = df[c].fillna(0)
    X[c + "_unknown"] = df[c].isna().astype(float)
lr = LogisticRegression(C=1e6, max_iter=3000).fit(X, df["memory_loss"], sample_weight=df["weight"])
pat = df.assign(state_name=df["state"].map(STATES), expected=lr.predict_proba(X)[:, 1],
                low_income=df["income"].isin(["1 Under $15k", "2 $15-25k"]).astype(float).where(df["income"].notna()))


def wpct(g, col):
    m = g[col].notna()
    return 100 * (g.loc[m, col] * g.loc[m, "weight"]).sum() / g.loc[m, "weight"].sum()


st_tab = tables["dash_state.csv"]
for col, name in [("expected", "expected_pct"), ("low_income", "low_income_pct"),
                  ("depression", "depression_pct"), ("deaf", "hearing_pct")]:
    st_tab[name] = st_tab["state_name"].map(pat.groupby("state_name").apply(wpct, col, include_groups=False)).round(1)
st_tab["vs_expected"] = (st_tab["memory_loss_pct"] - st_tab["expected_pct"]).round(1)

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
