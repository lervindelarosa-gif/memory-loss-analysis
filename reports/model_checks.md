# How good is the outreach model?

Tested on 52,043 people the model did not train on. Finds people reporting memory loss now.

ROC AUC: 0.721 on training data, 0.712 on test data (95% interval 0.706-0.718). This is fair.

Average: 16.3% report memory loss.

## Ten equal groups, sorted by model score

|   Group (1 = highest scores) |   People |   % reporting memory loss |
|-----------------------------:|---------:|--------------------------:|
|                            1 |     5370 |                      45.6 |
|                            2 |     5779 |                      27.4 |
|                            3 |     5924 |                      20.2 |
|                            4 |     5928 |                      17.1 |
|                            5 |     5476 |                      11.8 |
|                            6 |     4680 |                      10.1 |
|                            7 |     4697 |                       9.9 |
|                            8 |     4455 |                       8.7 |
|                            9 |     4949 |                       7   |
|                           10 |     4785 |                       5.3 |

## Score for different groups

| Group             |   People |   ROC AUC |
|:------------------|---------:|----------:|
| Ages 45-64        |    23365 |     0.743 |
| Ages 65+          |    28678 |     0.68  |
| Women             |    28539 |     0.711 |
| Men               |    23504 |     0.713 |
| Income under $25k |     6795 |     0.729 |
| Income $100k+     |    12072 |     0.666 |

All checks use the same survey. Real health records could give weaker results.