# Step 2: What the first charts show (simple words)

Data: BRFSS 2023 + 2024, 208,171 adults aged 45+ in 37 states. Weighted percentages.
Charts: [figures/](figures/). Notebook: [../notebooks/01_explore.ipynb](../notebooks/01_explore.ipynb).

**Memory loss** here means: "confusion or memory loss that is happening more often or getting worse"
in the past 12 months. People say this themselves; it is **not** a diagnosis.

## 1. Age

| 45-49 | 50-54 | 55-59 | 60-64 | 65-69 | 70-74 | 75-79 | 80+ |
|---|---|---|---|---|---|---|---|
| 14.8% | 16.6% | 16.6% | 16.7% | 15.5% | 16.3% | 17.4% | 20.7% |

Memory loss is **almost as common at 50 as at 75**. Only at 80+ is it clearly higher.

## 2. Income

| | Under $15k | $200k+ | Times higher |
|---|---|---|---|
| Younger (45-64) | **31.4%** | **8.1%** | about **4×** |
| Older (65+) | 20.2% | 13.5% | about 1.5× |

Among younger people with the lowest income, **almost 1 in 3** report memory loss getting worse.
The income gap is much bigger for younger people.

## 3. Education

College graduates report less memory loss: 11.6% (younger) and 14.8% (older),
compared with 23.3% and 21.9% for people without high school.

## 4. Health and lifestyle

**Every** health factor goes with more memory loss, and the link is **stronger for younger people**.
The strongest: depression (younger: 37.8% vs about 10% without), poor general health,
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
