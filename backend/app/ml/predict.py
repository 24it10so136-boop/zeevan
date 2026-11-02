from pathlib import Path
import joblib
import pandas as pd
from .preprocess import load_dataset

ROOT     = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "backend" / "app" / "ml" / "artifacts" / "symptom_model.joblib"
_bundle  = None
_profile_cache = None

# NLP concepts that do not use the source CSV's exact feature spelling.
# Only map clear synonym/wording variants; do not infer unrelated features.
FEATURE_ALIASES = {
    "abdominal_pain": ["stomach_pain"],
    "burning_urination": ["burning_micturition"],
    "cold_hands_feet": ["cold_hands_and_feets"],
    "blurred_vision": ["blurred_and_distorted_vision"],
    "sore_throat": ["throat_irritation"],
}

LOWER_CONCERN_CONDITIONS = {
    "common cold", "allergy", "fungal infection", "acne", "gerd",
    "migraine", "dimorphic hemmorhoids(piles)", "varicose veins",
    "osteoarthristis", "arthritis", "psoriasis", "impetigo",
}
HIGHER_CONCERN_CONDITIONS = {
    "heart attack", "paralysis (brain hemorrhage)", "pneumonia", "dengue",
    "malaria", "typhoid", "hypoglycemia", "aids", "tuberculosis",
    "hepatitis a", "hepatitis b", "hepatitis c", "hepatitis d", "hepatitis e",
    "alcoholic hepatitis", "chronic cholestasis",
}


def _concern_band(condition: str) -> tuple[int, str]:
    key = condition.strip().lower()
    if key in LOWER_CONCERN_CONDITIONS:
        return 0, "Lower concern if symptoms are mild"
    if key in HIGHER_CONCERN_CONDITIONS:
        return 2, "Potentially serious; seek prompt medical assessment"
    return 1, "Discuss with a clinician if persistent or worsening"


def _dataset_features(symptoms: list[str], available: list[str]) -> list[str]:
    selected = set(available)
    mapped = set()
    for symptom in symptoms:
        if symptom in selected:
            mapped.add(symptom)
        mapped.update(feature for feature in FEATURE_ALIASES.get(symptom, []) if feature in selected)
    return sorted(mapped)

def load_bundle():
    global _bundle
    if _bundle is None and ARTIFACT.exists():
        _bundle = joblib.load(ARTIFACT)
    return _bundle

def predict(symptoms: list[str], top_k: int = 3) -> list[dict]:
    """Return top-k disease predictions with confidence scores."""
    bundle = load_bundle()
    if not bundle:
        return []
    columns = bundle["symptom_columns"]
    row = {col: 0 for col in columns}
    matched = _dataset_features(symptoms, columns)
    for s in matched:
        row[s] = 1
    frame = pd.DataFrame([row])
    frame["symptom_count"] = frame[columns].sum(axis=1)
    model = bundle["model"]
    proba = model.predict_proba(frame)[0]
    classes = model.classes_
    order = proba.argsort()[::-1][:top_k]
    top_results = [
        {"label": str(classes[i]), "confidence": round(float(proba[i]), 4)}
        for i in order
        if proba[i] > 0.001
    ]
    return top_results

def predict_full(symptoms: list[str], top_k: int = 3) -> dict:
    """Return predictions + feature importance + matched symptoms."""
    bundle = load_bundle()
    if not bundle:
        return {"predictions": [], "matched_symptoms": [], "feature_importance_top": []}

    columns = bundle["symptom_columns"]
    row = {col: 0 for col in columns}
    matched = _dataset_features(symptoms, columns)
    for s in matched:
        row[s] = 1

    frame = pd.DataFrame([row])
    frame["symptom_count"] = frame[columns].sum(axis=1)
    model = bundle["model"]
    proba = model.predict_proba(frame)[0]
    classes = model.classes_

    # All predictions (confidence > 0)
    all_preds = [
        {"label": str(classes[i]), "confidence": round(float(proba[i]), 4)}
        for i in proba.argsort()[::-1]
        if proba[i] > 0.0001
    ][:12]  # cap at 12 for display

    top_preds = [p for p in all_preds[:top_k]]

    # Feature importance from RF model (global, top-20)
    feature_names = list(columns) + ["symptom_count"]
    importances = model.feature_importances_
    fi_pairs = sorted(
        zip(feature_names, importances), key=lambda x: x[1], reverse=True
    )[:20]
    fi_top = [
        {"symptom": name.replace("_", " ").title(), "importance": round(float(imp), 5)}
        for name, imp in fi_pairs
    ]

    # Which of the user's symptoms are in the top-20 important features
    top_feature_names = {name for name, _ in fi_pairs}
    triggered = [s.replace("_", " ").title() for s in matched if s in top_feature_names]

    return {
        "predictions": top_preds,
        "all_predictions": all_preds,
        "matched_symptoms": [s.replace("_", " ").title() for s in matched],
        "triggered_key_features": triggered,
        "feature_importance_top": fi_top,
    }


def rank_dataset_symptom_matches(symptoms: list[str], top_k: int = 5) -> list[dict]:
    """Rank condition rows by shared reported symptoms; this is not a diagnosis probability."""
    global _profile_cache
    bundle = load_bundle()
    if not bundle:
        return []
    feature_columns = bundle["symptom_columns"]
    reported = {}
    for symptom in set(symptoms):
        possible = FEATURE_ALIASES.get(symptom, [symptom])
        if symptom == "fever":
            # The data has severity-specific fever features; for overlap only,
            # generic fever can match either without asserting its severity.
            possible = ["mild_fever", "high_fever"]
        features = [feature for feature in possible if feature in feature_columns]
        if features:
            reported[symptom] = features
    if "high_fever" in reported:
        reported.pop("fever", None)
    if not reported:
        return []

    if _profile_cache is None:
        frame, csv_features = load_dataset()
        valid_features = [name for name in feature_columns if name in csv_features]
        means = frame.groupby("prognosis")[valid_features].mean()
        support = frame.groupby("prognosis").size()
        _profile_cache = (means, support, valid_features)

    means, support, available = _profile_cache
    reported = {name: [feature for feature in features if feature in available] for name, features in reported.items()}
    reported = {name: features for name, features in reported.items() if features}
    if not reported:
        return []

    ranked = []
    for disease, profile in means.iterrows():
        # Treat a feature as part of a condition's repeated dataset pattern when
        # it appears in at least half of that condition's source rows.
        shared = [
            name for name, features in reported.items()
            if any(float(profile[feature]) >= 0.5 for feature in features)
        ]
        if not shared:
            continue
        ranked.append({
            "label": str(disease),
            "concern_order": _concern_band(str(disease))[0],
            "concern_label": _concern_band(str(disease))[1],
            "shared_symptoms": [name.replace("_", " ").title() for name in shared],
            "shared_count": len(shared),
            "reported_symptom_count": len(reported),
            "overlap_pct": round(100 * len(shared) / len(reported)),
            "dataset_rows": int(support[disease]),
        })

    # Show lower concern patterns first and higher concern patterns last.
    # Match count breaks ties within each general concern band.
    ranked.sort(key=lambda item: (item["concern_order"], -item["shared_count"], -item["overlap_pct"], item["label"]))
    return ranked[:top_k]

def model_metadata() -> dict:
    bundle = load_bundle()
    if not bundle:
        return {"available": False, "version": "fallback", "message": "Model not loaded — run retrain first."}
    return {
        "available": True,
        "version": bundle.get("model_version"),
        "features": len(bundle["symptom_columns"]),
        "dataset_source": bundle.get("dataset_source"),
        "artifact_path": str(ARTIFACT),
    }
