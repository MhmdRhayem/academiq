import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "best_model.pkl"))
FEATURE_COLUMNS_PATH = os.getenv("FEATURE_COLUMNS_PATH", str(BASE_DIR / "models" / "feature_columns.pkl"))
TARGET_COLUMNS_PATH = os.getenv("TARGET_COLUMNS_PATH", str(BASE_DIR / "models" / "target_columns.pkl"))
METADATA_PATH = os.getenv("METADATA_PATH", str(BASE_DIR / "models" / "model_metadata.json"))

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "")
MLFLOW_MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME", "grade-predictor")