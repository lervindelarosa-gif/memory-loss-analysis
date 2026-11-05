"""Build one clean analysis table from NHANES 2011-2012 + 2013-2014 (people aged 60+).

One row per person aged 60+ who did all three memory and thinking tests:
  - CERAD word list: learn 10 words (3 tries) and recall them later  -> memory
  - Animal fluency: name as many animals as you can in 1 minute    -> language / thinking speed
  - DSST: match symbols to numbers in 2 minutes                       -> attention / speed

Main outcome, low_test_score = 1 for the bottom 25% (weighted) of the combined test score.
This is NOT a dementia diagnosis. It flags people who scored low compared with others aged 60+.
Also kept: memory_complaint (MCQ084, "difficulties remembering or periods of confusion"),
a self-report question like the one in BRFSS.

Survey weights: the exam weight WTMEC2YR divided by 2, as NCHS advises when two cycles are combined.
Hearing (AUQ054) was only asked in 2011-2012, so it is missing for 2013-2014.

Usage:  python src/build_nhanes.py   (run src/download_nhanes.py first)
Output: data/processed/nhanes_2011_2014.csv  (ignored by Git)
Prints only counts and weighted percentages.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "nhanes"
OUT = ROOT / "data" / "processed" / "nhanes_2011_2014.csv"
CYCLES = {"2011-2012": "G", "2013-2014": "H"}


def read(name):
    return pd.read_sas(RAW / f"{name}.xpt", format="xport").set_index("SEQN")


def yes_no(s, yes=(1,), no=(2,)):
    """1 = yes, 0 = no, missing for don't know / refused / not asked."""
    return pd.Series(np.select([s.isin(yes), s.isin(no)], [1.0, 0.0], default=np.nan), index=s.index)


blocks = []
for cycle, x in CYCLES.items():
    parts = [read(f"{f}_{x}") for f in ["DEMO", "CFQ", "DPQ", "MCQ", "DIQ", "SMQ", "BPQ", "PAQ"]]
    if x == "G":
        parts.append(read("AUQ_G")[["AUQ054"]])
    b = parts[0].join(parts[1:], how="left").copy()
    b.insert(0, "cycle", cycle)
    blocks.append(b)
raw = pd.concat(blocks)

# People 60+ with all three tests done
raw = raw[(raw["RIDAGEYR"] >= 60) & raw[["CFDCSR", "CFDAST", "CFDDS"]].notna().all(axis=1)]

df = pd.DataFrame(index=raw.index)
df["cycle"] = raw["cycle"]
df["strata"] = raw["SDMVSTRA"]
df["psu"] = raw["SDMVPSU"]
df["weight"] = raw["WTMEC2YR"] / len(CYCLES)
df["age"] = raw["RIDAGEYR"]  # top-coded at 80
df["age_group"] = pd.cut(df["age"], [59, 64, 69, 74, 79, 120],
                         labels=["60-64", "65-69", "70-74", "75-79", "80+"]).astype(str)
df["age_band"] = np.where(df["age"] < 70, "60-69", "70+")
df["female"] = yes_no(raw["RIAGENDR"], yes=(2,), no=(1,))
df["education"] = raw["DMDEDUC2"].map({1: "1 Less than high school", 2: "1 Less than high school",
                                       3: "2 High school", 4: "3 Some college", 5: "4 College graduate"})
# Household income, grouped into 4 bands (fewer people than BRFSS, so wider bands)
df["income"] = raw["INDHHIN2"].map({1: "1 Under $25k", 2: "1 Under $25k", 3: "1 Under $25k",
                                    4: "1 Under $25k", 5: "1 Under $25k", 13: "1 Under $25k",
                                    6: "2 $25-55k", 7: "2 $25-55k", 8: "2 $25-55k",
                                    9: "3 $55-100k", 10: "3 $55-100k", 14: "3 $55-100k",
                                    15: "4 $100k+"})

# Test scores
df["word_learning"] = raw[["CFDCST1", "CFDCST2", "CFDCST3"]].sum(axis=1, min_count=3)  # 0-30
df["word_recall"] = raw["CFDCSR"]  # 0-10, delayed recall
df["animals"] = raw["CFDAST"]
df["symbols"] = raw["CFDDS"]


def wz(s, w):
    """Weighted z-score."""
    m = np.average(s, weights=w)
    return (s - m) / np.sqrt(np.average((s - m) ** 2, weights=w))


tests = ["word_learning", "word_recall", "animals", "symbols"]
ok = df[tests].notna().all(axis=1)
df = df[ok].copy()
df["test_score"] = sum(wz(df[t], df["weight"]) for t in tests) / len(tests)
order = df["test_score"].sort_values().index
cum = df.loc[order, "weight"].cumsum() / df["weight"].sum()
df["low_test_score"] = 0.0
df.loc[cum[cum <= 0.25].index, "low_test_score"] = 1.0

# Self-reported memory problem (like BRFSS)
df["memory_complaint"] = yes_no(raw.loc[df.index, "MCQ084"])

# Health
phq = raw.loc[df.index, [f"DPQ0{i}0" for i in range(1, 10)]].where(lambda d: d <= 3)
df["depression"] = np.where(phq.notna().all(axis=1), (phq.sum(axis=1) >= 10).astype(float), np.nan)
df["hearing_problem"] = np.select([raw.loc[df.index, "AUQ054"].isin([4, 5, 6]),
                                   raw.loc[df.index, "AUQ054"].isin([1, 2, 3])], [1.0, 0.0], default=np.nan)
r = raw.loc[df.index]
df["stroke"] = yes_no(r["MCQ160F"])
df["heart_disease"] = yes_no(r["MCQ160C"])
lung = pd.concat([yes_no(r[c]) for c in ["MCQ160G", "MCQ160K", "MCQ160O"] if c in r], axis=1)
df["copd"] = np.where((lung == 1).any(axis=1), 1.0, np.where((lung == 0).any(axis=1), 0.0, np.nan))
df["diabetes"] = yes_no(r["DIQ010"], yes=(1,), no=(2, 3))
df["high_bp"] = yes_no(r["BPQ020"])
df["current_smoker"] = np.select([r["SMQ040"].isin([1, 2]), r["SMQ040"].eq(3) | r["SMQ020"].eq(2)],
                                 [1.0, 0.0], default=np.nan)
df["no_exercise"] = np.select([r["PAQ650"].eq(2) & r["PAQ665"].eq(2), r["PAQ650"].eq(1) | r["PAQ665"].eq(1)],
                              [1.0, 0.0], default=np.nan)

df = df.reset_index(drop=True)  # drop the NHANES person ID
OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)


def wpct(d, col):
    d = d.dropna(subset=[col])
    return 100 * (d[col] * d["weight"]).sum() / d["weight"].sum()


print(f"People 60+ with all tests: {len(df):,}  (2011-12: {(df.cycle == '2011-2012').sum():,}, "
      f"2013-14: {(df.cycle == '2013-2014').sum():,})")
for band, g in df.groupby("age_band"):
    print(f"  {band}: {len(g):,} people | low test score {wpct(g, 'low_test_score'):.1f}% | "
          f"memory complaint {wpct(g, 'memory_complaint'):.1f}%")
print("Missing values (%):")
print((df.isna().mean() * 100).round(1)[lambda s: s > 0].to_string())
