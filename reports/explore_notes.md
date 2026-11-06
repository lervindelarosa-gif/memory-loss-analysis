# Step 2: What the first charts show (simple words)

Data: BRFSS 2023 + 2024, 208,171 adults aged 45+ in 37 states. Weighted percentages.
Charts: [figures/](figures/). Notebook: [../notebooks/01_explore.ipynb](../notebooks/01_explore.ipynb).

**Memory loss** here means: "confusion or memory loss that is happening more often or getting worse"
in the past 12 months. People say this themselves; it is **not** a diagnosis.

## 1. Age

| 45-49 | 50-54 | 55-59 | 60-64 | 65-69 | 70-74 | 75-79 | 80+ |
|---|---|---|---|---|---|---|---|
| 14.5% | 16.5% | 17.0% | 16.2% | 15.4% | 16.3% | 17.3% | 20.5% |

Memory loss is **almost as common at 50 as at 75**. Only at 80+ is it clearly higher.

## 2. Income

| | Under $15k | $200k+ | Times higher |
|---|---|---|---|
| Younger (45-64) | **32.0%** | **8.2%** | about **4×** |
| Older (65+) | 20.4% | 13.7% | about 1.5× |

Among younger people with the lowest income, **almost 1 in 3** report memory loss getting worse.
The income gap is much bigger for younger people.

## 3. Education

College graduates report less memory loss: 11.8% (younger) and 15.0% (older),
compared with 22.7% and 22.0% for people without high school.

## 4. Health and lifestyle

**Every** health factor goes with more memory loss, and the link is **stronger for younger people**.
The strongest: depression (younger: 37.1% vs about 10% without), poor general health,
unable to work, COPD, serious hearing problems and stroke.

## Be careful

- These are simple comparisons. Income, education and health are mixed together
  (for example, people who are unable to work often have lower income).
- **Depression** can make people feel their memory is worse, and memory problems can cause depression.
  The statistics step must take this into account.
- Income is missing for 17% of people ("don't know" or refused). Their memory loss rate (16.1%)
  is close to the average.
- High blood pressure is only asked in 2023.

**Next step:** statistics (weighted logistic regression) to compare people of the same age, sex,
education and health at the same time.
