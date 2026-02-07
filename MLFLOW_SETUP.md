# MLflow Model Registry Setup Guide

## ✅ What's Been Done

### 1. **Dagshub MLflow Integration**
- Configured Dagshub as your free MLflow tracking server
- URL: https://dagshub.com/MhmdRhayem/academiq

### 2. **Training Script Updated** ([scripts/train.py](scripts/train.py))
- Automatically registers trained models in MLflow Model Registry
- Logs all experiments to Dagshub
- Tracks metrics (RMSE, R2) and parameters
- Works with environment variables from `.env` file

### 3. **Backend API Updated** ([backend/app/predictor.py](backend/app/predictor.py))
- Can load models from MLflow Model Registry OR local files
- Automatically falls back to local files if MLflow fails
- Supports Production/Latest model versions

### 4. **Deployment Configured** ([.github/workflows/backend.yml](.github/workflows/backend.yml))
- Koyeb deployment includes MLflow credentials
- Requires GitHub Secrets to be configured

### 5. **Local Environment** ([.env](.env))
- Environment variables configured for local development
- DVC credentials configured for Dagshub

---

## 🔧 What You Need to Do Next

### **Step 1: Add GitHub Secrets** (Required for Production)

Go to your GitHub repository settings and add these secrets:
1. Navigate to: https://github.com/MhmdRhayem/academiq/settings/secrets/actions
2. Click **"New repository secret"** and add:

| Secret Name | Value |
|-------------|-------|
| `MLFLOW_TRACKING_URI` | `https://dagshub.com/MhmdRhayem/academiq.mlflow` |
| `MLFLOW_TRACKING_USERNAME` | `MhmdRhayem` |
| `MLFLOW_TRACKING_PASSWORD` | `your_dagshub_token_here` |

**Note:** Use the same token you added to your `.env` file.

---

## 🚀 How to Use MLflow

### **Local Development**

#### Train a Model (Registers in MLflow):
```bash
# Make sure .env has your Dagshub credentials
python scripts/train.py
```

This will:
- Train the model
- Log metrics to Dagshub MLflow
- Register the model as "grade-predictor"
- Save a local copy as backup

#### View Experiments:
Go to: https://dagshub.com/MhmdRhayem/academiq/experiments

### **Production Deployment**

#### Option A: Use MLflow Model Registry
1. Train and register a model (see above)
2. Go to Dagshub → Experiments → Models
3. Promote a model version to "Production"
4. Deploy backend - it will auto-load the Production model

#### Option B: Use Local Model Files (Current)
1. Deploy with local `.pkl` files in the `models/` directory
2. Backend loads from local files if MLflow is not configured

---

## 📋 Model Loading Priority

The backend tries to load models in this order:
1. **MLflow Model Registry** (if `MLFLOW_TRACKING_URI` is set)
   - Tries: `models:/grade-predictor/Production`
   - Fallback: `models:/grade-predictor/latest`
2. **Local Files** (fallback)
   - `models/best_model.pkl`
   - `models/feature_columns.pkl`
   - `models/target_columns.pkl`

---

## 🧪 Testing the Integration

### Test Locally:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Check the logs - you should see:
- ✓ `Attempting to load model from MLflow Registry: grade-predictor`
- OR ✓ `Model loaded successfully from local files`

### Test on Koyeb:
After adding GitHub secrets and deploying:
1. Check Koyeb logs
2. The backend should load the model from MLflow or local files
3. Test the API: `https://your-koyeb-url.com/health`

---

## 📚 Useful Commands

### MLflow UI (if running locally):
```bash
mlflow ui
```
Then visit: http://localhost:5000

### View Dagshub Experiments:
https://dagshub.com/MhmdRhayem/academiq/experiments

### DVC Commands:
```bash
# Pull data from Dagshub
dvc pull

# Push data to Dagshub
dvc push
```

---

## 🆘 Troubleshooting

### "Model not found in registry"
- Make sure you've run training at least once with MLflow configured
- Check that the model name matches: `grade-predictor`
- Visit Dagshub experiments to verify the model exists

### "Authentication failed"
- Verify your Dagshub token in `.env` (local) or GitHub Secrets (production)
- Check that `MLFLOW_TRACKING_USERNAME` is `MhmdRhayem`

### Backend falls back to local files
- This is normal if MLflow is not configured or if there's no model in the registry yet
- The backend will work fine with local `.pkl` files

---

## 📖 Next Steps

1. ✅ Add GitHub Secrets (required for production)
2. ✅ Run training to register your first model
3. ✅ View experiments on Dagshub
4. ✅ Deploy and test!

For more information:
- MLflow Docs: https://mlflow.org/docs/latest/model-registry.html
- Dagshub Docs: https://dagshub.com/docs/
