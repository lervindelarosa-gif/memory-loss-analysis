# Step 3: What the statistics say (simple words)

Full tables: [regression.md](regression.md). Data: BRFSS 2023 + 2024, 190,699 people aged 45+
with complete answers. Weighted logistic regression: all factors at the same time, plus state and year.

**Odds ratio (OR):** 1 = no difference, 2 = twice the odds of memory loss.

## Main results (model B, with depression)

| Factor | Younger (45-64) | Older (65+) | Different for younger? |
|---|---|---|---|
| **Lowest income** (under $15k vs $200k+) | **2.4×** | 1.2× (not proven) | **Yes** (p < 0.001) |
| **Depression** | **4.1×** | 3.1× | **Yes** (p < 0.001) |
| **Deaf / serious hearing problem** | **2.5×** | 1.9× | **Yes** (p = 0.003) |
| **Stroke** | 1.8× | 1.5× | **Yes** (p = 0.013) |
| **COPD** (lung disease) | 1.6× | 1.6× | Yes, small (p = 0.013) |
| **Heart disease** | 1.5× | 1.3× | Yes (p = 0.026) |
| **No exercise** | 1.4× | 1.2× | **Yes** (p < 0.001) |
| Diabetes | 1.1× | 1.1× | Not proven |
| **Age** (per 10 years) | **1.0× (no effect)** | 1.2× | |
| Obese, current smoker | no clear effect | no clear effect | |

## What this means

- **Inside the 45-64 group, age does not matter** (OR 0.98). For people 65+ it matters a little (1.22 per 10 years).
- **Income matters only for younger people:** 2.4× higher odds for the lowest income (3.1× without depression
  in the model). For older people, income makes no clear difference.
- **Depression is the strongest factor** in both groups, but stronger for younger people.
- **Hearing problems** stand out: 2.5× for younger people. Hearing loss is a known, treatable risk factor.
- **Almost every health factor is stronger for younger people.**
- **Education** matters little once income and health are in the model.

## Same story as the HRS dementia project

| | Dementia (HRS) | Memory loss (BRFSS) |
|---|---|---|
| Age matters inside 50/45-64? | No | No |
| Low income, younger | 8.2× | 2.4× |
| Low income, older | 2.4× | 1.2× (not proven) |
| Stroke stronger for younger? | Yes | Yes |

Two different datasets and two different measures give the **same direction**.

## Be careful

- **Self-reported**, not a diagnosis. Depression can make people feel their memory is worse,
  and memory problems can cause depression. That is why model B includes depression; the main
  results stay the same with or without it.
- **Links, not causes.** Memory problems can also lower income (people stop working).
- **One moment in time:** BRFSS asks different people each year, so we cannot follow people over time.
- Standard errors use a common approximation of the survey design (clustered by PSU).
