"""First look at the memory questions in BRFSS (counts and percentages only).

Two questions:
- CIMEMLO1 (Cognitive Decline module, adults 45+, only some states):
  "During the past 12 months, have you experienced confusion or memory loss
   that is happening more often or is getting worse?"  1 = yes, 2 = no
- DECIDE (core question, all adults, all states):
  serious difficulty concentrating, remembering or making decisions.  1 = yes, 2 = no

Usage:  python src/first_look.py 2023
Percentages here are not weighted yet (no survey weights).
"""
import sys
from pathlib import Path

import pandas as pd

YEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2023
ROOT = Path(__file__).resolve().parent.parent
XPT = ROOT / "data" / "raw" / "brfss" / f"LLCP{YEAR}.XPT"

AGE = {1: "18-24", 2: "25-29", 3: "30-34", 4: "35-39", 5: "40-44", 6: "45-49", 7: "50-54",
       8: "55-59", 9: "60-64", 10: "65-69", 11: "70-74", 12: "75-79", 13: "80+"}
COLS = ["_STATE", "_AGEG5YR", "DECIDE", "CIMEMLO1"]

parts = [chunk[[c for c in COLS if c in chunk.columns]]
         for chunk in pd.read_sas(XPT, format="xport", chunksize=100_000)]
df = pd.concat(parts)
df["age_group"] = df["_AGEG5YR"].map(AGE)
print(f"BRFSS {YEAR}: {len(df):,} people, {df['_STATE'].nunique()} states/territories")


def pct_yes(col):
    d = df[df[col].isin([1, 2])]
    t = d.groupby("age_group").agg(people=(col, "size"), pct_yes=(col, lambda s: round(100 * (s == 1).mean(), 1)))
    print(f"\n{col}: answered by {len(d):,} people in {d['_STATE'].nunique()} states")
    print(t.to_string())


pct_yes("DECIDE")
if "CIMEMLO1" in df:
    pct_yes("CIMEMLO1")
