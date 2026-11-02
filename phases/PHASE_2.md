# Phase 2 — Real symptom dataset and machine learning

## Pipeline

```text
Real symptom dataset
        ↓
Data preprocessing
        ↓
Feature engineering
        ↓
ML model
        ↓
Model evaluation
        ↓
Prediction API
        ↓
ZEEVAN
```

## Implementation

- Dataset: `data/raw/training_data.csv`, sourced from the public repository cited in `data/DATASET_CARD.md`
- Preprocessing: normalized headers, duplicate-header handling, numeric coercion, missing-value fill, binary clipping
- Feature engineering: 133 cleaned symptom features plus `symptom_count`
- Model: `RandomForestClassifier`, 240 estimators, stratified 80/20 split, fixed random seed
- Evaluation: accuracy, macro-F1, and full per-class classification report
- Artifact: `backend/app/ml/artifacts/symptom_model.joblib`
- Metrics: `reports/model_evaluation.json`
- Training command (PowerShell):

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m app.ml.train
```

## Important limitation

The source dataset is an educational disease/symptom dataset and is not clinically validated. The model is only a software-pipeline demonstration. It must not be used for diagnosis, triage, or treatment decisions.
