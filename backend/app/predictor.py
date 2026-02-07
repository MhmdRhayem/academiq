import joblib
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.config import MODEL_PATH, FEATURE_COLUMNS_PATH, TARGET_COLUMNS_PATH, METADATA_PATH


class GradePredictor:
    def __init__(self):
        self.model = None
        self.feature_columns: List[str] = []
        self.target_columns: List[str] = []
        self.metadata: Dict = {}
        self._loaded = False

    def load_model(self) -> bool:
        try:
            self.model = joblib.load(MODEL_PATH)
            self.feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
            self.target_columns = joblib.load(TARGET_COLUMNS_PATH)

            with open(METADATA_PATH, 'r') as f:
                self.metadata = json.load(f)

            self._loaded = True
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            self._loaded = False
            return False

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