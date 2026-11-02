# Phase 3 — Natural language to safe Zeevan results

## Pipeline

```text
Natural language
        ↓
NLP
        ↓
Symptom extraction
        ↓
ML prediction
        ↓
Safety engine
        ↓
ZEEVAN result
```

## Implementation

- Natural-language input enters `/api/symptoms/check`.
- Deterministic local NLP in `backend/app/nlp.py` normalizes text, applies aliases, and extracts canonical symptoms.
- Extracted symptoms become the model feature vector in `backend/app/ml/predict.py`.
- The Phase 2 artifact returns top-k prediction labels and confidence scores.
- Independent urgent phrase detection runs separately from prediction.
- The response includes extracted symptoms, model metadata, predictions, explanations, practical advice, safety steps, and a non-diagnostic disclaimer.
- No LLM, paid API, cloud model, or external runtime is required.

## Safety boundary

The model is not a medical device and does not establish a diagnosis. Urgent phrases such as chest pain, severe breathing difficulty, fainting, or loss of consciousness trigger a safety notice. Users should contact local emergency services or a qualified professional when symptoms feel urgent.
