"""NHANES 2011-2014: is a low memory test score only about age? (people 60+)

1. Weighted % with a low test score (bottom 25%) by age, income, education and health,
   for younger (60-69) and older (70+) people.
2. Weighted logistic regression, the same way as src/regression.py for BRFSS
   (survey weights as variance weights, standard errors clustered by PSU within strata).
   Model 1: everyone, without hearing.  Model 2: 2011-2012 only, with hearing.

Usage:  python src/nhanes_analysis.py   (run src/build_nhanes.py first)
Output: reports/nhanes_results.md, tableau/nhanes_groups.csv, tableau/nhanes_odds_ratios.csv
        (group totals only; groups with fewer than 50 people are hidden)
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent.parent
MIN_GROUP = 50
df = pd.read_csv(ROOT / "data" / "processed" / "nhanes_2011_2014.csv")
df["group"] = df["age_band"].map({"60-69": "Younger (60-69)", "70+": "Older (70+)"})
df["cluster"] = df["strata"].astype(str) + "_" + df["psu"].astype(str)
df["age_10y"] = df["age"] / 10


def wpct(g, col):
    g = g.dropna(subset=[col])
    return round(100 * (g[col] * g["weight"]).sum() / g["weight"].sum(), 1)


def summary(d, by, label):
    rows = []
    for key, g in d.dropna(subset=[by]).groupby(["group", by]):
        if len(g) >= MIN_GROUP:
            rows.append({"topic": label, "group": key[0], "category": key[1], "people": len(g),
                         "low_test_score_pct": wpct(g, "low_test_score"),
                         "memory_complaint_pct": wpct(g, "memory_complaint")})
    return rows


# ---- 1. Group percentages ----
rows = summary(df.assign(all="Everyone"), "all", "Overall") + summary(df, "age_group", "Age")
rows += summary(df, "income", "Income") + summary(df, "education", "Education")
HEALTH = {"depression": "Depression", "hearing_problem": "Hearing problem", "stroke": "Stroke",
          "copd": "COPD", "heart_disease": "Heart disease", "diabetes": "Diabetes",
          "high_bp": "High blood pressure", "no_exercise": "No exercise", "current_smoker": "Current smoker"}
for col, name in HEALTH.items():
    rows += summary(df[df[col] == 1].assign(has=name), "has", "Health")
groups = pd.DataFrame(rows)
groups["category"] = groups["category"].astype(str).str.replace(r"^\d ", "", regex=True)
groups.to_csv(ROOT / "tableau" / "nhanes_groups.csv", index=False)

# ---- 2. Regression ----
EDU = "C(education, Treatment('4 College graduate'))"
INC = "C(income, Treatment('4 $100k+'))"
BASE = ["age_10y", "female", EDU, INC, "depression", "stroke", "diabetes", "heart_disease", "copd",
        "no_exercise", "current_smoker", "C(cycle)"]
NICE = {"age_10y": "Age (per 10 years)", "female": "Female",
        f"{EDU}[T.1 Less than high school]": "Less than high school (vs college)",
        f"{EDU}[T.2 High school]": "High school (vs college)",
        f"{EDU}[T.3 Some college]": "Some college (vs college)",
        f"{INC}[T.1 Under $25k]": "Income under $25k (vs $100k+)",
        f"{INC}[T.2 $25-55k]": "Income $25-55k (vs $100k+)",
        f"{INC}[T.3 $55-100k]": "Income $55-100k (vs $100k+)",
        "depression": "Depression", "stroke": "Stroke", "diabetes": "Diabetes",
        "heart_disease": "Heart disease", "copd": "COPD", "no_exercise": "No exercise",
        "current_smoker": "Current smoker", "hearing_problem": "Hearing problem"}


def fit(data, terms):
    w = data["weight"] / data["weight"].mean()
    return smf.glm("low_test_score ~ " + " + ".join(terms), data=data, family=sm.families.Binomial(),
                   var_weights=w).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(data["cluster"])[0]})


def fmt(r):
    return f"{r['OR']:.2f} ({r['low']:.2f}-{r['high']:.2f})" + (" *" if r["p"] < 0.05 else "")


MODELS = {"1": ("Model 1: everyone (2011-2014), without hearing", BASE, df),
          "2": ("Model 2: 2011-2012 only, with hearing", [t for t in BASE if t != "C(cycle)"] + ["hearing_problem"],
                df[df["cycle"] == "2011-2012"])}
lines = ["# NHANES 2011-2014: low memory test score, people 60+", "",
         "Low test score = bottom 25% (weighted) of the combined score of three tests "
         "(word list learning and recall, animal naming, symbol matching). Not a dementia diagnosis.", "",
         "## Weighted % with a low test score", ""]
show = groups.pivot_table(index=["topic", "category"], columns="group", values="low_test_score_pct", sort=False)
lines += [show[["Younger (60-69)", "Older (70+)"]].to_markdown(), ""]
odds = []
for key, (title, terms, data) in MODELS.items():
    cols = ["low_test_score", "weight", "cluster", "group", "age_10y", "female", "education", "income", "cycle"]
    cols += [t for t in terms if t in df.columns]
    data = data[list(dict.fromkeys(cols))].dropna()  # dict.fromkeys drops duplicate column names
    res_tables = {}
    for name in ["Younger (60-69)", "Older (70+)"]:
        g = data[data["group"] == name]
        res = fit(g, terms)
        ci = np.exp(res.conf_int())
        t = pd.DataFrame({"OR": np.exp(res.params), "low": ci[0], "high": ci[1], "p": res.pvalues})
        t = t.loc[[i for i in t.index if i in NICE]]
        t.index = [NICE[i] for i in t.index]
        res_tables[f"{name} (n={len(g):,})"] = t.apply(fmt, axis=1)
        odds.append(t.round(3).assign(model=key, group=name).rename_axis("factor").reset_index())
    lines += [f"## {title}", "", "Odds ratio (95% CI); * = p < 0.05. All factors adjusted for each other.", "",
              pd.DataFrame(res_tables).to_markdown(), ""]
pd.concat(odds).to_csv(ROOT / "tableau" / "nhanes_odds_ratios.csv", index=False)
lines += ["Data: CDC National Health and Nutrition Examination Survey (NHANES) 2011-2012 and 2013-2014, "
          "public-use files, cognitive functioning (CFQ)."]
(ROOT / "reports" / "nhanes_results.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
