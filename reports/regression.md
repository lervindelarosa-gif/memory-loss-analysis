# Statistics: memory loss in BRFSS 2023 + 2024

Weighted logistic regression. Odds ratio (95% confidence interval); * = p < 0.05. All factors adjusted for each other, plus state and year. Standard errors clustered by survey PSU.

| Group | People (complete answers) | With memory loss | Weighted % |
| --- | --- | --- | --- |
| Younger (45-64) | 86,190 | 13,928 | 16.0% |
| Older (65+) | 104,509 | 17,908 | 17.0% |

## Model A: without depression

|                                    | Younger (45-64)    | Older (65+)        |
|:-----------------------------------|:-------------------|:-------------------|
| Less than high school (vs college) | 1.06 (0.87-1.29)   | 1.22 (1.01-1.48) * |
| High school (vs college)           | 1.06 (0.93-1.20)   | 0.98 (0.88-1.09)   |
| Some college (vs college)          | 1.10 (0.98-1.23)   | 0.98 (0.89-1.07)   |
| Income under $15k (vs $200k+)      | 3.09 (2.42-3.95) * | 1.26 (0.87-1.82)   |
| Income $15-25k (vs $200k+)         | 2.54 (1.93-3.33) * | 1.34 (0.95-1.88)   |
| Income $25-35k (vs $200k+)         | 2.02 (1.58-2.58) * | 1.24 (0.88-1.73)   |
| Income $35-50k (vs $200k+)         | 1.66 (1.33-2.08) * | 1.16 (0.84-1.60)   |
| Income $50-100k (vs $200k+)        | 1.53 (1.25-1.87) * | 1.11 (0.81-1.50)   |
| Income $100-200k (vs $200k+)       | 1.30 (1.07-1.57) * | 0.90 (0.66-1.22)   |
| Income unknown (vs $200k+)         | 1.43 (1.14-1.80) * | 1.06 (0.77-1.46)   |
| Age (per 10 years)                 | 0.91 (0.84-0.99) * | 1.08 (0.99-1.18)   |
| Female                             | 1.30 (1.18-1.43) * | 1.08 (0.99-1.18)   |
| Stroke                             | 2.09 (1.77-2.47) * | 1.55 (1.37-1.76) * |
| Diabetes                           | 1.21 (1.08-1.35) * | 1.14 (1.04-1.25) * |
| Heart disease                      | 1.56 (1.31-1.86) * | 1.32 (1.18-1.48) * |
| COPD                               | 2.11 (1.86-2.39) * | 1.77 (1.57-1.99) * |
| Deaf / serious hearing problem     | 2.76 (2.40-3.18) * | 2.05 (1.86-2.27) * |
| No exercise                        | 1.51 (1.36-1.68) * | 1.25 (1.14-1.37) * |
| Current smoker                     | 1.13 (1.00-1.27) * | 0.90 (0.79-1.04)   |
| Obese                              | 1.02 (0.93-1.12)   | 1.04 (0.96-1.14)   |

## Model B: with depression

|                                    | Younger (45-64)    | Older (65+)        |
|:-----------------------------------|:-------------------|:-------------------|
| Less than high school (vs college) | 1.16 (0.96-1.41)   | 1.26 (1.04-1.51) * |
| High school (vs college)           | 1.18 (1.04-1.35) * | 1.05 (0.94-1.17)   |
| Some college (vs college)          | 1.12 (0.99-1.25)   | 1.01 (0.92-1.11)   |
| Income under $15k (vs $200k+)      | 2.38 (1.85-3.05) * | 1.16 (0.80-1.69)   |
| Income $15-25k (vs $200k+)         | 2.02 (1.55-2.62) * | 1.22 (0.86-1.73)   |
| Income $25-35k (vs $200k+)         | 1.86 (1.44-2.40) * | 1.17 (0.83-1.65)   |
| Income $35-50k (vs $200k+)         | 1.49 (1.18-1.87) * | 1.12 (0.80-1.56)   |
| Income $50-100k (vs $200k+)        | 1.40 (1.14-1.73) * | 1.07 (0.78-1.47)   |
| Income $100-200k (vs $200k+)       | 1.25 (1.03-1.53) * | 0.88 (0.64-1.22)   |
| Income unknown (vs $200k+)         | 1.35 (1.07-1.72) * | 1.04 (0.74-1.44)   |
| Age (per 10 years)                 | 0.98 (0.90-1.06)   | 1.22 (1.12-1.33) * |
| Female                             | 1.05 (0.95-1.16)   | 0.94 (0.86-1.02)   |
| Stroke                             | 1.85 (1.55-2.20) * | 1.50 (1.32-1.70) * |
| Diabetes                           | 1.12 (1.00-1.26) * | 1.10 (1.00-1.21)   |
| Heart disease                      | 1.50 (1.24-1.81) * | 1.25 (1.11-1.40) * |
| COPD                               | 1.61 (1.41-1.84) * | 1.57 (1.39-1.77) * |
| Deaf / serious hearing problem     | 2.46 (2.12-2.85) * | 1.92 (1.74-2.13) * |
| No exercise                        | 1.37 (1.24-1.51) * | 1.19 (1.09-1.30) * |
| Current smoker                     | 1.01 (0.90-1.14)   | 0.87 (0.76-1.01)   |
| Obese                              | 0.96 (0.87-1.05)   | 1.01 (0.92-1.10)   |
| Depression                         | 4.31 (3.90-4.75) * | 3.15 (2.85-3.48) * |

## Is the effect different for younger people? (model B)

| Factor         | Different for younger?   | p-value   |
|:---------------|:-------------------------|:----------|
| Income         | Yes                      | < 0.001   |
| Education      | Yes                      | 0.003     |
| Stroke         | Yes                      | 0.005     |
| COPD           | Yes                      | 0.009     |
| Deaf / hearing | Yes                      | 0.009     |
| Depression     | Yes                      | < 0.001   |
| No exercise    | Yes                      | < 0.001   |
| Diabetes       | Not proven               | 0.189     |
| Heart disease  | Yes                      | 0.023     |

Data: CDC Behavioral Risk Factor Surveillance System (BRFSS) 2023 and 2024, national files, Cognitive Decline module.