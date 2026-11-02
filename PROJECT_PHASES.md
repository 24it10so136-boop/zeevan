# ZEEVAN project phases

| Phase | Scope | Status | Evidence |
|---|---|---:|---|
| Phase 1 | Frontend, backend, PostgreSQL, authentication, symptom workflow, Health Journey, local demo engine | Complete | `phases/PHASE_1.md`, `backend/test_api.py` |
| Phase 2 | Real dataset, preprocessing, feature engineering, ML model, evaluation, prediction API | Complete | `phases/PHASE_2.md`, `data/raw/training_data.csv`, `backend/app/ml/`, `reports/model_evaluation.json` |
| Phase 3 | Natural language, NLP, symptom extraction, ML prediction, safety engine, Zeevan result | Complete | `phases/PHASE_3.md`, `backend/app/nlp.py`, `backend/app/ai.py` |

## Verification checklist

- [x] Local frontend package runs with npm
- [x] Local backend runs with Python
- [x] PostgreSQL schema and seed are included
- [x] JWT authentication is local
- [x] Symptom and follow-up endpoints are covered by tests
- [x] Model training is reproducible locally
- [x] Model evaluation report is generated
- [x] Prediction API uses the trained artifact when available
- [x] NLP extraction is deterministic and offline
- [x] Safety engine runs independently from prediction
- [x] Result is non-diagnostic and includes practical guidance
