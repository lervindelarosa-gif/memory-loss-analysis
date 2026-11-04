# Machine learning: spotting memory loss (BRFSS 2023 + 2024)

**People:** 208,171 aged 45+, 35,187 report memory loss getting worse (16.9%).
Same-interview model (BRFSS does not follow people over time). Balanced with class weights.

## 1. Model comparison (5-fold cross-validation)

| Model               | ROC AUC         |   PR AUC | Cases found (recall)   |
|:--------------------|:----------------|---------:|:-----------------------|
| Logistic regression | 0.704 (± 0.003) |    0.352 | 58%                    |
| Gradient boosting   | 0.713 (± 0.003) |    0.367 | 60%                    |

## 2. Test set (25%), ROC AUC per group

| Model               |   Everyone |   Younger (45-64) |   Older (65+) |
|:--------------------|-----------:|------------------:|--------------:|
| Logistic regression |      0.704 |             0.737 |          0.67 |
| Gradient boosting   |      0.712 |             0.743 |          0.68 |

## 3. Most important factors (Gradient boosting, permutation importance, 10 repeats)

| Factor                 |   Younger (45-64) |   Older (65+) |
|:-----------------------|------------------:|--------------:|
| Depression             |            0.1076 |        0.0801 |
| Income                 |            0.0126 |        0.0039 |
| Deaf / hearing problem |            0.011  |        0.0232 |
| COPD                   |            0.0105 |        0.0084 |
| Stroke                 |            0.0062 |        0.0065 |
| No exercise            |            0.0046 |        0.0027 |
| Education              |            0.0042 |        0.0012 |
| Diabetes               |            0.0015 |        0.0011 |
| Age                    |            0.0013 |        0.0165 |
| Female                 |            0.0012 |        0.0005 |
| Obese                  |            0.0012 |        0.0023 |
| Heart disease          |            0.0011 |        0.0047 |
| Current smoker         |            0.0003 |        0.0002 |

Data: CDC BRFSS 2023 and 2024, national files, Cognitive Decline module.