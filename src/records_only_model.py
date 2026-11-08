"""Would the outreach model still work with only the data a health organisation is likely to have?

Same split, same settings and same test people as business_analysis.py. Only the inputs change.
The answers still come from the survey, not from real medical records, and real records can be
incomplete, so a real organisation could get weaker results than these.

Usage:  python src/records_only_model.py   (run src/build_table.py first)
Output: reports/records_only_results.md (group totals only)
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent
SEED = 42
df = pd.read_csv(ROOT / "data" / "processed" / "brfss_2023_2024.csv")
df["education_level"] = df["education"].str[0].astype(float)
df["income_level"] = df["income"].str[0].astype(float)

RECORDS = ["age", "female", "depression", "deaf", "stroke", "copd", "heart_disease", "diabetes"]
INPUTS = {
    "All survey answers (slide 9)": RECORDS + ["education_level", "income_level", "no_exercise", "current_smoker",
                                               "obese"],
    "Records plus smoking and weight": RECORDS + ["current_smoker", "obese"],
    "Records only": RECORDS,
    "Records without depression": [c for c in RECORDS if c != "depression"],
    "Records without hearing": [c for c in RECORDS if c != "deaf"],
    "Age and sex only": ["age", "female"],
}

train, test = train_test_split(df, test_size=0.25, stratify=df["memory_loss"], random_state=SEED)
rng = np.random.default_rng(SEED)


def reach_at_20(d, by):
    """Weighted share of all cases reached when contacting the top 20% of adults, ranked by `by`."""
    d = d.sort_values(by, ascending=False)
    w = d["weight"].to_numpy()
    c = (d["memory_loss"] * d["weight"]).to_numpy()
    return float(np.interp(0.20, np.cumsum(w) / w.sum(), np.cumsum(c) / c.sum()) * 100)


test = test.assign(tiebreak=rng.random(len(test)))
test["age_rank"] = test["age"] + test["tiebreak"] / 10

rows = []
for name, cols in INPUTS.items():
    model = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31,
                                           class_weight="balanced", random_state=SEED)
    model.fit(train[cols], train["memory_loss"])
    scored = test.assign(score=model.predict_proba(test[cols])[:, 1])
    boot = [reach_at_20(scored.iloc[rng.integers(0, len(scored), len(scored))], "score") for _ in range(300)]
    low, high = np.percentile(boot, [2.5, 97.5])
    rows.append({"Inputs": name, "Number of inputs": len(cols), "Reached at 20% contacted": round(reach_at_20(scored, "score"), 1),
                 "95% interval": f"{low:.1f}-{high:.1f}", "ROC AUC": round(roc_auc_score(scored["memory_loss"], scored["score"]), 3)})

table = pd.DataFrame(rows)
lines = ["# Outreach model with only the data a health organisation is likely to have", "",
         f"Tested on {len(test):,} people the model did not train on. Example scenario, for outreach only.", "",
         table.to_markdown(index=False), "",
         f"Oldest first reaches {reach_at_20(test, 'age_rank'):.1f}%. Picking at random reaches 20.0%.", "",
         "Records only = age, sex, depression, hearing problem, stroke, COPD, heart disease, diabetes.",
         "These answers still come from the survey, not from real records, which can be incomplete.",
         "So a real organisation could get weaker results. A pilot would be needed to check."]
(ROOT / "reports" / "records_only_results.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
