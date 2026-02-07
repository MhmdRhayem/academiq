"""
Register existing trained model to MLflow Model Registry
This script takes the current production model and registers it in MLflow
"""
import mlflow
import mlflow.sklearn
import joblib
import json
import os
import sys
from dotenv import load_dotenv

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def main():
    # MLflow Configuration
    mlflow_uri = os.getenv('MLFLOW_TRACKING_URI', '')
    mlflow_user = os.getenv('MLFLOW_TRACKING_USERNAME', '')
    mlflow_password = os.getenv('MLFLOW_TRACKING_PASSWORD', '')
    model_name = os.getenv('MLFLOW_MODEL_NAME', 'grade-predictor')

    if not mlflow_uri:
        print("[ERROR] MLFLOW_TRACKING_URI not set in .env file")
        return

    # Set MLflow tracking URI
    mlflow.set_tracking_uri(mlflow_uri)

    # Set credentials
    if mlflow_user and mlflow_password:
        os.environ['MLFLOW_TRACKING_USERNAME'] = mlflow_user
        os.environ['MLFLOW_TRACKING_PASSWORD'] = mlflow_password

    print(f"[INFO] Connecting to MLflow: {mlflow_uri}")

    # Set experiment
    mlflow.set_experiment("grade-prediction")

    # Load the existing model
    print(f"\n[INFO] Loading existing model from backend/models/...")
    model = joblib.load('backend/models/best_model.pkl')

    # Load metadata
    with open('backend/models/model_metadata.json', 'r') as f:
        metadata = json.load(f)

    # Get model info
    best_model_name = metadata.get('best_model', 'Unknown')
    best_model_key = best_model_name.lower().replace(" ", "_")
    model_metrics = metadata.get(best_model_key, {})

    print(f"[OK] Model loaded: {best_model_name}")
    print(f"  - RMSE: {model_metrics.get('rmse', 'N/A')}")
    print(f"  - R2: {model_metrics.get('r2', 'N/A')}")

    # Create MLflow run and register model
    print(f"\n[INFO] Registering model to MLflow as '{model_name}'...")

    with mlflow.start_run(run_name=f"Register existing {best_model_name}") as run:
        # Log model info as tags
        mlflow.set_tag("model_type", best_model_name)
        mlflow.set_tag("source", "existing_production_model")
        mlflow.set_tag("registered_manually", "true")

        # Log metrics if available
        if model_metrics.get('rmse'):
            mlflow.log_metric('rmse', model_metrics['rmse'])
        if model_metrics.get('r2'):
            mlflow.log_metric('r2', model_metrics['r2'])
        if model_metrics.get('cv_r2'):
            mlflow.log_metric('cv_r2', model_metrics['cv_r2'])

        # Log and register the model
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name=model_name
        )

        print(f"\n{'='*60}")
        print(f"SUCCESS! Model registered to MLflow Model Registry!")
        print(f"{'='*60}")
        print(f"Model Name: {model_name}")
        print(f"Run ID: {run.info.run_id}")
        print(f"\nView your model:")
        print(f"   Experiments: {mlflow_uri}/#/experiments")
        print(f"   Models: https://dagshub.com/{mlflow_user}/academiq/models")
        print(f"{'='*60}\n")

        print("Next steps:")
        print("1. Go to Dagshub Models page")
        print("2. Find your 'grade-predictor' model")
        print("3. Promote the version to 'Production' stage")
        print("4. Your deployed API will use this model!")

if __name__ == '__main__':
    main()
