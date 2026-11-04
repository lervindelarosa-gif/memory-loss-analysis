"""Download the national BRFSS data files from the CDC.

Public data, free, no account needed. Only the NATIONAL files from cdc.gov are used
(state files have their own data use agreements).

Usage:  python src/download_brfss.py 2023        (one year)
        python src/download_brfss.py 2022 2023   (several years)
Output: data/raw/brfss/LLCP<year>.XPT  (SAS transport file, about 1 GB unzipped)
"""
import sys
import zipfile
from pathlib import Path

import requests
import truststore

truststore.inject_into_ssl()  # use Windows' certificates (fixes SSL errors in Anaconda)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "brfss"
URL = "https://www.cdc.gov/brfss/annual_data/{year}/files/LLCP{year}XPT.zip"

years = [int(y) for y in sys.argv[1:]] or [2023]
OUT.mkdir(parents=True, exist_ok=True)

for year in years:
    xpt = OUT / f"LLCP{year}.XPT"
    if xpt.exists():
        print(f"{year}: already downloaded ({xpt.stat().st_size / 1e6:,.0f} MB)")
        continue
    zip_path = OUT / f"LLCP{year}XPT.zip"
    print(f"{year}: downloading {URL.format(year=year)}")
    with requests.get(URL.format(year=year), stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    with zipfile.ZipFile(zip_path) as z:
        # The zip holds one .XPT file; its name sometimes ends with a space
        member = next(m for m in z.namelist() if m.strip().upper().endswith(".XPT"))
        with z.open(member) as src, open(xpt, "wb") as dst:
            while chunk := src.read(1 << 20):
                dst.write(chunk)
    zip_path.unlink()
    print(f"{year}: saved {xpt.relative_to(ROOT)} ({xpt.stat().st_size / 1e6:,.0f} MB)")
