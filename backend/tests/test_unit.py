import pytest
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGradePredictor:
    """Unit tests for the GradePredictor class"""

    def test_predictor_initialization(self):
        """Test that predictor initializes with correct default values"""
        from app.predictor import GradePredictor

        predictor = GradePredictor()

        assert predictor.model is None
        assert predictor.feature_columns == []
        assert predictor.target_columns == []
        assert predictor.is_loaded is False

    def test_predictor_load_model_success(self):
        """Test successful model loading"""
        from app.predictor import GradePredictor

        predictor = GradePredictor()
        result = predictor.load_model()

        assert result is True
        assert predictor.is_loaded is True
        assert len(predictor.feature_columns) > 0
        assert len(predictor.target_columns) > 0
        assert predictor.model_name in ["XGBoost", "RandomForest", "Random Forest"]

    def test_predictor_get_model_info(self):
        """Test getting model information"""
        from app.predictor import GradePredictor

        predictor = GradePredictor()
        predictor.load_model()
        info = predictor.get_model_info()

        assert "model_name" in info
        assert "input_courses" in info
        assert "output_courses" in info
        assert "metrics" in info
        assert "rmse" in info["metrics"]
        assert "r2" in info["metrics"]