"""Does a model trained on BRFSS also work on NHANES (people aged 60+)?

The model is trained only on BRFSS, using inputs that both surveys share. It is then scored on NHANES people
it never saw. Two answers are checked: people who SAY they have memory problems, and people who SCORE LOW
on memory tests. Income bands and some health questions differ between surveys, so the match is approximate.

Usage:  python src/nhanes_validation.py   (run src/build_table.py and src/build_nhanes.py first)
Output: reports/nhanes_validation.md (group totals only)
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent
SEED = 42
brfss = pd.read_csv(ROOT / "data" / "processed" / "brfss_2023_2024.csv")
nhanes = pd.read_csv(ROOT / "data" / "processed" / "nhanes_2011_2014.csv")

# Put income on the same 4 bands. BRFSS: 25-50k and 50-100k stand in for NHANES 25-55k and 55-100k
brfss["income_band"] = brfss["income"].str[0].astype(float).map({1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 4, 7: 4})
nhanes["income_band"] = nhanes["income"].str[0].astype(float)
for d in (brfss, nhanes):
    d["education_level"] = d["education"].str[0].astype(float)

cols = ["age", "female", "education_level", "income_band", "depression", "stroke", "heart_disease", "copd",
        "diabetes", "no_exercise", "current_smoker"]

train, brfss_test = train_test_split(brfss, test_size=0.25, stratify=brfss["memory_loss"], random_state=SEED)
model = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, class_weight="balanced",
                                       random_state=SEED)
model.fit(train[cols], train["memory_loss"])
rng = np.random.default_rng(SEED)


def reach(d, y, by):
    """Weighted share of all cases reached when contacting the top 20% of adults, ranked by `by`."""
    d = d.sort_values(by, ascending=False)
    w = d["weight"].to_numpy()
    c = (d[y] * d["weight"]).to_numpy()
    return float(np.interp(0.20, np.cumsum(w) / w.sum(), np.cumsum(c) / c.sum()) * 100)


def check(name, data, y):
    d = data.dropna(subset=[y]).copy()
    d["score"] = model.predict_proba(d[cols])[:, 1]
    d["age_rank"] = d["age"] + rng.random(len(d)) / 10
    boot = []
    for _ in range(500):
        s = d.iloc[rng.integers(0, len(d), len(d))]
        boot.append((roc_auc_score(s[y], s["score"], sample_weight=s["weight"]), reach(s, y, "score"),
                     reach(s, y, "age_rank")))
    low, high = np.percentile(boot, [2.5, 97.5], axis=0)
    return {"Tested on": name, "People": len(d), "% with the outcome": round(100 * (d[y] * d["weight"]).sum() / d["weight"].sum(), 1),
            "ROC AUC (model)": f"{roc_auc_score(d[y], d['score'], sample_weight=d['weight']):.3f} ({low[0]:.3f}-{high[0]:.3f})",
            "ROC AUC (age only)": f"{roc_auc_score(d[y], d['age_rank'], sample_weight=d['weight']):.3f}",
            "Reached at 20%, model": f"{reach(d, y, 'score'):.1f}% ({low[1]:.1f}-{high[1]:.1f})",
            "Reached at 20%, oldest first": f"{reach(d, y, 'age_rank'):.1f}% ({low[2]:.1f}-{high[2]:.1f})"}


brfss_60 = brfss_test[brfss_test["age"] >= 60]
table = pd.DataFrame([check("BRFSS 60+ (not used in training): say memory is worse", brfss_60, "memory_loss"),
                      check("NHANES 60+: say they have memory problems", nhanes, "memory_complaint"),
                      check("NHANES 60+: low memory test score", nhanes, "low_test_score")])
lines = ["# Does the BRFSS model also work on NHANES?", "",
         "Trained only on BRFSS with inputs both surveys share. 95% intervals in brackets (simple bootstrap).", "",
         "Inputs: " + ", ".join(cols) + ". Income bands and the depression and exercise questions differ between surveys.", "",
         table.to_markdown(index=False), "", "Only covers people aged 60+. Picking at random reaches 20%."]
(ROOT / "reports" / "nhanes_validation.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
print("\nMissing input values in NHANES (%):")
print((nhanes[cols].isna().mean() * 100).round(1).to_string())
