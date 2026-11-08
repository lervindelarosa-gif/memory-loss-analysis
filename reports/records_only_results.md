# Outreach model with only the data a health organisation is likely to have

Tested on 52,043 people the model did not train on. Example scenario, for outreach only.

| Inputs                          |   Number of inputs |   Reached at 20% contacted | 95% interval   |   ROC AUC |
|:--------------------------------|-------------------:|---------------------------:|:---------------|----------:|
| All survey answers (slide 9)    |                 13 |                       44.8 | 42.7-46.8      |     0.712 |
| Records plus smoking and weight |                 10 |                       43.7 | 41.7-46.0      |     0.705 |
| Records only                    |                  8 |                       43.8 | 41.7-46.0      |     0.703 |
| Records without depression      |                  7 |                       37.8 | 36.0-40.0      |     0.641 |
| Records without hearing         |                  7 |                       43.3 | 41.4-45.4      |     0.693 |
| Age and sex only                |                  2 |                       23.4 | 21.6-25.1      |     0.538 |

Oldest first reaches 22.2%. Picking at random reaches 20.0%.

Records only = age, sex, depression, hearing problem, stroke, COPD, heart disease, diabetes.
These answers still come from the survey, not from real records, which can be incomplete.
So a real organisation could get weaker results. A pilot would be needed to check.