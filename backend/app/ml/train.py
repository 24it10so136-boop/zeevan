import json
from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, classification_report, f1_score,
    precision_score, recall_score, confusion_matrix
)
from sklearn.model_selection import cross_val_score, train_test_split
from .preprocess import RAW_DATASET, build_features, load_dataset

ROOT     = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "backend" / "app" / "ml" / "artifacts" / "symptom_model.joblib"
REPORT   = ROOT / "reports" / "model_evaluation.json"

def train():
    df, symptom_columns = load_dataset(RAW_DATASET)
    X = build_features(df, symptom_columns)
    y = df["prognosis"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=240,
        random_state=42,
        class_weight="balanced_subsample",
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    # Core metrics
    acc  = float(accuracy_score(y_test, predictions))
    f1   = float(f1_score(y_test, predictions, average="macro"))
    prec = float(precision_score(y_test, predictions, average="macro", zero_division=0))
    rec  = float(recall_score(y_test, predictions, average="macro", zero_division=0))

    # Per-class report
    cls_report = classification_report(y_test, predictions, output_dict=True)

    # 5-fold cross-validation on full dataset (accuracy)
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="accuracy", n_jobs=-1)
    cv_result = {
        "mean": float(cv_scores.mean()),
        "std": float(cv_scores.std()),
        "scores": [float(s) for s in cv_scores],
    }

    # Confusion matrix (class names + matrix)
    cm = confusion_matrix(y_test, predictions, labels=model.classes_)

    # Feature importances (top 30)
    feature_names = list(symptom_columns) + ["symptom_count"]
    importances = model.feature_importances_
    fi = sorted(
        zip(feature_names, importances), key=lambda x: x[1], reverse=True
    )[:30]
    feature_importance_top = [
        {"symptom": name.replace("_", " ").title(), "importance": round(float(imp), 6)}
        for name, imp in fi
    ]

    metrics = {
        "dataset": str(RAW_DATASET.relative_to(ROOT)),
        "rows": int(len(df)),
        "classes": int(y.nunique()),
        "symptom_features": int(len(symptom_columns)),
        "accuracy": acc,
        "macro_f1": f1,
        "precision_macro": prec,
        "recall_macro": rec,
        "cross_validation": cv_result,
        "classification_report": cls_report,
        "feature_importance_top30": feature_importance_top,
        "confusion_matrix_classes": list(model.classes_),
        "confusion_matrix": cm.tolist(),
        "model": "RandomForestClassifier",
        "n_estimators": 240,
        "random_state": 42,
        "split": "stratified 80/20 holdout",
        "artifact_path": str(ARTIFACT),
        "limitations": (
            "The source dataset contains repeated/near-duplicate symptom patterns, "
            "so holdout scores may be optimistic. This is not clinical validation."
        ),
    }

    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump({
        "model": model,
        "symptom_columns": symptom_columns,
        "feature_columns": list(X.columns),
        "dataset_source": "anujdutt9/Disease-Prediction-from-Symptoms",
        "model_version": "phase-3-rf-v2",
        "feature_importance_top30": feature_importance_top,
    }, ARTIFACT)

    REPORT.write_text(json.dumps(metrics, indent=2))

    summary = {k: metrics[k] for k in ["rows", "classes", "symptom_features", "accuracy", "macro_f1", "precision_macro", "recall_macro", "model"]}
    print(json.dumps(summary, indent=2))
    return metrics

if __name__ == "__main__":
    train()
