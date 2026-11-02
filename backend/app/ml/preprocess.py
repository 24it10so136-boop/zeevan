from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW_DATASET = ROOT / "data" / "raw" / "training_data.csv"

def clean_name(value: str) -> str:
    value = re.sub(r"\s+", "_", str(value).strip().lower())
    value = re.sub(r"[^a-z0-9_]+", "", value)
    return re.sub(r"_+", "_", value).strip("_")

def load_dataset(path: Path = RAW_DATASET) -> tuple[pd.DataFrame, list[str]]:
    df = pd.read_csv(path)
    cleaned = []
    counts = {}
    for column in df.columns:
        name = clean_name(column)
        counts[name] = counts.get(name, 0) + 1
        cleaned.append(name if counts[name] == 1 else f"{name}_{counts[name]}")
    df.columns = cleaned
    target = "prognosis"
    symptom_columns = [column for column in df.columns if column != target]
    for column in symptom_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int).clip(0, 1)
    df[target] = df[target].astype(str).str.strip()
    return df, symptom_columns

def build_features(df: pd.DataFrame, symptom_columns: list[str]) -> pd.DataFrame:
    features = df[symptom_columns].copy()
    features["symptom_count"] = features.sum(axis=1)
    return features
