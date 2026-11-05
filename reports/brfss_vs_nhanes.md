# BRFSS vs NHANES: is memory loss only about age?

Two CDC datasets, two ways to measure memory:

| | BRFSS 2023 + 2024 | NHANES 2011-2014 |
| --- | --- | --- |
| What it measures | People **say** their memory is getting worse | People **score low** on memory and thinking tests |
| People | 208,171 aged 45+ | 2,934 aged 60+ |
| Younger vs older | 45-64 vs 65+ | 60-69 vs 70+ |
| Younger group | 16.2% memory loss | 14.7% low test score |
| Older group | 17.2% memory loss | 38.0% low test score |

Low test score = bottom 25% of people aged 60+. It is **not** a dementia diagnosis.

## What both datasets agree on

| Factor | BRFSS | NHANES | Agree? |
| --- | --- | --- | --- |
| Low income | Strong link, mostly in the younger group | Link in both groups (under $25k: about 2-2.5x the odds) | Yes |
| Depression | Very strong (3-4x the odds) | Clear (about 1.7-1.9x the odds) | Yes |
| No exercise | Small link | Small link (about 1.5x the odds) | Yes |
| Stroke | Link in both groups | Link in the older group | Yes |

## Where they differ

| Factor | BRFSS | NHANES | Why it may differ |
| --- | --- | --- | --- |
| **Age** | Small effect | **Strong effect** (55% of people 80+ score low) | Tests pick up slow, normal ageing that people may not notice in themselves |
| **Education** | Small effect | **Very strong effect** | The tests use words, reading and speed, which schooling trains. Part of this is the test, not memory |
| **Hearing** | Strong link | Higher %, but not significant once other factors are counted | Hearing was only asked in 2011-12 (about 1,200 people), so too few to be sure |
| Women | No difference | Women score better | Women often do better on word-list tests |

## Answer in plain English

- **It is not only about age.** In both datasets, money, depression, exercise and stroke matter after age is taken into account.
- **Age matters more when memory is tested** than when people judge their own memory.
- **Education looks very important in the tests,** but some of that comes from how the tests work.

## Limits

- Both datasets are a snapshot in time, so they show links, not causes.
- NHANES is older (2011-2014) and much smaller than BRFSS.
- The two age groups are not the same (45-64 / 65+ vs 60-69 / 70+).

Details: [regression.md](regression.md) (BRFSS) and [nhanes_results.md](nhanes_results.md) (NHANES).
Data: CDC BRFSS 2023-2024 and CDC NHANES 2011-2014, public files from cdc.gov. Not reviewed or endorsed by CDC.
