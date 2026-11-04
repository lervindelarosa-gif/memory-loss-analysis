"""Machine learning: which factors does a model need to spot memory loss? (BRFSS 2023 + 2024)

BRFSS asks different people each year, so we cannot predict the future here.
The model learns who REPORTS memory loss getting worse, from the same interview.

Two models: logistic regression and gradient boosting (fast trees that handle missing values).
Both are balanced with class weights (only about 16% report memory loss).
Importance: permutation importance on the test set, for younger (45-64) and older (65+) separately.

Usage:  python src/ml_model.py
Output: reports/ml_results.md, reports/figures/05_ml_importance.png, tableau/ml_importance.csv
        (summary results only, no saved model)
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
SEED = 42
df = pd.read_csv(ROOT / "data" / "processed" / "brfss_2023_2024.csv")

# Ordered numbers for education (1-4) and income (1-7); unknown income stays missing
df["education_level"] = df["education"].str[0].astype(float)
df["income_level"] = df["income"].str[0].astype(float)
df["younger"] = df["age_band"] == "45-64"

FEATURES = {"age": "Age", "female": "Female", "education_level": "Education", "income_level": "Income",
            "depression": "Depression", "deaf": "Deaf / hearing problem", "stroke": "Stroke", "copd": "COPD",
            "heart_disease": "Heart disease", "diabetes": "Diabetes", "no_exercise": "No exercise",
            "current_smoker": "Current smoker", "obese": "Obese"}
cols = list(FEATURES)
y = df["memory_loss"]


def models():
    return {
        "Logistic regression": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                             LogisticRegression(class_weight="balanced", max_iter=2000)),
        "Gradient boosting": HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31,
                                                            class_weight="balanced", random_state=SEED),
    }


# ---- 1. Cross-validation ----
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
cv_rows = []
for name, model in models().items():
    s = cross_validate(model, df[cols], y, cv=cv, scoring=["roc_auc", "average_precision", "recall"])
    cv_rows.append({"Model": name, "ROC AUC": f"{s['test_roc_auc'].mean():.3f} (± {s['test_roc_auc'].std():.3f})",
                    "PR AUC": f"{s['test_average_precision'].mean():.3f}",
                    "Cases found (recall)": f"{s['test_recall'].mean():.0%}", "_auc": s["test_roc_auc"].mean()})
cv_table = pd.DataFrame(cv_rows)

# ---- 2. Test set: younger vs older ----
train, test = train_test_split(df, test_size=0.25, stratify=y, random_state=SEED)
fitted, sub_rows = {}, []
for name, model in models().items():
    model.fit(train[cols], train["memory_loss"])
    fitted[name] = model
    risk = model.predict_proba(test[cols])[:, 1]
    row = {"Model": name}
    for label, mask in [("Everyone", np.ones(len(test), bool)), ("Younger (45-64)", test["younger"].values),
                        ("Older (65+)", ~test["younger"].values)]:
        row[label] = f"{roc_auc_score(test['memory_loss'][mask], risk[mask]):.3f}"
    sub_rows.append(row)
sub_table = pd.DataFrame(sub_rows)

# ---- 3. Permutation importance (best model), per age group ----
best = max(cv_rows, key=lambda r: r["_auc"])["Model"]
imp = {}
for label, part in [("Younger (45-64)", test[test["younger"]]), ("Older (65+)", test[~test["younger"]])]:
    part = part.sample(min(len(part), 15000), random_state=SEED)
    r = permutation_importance(fitted[best], part[cols], part["memory_loss"], scoring="roc_auc",
                               n_repeats=10, random_state=SEED, n_jobs=-1)
    imp[label] = pd.Series(r.importances_mean, index=[FEATURES[c] for c in cols])
imp = pd.DataFrame(imp).sort_values("Younger (45-64)", ascending=False)
imp_table = imp.round(4).reset_index().rename(columns={"index": "Factor"})
imp_table.melt(id_vars="Factor", var_name="Group", value_name="Importance").to_csv(
    ROOT / "tableau" / "ml_importance.csv", index=False)

# ---- Chart ----
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#C9CDD4", "xtick.color": "#6B7280", "ytick.color": "#6B7280"})
plot = imp.sort_values("Younger (45-64)")
fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=110)
yy = np.arange(len(plot))
ax.barh(yy + 0.2, plot["Younger (45-64)"], height=0.38, color="#2A5C8A", label="Younger (45-64)")
ax.barh(yy - 0.2, plot["Older (65+)"], height=0.38, color="#B4532A", label="Older (65+)")
ax.set_yticks(yy, plot.index)
ax.axvline(0, color="#6B7280", lw=1)
ax.set_xlabel("Drop in ROC AUC when the factor is shuffled (bigger = more important)")
ax.set_title(f"What does the model need to spot memory loss? ({best})", loc="left",
             fontweight="bold", color="#1E2A44", fontsize=12)
ax.legend(frameon=False, loc="lower right")
ax.grid(axis="x", color="#ECEEF1"); ax.set_axisbelow(True)
fig.savefig(ROOT / "reports" / "figures" / "05_ml_importance.png", bbox_inches="tight", facecolor="white")

lines = ["# Machine learning: spotting memory loss (BRFSS 2023 + 2024)", "",
         f"**People:** {len(df):,} aged 45+, {int(y.sum()):,} report memory loss getting worse ({y.mean():.1%}).",
         "Same-interview model (BRFSS does not follow people over time). Balanced with class weights.", "",
         "## 1. Model comparison (5-fold cross-validation)", "", cv_table.drop(columns="_auc").to_markdown(index=False),
         "", "## 2. Test set (25%), ROC AUC per group", "", sub_table.to_markdown(index=False), "",
         f"## 3. Most important factors ({best}, permutation importance, 10 repeats)", "",
         imp_table.to_markdown(index=False), "",
         "Data: CDC BRFSS 2023 and 2024, national files, Cognitive Decline module."]
(ROOT / "reports" / "ml_results.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
