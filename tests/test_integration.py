import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPredictionIntegration:
    """Integration tests for the prediction pipeline"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup predictor before each test"""
        from app.predictor import GradePredictor

        self.predictor = GradePredictor()
        self.predictor.load_model()

    def test_prediction_with_complete_grades(self):
        """Test prediction with all input courses provided"""
        grades = {course: 75.0 for course in self.predictor.feature_columns}
        predictions, model_name = self.predictor.predict(grades)

        assert isinstance(predictions, dict)
        assert len(predictions) == len(self.predictor.target_columns)
        for course, grade in predictions.items():
            assert 0 <= grade <= 100
            assert course in self.predictor.target_columns

    def test_prediction_with_partial_grades(self):
        """Test prediction with only some input courses (should use defaults)"""
        partial_grades = {
            self.predictor.feature_columns[0]: 80.0,
            self.predictor.feature_columns[1]: 70.0,
        }

        predictions, model_name = self.predictor.predict(partial_grades)

        assert isinstance(predictions, dict)
        assert len(predictions) == len(self.predictor.target_columns)

    def test_prediction_consistency(self):
        """Test that same input produces consistent output"""
        grades = {course: 60.0 for course in self.predictor.feature_columns}

        predictions1, _ = self.predictor.predict(grades)
        predictions2, _ = self.predictor.predict(grades)

        for course in predictions1:
            assert predictions1[course] == predictions2[course]