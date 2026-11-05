# Is memory loss only about age?

*What people say about their memory, and how they score on memory tests (CDC BRFSS and NHANES)*

A data analytics final project in two parts, using two different CDC datasets:

| | **Part 1: BRFSS** | **Part 2: NHANES** |
|---|---|---|
| Memory measured by | People **say** their memory is getting worse | People **score low** on memory tests |
| Years | 2023 + 2024 | 2011–2012 + 2013–2014 |
| People | 208,171 aged 45+ | 2,934 aged 60+ |
| Younger vs older | 45–64 vs 65+ | 60–69 vs 70+ |
| Younger group | **16.2%** memory loss | **14.7%** low test score |
| Older group | **17.2%** memory loss | **38.0%** low test score |

Neither dataset gives a dementia diagnosis. The two datasets are about different people,
so they are analysed **separately** and only the results are compared.

**Short answer: no, memory loss is not only about age.** See [Comparison](#comparison-part-1-vs-part-2).

## Dashboard and app (Part 1: BRFSS)

**Tableau Public:** [Is memory loss only about age?](https://public.tableau.com/app/profile/lervin.de.la.rosa/viz/Ismemorylossonlyaboutage/Home)
Home page with KPI tiles; every page has the same button bar at the top (Home, Age, Income, Education,
Health, What predicts it?, Memory tests) and fits on one screen (1000 x 600). The **Memory tests** page puts
BRFSS (people say) and NHANES (people tested) side by side: *BRFSS asks people about their memory. NHANES
tests it. Using both lets me check whether the answer is the same.* Built from the small summary tables in
`tableau/` (`python src/make_dashboard_tables.py`; `dash_compare.csv` needs `src/nhanes_analysis.py` first).

**Live app:** [memory-loss-analysis.streamlit.app](https://memory-loss-analysis.streamlit.app/)
Streamlit app with 9 pages (Home KPIs, Age, Income, Education, Health, What predicts memory loss,
Memory tests (NHANES), Try the tests, Risk checker). "Try the tests" has short versions of the 3 NHANES tests (own versions
of the NHANES tests: word recall, animal naming, symbol matching; nothing is saved). It only reads the summary tables in `tableau/`.

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Why this project

Most people think memory problems only come with old age. I want to find out what else
plays a role: education, income, health and lifestyle.

## The question

- Is memory loss only about age?
- Which factors matter most for younger adults?
- Are they the same factors as for older adults?
- Do we get the same answer when people **judge their own memory** (BRFSS) and when memory is **tested** (NHANES)?

---

## Part 1: BRFSS (self-reported memory loss)

**Data:** [BRFSS](https://www.cdc.gov/brfss/) (CDC), national files, 2023 and 2024. A phone survey of more
than 400,000 adults per year. The Cognitive Decline module asks people 45+ about "confusion or memory loss
that is happening more often or getting worse" (only some states).

| Year | Memory question | People 45+ who answered | States |
|---|---|---|---|
| 2022 | CIMEMLOS (old version) | 63,948 | 12 |
| 2023 | CIMEMLO1 (new version) | 134,033 | 28 |
| 2024 | CIMEMLO1 (new version) | 78,111 | 19 |

The module changed in 2023, so 2023 and 2024 are combined and 2022 is kept apart.
**Analysis table (2023 + 2024):** 208,171 people aged 45+ from 37 states.
High blood pressure is only asked in odd years, so it is available for 2023 only.

**Main findings**
- Memory loss is almost as common at 45–64 (16.2%) as at 65+ (17.2%).
- Low income matters most for younger people: 31.4% of the lowest income group vs 8.1% of the highest.
- Depression and hearing problems are strongly linked in both groups.

**Run it**
```bash
python src/download_brfss.py 2022 2023 2024
python src/first_look.py 2023
python src/build_table.py
python src/regression.py
python src/ml_model.py
python src/make_dashboard_tables.py
```

Reports: [explore_notes.md](reports/explore_notes.md) · [statistics_notes.md](reports/statistics_notes.md) ·
[regression.md](reports/regression.md) · [ml_notes.md](reports/ml_notes.md)

---

## Part 2: NHANES (memory test scores)

**Data:** [NHANES](https://wwwn.cdc.gov/nchs/nhanes/) (CDC), public-use files, 2011–2012 and 2013–2014.
A health survey with a medical exam. People 60+ did three memory and thinking tests:
- **Word list:** learn 10 words, then recall them later (memory)
- **Animal naming:** name as many animals as possible in 1 minute (language, thinking speed)
- **Symbol matching:** match symbols to numbers in 2 minutes (attention, speed)

These are tests that doctors also use to **screen for dementia** (the word list comes from CERAD, a
research group on Alzheimer's disease). So Part 2 brings the project closer to dementia, but a low score
is **not** a dementia diagnosis.

**Low test score** = bottom 25% (weighted) of the combined score.
**Analysis table:** 2,934 people aged 60+ who did all the tests. Hearing was only asked in 2011–2012.

**Main findings**
- Low test scores are much more common at 70+ (38.0%) than at 60–69 (14.7%), and 55% at 80+.
- Low income, depression and no exercise are linked in both groups, after age is taken into account.
- Education is very strongly linked, partly because the tests reward reading and speed.

**Run it**
```bash
python src/download_nhanes.py
python src/build_nhanes.py
python src/nhanes_analysis.py
```

Report: [nhanes_results.md](reports/nhanes_results.md)

---

## Comparison: Part 1 vs Part 2

| Factor | Part 1: BRFSS (say) | Part 2: NHANES (tested) | Agree? |
|---|---|---|---|
| Low income | Strong link, mostly in younger people | Link in both groups | Yes |
| Depression | Very strong | Clear | Yes |
| No exercise | Small link | Small link | Yes |
| Stroke | Both groups | Older group | Yes |
| Age | Small effect | **Strong effect** | No |
| Education | Small effect | **Very strong effect** | No |
| Hearing | Strong link | Not clear (small sample) | No |

**In short:** it is not only about age in either dataset, but age matters more when memory is tested.
Full comparison: [reports/brfss_vs_nhanes.md](reports/brfss_vs_nhanes.md).

---

## Data terms (checked on 4 November 2026)

- **BRFSS national files:** no data use agreement on the [download page](https://www.cdc.gov/brfss/annual_data/annual_2023.html).
  State BRFSS files are NOT used (they have their own agreements).
- **NHANES:** the [NCHS Data User Agreement](https://www.cdc.gov/nchs/policy/data-user-agreement.html) applies:
  statistical use only, no attempt to identify anyone, no linking with identifiable data.
  It does not mention AI tools. Restricted / limited-access NHANES files are NOT used.
- **CDC reuse policy:** most CDC data is [public domain](https://www.cdc.gov/other/agencymaterials.html);
  credit the source and do not suggest that CDC endorses the work.
- Only group totals are shared (groups with fewer than 50 people are hidden). The raw data is not in this
  repository: download it with the scripts above.

## Project structure

```
src/
  Part 1: BRFSS
    download_brfss.py       download the national BRFSS files
    first_look.py           counts and percentages for the memory questions
    build_table.py          clean table, 2023 + 2024, people 45+ (with survey weights)
    regression.py           weighted logistic regression, 45-64 vs 65+
    ml_model.py             machine learning (logistic regression vs gradient boosting)
    make_dashboard_tables.py  summary tables for Tableau and the app
  Part 2: NHANES
    download_nhanes.py      download the NHANES 2011-2014 files
    build_nhanes.py         clean table, people 60+ with test scores (with survey weights)
    nhanes_analysis.py      percentages and weighted logistic regression, 60-69 vs 70+
app/                  Streamlit app (Part 1)
tableau/              summary tables, safe to share (dash_*.csv = BRFSS, nhanes_*.csv = NHANES)
reports/              results and charts
notebooks/            exploration
data/                 downloaded data (not uploaded)
```

(The `src/` files are all in one folder; the Part 1 / Part 2 split above is just for reading.)

## Credits

Centers for Disease Control and Prevention (CDC), Behavioral Risk Factor Surveillance System Survey Data,
2023 and 2024. Atlanta, Georgia: U.S. Department of Health and Human Services, CDC.

National Center for Health Statistics (NCHS), National Health and Nutrition Examination Survey Data,
2011-2012 and 2013-2014. Hyattsville, MD: U.S. Department of Health and Human Services, CDC.

The data is available on the [CDC website](https://www.cdc.gov/) at no charge.
This is a student project. It is not reviewed or endorsed by CDC, and the analysis and conclusions are my own.
