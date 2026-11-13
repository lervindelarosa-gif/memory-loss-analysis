"""How good is the outreach model? Checks on the people it did not train on.

Same split and settings as business_analysis.py. The checks cover: score on training and test data,
how well the score sorts people into ten equal groups, and the score for different groups of people.

Usage:  python src/model_checks.py   (run src/build_table.py first)
Output: reports/model_checks.md (group totals only)
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
cols = ["age", "female", "education_level", "income_level", "depression", "deaf", "stroke", "copd", "heart_disease",
        "diabetes", "no_exercise", "current_smoker", "obese"]

train, test = train_test_split(df, test_size=0.25, stratify=df["memory_loss"], random_state=SEED)
model = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, class_weight="balanced",
                                       random_state=SEED)
model.fit(train[cols], train["memory_loss"])
train = train.assign(score=model.predict_proba(train[cols])[:, 1])
test = test.assign(score=model.predict_proba(test[cols])[:, 1])


def rate(d):
    return round(100 * (d["memory_loss"] * d["weight"]).sum() / d["weight"].sum(), 1)


def auc(d):
    return roc_auc_score(d["memory_loss"], d["score"])


rng = np.random.default_rng(SEED)
boot = [auc(test.iloc[rng.integers(0, len(test), len(test))]) for _ in range(200)]
low, high = np.percentile(boot, [2.5, 97.5])

# Ten equal groups of adults (using the survey weights), highest scores first
ranked = test.sort_values("score", ascending=False)
share = ranked["weight"].cumsum() / ranked["weight"].sum()
ranked = ranked.assign(group=np.minimum((share * 10).astype(int), 9) + 1)
tenths = pd.DataFrame([{"Group (1 = highest scores)": g, "People": len(d), "% reporting memory loss": rate(d)}
                       for g, d in ranked.groupby("group")])

GROUPS = {"Ages 45-64": test["age_band"] == "45-64", "Ages 65+": test["age_band"] == "65+",
          "Women": test["female"] == 1, "Men": test["female"] == 0,
          "Income under $25k": test["income_level"] <= 2, "Income $100k+": test["income_level"] >= 6}
by_group = pd.DataFrame([{"Group": name, "People": int(mask.sum()), "ROC AUC": round(auc(test[mask]), 3)}
                         for name, mask in GROUPS.items()])

lines = ["# How good is the outreach model?", "",
         f"Tested on {len(test):,} people the model did not train on. Finds people reporting memory loss now.", "",
         f"ROC AUC: {auc(train):.3f} on training data, {auc(test):.3f} on test data "
         f"(95% interval {low:.3f}-{high:.3f}). This is fair.", "",
         f"Average: {rate(test)}% report memory loss.", "",
         "## Ten equal groups, sorted by model score", "", tenths.to_markdown(index=False), "",
         "## Score for different groups", "", by_group.to_markdown(index=False), "",
         "All checks use the same survey. Real health records could give weaker results."]
(ROOT / "reports" / "model_checks.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
