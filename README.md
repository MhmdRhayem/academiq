# Student Grade Prediction API

A FastAPI-based machine learning service that predicts student grades for Semesters 5-6 based on their performance in Semesters 1-4.

## Project Overview

| Component | Technology |
|-----------|------------|
| Backend | FastAPI |
| ML Model | XGBoost |
| Model Registry | MLFlow + DagsHub |
| Data Versioning | DVC |
| CI/CD | GitHub Actions |
| Containerization | Docker |
| Deployment | Koyeb |

## Project Structure

```
├── app/                    # FastAPI application
│   ├── main.py            # API endpoints
│   ├── predictor.py       # ML prediction logic
│   ├── schemas.py         # Pydantic models
│   └── config.py          # Configuration
├── tests/                  # Test suite
│   ├── test_unit.py       # Unit tests
│   ├── test_integration.py # Integration tests
│   └── test_e2e.py        # End-to-end tests
├── models/                 # Trained models
├── notebooks/              # Jupyter notebooks
├── scripts/                # Training scripts
├── data/                   # Data files (DVC tracked)
├── .github/workflows/      # CI/CD pipelines
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── dvc.yaml               # DVC pipeline
└── params.yaml            # Model parameters
```

## Model Performance

| Metric | Value |
|--------|-------|
| RMSE | 12.33 |
| R² | 0.110 |
| Input Features | 30 courses (S1-S4) |
| Output Targets | 17 courses (S5-S6) |

## Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v
```

### Docker

```bash
# Build and run
docker-compose up --build

# Or build manually
docker build -t grade-predictor .
docker run -p 8000:8000 grade-predictor
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Health status |
| `/predict` | POST | Predict grades |
| `/model/info` | GET | Model information |
| `/courses/input` | GET | Input course list |
| `/courses/output` | GET | Output course list |

### Example Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "grades": {
      "M1100": 75,
      "M1101": 80,
      "M1102": 70
    }
  }'
```

## CI/CD Pipeline

| Branch | Trigger | Actions |
|--------|---------|---------|
| dev (PR) | Pull Request | Lint + Test |
| dev (push) | Push | Test + Build Docker |
| main | Push | Test + Build + Push to DockerHub + Deploy |

## Setup Guide

### 1. DagsHub (MLFlow + DVC)

1. Create account at [dagshub.com](https://dagshub.com)
2. Create new repository
3. Copy MLFlow tracking URI and set as secret

### 2. DockerHub

1. Create account at [hub.docker.com](https://hub.docker.com)
2. Create access token
3. Add secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`

### 3. Koyeb Deployment

1. Create account at [koyeb.com](https://koyeb.com)
2. Create API token
3. Add secret: `KOYEB_TOKEN`

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MODEL_PATH` | Path to model file |
| `MLFLOW_TRACKING_URI` | MLFlow server URI |
| `MLFLOW_MODEL_NAME` | Registered model name |

## License

MIT