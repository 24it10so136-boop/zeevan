from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, Table
from sqlalchemy.orm import relationship
from .database import Base

symptom_check_symptoms = Table("symptom_check_symptoms", Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("symptom_check_id", ForeignKey("symptom_checks.id", ondelete="CASCADE"), nullable=False),
    Column("symptom_id", ForeignKey("symptoms.id", ondelete="CASCADE"), nullable=False),
    Column("severity", String(32)), Column("duration", String(64)))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(320), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    date_of_birth = Column(String(32))
    gender = Column(String(32))
    preferred_language = Column(String(32), default="English")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    checks = relationship("SymptomCheck", back_populates="user")
    prediction_logs = relationship("PredictionLog", back_populates="user")
    feedback_logs = relationship("FeedbackLog", back_populates="user")

class Symptom(Base):
    __tablename__ = "symptoms"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    category = Column(String(120))
    checks = relationship("SymptomCheck", secondary=symptom_check_symptoms, back_populates="symptoms")

class SymptomCheck(Base):
    __tablename__ = "symptom_checks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    initial_description = Column(Text, nullable=False)
    normalized_symptoms = Column(Text, nullable=False)
    status = Column(String(32), default="active", nullable=False)
    follow_up_answers = Column(Text)
    result_json = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="checks")
    symptoms = relationship("Symptom", secondary=symptom_check_symptoms, back_populates="checks")
    questions = relationship("FollowUpQuestion", back_populates="check", cascade="all, delete-orphan")
    notes = relationship("HealthJourneyNote", back_populates="check", cascade="all, delete-orphan")
    prediction_logs = relationship("PredictionLog", back_populates="symptom_check")
    feedback_logs = relationship("FeedbackLog", back_populates="symptom_check")

class FollowUpQuestion(Base):
    __tablename__ = "follow_up_questions"
    id = Column(Integer, primary_key=True)
    symptom_check_id = Column(Integer, ForeignKey("symptom_checks.id", ondelete="CASCADE"), nullable=False)
    question_key = Column(String(80), nullable=False)
    question_text = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)
    check = relationship("SymptomCheck", back_populates="questions")
    answers = relationship("FollowUpAnswer", back_populates="question", cascade="all, delete-orphan")

class FollowUpAnswer(Base):
    __tablename__ = "follow_up_answers"
    id = Column(Integer, primary_key=True)
    follow_up_question_id = Column(Integer, ForeignKey("follow_up_questions.id", ondelete="CASCADE"), nullable=False)
    answer = Column(String(200), nullable=False)
    question = relationship("FollowUpQuestion", back_populates="answers")

class HealthJourneyNote(Base):
    __tablename__ = "health_journey_notes"
    id = Column(Integer, primary_key=True)
    symptom_check_id = Column(Integer, ForeignKey("symptom_checks.id", ondelete="CASCADE"), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    check = relationship("SymptomCheck", back_populates="notes")

# ── AI Tracking Tables ────────────────────────────────────────────────────────

class ModelRun(Base):
    """Stores a record every time the ML model is trained or retrained."""
    __tablename__ = "model_runs"
    id = Column(Integer, primary_key=True)
    version = Column(String(120))
    accuracy = Column(Float)
    f1_macro = Column(Float)
    precision_macro = Column(Float)
    recall_macro = Column(Float)
    dataset_rows = Column(Integer)
    classes = Column(Integer)
    features = Column(Integer)
    artifact_path = Column(String(600))
    trained_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class PredictionLog(Base):
    """Logs every disease prediction made by the AI for audit and improvement."""
    __tablename__ = "prediction_logs"
    id = Column(Integer, primary_key=True)
    symptom_check_id = Column(Integer, ForeignKey("symptom_checks.id", ondelete="SET NULL"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    input_symptoms = Column(Text)          # JSON list of symptom names
    top_prediction = Column(String(200))   # Label of #1 predicted disease
    top_confidence = Column(Float)
    all_predictions = Column(Text)         # JSON list of {label, confidence}
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="prediction_logs")
    symptom_check = relationship("SymptomCheck", back_populates="prediction_logs")

class FeedbackLog(Base):
    """Stores user feedback — 'was this result helpful?' — for model improvement."""
    __tablename__ = "feedback_logs"
    id = Column(Integer, primary_key=True)
    symptom_check_id = Column(Integer, ForeignKey("symptom_checks.id", ondelete="SET NULL"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    was_helpful = Column(Boolean, nullable=False)
    actual_disease = Column(String(200))   # Optional: what the user's actual diagnosis was
    comment = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="feedback_logs")
    symptom_check = relationship("SymptomCheck", back_populates="feedback_logs")
