# Outreach scenario: who to reach first (BRFSS 2023 + 2024)

An example scenario, not a real client. For outreach only, never for pricing or refusing cover.

## Group sizes (one average year, 37 states, rounded, rough)

| group                                          |   people_in_survey |   est_adults |   memory_loss_pct |   est_with_memory_loss |   share_of_all_cases_pct |
|:-----------------------------------------------|-------------------:|-------------:|------------------:|-----------------------:|-------------------------:|
| Everyone 45+                                   |             208171 |     71993000 |              16.6 |               11928000 |                    100   |
| Everyone 65+ (age only)                        |             115070 |     31988000 |              17.2 |                5486000 |                     46   |
| Everyone 45-64                                 |              93101 |     40005000 |              16.1 |                6442000 |                     54   |
| 45-64, low income (under $25k)                 |              12290 |      5028000 |              29.7 |                1495000 |                     12.5 |
| 45-64, depression                              |              22150 |      8589000 |              37.1 |                3184000 |                     26.7 |
| 45-64, hearing problem                         |               6230 |      2612000 |              37.1 |                 968000 |                      8.1 |
| 45-64, stroke                                  |               3680 |      1575000 |              36.5 |                 575000 |                      4.8 |
| 45-64, any of: low income, depression, hearing |              32564 |     13128000 |              30.5 |                4008000 |                     33.6 |
| 65+, low income (under $25k)                   |              14851 |      4504000 |              21.4 |                 965000 |                      8.1 |
| 65+, depression                                |              18528 |      4851000 |              35   |                1697000 |                     14.2 |
| 65+, hearing problem                           |              19647 |      5168000 |              28.3 |                1461000 |                     12.3 |
| 65+, stroke                                    |               8863 |      2510000 |              26.6 |                 667000 |                      5.6 |

## Targeting on the test set (52,043 people, ROC AUC 0.712)

|   pct_contacted |   pct_cases_model |   pct_cases_oldest_first |   pct_cases_random |
|----------------:|------------------:|-------------------------:|-------------------:|
|               5 |              15.7 |                      6   |                  5 |
|              10 |              28   |                     12   |                 10 |
|              20 |              44.8 |                     22.2 |                 20 |
|              30 |              57.2 |                     32.7 |                 30 |
|              50 |              74.9 |                     52.5 |                 50 |

Contact 20%: model reaches 44.8% of cases (95% interval 42.7-46.8), oldest first 22.2% (20.9-23.8), random 20%.

The model uses answers from the same interview, including depression and hearing. A real organisation may not have these answers for its members, and would get weaker results without them.

Data: CDC BRFSS 2023 and 2024, national files, Cognitive Decline module.