# Does the BRFSS model also work on NHANES?

Trained only on BRFSS with inputs both surveys share. 95% intervals in brackets (simple bootstrap).

Inputs: age, female, education_level, income_band, depression, stroke, heart_disease, copd, diabetes, no_exercise, current_smoker. Income bands and the depression and exercise questions differ between surveys.

| Tested on                                             |   People |   % with the outcome | ROC AUC (model)     |   ROC AUC (age only) | Reached at 20%, model   | Reached at 20%, oldest first   |
|:------------------------------------------------------|---------:|---------------------:|:--------------------|---------------------:|:------------------------|:-------------------------------|
| BRFSS 60+ (not used in training): say memory is worse |    35877 |                 16.8 | 0.679 (0.659-0.698) |                0.52  | 40.6% (38.1-42.9)       | 23.0% (21.1-25.2)              |
| NHANES 60+: say they have memory problems             |     2932 |                 12.8 | 0.700 (0.659-0.741) |                0.579 | 41.3% (36.0-46.7)       | 30.4% (25.3-35.4)              |
| NHANES 60+: low memory test score                     |     2934 |                 25   | 0.716 (0.690-0.741) |                0.706 | 31.8% (28.6-36.2)       | 42.5% (38.5-45.3)              |

Only covers people aged 60+. Picking at random reaches 20%.