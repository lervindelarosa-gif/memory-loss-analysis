"""Download the NHANES 2011-2012 and 2013-2014 files from the CDC.

Public data, free, no account needed. Only these two cycles have the memory and thinking
tests (CFQ files, people aged 60+). Rule: never try to identify anyone; share group totals only.

Usage:  python src/download_nhanes.py
Output: data/raw/nhanes/<FILE>.xpt  (about 48 MB in total, ignored by Git)
"""
from pathlib import Path

import requests
import truststore

truststore.inject_into_ssl()  # use Windows' certificates (fixes SSL errors in Anaconda)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "nhanes"
URL = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{year}/DataFiles/{name}.xpt"

# DEMO = age, income, education, weights   CFQ = memory tests   DPQ = depression
# AUQ = hearing (2011-12 only)   MCQ = stroke, heart, COPD   DIQ = diabetes
# SMQ = smoking   BPQ = blood pressure   PAQ = exercise
FILES = {2011: ["DEMO_G", "CFQ_G", "DPQ_G", "AUQ_G", "MCQ_G", "DIQ_G", "SMQ_G", "BPQ_G", "PAQ_G"],
         2013: ["DEMO_H", "CFQ_H", "DPQ_H", "MCQ_H", "DIQ_H", "SMQ_H", "BPQ_H", "PAQ_H"]}

OUT.mkdir(parents=True, exist_ok=True)
for year, names in FILES.items():
    for name in names:
        path = OUT / f"{name}.xpt"
        if path.exists():
            print(f"{name}: already downloaded")
            continue
        r = requests.get(URL.format(year=year, name=name), timeout=120,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        path.write_bytes(r.content)
        print(f"{name}: saved ({len(r.content) / 1e6:.1f} MB)")
