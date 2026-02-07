import joblib
import json
import numpy as np
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.config import (
    MODEL_PATH,
    FEATURE_COLUMNS_PATH,
    TARGET_COLUMNS_PATH,
    METADATA_PATH,
    MLFLOW_TRACKING_URI,
    MLFLOW_MODEL_NAME
)

# Lazy import MLflow only if needed
try:
    import mlflow
    import mlflow.pyfunc
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False


class GradePredictor:
    def __init__(self):
        self.model = None
        self.feature_columns: List[str] = []
        self.target_columns: List[str] = []
        self.metadata: Dict = {}
        self._loaded = False

    def load_model(self) -> bool:
        """
        Load model from MLflow Model Registry (if configured) or from local files.
        Priority: MLflow Registry > Local Files
        """
        try:
            # Try loading from MLflow Model Registry first
            if MLFLOW_AVAILABLE and MLFLOW_TRACKING_URI and MLFLOW_MODEL_NAME:
                try:
                    print(f"Attempting to load model from MLflow Registry: {MLFLOW_MODEL_NAME}")
                    return self._load_from_mlflow()
                except Exception as mlflow_error:
                    print(f"MLflow loading failed: {mlflow_error}")
                    print("Falling back to local model files...")

            # Fallback to local files
            print(f"Loading model from local files: {MODEL_PATH}")
            self.model = joblib.load(MODEL_PATH)
            self.feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
            self.target_columns = joblib.load(TARGET_COLUMNS_PATH)

            with open(METADATA_PATH, 'r') as f:
                self.metadata = json.load(f)

            self._loaded = True
            print(f"✓ Model loaded successfully from local files")
            return True
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            self._loaded = False
            return False

    def _load_from_mlflow(self) -> bool:
        """Load model from MLflow Model Registry"""
        # Set MLflow tracking URI
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

        # Set credentials if provided
        mlflow_user = os.getenv('MLFLOW_TRACKING_USERNAME', '')
        mlflow_password = os.getenv('MLFLOW_TRACKING_PASSWORD', '')
        if mlflow_user and mlflow_password:
            os.environ['MLFLOW_TRACKING_USERNAME'] = mlflow_user
            os.environ['MLFLOW_TRACKING_PASSWORD'] = mlflow_password

        # Load the latest production model or latest version
        try:
            model_uri = f"models:/{MLFLOW_MODEL_NAME}/Production"
            print(f"Trying to load Production version...")
            self.model = mlflow.pyfunc.load_model(model_uri)
        except Exception:
            # Fallback to latest version if no production model
            model_uri = f"models:/{MLFLOW_MODEL_NAME}/latest"
            print(f"No Production model found. Loading latest version...")
            self.model = mlflow.pyfunc.load_model(model_uri)

        # Load metadata from local files (features and targets)
        # Note: In a full MLflow setup, these could also be logged as artifacts
        self.feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
        self.target_columns = joblib.load(TARGET_COLUMNS_PATH)

        with open(METADATA_PATH, 'r') as f:
            self.metadata = json.load(f)

        self._loaded = True
        print(f"✓ Model loaded successfully from MLflow Registry: {model_uri}")
        return True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def model_name(self) -> str:
        return self.metadata.get("best_model", "Unknown")

    def get_model_info(self) -> Dict:
        if not self._loaded:
            return {}

        best_model_key = self.model_name.lower().replace(" ", "_")
        model_metrics = self.metadata.get(best_model_key, self.metadata.get("xgboost", {}))

        return {
            "model_name": self.model_name,
            "input_courses": self.feature_columns,
            "output_courses": self.target_columns,
            "metrics": {
                "rmse": model_metrics.get("rmse", 0),
                "r2": model_metrics.get("r2", 0),
                "cv_r2": model_metrics.get("cv_r2", 0)
            }
        }

    def predict(self, grades: Dict[str, float]) -> Tuple[Dict[str, float], str]:
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        input_array = np.array([[grades.get(c, 50.0) for c in self.feature_columns]])
        predictions = self.model.predict(input_array)[0]

        result = {}
        for i, course in enumerate(self.target_columns):
            result[course] = round(float(np.clip(predictions[i], 0, 100)), 2)

        return result, self.model_name


predictor = GradePredictor()