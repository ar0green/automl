import os
import shutil
import errno
import pandas as pd
from .utils import load_data, preprocess_data
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import optuna
import mlflow
import mlflow.sklearn


def create_pipeline(model):
    pipeline_steps = []
    pipeline_steps.append(('scaler', StandardScaler()))
    pipeline_steps.append(('model', model))
    pipeline = Pipeline(steps=pipeline_steps)
    return pipeline


def objective(trial, X_train, y_train, X_val, y_val, task_type):
    n_estimators = trial.suggest_int('n_estimators', 50, 200)
    max_depth = trial.suggest_int('max_depth', 3, 20)
    max_features = trial.suggest_categorical(
        'max_features', [None, 'sqrt', 'log2'])

    if task_type == 'classification':
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            max_features=max_features,
            random_state=42
        )
    else:
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            max_features=max_features,
            random_state=42
        )

    pipeline = create_pipeline(model)
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_val)

    if task_type == 'classification':
        score = accuracy_score(y_val, y_pred)
    else:
        score = mean_squared_error(y_val, y_pred, squared=False)  # RMSE

    return score


def train_with_mlflow(
    pipeline, X_train, y_train, X_val, y_val, params, task_type, model_name, overwrtie
):
    # mlflow.set_tracking_uri('file:///{}'.format(os.path.abspath('mlruns')))
    mlflow.set_tracking_uri('http://localhost:5000')

    with mlflow.start_run():
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_val)

        if task_type == 'classification':
            score = accuracy_score(y_val, y_pred)
            mlflow.log_metric('accuracy', score)
        else:
            score = mean_squared_error(y_val, y_pred, squared=False)
            mlflow.log_metric('rmse', score)

        mlflow.log_params(params)
        mlflow.sklearn.log_model(pipeline, "model")

        model_path = f'models/{model_name}'

        if os.path.exists(model_path) and overwrtie:
            try:
                shutil.rmtree(model_path)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise

        mlflow.sklearn.save_model(pipeline, model_path)

        print(f"Model Score: {score}")


def run_pipeline(
    data_path, column_names, target_column,
    task_type='classification', sep=',', model_name='best_model', overwrite=False
):
    data = load_data(data_path, column_names=column_names, sep=sep)
    data.replace('?', pd.NA, inplace=True)
    data.dropna(inplace=True)

    X_train, X_val, y_train, y_val = preprocess_data(data, target_column)

    direction = 'maximize' if task_type == 'classification' else 'minimize'
    study = optuna.create_study(direction=direction)
    study.optimize(
        lambda trial: objective(
            trial, X_train, y_train, X_val, y_val, task_type
        ),
        n_trials=50
    )

    best_params = study.best_params

    if task_type == 'classification':
        best_model = RandomForestClassifier(
            **best_params, random_state=42
        )
    else:
        best_model = RandomForestRegressor(
            **best_params, random_state=42
        )

    best_pipeline = create_pipeline(best_model)

    train_with_mlflow(
        best_pipeline, X_train, y_train, X_val, y_val,
        best_params, task_type, model_name, overwrite
    )
