import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.predictor import predictor


@pytest.fixture(scope="module", autouse=True)
def setup_model():
    """Ensure model is loaded before tests"""
    predictor.load_model()
    yield


client = TestClient(app)


class TestAPIEndToEnd:
    """End-to-end tests for the API"""

    def test_health_endpoint(self):
        """Test the health check endpoint returns correct response"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True
        assert data["model_name"] is not None

    def test_full_prediction_flow(self):
        """Test complete prediction flow from input to output"""
        input_response = client.get("/courses/input")
        assert input_response.status_code == 200
        input_courses = input_response.json()["courses"]

        grades = {course: 70.0 for course in input_courses[:10]}

        predict_response = client.post("/predict", json={"grades": grades})
        assert predict_response.status_code == 200

        result = predict_response.json()
        assert "predictions" in result
        assert "model_used" in result
        assert len(result["predictions"]) > 0

    def test_model_info_endpoint(self):
        """Test model info endpoint provides complete information"""
        response = client.get("/model/info")

        assert response.status_code == 200
        data = response.json()

        assert "model_name" in data
        assert "input_courses" in data
        assert "output_courses" in data
        assert "metrics" in data
        assert len(data["input_courses"]) == 30
        assert len(data["output_courses"]) == 17