# Step 4: What the machine learning says (simple words)

Full tables: [ml_results.md](ml_results.md). Chart: [figures/05_ml_importance.png](figures/05_ml_importance.png).

## What the model does

BRFSS asks **different people every year**, so we cannot follow people and predict the future.
The model learns **who reports memory loss getting worse**, from the same interview.
208,171 people aged 45+, of whom 35,187 (16.9%) report memory loss. Balanced with class weights.

## Results

| Model | ROC AUC | Cases found |
|---|---|---|
| Logistic regression | 0.70 | 58% |
| Gradient boosting | **0.71** | 60% |

- ROC AUC 0.71 is **fair**. Memory loss here is people's own feeling, which is hard to predict
  from a few survey answers. (The HRS dementia model, with real memory tests, reached 0.83.)
- The model works **better for younger people (0.74)** than for older people (0.68):
  for younger people, the factors in the survey explain more.

## Which factors does the model need most?

| | Younger (45-64) | Older (65+) |
|---|---|---|
| 1 | **Depression** | **Depression** |
| 2 | **Income** | Hearing problem |
| 3 | Hearing problem | **Age** |
| 4 | COPD | COPD |
| Age | **almost not needed** (0.001) | needed (0.017) |

**For younger people, the model hardly needs age.** Depression, income and hearing matter more.
For older people, age is one of the top 3 factors.

This matches the statistics (step 3) and the HRS dementia project.

## Be careful

- Self-reported memory loss, not a diagnosis.
- Depression and memory complaints go together in both directions.
- Links, not causes. For learning, not for diagnosing a person. No model is saved.
