# Statistics: memory loss in BRFSS 2023 + 2024

Weighted logistic regression. Odds ratio (95% confidence interval); * = p < 0.05. All factors adjusted for each other, plus state and year. Standard errors clustered by survey PSU.

| Group | People (complete answers) | With memory loss | Weighted % |
| --- | --- | --- | --- |
| Younger (45-64) | 86,190 | 13,928 | 15.9% |
| Older (65+) | 104,509 | 17,908 | 16.9% |

## Model A: without depression

|                                    | Younger (45-64)    | Older (65+)        |
|:-----------------------------------|:-------------------|:-------------------|
| Less than high school (vs college) | 0.97 (0.82-1.16)   | 1.19 (1.00-1.41)   |
| High school (vs college)           | 1.00 (0.89-1.13)   | 0.95 (0.86-1.05)   |
| Some college (vs college)          | 1.06 (0.95-1.17)   | 0.97 (0.89-1.06)   |
| Income under $15k (vs $200k+)      | 3.14 (2.53-3.91) * | 1.26 (0.90-1.76)   |
| Income $15-25k (vs $200k+)         | 2.61 (2.06-3.30) * | 1.35 (1.00-1.83)   |
| Income $25-35k (vs $200k+)         | 1.99 (1.60-2.48) * | 1.24 (0.92-1.66)   |
| Income $35-50k (vs $200k+)         | 1.65 (1.35-2.02) * | 1.15 (0.86-1.53)   |
| Income $50-100k (vs $200k+)        | 1.55 (1.30-1.85) * | 1.11 (0.84-1.46)   |
| Income $100-200k (vs $200k+)       | 1.26 (1.06-1.50) * | 0.92 (0.69-1.21)   |
| Income unknown (vs $200k+)         | 1.41 (1.15-1.73) * | 1.07 (0.81-1.43)   |
| Age (per 10 years)                 | 0.92 (0.85-0.99) * | 1.09 (1.00-1.18) * |
| Female                             | 1.27 (1.17-1.39) * | 1.06 (0.98-1.14)   |
| Stroke                             | 2.00 (1.70-2.36) * | 1.55 (1.37-1.76) * |
| Diabetes                           | 1.20 (1.07-1.33) * | 1.14 (1.04-1.25) * |
| Heart disease                      | 1.54 (1.31-1.82) * | 1.33 (1.19-1.48) * |
| COPD                               | 2.05 (1.81-2.33) * | 1.76 (1.58-1.97) * |
| Deaf / serious hearing problem     | 2.81 (2.43-3.25) * | 2.01 (1.83-2.20) * |
| No exercise                        | 1.55 (1.41-1.71) * | 1.23 (1.13-1.34) * |
| Current smoker                     | 1.11 (0.99-1.24)   | 0.92 (0.80-1.05)   |
| Obese                              | 1.02 (0.94-1.12)   | 1.06 (0.98-1.16)   |

## Model B: with depression

|                                    | Younger (45-64)    | Older (65+)        |
|:-----------------------------------|:-------------------|:-------------------|
| Less than high school (vs college) | 1.07 (0.90-1.27)   | 1.22 (1.03-1.45) * |
| High school (vs college)           | 1.12 (0.98-1.27)   | 1.02 (0.92-1.12)   |
| Some college (vs college)          | 1.08 (0.97-1.20)   | 1.01 (0.92-1.10)   |
| Income under $15k (vs $200k+)      | 2.45 (1.96-3.05) * | 1.16 (0.83-1.64)   |
| Income $15-25k (vs $200k+)         | 2.10 (1.66-2.65) * | 1.22 (0.90-1.67)   |
| Income $25-35k (vs $200k+)         | 1.83 (1.46-2.29) * | 1.16 (0.86-1.58)   |
| Income $35-50k (vs $200k+)         | 1.50 (1.21-1.85) * | 1.09 (0.82-1.47)   |
| Income $50-100k (vs $200k+)        | 1.44 (1.19-1.73) * | 1.07 (0.81-1.42)   |
| Income $100-200k (vs $200k+)       | 1.24 (1.04-1.48) * | 0.90 (0.68-1.19)   |
| Income unknown (vs $200k+)         | 1.35 (1.09-1.67) * | 1.05 (0.79-1.41)   |
| Age (per 10 years)                 | 0.98 (0.91-1.05)   | 1.22 (1.12-1.32) * |
| Female                             | 1.04 (0.95-1.14)   | 0.92 (0.85-1.00) * |
| Stroke                             | 1.80 (1.52-2.15) * | 1.50 (1.32-1.71) * |
| Diabetes                           | 1.11 (0.99-1.24)   | 1.10 (1.01-1.21) * |
| Heart disease                      | 1.50 (1.26-1.78) * | 1.26 (1.13-1.41) * |
| COPD                               | 1.60 (1.40-1.82) * | 1.57 (1.40-1.76) * |
| Deaf / serious hearing problem     | 2.50 (2.14-2.92) * | 1.88 (1.71-2.07) * |
| No exercise                        | 1.41 (1.28-1.55) * | 1.17 (1.07-1.28) * |
| Current smoker                     | 1.00 (0.89-1.12)   | 0.89 (0.77-1.02)   |
| Obese                              | 0.96 (0.88-1.05)   | 1.02 (0.94-1.11)   |
| Depression                         | 4.08 (3.73-4.47) * | 3.10 (2.82-3.40) * |

## Is the effect different for younger people? (model B)

| Factor         | Different for younger?   | p-value   |
|:---------------|:-------------------------|:----------|
| Income         | Yes                      | < 0.001   |
| Education      | Yes                      | 0.004     |
| Stroke         | Yes                      | 0.013     |
| COPD           | Yes                      | 0.013     |
| Deaf / hearing | Yes                      | 0.003     |
| Depression     | Yes                      | < 0.001   |
| No exercise    | Yes                      | < 0.001   |
| Diabetes       | Not proven               | 0.263     |
| Heart disease  | Yes                      | 0.026     |

Data: CDC Behavioral Risk Factor Surveillance System (BRFSS) 2023 and 2024, national files, Cognitive Decline module.