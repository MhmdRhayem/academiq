import pandas as pd
import numpy as np
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
import mlflow
import mlflow.sklearn
import joblib
import json
import yaml
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    with open('params.yaml', 'r') as f:
        params = yaml.safe_load(f)['train']

    train_data = pd.read_csv('data/processed/train.csv')
    test_data = pd.read_csv('data/processed/test.csv')

    with open('models/model_metadata.json', 'r') as f:
        metadata = json.load(f)

    input_courses = metadata['input_courses']
    output_courses = metadata['output_courses']

    X_train = train_data[input_courses]
    y_train = train_data[output_courses]
    X_test = test_data[input_courses]
    y_test = test_data[output_courses]

    # Configure MLflow tracking
    mlflow_uri = os.getenv('MLFLOW_TRACKING_URI', '')
    if mlflow_uri:
        mlflow.set_tracking_uri(mlflow_uri)
        # Set Dagshub credentials if provided
        mlflow_user = os.getenv('MLFLOW_TRACKING_USERNAME', '')
        mlflow_password = os.getenv('MLFLOW_TRACKING_PASSWORD', '')
        if mlflow_user and mlflow_password:
            os.environ['MLFLOW_TRACKING_USERNAME'] = mlflow_user
            os.environ['MLFLOW_TRACKING_PASSWORD'] = mlflow_password

    mlflow.set_experiment("grade-prediction")
    model_name = os.getenv('MLFLOW_MODEL_NAME', 'grade-predictor')

    with mlflow.start_run() as run:
        # Log parameters
        mlflow.log_params(params)

        # Train model
        model = MultiOutputRegressor(
            xgb.XGBRegressor(
                n_estimators=params['n_estimators'],
                max_depth=params['max_depth'],
                learning_rate=params['learning_rate'],
                subsample=params['subsample'],
                colsample_bytree=params['colsample_bytree'],
                random_state=params['random_state'],
                n_jobs=-1
            )
        )

        model.fit(X_train, y_train)

        # Evaluate model
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        # Log metrics
        mlflow.log_metrics({
            'rmse': rmse,
            'r2': r2
        })

        # Save models locally (fallback)
        os.makedirs('models', exist_ok=True)
        joblib.dump(model, 'models/best_model.pkl')
        joblib.dump(input_courses, 'models/feature_columns.pkl')
        joblib.dump(output_courses, 'models/target_columns.pkl')

        # Save metrics
        metrics = {
            'rmse': float(rmse),
            'r2': float(r2)
        }
        with open('models/metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)

        # Log and register model in MLflow Model Registry
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name=model_name  # This registers the model!
        )

        print(f"\n{'='*50}")
        print(f"Training completed successfully!")
        print(f"{'='*50}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R2: {r2:.4f}")
        print(f"Run ID: {run.info.run_id}")
        if mlflow_uri:
            print(f"Model registered in MLflow Registry as '{model_name}'")
            print(f"View experiment: {mlflow_uri}/#/experiments")
        print(f"{'='*50}\n")


if __name__ == '__main__':
    main()