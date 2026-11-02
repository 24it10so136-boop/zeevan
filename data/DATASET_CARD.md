# Symptom dataset card

## Source

- Original repository: https://github.com/anujdutt9/Disease-Prediction-from-Symptoms
- Original dataset source cited by that repository: https://www.kaggle.com/kaushil268/disease-prediction-using-machine-learning
- File used: `dataset/training_data.csv`
- Retrieved for this local development project on 2026-09-26.

## Contents

The dataset contains binary symptom columns and a `prognosis` target column. It is used here only for an educational, illustrative model pipeline. It is **not clinically validated** and must not be used for diagnosis or treatment decisions.

## Local handling

`backend/app/ml/train.py` cleans column names, handles duplicate headers, fills missing values, adds a symptom-count feature, trains a RandomForest classifier, reports accuracy/macro-F1, and saves the model artifact used by the API.

## Symptom-led matching and limits

Free-text symptom matching is maintained separately in `backend/app/nlp.py`. Its English, Hindi, and Hinglish aliases map patient wording to symptom concepts; several extra concepts are retained for safety and follow-up even when the original CSV has no corresponding feature. A symptom phrase match is not evidence that a disease is present. The classifier can only use features represented in the source CSV, so newly recognized concepts do not expand its learned disease associations.

Do not add synthetic symptom/disease rows to this source dataset and present them as better clinical evidence. A meaningful training-data expansion needs diverse, deduplicated patient examples with clinician-confirmed labels, provenance, consent, and an independent validation set. Until that exists, the app should describe its model output as an educational pattern match and base care guidance on reported symptoms and urgent warning signs, not on the top disease label.

## Condition overlap shown to users

For at least two symptoms represented in the CSV, `backend/app/ml/predict.py` compares the reported features with each condition's grouped CSV profile. A feature is included in a condition pattern when it occurs in at least half of that condition's rows. Results list the shared symptom names and count. The count is an overlap measure only; it is not a likelihood, probability, or diagnosis. The CSV has no validated urgency or home-treatment labels, so care guidance is based separately on symptoms, red flags, and whether symptoms are mild and improving.
