"""Outreach scenario: who should a health team reach first? (BRFSS 2023 + 2024, people 45+)

An example scenario, not a real client. For outreach only, never for pricing or refusing cover.

1. Group sizes: how many adults does each group represent, and what share of all reported memory loss?
2. Targeting: on a test set the model never saw, how much reported memory loss do we reach if we contact
   the people the model ranks highest, compared with oldest-first and with picking at random?

The weights give one average year in these 37 states. Estimates are rough: not all states asked the question.
The model finds people who report memory loss NOW (same interview). It does not predict the future.

Usage:  python src/business_analysis.py   (run src/build_table.py first)
Output: tableau/biz_groups.csv, tableau/biz_gains.csv, reports/business_results.md (group totals only)
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent
SEED = 42
MIN_GROUP = 50
df = pd.read_csv(ROOT / "data" / "processed" / "brfss_2023_2024.csv")

def rate(d, w="weight"):
    return 100 * (d["memory_loss"] * d[w]).sum() / d[w].sum()


# ---- 1. Groups ----
young = df["age_band"] == "45-64"
low_income = df["income"].str[0].isin(["1", "2"])  # under $25k
SEGMENTS = {
    "Everyone 45+": pd.Series(True, index=df.index),
    "Everyone 65+ (age only)": ~young,
    "Everyone 45-64": young,
    "45-64, low income (under $25k)": young & low_income,
    "45-64, depression": young & (df["depression"] == 1),
    "45-64, hearing problem": young & (df["deaf"] == 1),
    "45-64, stroke": young & (df["stroke"] == 1),
    "45-64, any of: low income, depression, hearing": young & (low_income | (df["depression"] == 1) | (df["deaf"] == 1)),
    "65+, low income (under $25k)": ~young & low_income,
    "65+, depression": ~young & (df["depression"] == 1),
    "65+, hearing problem": ~young & (df["deaf"] == 1),
    "65+, stroke": ~young & (df["stroke"] == 1),
}
all_cases = (df["memory_loss"] * df["weight"]).sum()
rows = []
for name, mask in SEGMENTS.items():
    g = df[mask]
    if len(g) < MIN_GROUP:
        continue
    adults = g["weight"].sum()
    cases = (g["memory_loss"] * g["weight"]).sum()
    rows.append({"group": name, "people_in_survey": len(g), "est_adults": int(round(adults, -3)),
                 "memory_loss_pct": round(100 * cases / adults, 1), "est_with_memory_loss": int(round(cases, -3)),
                 "share_of_all_cases_pct": round(100 * cases / all_cases, 1)})
groups = pd.DataFrame(rows)
groups.to_csv(ROOT / "tableau" / "biz_groups.csv", index=False)

# ---- 2. Targeting on a test set ----
df["education_level"] = df["education"].str[0].astype(float)
df["income_level"] = df["income"].str[0].astype(float)
cols = ["age", "female", "education_level", "income_level", "depression", "deaf", "stroke", "copd", "heart_disease",
        "diabetes", "no_exercise", "current_smoker", "obese"]
train, test = train_test_split(df, test_size=0.25, stratify=df["memory_loss"], random_state=SEED)
model = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, class_weight="balanced",
                                       random_state=SEED)
model.fit(train[cols], train["memory_loss"])
test = test.assign(score=model.predict_proba(test[cols])[:, 1])
rng = np.random.default_rng(SEED)
test["tiebreak"] = rng.random(len(test))  # age stops at 80, so break ties at random
STEPS = list(range(5, 101, 5))


def gains(d, by):
    """Weighted share of all cases reached when contacting the top p% of adults, ranked by `by`."""
    d = d.sort_values(by, ascending=False)
    w = d["weight"].to_numpy()
    c = (d["memory_loss"] * d["weight"]).to_numpy()
    reached, found = np.cumsum(w) / w.sum(), np.cumsum(c) / c.sum()
    return np.interp(np.array(STEPS) / 100, reached, found) * 100


test["age_rank"] = test["age"] + test["tiebreak"] / 10
gain = pd.DataFrame({"pct_contacted": STEPS, "pct_cases_model": gains(test, "score").round(1),
                     "pct_cases_oldest_first": gains(test, "age_rank").round(1), "pct_cases_random": STEPS})
gain.to_csv(ROOT / "tableau" / "biz_gains.csv", index=False)

# Uncertainty for the headline: bootstrap the test set
i20 = STEPS.index(20)
boot = []
for _ in range(300):
    s = test.iloc[rng.integers(0, len(test), len(test))]
    boot.append((gains(s, "score")[i20], gains(s, "age_rank")[i20]))
boot = np.array(boot)
ci_model = np.percentile(boot[:, 0], [2.5, 97.5]).round(1)
ci_age = np.percentile(boot[:, 1], [2.5, 97.5]).round(1)

auc = roc_auc_score(test["memory_loss"], test["score"])
top = gain.iloc[i20]
lines = ["# Outreach scenario: who to reach first (BRFSS 2023 + 2024)", "",
         "An example scenario, not a real client. For outreach only, never for pricing or refusing cover.", "",
         "## Group sizes (one average year, 37 states, rounded, rough)", "", groups.to_markdown(index=False), "",
         f"## Targeting on the test set ({len(test):,} people, ROC AUC {auc:.3f})", "",
         gain[gain["pct_contacted"].isin([5, 10, 20, 30, 50])].to_markdown(index=False), "",
         f"Contact 20%: model reaches {top['pct_cases_model']}% of cases (95% interval {ci_model[0]}-{ci_model[1]}), "
         f"oldest first {top['pct_cases_oldest_first']}% ({ci_age[0]}-{ci_age[1]}), random 20%.", "",
         "The model uses answers from the same interview, including depression and hearing. "
         "A real organisation may not have these answers for its members, and would get weaker results without them.", "",
         "Data: CDC BRFSS 2023 and 2024, national files, Cognitive Decline module."]
(ROOT / "reports" / "business_results.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
