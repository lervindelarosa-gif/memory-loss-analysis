# Is memory loss only about age?

A data analytics final project about **memory loss in adults aged 45+**, comparing
**younger people (45–64)** with **older people (65+)**.

## Dashboard

**Tableau Public:** [Is memory loss only about age?](https://public.tableau.com/app/profile/lervin.de.la.rosa/viz/Ismemorylossonlyaboutage/Home)
Home page with KPI tiles and clickable topic buttons (Age, Income, Education, Health,
What predicts it?); every topic page has a "← Home" button. Built from the small summary tables in `tableau/`
(`python src/make_dashboard_tables.py`).

## App

Streamlit app with 7 pages (Home KPIs, Age, Income, Education, Health, What predicts memory loss,
Risk checker). It only reads the summary tables in `tableau/`.

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Why this project

Most people think memory problems only come with old age. I want to find out what else
plays a role: education, income, health and lifestyle.

## The question

- Is memory loss only about age?
- Which factors matter most for people aged 45–64?
- Are they the same factors as for people aged 65+?

## Data

| Source | What it is | Ages |
|---|---|---|
| [BRFSS](https://www.cdc.gov/brfss/) (CDC), national files | Phone survey, more than 400,000 adults per year | 18+ |
| – Cognitive Decline module | "Confusion or memory loss that is happening more often or getting worse" (only some states) | 45+ |
| [NHANES](https://wwwn.cdc.gov/nchs/nhanes/) (CDC), public-use files | Health exam survey; memory tests in 2011–2014 | tests: 60+ |

**Important:** these surveys measure **self-reported memory problems**, not a dementia diagnosis.

### Data terms (checked on 4 November 2026)

- **BRFSS national files:** no data use agreement on the [download page](https://www.cdc.gov/brfss/annual_data/annual_2023.html).
  State BRFSS files are NOT used (they have their own agreements).
- **NHANES:** the [NCHS Data User Agreement](https://www.cdc.gov/nchs/policy/data-user-agreement.html) applies:
  statistical use only, no attempt to identify anyone, no linking with identifiable data.
  It does not mention AI tools. Restricted / limited-access NHANES files are NOT used.
- **CDC reuse policy:** most CDC data is [public domain](https://www.cdc.gov/other/agencymaterials.html);
  credit the source and do not suggest that CDC endorses the work (see below).
- No attempt is made to identify any person, and no linking with other data.
- Only group totals are shared. The raw data is not in this repository (large files):
  download it with the script below.

**Source:** Centers for Disease Control and Prevention (CDC), Behavioral Risk Factor Surveillance System
Survey Data, 2023 and 2024. Atlanta, Georgia: U.S. Department of Health and Human Services, CDC.
The data is available on the [CDC website](https://www.cdc.gov/brfss/annual_data/annual_data.htm) at no charge.
This is a student project. It is not reviewed or endorsed by CDC, and the analysis and conclusions are my own.

## How to run

```bash
python src/download_brfss.py 2022 2023 2024
python src/first_look.py 2023
python src/build_table.py
python src/regression.py
python src/ml_model.py
```

## Project structure

```
src/
  download_brfss.py   download the national BRFSS files from the CDC
  first_look.py       counts and percentages for the memory questions
  build_table.py      clean analysis table, 2023 + 2024, people 45+ (with survey weights)
  regression.py       step 3: weighted logistic regression, younger vs older
  ml_model.py         step 4: machine learning (logistic regression vs gradient boosting)
notebooks/01_explore.ipynb  step 2: first charts (weighted, group totals only)
data/                 downloaded data (not uploaded)
tableau/              summary tables (safe to share)
reports/              results and charts
notebooks/            exploration
```

## Status

Just started: BRFSS 2022, 2023 and 2024 downloaded and checked.

| Year | Memory question | People 45+ who answered | States |
|---|---|---|---|
| 2022 | CIMEMLOS (old version) | 63,948 | 12 |
| 2023 | CIMEMLO1 (new version) | 134,033 | 28 |
| 2024 | CIMEMLO1 (new version) | 78,111 | 19 |

The module changed in 2023, so 2023 and 2024 are combined and 2022 is kept apart.

**Analysis table (2023 + 2024):** 208,171 people aged 45+ from 37 states.
Weighted share with memory loss getting worse: **16.2% at 45-64** and **17.2% at 65+**.
High blood pressure is only asked in odd years, so it is available for 2023 only.

First charts: see [reports/explore_notes.md](reports/explore_notes.md).
Statistics: see [reports/statistics_notes.md](reports/statistics_notes.md).
Machine learning: see [reports/ml_notes.md](reports/ml_notes.md).

## Credits

Centers for Disease Control and Prevention (CDC). Behavioral Risk Factor Surveillance System Survey Data.
National Center for Health Statistics (NCHS). National Health and Nutrition Examination Survey Data.
