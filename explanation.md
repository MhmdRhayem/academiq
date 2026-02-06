# AcademiQ - Complete Project Explanation

This document explains every component of the MLOps pipeline and what each part does.

---

## What We Built

A complete **MLOps pipeline** for a Student Grade Prediction system that:
- Takes grades from Semesters 1-4 as input
- Predicts grades for Semesters 5-6
- Serves predictions via a REST API
- Automatically tests, builds, and deploys on every code change

---

## 1. The ML Model

**What it does:** Predicts grades for Semesters 5-6 based on Semesters 1-4 grades.

```
Input (30 courses from S1-S4) → XGBoost Model → Output (17 predicted grades for S5-S6)
```

### Model Files

| File | Purpose |
|------|---------|
| `models/best_model.pkl` | The trained XGBoost model (binary file) |
| `models/feature_columns.pkl` | List of 30 input course codes |
| `models/target_columns.pkl` | List of 17 output course codes |
| `models/model_metadata.json` | Model metrics (RMSE, R²) and parameters |

### Model Performance

| Metric | Value | Meaning |
|--------|-------|---------|
| RMSE | 12.33 | Predictions off by ~12 points on average (scale 0-100) |
| R² | 0.110 | Model explains ~11% of grade variance |

---

## 2. FastAPI Backend

**What it is:** A REST API that serves your ML model over HTTP.

### File Structure

```
app/
├── main.py        # API endpoints (routes)
├── predictor.py   # Loads model & makes predictions
├── schemas.py     # Data validation (what input/output looks like)
└── config.py      # Configuration (file paths, env variables)
```

### Endpoints

| Endpoint | Method | What it does |
|----------|--------|--------------|
| `/` | GET | Health check - "is the API alive?" |
| `/health` | GET | Same as above with more details |
| `/predict` | POST | Send grades → get predictions |
| `/model/info` | GET | Get model details and metrics |
| `/courses/input` | GET | List of required input courses |
| `/courses/output` | GET | List of predicted output courses |

### Request Flow

```
Client sends POST /predict with {"grades": {"M1100": 75, "M1101": 80, ...}}
    ↓
FastAPI validates input using schemas.py
    ↓
predictor.py loads model and runs prediction
    ↓
Returns {"predictions": {"DRH300": 72.5, "I3301": 68.3, ...}, "model_used": "XGBoost"}
```

---

## 3. Tests

**Why:** Ensure code works correctly before deploying.

### Test Files

```
tests/
├── test_unit.py        # Tests individual functions (predictor class)
├── test_integration.py # Tests components working together
└── test_e2e.py         # Tests full API request/response cycle
```

### Test Types Explained

| Test Type | What it tests | Example |
|-----------|---------------|---------|
| **Unit** | Single function/class in isolation | "Does predictor load model correctly?" |
| **Integration** | Multiple parts working together | "Does prediction work with real model?" |
| **E2E (End-to-End)** | Full system from start to finish | "Does API return correct response?" |

### Running Tests

```bash
pytest tests/ -v           # Run all tests
pytest tests/test_unit.py  # Run only unit tests
```

---

## 4. Docker

**What it is:** Packages your app + all dependencies into a container that runs anywhere.

### Why Docker?

| Problem | Docker Solution |
|---------|-----------------|
| "Works on my machine" but not on server | Same container runs everywhere |
| Different Python versions cause issues | Container has exact Python version |
| Missing dependencies | All dependencies bundled inside |

### Dockerfile Explained

```dockerfile
FROM python:3.11-slim          # Start with a base Python image
WORKDIR /app                   # Set working directory inside container
COPY requirements.txt .        # Copy dependencies list
RUN pip install ...            # Install all dependencies
COPY app/ ./app/               # Copy your application code
COPY models/ ./models/         # Copy ML models
EXPOSE 8000                    # Tell Docker the app uses port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]  # Start command
```

### docker-compose.yml

Makes running Docker easier locally:

```bash
docker-compose up  # One command to build and run everything
```

---

## 5. Git & GitHub

**Git:** Version control - tracks all changes to your code over time.

**GitHub:** Cloud hosting for your Git repository.

### Branches Explained

```
main (production)     ← Final, deployed code (users see this)
  ↑
staging              ← Testing before production
  ↑
dev                  ← Active development (work happens here)
```

### Why Multiple Branches?

| Branch | Purpose | Who uses it |
|--------|---------|-------------|
| `dev` | Daily development work | Developers |
| `staging` | Test before going live | QA/Testing |
| `main` | Production (live) code | End users |

### Typical Workflow

1. Developer works on `dev` branch
2. Creates Pull Request (PR) to merge `dev` → `staging`
3. Tests run automatically on PR
4. If tests pass, merge to `staging`
5. After testing on staging, merge `staging` → `main`
6. Code automatically deploys to production

---

## 6. GitHub Actions (CI/CD)

**CI = Continuous Integration:** Automatically test code on every change
**CD = Continuous Deployment:** Automatically deploy when tests pass

### Workflow Files

```
.github/workflows/
├── dev.yml         # Runs on PR to dev
├── staging.yml     # Runs on push to dev
└── production.yml  # Runs on push to main
```

### What Each Workflow Does

| Workflow | Trigger | Actions |
|----------|---------|---------|
| `dev.yml` | Pull Request to dev | 1. Lint code (Black, Flake8) 2. Run all tests |
| `staging.yml` | Push to dev | 1. Run tests 2. Build Docker image |
| `production.yml` | Push to main | 1. Run tests 2. Build Docker 3. Push to DockerHub 4. Deploy to Koyeb |

### Production Pipeline Flow

```
Push to main
    ↓
Run all tests (pytest)
    ↓ (only if tests pass)
Build Docker image
    ↓
Push to DockerHub (mhmdrhayem/academiq:latest)
    ↓
Deploy to Koyeb (live website)
```

---

## 7. DVC (Data Version Control)

**What it is:** Git for data files (because Git can't handle large files).

### The Problem

- Git is great for code (small text files)
- Git struggles with large files (data, models, images)
- Your data file is 672KB (small), but could be GB in real projects

### The Solution

DVC tracks a small "pointer" file in Git, while actual data is stored elsewhere.

```
data/
├── cleaned_data.xlsx      # Actual data (NOT in Git) → Stored on DagsHub
└── cleaned_data.xlsx.dvc  # Pointer file (in Git) → Only 104 bytes
```

### How .dvc File Works

The `.dvc` file contains:
```yaml
md5: abc123...  # Hash of the actual file
size: 672746    # File size in bytes
path: cleaned_data.xlsx
```

Git tracks this tiny file. DVC uses the hash to fetch the real data from remote storage.

### Commands

```bash
dvc add data/file.xlsx  # Start tracking file with DVC
dvc push                # Upload data to remote (DagsHub)
dvc pull                # Download data from remote
```

---

## 8. DagsHub

**What it is:** GitHub for ML projects - combines Git, DVC, and MLFlow.

### What DagsHub Provides

| Feature | What it does |
|---------|--------------|
| **Git Hosting** | Mirrors your GitHub repo |
| **DVC Remote** | Stores your large data files |
| **MLFlow Server** | Tracks experiments and models |

### Your DagsHub URLs

| Service | URL |
|---------|-----|
| Repository | https://dagshub.com/MhmdRhayem/academiq |
| MLFlow UI | https://dagshub.com/MhmdRhayem/academiq.mlflow |
| DVC Remote | https://dagshub.com/MhmdRhayem/academiq.dvc |

---

## 9. MLFlow

**What it is:** Tool to track ML experiments - parameters, metrics, and models.

### Why Track Experiments?

When training models, you try many different settings:
```
Run 1: n_estimators=100, max_depth=5  → RMSE=13.5
Run 2: n_estimators=200, max_depth=10 → RMSE=12.3  ← Best!
Run 3: n_estimators=300, max_depth=15 → RMSE=12.8
```

Without tracking, you forget which settings worked best.

### How MLFlow is Used (in scripts/train.py)

```python
import mlflow

with mlflow.start_run():
    # Log parameters (settings you chose)
    mlflow.log_params({
        "n_estimators": 200,
        "max_depth": 10,
        "learning_rate": 0.01
    })

    # Train model...

    # Log metrics (results)
    mlflow.log_metrics({
        "rmse": 12.33,
        "r2": 0.11
    })

    # Log the model itself
    mlflow.sklearn.log_model(model, "model")
```

### MLFlow UI

Visit DagsHub MLFlow UI to see:
- All your experiment runs
- Compare metrics across runs
- Download any saved model

---

## 10. DockerHub

**What it is:** Public registry for Docker images (like GitHub but for containers).

### Your Image

```
mhmdrhayem/academiq:latest
```

### How It Works

1. GitHub Actions builds your Docker image
2. Pushes it to DockerHub
3. Anyone can pull and run it:

```bash
docker pull mhmdrhayem/academiq:latest
docker run -p 8000:8000 mhmdrhayem/academiq:latest
# API now running at http://localhost:8000
```

---

## 11. Koyeb (Deployment)

**What it is:** Free cloud platform that runs your Docker container 24/7.

### How Deployment Works

```
1. Koyeb receives deploy signal from GitHub Actions
    ↓
2. Pulls latest image from DockerHub (mhmdrhayem/academiq:latest)
    ↓
3. Starts container on their servers
    ↓
4. Assigns public URL (e.g., academiq-xxx.koyeb.app)
    ↓
5. Routes internet traffic to your container
```

### Why Koyeb?

| Feature | Benefit |
|---------|---------|
| Free tier | No cost for small projects |
| Auto-scaling | Handles traffic spikes |
| HTTPS | Secure by default |
| Global CDN | Fast worldwide |

---

## 12. GitHub Secrets

**What they are:** Encrypted environment variables stored in GitHub.

### Why Secrets?

You need passwords/tokens for:
- DockerHub (to push images)
- Koyeb (to deploy)

These should NEVER be in your code. GitHub Secrets keeps them safe.

### Secrets You Set Up

| Secret Name | Purpose | Where to get it |
|-------------|---------|-----------------|
| `DOCKERHUB_USERNAME` | Login to DockerHub | Your DockerHub username |
| `DOCKERHUB_TOKEN` | DockerHub password | hub.docker.com → Settings → Security → New Access Token |
| `KOYEB_TOKEN` | Deploy to Koyeb | app.koyeb.com → Settings → API → Create Token |

### How Workflows Use Secrets

```yaml
# In .github/workflows/production.yml
- name: Login to DockerHub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}  # Gets secret value
    password: ${{ secrets.DOCKERHUB_TOKEN }}     # Gets secret value
```

---

## Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         YOUR COMPUTER                                │
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                      │
│  │  Write   │ →  │   git    │ →  │   git    │                      │
│  │   Code   │    │  commit  │    │   push   │                      │
│  └──────────┘    └──────────┘    └────┬─────┘                      │
│                                       │                             │
│  ┌──────────┐    ┌──────────┐        │                             │
│  │   Data   │ →  │   dvc    │ ───────────────────┐                 │
│  │  Files   │    │   push   │        │           │                 │
│  └──────────┘    └──────────┘        │           │                 │
└──────────────────────────────────────│───────────│─────────────────┘
                                       │           │
                    ┌──────────────────▼──┐    ┌───▼──────────────────┐
                    │       GITHUB        │    │      DAGSHUB         │
                    │  ┌──────────────┐   │    │  ┌────────────────┐  │
                    │  │ Your Code    │   │    │  │  Data Storage  │  │
                    │  │ + .dvc files │   │    │  │  (DVC Remote)  │  │
                    │  └──────────────┘   │    │  ├────────────────┤  │
                    │          │          │    │  │ MLFlow Server  │  │
                    │          ▼          │    │  │ (Experiments)  │  │
                    │  ┌──────────────┐   │    │  └────────────────┘  │
                    │  │GitHub Actions│   │    └──────────────────────┘
                    │  │  (CI/CD)     │   │
                    │  └──────┬───────┘   │
                    └─────────│───────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │     DOCKERHUB       │
                    │  ┌───────────────┐  │
                    │  │ Docker Image  │  │
                    │  │ academiq:     │  │
                    │  │   latest      │  │
                    │  └───────┬───────┘  │
                    └──────────│──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       KOYEB         │
                    │  ┌───────────────┐  │
                    │  │   Running     │  │
                    │  │   Container   │  │
                    │  └───────┬───────┘  │
                    │          │          │
                    │  academiq.koyeb.app │
                    └──────────│──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       USERS         │
                    │                     │
                    │  POST /predict      │
                    │  → Get predictions  │
                    └─────────────────────┘
```

---

## Summary Table

| Component | What it is | What it does | Service Used |
|-----------|------------|--------------|--------------|
| **FastAPI** | Web framework | Serves ML model as API | Local/Cloud |
| **XGBoost** | ML library | Makes predictions | Built into app |
| **pytest** | Testing framework | Ensures code works | GitHub Actions |
| **Docker** | Containerization | Packages app | DockerHub |
| **Git** | Version control | Tracks code changes | GitHub |
| **GitHub Actions** | CI/CD | Automates testing & deployment | GitHub |
| **DVC** | Data versioning | Tracks large files | DagsHub |
| **MLFlow** | Experiment tracking | Logs model metrics | DagsHub |
| **Koyeb** | Cloud platform | Hosts the live app | Koyeb |

---

## Glossary

| Term | Definition |
|------|------------|
| **API** | Application Programming Interface - way for programs to communicate |
| **REST** | Architectural style for APIs using HTTP methods (GET, POST, etc.) |
| **Endpoint** | A specific URL path in an API (e.g., `/predict`) |
| **CI/CD** | Continuous Integration/Continuous Deployment - automating test & deploy |
| **Container** | Lightweight, standalone package containing app + dependencies |
| **Image** | Blueprint for creating containers |
| **Pipeline** | Automated sequence of steps (test → build → deploy) |
| **Remote** | Server where data/code is stored (GitHub, DagsHub) |
| **Secret** | Encrypted credential stored securely |
| **Webhook** | Automated message sent when something happens |