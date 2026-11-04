"""Statistics: which factors besides age go with memory loss? (BRFSS 2023 + 2024)

Weighted logistic regression for younger (45-64) and older (65+) people.
- Survey weights (normalized to mean 1) as variance weights.
- Standard errors clustered by survey PSU within strata (a common approximation
  of the BRFSS survey design).
- State and year are in every model, so differences between states and years are not counted as factors.

Two models:
  A. background + physical health (no depression)
  B. A + depression  (depression can affect how people judge their own memory)
Poor general health and "unable to work" are left out: they can be results of memory problems.
High blood pressure is left out: it was only asked in 2023.

Usage:  python src/regression.py
Output: reports/regression.md, tableau/odds_ratios.csv (summary results only)
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data" / "processed" / "brfss_2023_2024.csv")

df["age_10y"] = df["age"] / 10
df["younger"] = (df["age_band"] == "45-64").astype(int)
df["income"] = df["income"].fillna("8 Unknown")
df["cluster"] = df["strata"].astype(str) + "_" + df["psu"].astype(str)

EDU = "C(education, Treatment('4 College graduate'))"
INC = "C(income, Treatment('7 $200k+'))"
HEALTH = ["stroke", "diabetes", "heart_disease", "copd", "deaf", "no_exercise", "current_smoker", "obese"]
BASE = ["age_10y", "female", EDU, INC] + HEALTH + ["C(state)", "C(year)"]
MODELS = {"A": BASE, "B": BASE + ["depression"]}

NICE = {"age_10y": "Age (per 10 years)", "female": "Female",
        f"{EDU}[T.1 Less than high school]": "Less than high school (vs college)",
        f"{EDU}[T.2 High school]": "High school (vs college)",
        f"{EDU}[T.3 Some college]": "Some college (vs college)",
        f"{INC}[T.1 Under $15k]": "Income under $15k (vs $200k+)",
        f"{INC}[T.2 $15-25k]": "Income $15-25k (vs $200k+)",
        f"{INC}[T.3 $25-35k]": "Income $25-35k (vs $200k+)",
        f"{INC}[T.4 $35-50k]": "Income $35-50k (vs $200k+)",
        f"{INC}[T.5 $50-100k]": "Income $50-100k (vs $200k+)",
        f"{INC}[T.6 $100-200k]": "Income $100-200k (vs $200k+)",
        f"{INC}[T.8 Unknown]": "Income unknown (vs $200k+)",
        "stroke": "Stroke", "diabetes": "Diabetes", "heart_disease": "Heart disease", "copd": "COPD",
        "deaf": "Deaf / serious hearing problem", "no_exercise": "No exercise",
        "current_smoker": "Current smoker", "obese": "Obese", "depression": "Depression"}

NEEDED = ["memory_loss", "age_10y", "female", "education", "income", "state", "year", "weight",
          "cluster", "younger", "depression"] + HEALTH
complete = df[NEEDED].dropna().copy()


def fit(data, terms):
    w = data["weight"] / data["weight"].mean()
    return smf.glm("memory_loss ~ " + " + ".join(terms), data=data, family=sm.families.Binomial(),
                   var_weights=w).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(data["cluster"])[0]})


groups = {"Younger (45-64)": complete[complete["younger"] == 1], "Older (65+)": complete[complete["younger"] == 0]}
tables, rows = {}, []
for model, terms in MODELS.items():
    for name, g in groups.items():
        res = fit(g, terms)
        ci = np.exp(res.conf_int())
        t = pd.DataFrame({"OR": np.exp(res.params), "low": ci[0], "high": ci[1], "p": res.pvalues})
        t = t.loc[[i for i in t.index if i in NICE]]
        t.index = [NICE[i] for i in t.index]
        tables[(model, name)] = t
        rows.append(t.assign(model=model, group=name).rename_axis("factor").reset_index())

out = pd.concat(rows).round({"OR": 3, "low": 3, "high": 3, "p": 4})
out.to_csv(ROOT / "tableau" / "odds_ratios.csv", index=False)


def fmt(r):
    return f"{r['OR']:.2f} ({r['low']:.2f}-{r['high']:.2f})" + (" *" if r["p"] < 0.05 else "")


# ---- Is the effect different for younger people? (model B, Wald test on factor x younger) ----
inter = []
for label, term in [("Income", INC), ("Education", EDU), ("Stroke", "stroke"), ("COPD", "copd"),
                    ("Deaf / hearing", "deaf"), ("Depression", "depression"), ("No exercise", "no_exercise"),
                    ("Diabetes", "diabetes"), ("Heart disease", "heart_disease")]:
    res = fit(complete, MODELS["B"] + ["younger", f"{term}:younger"])
    names = [n for n in res.params.index if n.endswith(":younger")]
    p = float(res.wald_test(", ".join(f"{n} = 0" for n in names), scalar=True).pvalue)
    inter.append({"Factor": label, "Different for younger?": "Yes" if p < 0.05 else "Not proven",
                  "p-value": "< 0.001" if p < 0.001 else f"{p:.3f}"})

counts = {n: (len(g), int(g["memory_loss"].sum()),
              round(100 * np.average(g["memory_loss"], weights=g["weight"]), 1)) for n, g in groups.items()}
lines = ["# Statistics: memory loss in BRFSS 2023 + 2024", "",
         "Weighted logistic regression. Odds ratio (95% confidence interval); * = p < 0.05. "
         "All factors adjusted for each other, plus state and year. Standard errors clustered by survey PSU.", "",
         "| Group | People (complete answers) | With memory loss | Weighted % |", "| --- | --- | --- | --- |"]
lines += [f"| {n} | {c[0]:,} | {c[1]:,} | {c[2]}% |" for n, c in counts.items()]
for model, title in [("A", "Model A: without depression"), ("B", "Model B: with depression")]:
    summary = pd.DataFrame({n: tables[(model, n)].apply(fmt, axis=1) for n in groups})
    lines += ["", f"## {title}", "", summary.to_markdown()]
lines += ["", "## Is the effect different for younger people? (model B)", "",
          pd.DataFrame(inter).to_markdown(index=False), "",
          "Data: CDC Behavioral Risk Factor Surveillance System (BRFSS) 2023 and 2024, national files, "
          "Cognitive Decline module."]
(ROOT / "reports" / "regression.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
