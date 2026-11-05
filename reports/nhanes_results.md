# NHANES 2011-2014: low memory test score, people 60+

Low test score = bottom 25% (weighted) of the combined score of three tests (word list learning and recall, animal naming, symbol matching). Not a dementia diagnosis.

## Weighted % with a low test score

|                                        |   Younger (60-69) |   Older (70+) |
|:---------------------------------------|------------------:|--------------:|
| ('Overall', 'Everyone')                |              14.7 |          38   |
| ('Age', '70-74')                       |             nan   |          24.7 |
| ('Age', '75-79')                       |             nan   |          37.9 |
| ('Age', '80+')                         |             nan   |          55.3 |
| ('Age', '60-64')                       |              12.6 |         nan   |
| ('Age', '65-69')                       |              17.6 |         nan   |
| ('Income', 'Under $25k')               |              30.8 |          50.2 |
| ('Income', '$25-55k')                  |              17.6 |          39.6 |
| ('Income', '$55-100k')                 |               7.7 |          29.6 |
| ('Income', '$100k+')                   |               5.6 |          21.9 |
| ('Education', 'Less than high school') |              41.9 |          64   |
| ('Education', 'High school')           |              21.4 |          40.9 |
| ('Education', 'Some college')          |               9.6 |          30.8 |
| ('Education', 'College graduate')      |               4.9 |          24.5 |
| ('Health', 'Depression')               |              29.8 |          55.2 |
| ('Health', 'Hearing problem')          |              23   |          49.4 |
| ('Health', 'Stroke')                   |              29.6 |          57   |
| ('Health', 'COPD')                     |              22.2 |          33.3 |
| ('Health', 'Heart disease')            |              21.8 |          40.5 |
| ('Health', 'Diabetes')                 |              24.2 |          46.7 |
| ('Health', 'High blood pressure')      |              17.1 |          41.1 |
| ('Health', 'No exercise')              |              19.8 |          44.8 |
| ('Health', 'Current smoker')           |              18.2 |          50.9 |

## Model 1: everyone (2011-2014), without hearing

Odds ratio (95% CI); * = p < 0.05. All factors adjusted for each other.

|                                    | Younger (60-69) (n=1,422)   | Older (70+) (n=1,197)   |
|:-----------------------------------|:----------------------------|:------------------------|
| Less than high school (vs college) | 7.93 (3.40-18.49) *         | 3.91 (2.15-7.13) *      |
| High school (vs college)           | 4.70 (1.62-13.64) *         | 1.81 (1.15-2.84) *      |
| Some college (vs college)          | 1.93 (0.82-4.55)            | 1.35 (0.92-2.00)        |
| Income under $25k (vs $100k+)      | 2.57 (0.99-6.70)            | 2.20 (1.23-3.95) *      |
| Income $25-55k (vs $100k+)         | 1.56 (0.61-3.98)            | 1.65 (1.01-2.68) *      |
| Income $55-100k (vs $100k+)        | 0.99 (0.35-2.84)            | 1.27 (0.67-2.39)        |
| Age (per 10 years)                 | 2.94 (1.27-6.79) *          | 5.26 (3.27-8.45) *      |
| Female                             | 0.49 (0.30-0.80) *          | 0.54 (0.39-0.75) *      |
| Depression                         | 1.71 (1.04-2.81) *          | 1.88 (1.14-3.11) *      |
| Stroke                             | 1.18 (0.49-2.81)            | 1.87 (1.08-3.24) *      |
| Diabetes                           | 1.28 (0.79-2.09)            | 1.33 (0.94-1.89)        |
| Heart disease                      | 1.10 (0.49-2.50)            | 0.74 (0.47-1.15)        |
| COPD                               | 1.31 (0.72-2.37)            | 0.72 (0.40-1.27)        |
| No exercise                        | 1.47 (1.00-2.17) *          | 1.45 (1.02-2.07) *      |
| Current smoker                     | 0.71 (0.35-1.44)            | 1.79 (0.84-3.85)        |

## Model 2: 2011-2012 only, with hearing

Odds ratio (95% CI); * = p < 0.05. All factors adjusted for each other.

|                                    | Younger (60-69) (n=673)   | Older (70+) (n=539)   |
|:-----------------------------------|:--------------------------|:----------------------|
| Less than high school (vs college) | 7.99 (2.33-27.45) *       | 6.27 (2.28-17.26) *   |
| High school (vs college)           | 5.24 (0.91-30.38)         | 1.67 (0.89-3.12)      |
| Some college (vs college)          | 1.31 (0.38-4.56)          | 1.35 (0.73-2.47)      |
| Income under $25k (vs $100k+)      | 5.33 (1.11-25.75) *       | 2.54 (1.01-6.42) *    |
| Income $25-55k (vs $100k+)         | 3.84 (0.89-16.70)         | 1.65 (0.75-3.61)      |
| Income $55-100k (vs $100k+)        | 1.94 (0.42-8.83)          | 1.46 (0.49-4.36)      |
| Age (per 10 years)                 | 3.50 (0.83-14.83)         | 5.09 (2.51-10.30) *   |
| Female                             | 0.25 (0.11-0.60) *        | 0.65 (0.41-1.04)      |
| Depression                         | 2.14 (0.90-5.08)          | 4.51 (1.65-12.29) *   |
| Stroke                             | 0.95 (0.29-3.08)          | 2.25 (1.03-4.90) *    |
| Diabetes                           | 1.57 (0.71-3.48)          | 1.54 (0.81-2.94)      |
| Heart disease                      | 2.47 (0.54-11.32)         | 0.49 (0.23-1.05)      |
| COPD                               | 1.17 (0.58-2.39)          | 0.41 (0.18-0.94) *    |
| No exercise                        | 1.93 (0.86-4.36)          | 1.36 (0.82-2.26)      |
| Current smoker                     | 0.52 (0.15-1.86)          | 1.18 (0.43-3.26)      |
| Hearing problem                    | 1.47 (0.55-3.94)          | 1.01 (0.58-1.78)      |

Data: CDC National Health and Nutrition Examination Survey (NHANES) 2011-2012 and 2013-2014, public-use files, cognitive functioning (CFQ).