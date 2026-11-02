import json, os
from pathlib import Path
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import (
    User, SymptomCheck, Symptom, FollowUpQuestion, FollowUpAnswer,
    HealthJourneyNote, ModelRun, PredictionLog, FeedbackLog
)
from .auth import create_token, current_user, hash_password, required_user, verify_password
from .ai import analyze, normalize
from .ml.predict import model_metadata, predict_full, ARTIFACT
from .ml.preprocess import RAW_DATASET, load_dataset

# ── App Setup ────────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Zeevan AI Health API", version="3.0.0")
origins = [
    x.strip()
    for x in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if x.strip()
]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

# Paths for AI status reporting
ROOT        = Path(__file__).resolve().parents[2]
WEB_DIST    = ROOT / "frontend" / "dist"
DB_PATH     = ROOT / "zeevan.db"
REPORT_PATH = ROOT / "reports" / "model_evaluation.json"

# ── Pydantic Models ──────────────────────────────────────────────────────────
class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2)
    email: str
    password: str = Field(min_length=8)

class LoginIn(BaseModel):
    email: str
    password: str

class CheckIn(BaseModel):
    description: str = Field(min_length=2)
    selected: list[str] = []

class AnalyzeIn(BaseModel):
    answers: dict[str, str] = {}

class FeedbackIn(BaseModel):
    was_helpful: bool
    actual_disease: str | None = None
    comment: str | None = None

# ── Health ───────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "zeevan-ai-api", "version": "3.0.0"}

# ── Auth ─────────────────────────────────────────────────────────────────────
@app.post("/api/auth/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    """Create a new user account. Credentials are stored in zeevan.db → users table."""
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(409, "An account with that email already exists.")
    user = User(
        full_name=payload.full_name,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password)
    )
    db.add(user); db.commit(); db.refresh(user)
    return {
        "access_token": create_token(user.id),
        "token_type": "bearer",
        "user": {"id": user.id, "full_name": user.full_name, "email": user.email},
    }

@app.post("/api/auth/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT access token."""
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password.")
    return {
        "access_token": create_token(user.id),
        "token_type": "bearer",
        "user": {"id": user.id, "full_name": user.full_name, "email": user.email},
    }

@app.get("/api/auth/me")
def me(user=Depends(required_user)):
    return {"id": user.id, "full_name": user.full_name, "email": user.email}

# ── AI System Info ───────────────────────────────────────────────────────────
@app.get("/api/ai/status")
def ai_status(db: Session = Depends(get_db)):
    """
    Returns the complete system status:
    - Backend URL where the API is running
    - Absolute path to the SQLite database
    - Absolute path to the trained ML model
    - Database table record counts
    - Model metadata
    """
    # Count records in each table
    table_counts = {
        "users":                db.query(User).count(),
        "symptom_checks":       db.query(SymptomCheck).count(),
        "symptoms":             db.query(Symptom).count(),
        "follow_up_questions":  db.query(FollowUpQuestion).count(),
        "follow_up_answers":    db.query(FollowUpAnswer).count(),
        "health_journey_notes": db.query(HealthJourneyNote).count(),
        "model_runs":           db.query(ModelRun).count(),
        "prediction_logs":      db.query(PredictionLog).count(),
        "feedback_logs":        db.query(FeedbackLog).count(),
    }
    meta = model_metadata()
    return {
        "backend": {
            "url":     "http://localhost:8000",
            "docs":    "http://localhost:8000/docs",
            "version": "3.0.0",
            "status":  "running",
        },
        "database": {
            "type":        "SQLite" if engine.dialect.name == "sqlite" else engine.dialect.name.capitalize(),
            "path":        str(DB_PATH.resolve()) if engine.dialect.name == "sqlite" else None,
            "tables":      table_counts,
            "description": "All user accounts, symptom checks, and AI prediction logs are stored here.",
        },
        "model": {
            **meta,
            "path":        str(ARTIFACT.resolve()),
            "report_path": str(REPORT_PATH.resolve()),
            "algorithm":   "RandomForestClassifier (240 trees)",
            "diseases":    41,
            "description": "Trained on anujdutt9/Disease-Prediction-from-Symptoms dataset with 4920 samples.",
        },
    }

@app.get("/api/ai/dataset")
def ai_dataset():
    """Expose a small, read-only view of the model's local training data for demos."""
    if not RAW_DATASET.exists():
        raise HTTPException(404, "Training dataset is not present on this server.")

    frame, symptom_columns = load_dataset(RAW_DATASET)
    class_counts = frame["prognosis"].value_counts().sort_index().to_dict()
    preview = []
    for _, row in frame.head(5).iterrows():
        preview.append({
            "prognosis": str(row["prognosis"]),
            "active_symptoms": [name for name in symptom_columns if int(row[name]) == 1],
        })

    return {
        "source": "anujdutt9/Disease-Prediction-from-Symptoms",
        "file": str(RAW_DATASET),
        "rows": int(len(frame)),
        "target_column": "prognosis",
        "class_count": int(frame["prognosis"].nunique()),
        "class_distribution": {str(key): int(value) for key, value in class_counts.items()},
        "symptom_feature_count": len(symptom_columns),
        "symptom_features": symptom_columns,
        "engineered_feature": "symptom_count (sum of active symptom columns)",
        "preview": preview,
        "training_configuration": {
            "algorithm": "RandomForestClassifier",
            "n_estimators": 240,
            "class_weight": "balanced_subsample",
            "random_state": 42,
            "split": "Stratified 80/20 holdout",
            "cross_validation": "5-fold accuracy evaluation",
        },
        "libraries": {
            "pandas": __import__("pandas").__version__,
            "numpy": __import__("numpy").__version__,
            "scikit_learn": __import__("sklearn").__version__,
            "joblib": __import__("joblib").__version__,
        },
        "limitations": "Educational dataset with repeated or near-duplicate symptom patterns; not clinically validated.",
    }

@app.get("/api/ai/metrics")
def ai_metrics():
    """
    Returns the saved ML model evaluation metrics from the last training run.
    Includes accuracy, precision, recall, F1, per-disease breakdown, and feature importances.
    
    How accuracy is measured:
    - 80/20 stratified holdout split (random_state=42)
    - Macro F1 / precision / recall averaged across all 41 disease classes
    
    How to improve accuracy:
    - Collect more diverse real-world symptom data
    - Use user feedback (FeedbackLog) to identify incorrect predictions
    - Trigger retraining via POST /api/ai/retrain
    - Tune n_estimators, max_depth, or switch to GradientBoostingClassifier
    """
    if not REPORT_PATH.exists():
        return {
            "available": False,
            "message": "No evaluation report found. Run POST /api/ai/retrain first.",
        }
    report = json.loads(REPORT_PATH.read_text())

    # Build per-class table (exclude aggregate rows)
    skip = {"accuracy", "macro avg", "weighted avg"}
    per_class = [
        {
            "disease":   disease,
            "precision": round(vals["precision"], 4),
            "recall":    round(vals["recall"], 4),
            "f1":        round(vals["f1-score"], 4),
            "support":   int(vals["support"]),
        }
        for disease, vals in report.get("classification_report", {}).items()
        if disease not in skip and isinstance(vals, dict)
    ]
    per_class.sort(key=lambda x: x["f1"], reverse=True)

    return {
        "available":       True,
        "accuracy":        report.get("accuracy"),
        "macro_f1":        report.get("macro_f1"),
        "precision_macro": report.get("precision_macro", report.get("classification_report", {}).get("macro avg", {}).get("precision")),
        "recall_macro":    report.get("recall_macro",    report.get("classification_report", {}).get("macro avg", {}).get("recall")),
        "cross_validation": report.get("cross_validation"),
        "dataset":         report.get("dataset"),
        "rows":            report.get("rows"),
        "classes":         report.get("classes"),
        "symptom_features": report.get("symptom_features"),
        "model":           report.get("model"),
        "n_estimators":    report.get("n_estimators", 240),
        "split":           report.get("split"),
        "limitations":     report.get("limitations"),
        "feature_importance_top30": report.get("feature_importance_top30", []),
        "per_class":       per_class,
        "how_to_improve": [
            "Collect more real-world patient symptom data with doctor-confirmed diagnoses",
            "Use the FeedbackLog table — user 'not helpful' responses identify weak predictions",
            "Retrain via POST /api/ai/retrain when new data is added",
            "Run 5-fold cross-validation (built into retrain) to detect overfitting",
            "Add patient metadata features: age, gender, symptom duration, severity scores",
            "Tune hyperparameters: increase n_estimators, add max_depth constraint",
            "Experiment with GradientBoostingClassifier or XGBoost ensemble",
            "Apply SMOTE to balance underrepresented disease classes",
        ],
    }

@app.post("/api/ai/retrain")
def ai_retrain(bg: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Triggers model retraining in the background.
    New metrics are saved to reports/model_evaluation.json.
    A ModelRun record is created in the database for audit.
    """
    def _do_retrain():
        from .ml.train import train as run_train
        metrics = run_train()
        run = ModelRun(
            version=f"retrained-{__import__('datetime').datetime.utcnow().strftime('%Y%m%d-%H%M')}",
            accuracy=metrics["accuracy"],
            f1_macro=metrics["macro_f1"],
            precision_macro=metrics["precision_macro"],
            recall_macro=metrics["recall_macro"],
            dataset_rows=metrics["rows"],
            classes=metrics["classes"],
            features=metrics["symptom_features"],
            artifact_path=str(ARTIFACT.resolve()),
        )
        db.add(run); db.commit()
    bg.add_task(_do_retrain)
    return {
        "status": "retraining_started",
        "message": "Model retraining started in the background. Check /api/ai/metrics in ~60 seconds for updated results.",
    }

@app.get("/api/ai/history")
def ai_history(db: Session = Depends(get_db)):
    """Returns all historical model training runs for accuracy trend tracking."""
    runs = db.query(ModelRun).order_by(ModelRun.trained_at.desc()).all()
    return [
        {
            "id":              r.id,
            "version":         r.version,
            "accuracy":        r.accuracy,
            "f1_macro":        r.f1_macro,
            "precision_macro": r.precision_macro,
            "recall_macro":    r.recall_macro,
            "dataset_rows":    r.dataset_rows,
            "classes":         r.classes,
            "trained_at":      r.trained_at.isoformat() if r.trained_at else None,
        }
        for r in runs
    ]

@app.get("/api/ai/feedback/stats")
def feedback_stats(db: Session = Depends(get_db)):
    """Returns aggregate feedback stats for model quality monitoring."""
    total     = db.query(FeedbackLog).count()
    helpful   = db.query(FeedbackLog).filter(FeedbackLog.was_helpful == True).count()
    unhelpful = total - helpful
    return {
        "total_feedback":   total,
        "helpful":          helpful,
        "not_helpful":      unhelpful,
        "helpfulness_rate": round(helpful / total, 3) if total > 0 else None,
        "message":          "Low helpfulness rate indicates prediction errors — retrain or expand training data.",
    }

# ── Symptom Check ────────────────────────────────────────────────────────────
@app.post("/api/symptoms/check")
def check(payload: CheckIn, db: Session = Depends(get_db), user=Depends(current_user)):
    normalized = normalize(payload.description, payload.selected)
    item = SymptomCheck(
        user_id=user.id if user else None,
        initial_description=payload.description,
        normalized_symptoms=json.dumps(normalized)
    )
    db.add(item); db.flush()
    for name in normalized:
        symptom = db.query(Symptom).filter(Symptom.name == name).first() or Symptom(name=name, category="general")
        db.add(symptom); db.flush()
        item.symptoms.append(symptom)
    db.commit()
    return {
        "id": item.id,
        "normalized": normalized,
    }

@app.post("/api/symptoms/check/{check_id}/analyze")
def check_analyze(check_id: int, payload: AnalyzeIn, db: Session = Depends(get_db), user=Depends(current_user)):
    item = db.get(SymptomCheck, check_id)
    if not item:                                                     raise HTTPException(404, "Symptom check not found")
    if item.user_id and (not user or item.user_id != user.id):      raise HTTPException(403, "Not allowed")

    normalized = json.loads(item.normalized_symptoms)
    result = analyze(item.initial_description, normalized, payload.answers)
    item.follow_up_answers = json.dumps(payload.answers)
    item.result_json = json.dumps(result)
    item.status = "analyzed"

    # Log prediction to PredictionLog for audit / accuracy tracking
    if result.get("predictions"):
        top = result["predictions"][0]
        log = PredictionLog(
            symptom_check_id=check_id,
            user_id=user.id if user else None,
            input_symptoms=json.dumps(normalized),
            top_prediction=top["label"],
            top_confidence=top["confidence"],
            all_predictions=json.dumps(result.get("all_predictions", [])),
        )
        db.add(log)

    db.commit()
    return result

@app.post("/api/symptoms/{check_id}/save")
def save(check_id: int, db: Session = Depends(get_db), user=Depends(required_user)):
    item = db.get(SymptomCheck, check_id)
    if not item:                                   raise HTTPException(404, "Symptom check not found")
    if item.user_id and item.user_id != user.id:   raise HTTPException(403, "Not allowed")
    item.user_id = user.id; item.status = "saved"; db.commit()
    return {"success": True}

@app.post("/api/symptoms/{check_id}/feedback")
def submit_feedback(check_id: int, payload: FeedbackIn, db: Session = Depends(get_db), user=Depends(current_user)):
    """Record whether the AI result was helpful. Used to track and improve accuracy."""
    item = db.get(SymptomCheck, check_id)
    if not item: raise HTTPException(404, "Symptom check not found")
    log = FeedbackLog(
        symptom_check_id=check_id,
        user_id=user.id if user else None,
        was_helpful=payload.was_helpful,
        actual_disease=payload.actual_disease,
        comment=payload.comment,
    )
    db.add(log); db.commit()
    return {"success": True, "message": "Feedback recorded. Thank you for helping improve Zeevan's accuracy."}

# ── Health Journey ────────────────────────────────────────────────────────────
@app.get("/api/journeys")
def journeys(db: Session = Depends(get_db), user=Depends(required_user)):
    items = db.query(SymptomCheck).filter(SymptomCheck.user_id == user.id).order_by(SymptomCheck.created_at.desc()).all()
    result = []
    for x in items:
        syms = json.loads(x.normalized_symptoms) if x.normalized_symptoms else []
        res  = json.loads(x.result_json) if x.result_json else {}
        result.append({
            "id":         x.id,
            "title":      (syms[0].replace("_", " ").title() + " check") if syms else "Symptom check",
            "status":     x.status,
            "created_at": x.created_at.isoformat() if x.created_at else None,
            "detail":     x.initial_description[:120],
            "prediction": res.get("primary_label"),
            "confidence": res.get("predictions", [{}])[0].get("confidence") if res.get("predictions") else None,
        })
    return result

@app.post("/api/journeys/{check_id}/notes")
def add_note(check_id: int, note: str, db: Session = Depends(get_db), user=Depends(required_user)):
    item = db.query(SymptomCheck).filter(SymptomCheck.id == check_id, SymptomCheck.user_id == user.id).first()
    if not item: raise HTTPException(404, "Journey not found")
    db.add(HealthJourneyNote(symptom_check_id=check_id, note=note)); db.commit()
    return {"success": True}

@app.get("/api/journeys/{check_id}/result")
def get_journey_result(check_id: int, db: Session = Depends(get_db), user=Depends(required_user)):
    item = db.query(SymptomCheck).filter(SymptomCheck.id == check_id, SymptomCheck.user_id == user.id).first()
    if not item: raise HTTPException(404, "Journey not found")
    if not item.result_json: raise HTTPException(404, "No result for this check yet.")
    return json.loads(item.result_json)

# ── Legacy compat ─────────────────────────────────────────────────────────────
@app.get("/api/model")
def model_status():
    return model_metadata()

@app.get("/api/phases")
def phases():
    return {"phases": [
        {"id": 1, "name": "Product foundation",            "status": "complete"},
        {"id": 2, "name": "Dataset and machine learning",  "status": "complete", "model": model_metadata()},
        {"id": 3, "name": "NLP and safety integration",    "status": "complete"},
        {"id": 4, "name": "AI dashboard and auth rebuild", "status": "complete"},
    ]}

# ── Frontend ──────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def frontend_index():
    index = WEB_DIST / "index.html"
    if not index.is_file():
        raise HTTPException(404, "Frontend build not found. Run npm --prefix frontend run build.")
    return FileResponse(index)

@app.get("/{path:path}", include_in_schema=False)
def frontend_routes(path: str):
    # Keep unknown API URLs as API 404s instead of returning the SPA document.
    if path == "api" or path.startswith("api/"):
        raise HTTPException(404, "API endpoint not found.")
    dist_root = WEB_DIST.resolve()
    requested = (dist_root / path).resolve()
    try:
        requested.relative_to(dist_root)
    except ValueError:
        raise HTTPException(404, "Not found.")
    if requested.is_file():
        return FileResponse(requested)
    # Client-side routes such as /check and /journey load through the SPA shell.
    index = dist_root / "index.html"
    if index.is_file():
        return FileResponse(index)
    raise HTTPException(404, "Frontend build not found.")
