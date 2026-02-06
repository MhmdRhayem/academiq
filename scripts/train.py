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

    mlflow_uri = os.getenv('MLFLOW_TRACKING_URI', '')
    if mlflow_uri:
        mlflow.set_tracking_uri(mlflow_uri)

    mlflow.set_experiment("grade-prediction")

    with mlflow.start_run():
        mlflow.log_params(params)

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

        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        mlflow.log_metrics({
            'rmse': rmse,
            'r2': r2
        })

        os.makedirs('models', exist_ok=True)
        joblib.dump(model, 'models/best_model.pkl')
        joblib.dump(input_courses, 'models/feature_columns.pkl')
        joblib.dump(output_courses, 'models/target_columns.pkl')

        metrics = {
            'rmse': float(rmse),
            'r2': float(r2)
        }
        with open('models/metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)

        mlflow.sklearn.log_model(model, "model")

        print(f"RMSE: {rmse:.4f}")
        print(f"R2: {r2:.4f}")


if __name__ == '__main__':
    main()