"""Build one clean analysis table from BRFSS 2023 + 2024.

One row per person aged 45+ who answered the memory question (Cognitive Decline
module, only asked in some states). Both years use the same new question (CIMEMLO1).

Survey weights: _LLCPWT divided by the number of years EACH STATE is in the module (1 or 2),
because many states asked the question in only one of the two years.
Design variables (_STSTR, _PSU) are kept for correct standard errors later.

Usage:  python src/build_table.py
Output: data/processed/brfss_2023_2024.csv  (ignored by Git)
Prints only counts and weighted percentages.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "brfss"
OUT = ROOT / "data" / "processed" / "brfss_2023_2024.csv"
YEARS = [2023, 2024]

COLS = ["_STATE", "_STSTR", "_PSU", "_LLCPWT", "_AGEG5YR", "_AGE80", "SEXVAR", "_EDUCAG", "_INCOMG1",
        "CIMEMLO1", "CVDSTRK3", "BPHIGH6", "DIABETE4", "EXERANY2", "ADDEPEV3", "_SMOKER3", "_BMI5CAT",
        "GENHLTH", "EMPLOY1", "DEAF", "CHCCOPD3", "CVDCRHD4"]


def yes_no(s, yes=(1,), no=(2,)):
    """1 = yes, 0 = no, missing for don't know / refused / not asked."""
    return np.select([s.isin(yes), s.isin(no)], [1.0, 0.0], default=np.nan)


blocks = []
for year in YEARS:
    parts = []
    for chunk in pd.read_sas(RAW / f"LLCP{year}.XPT", format="xport", chunksize=100_000):
        chunk = chunk[[c for c in COLS if c in chunk.columns]]
        parts.append(chunk[chunk["CIMEMLO1"].isin([1, 2]) & chunk["_AGEG5YR"].between(6, 13)])
    b = pd.concat(parts)
    b.insert(0, "year", year)
    blocks.append(b)
raw = pd.concat(blocks, ignore_index=True)

df = pd.DataFrame({
    "year": raw["year"],
    "state": raw["_STATE"].astype(int),
    "strata": raw["_STSTR"],
    "psu": raw["_PSU"],
    "weight": raw["_LLCPWT"] / raw.groupby("_STATE")["year"].transform("nunique"),
    "age": raw["_AGE80"],  # top-coded at 80
    "age_group": raw["_AGEG5YR"].map({6: "45-49", 7: "50-54", 8: "55-59", 9: "60-64",
                                      10: "65-69", 11: "70-74", 12: "75-79", 13: "80+"}),
    "memory_loss": yes_no(raw["CIMEMLO1"]),
    "female": yes_no(raw["SEXVAR"], yes=(2,), no=(1,)),
    "education": raw["_EDUCAG"].map({1: "1 Less than high school", 2: "2 High school",
                                     3: "3 Some college", 4: "4 College graduate"}),
    "income": raw["_INCOMG1"].map({1: "1 Under $15k", 2: "2 $15-25k", 3: "3 $25-35k", 4: "4 $35-50k",
                                   5: "5 $50-100k", 6: "6 $100-200k", 7: "7 $200k+"}),
    "stroke": yes_no(raw["CVDSTRK3"]),
    # 2 = only during pregnancy, 4 = borderline: counted as "no"
    "high_blood_pressure": yes_no(raw["BPHIGH6"], no=(2, 3, 4)) if "BPHIGH6" in raw else np.nan,
    "diabetes": yes_no(raw["DIABETE4"], no=(2, 3, 4)),
    "heart_disease": yes_no(raw["CVDCRHD4"]),
    "copd": yes_no(raw["CHCCOPD3"]),
    "depression": yes_no(raw["ADDEPEV3"]),
    "no_exercise": yes_no(raw["EXERANY2"], yes=(2,), no=(1,)),
    "current_smoker": yes_no(raw["_SMOKER3"], yes=(1, 2), no=(3, 4)),
    "obese": yes_no(raw["_BMI5CAT"], yes=(4,), no=(1, 2, 3)),
    "poor_health": yes_no(raw["GENHLTH"], yes=(4, 5), no=(1, 2, 3)),
    "deaf": yes_no(raw["DEAF"]),
    "unable_to_work": yes_no(raw["EMPLOY1"], yes=(8,), no=(1, 2, 3, 4, 5, 6, 7)),
})
# High blood pressure was only asked in 2023 (BRFSS asks it every other year)
df.loc[df["year"] != 2023, "high_blood_pressure"] = np.nan
df["age_band"] = np.where(df["age"] < 65, "45-64", "65+")

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)


def wpct(d, col="memory_loss"):
    d = d.dropna(subset=[col])
    return round(100 * np.average(d[col], weights=d["weight"]), 1)


print(f"People: {len(df):,} | states: {df['state'].nunique()} | years: {YEARS}")
print("\nPeople per year:", df.groupby("year").size().to_dict())
print("\nMemory loss getting worse, weighted % by age group:")
print(df.groupby("age_group").apply(lambda g: pd.Series({"people": len(g), "weighted_pct": wpct(g)}),
                                    include_groups=False).to_string())
print("\nBy age band:", {b: wpct(g) for b, g in df.groupby("age_band")})
print("\nMissing values per column (%):")
print((df.isna().mean() * 100).round(1).sort_values(ascending=False).head(10).to_string())
print("\nSaved:", OUT.relative_to(ROOT))
