# pipeline.py

import os
import shutil
import errno
import pandas as pd
from .utils import load_data, preprocess_data, get_models
from sklearn.metrics import (
    accuracy_score,
    mean_squared_error,
    precision_score,
    recall_score,
    f1_score,
    r2_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, StratifiedKFold, KFold
import optuna
import mlflow
import mlflow.sklearn
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import numpy as np
import json
import uuid
from .models import Report


def create_pipeline(model):
    pipeline_steps = []
    pipeline_steps.append(("scaler", StandardScaler()))
    pipeline_steps.append(("model", model))
    pipeline = Pipeline(steps=pipeline_steps)
    return pipeline


def save_report(report_id, report_data, report_filename):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(root_dir, "reports", str(report_id))

    os.makedirs(reports_dir, exist_ok=True)
    report_file_path = os.path.join(reports_dir, report_filename)

    with open(report_file_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)


def get_hyperparameters(model_name, trial, task_type):
    params = {}
    if model_name == "Random Forest":
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 50, 200),
            "max_depth": trial.suggest_int("max_depth", 3, 20),
            "max_features": trial.suggest_categorical(
                "max_features", [None, "sqrt", "log2"]
            ),
        }
    elif model_name == "Logistic Regression":
        params = {"C": trial.suggest_loguniform("C", 1e-4, 1e2)}
    elif model_name == "Linear Regression":
        params = {}
    elif model_name == "XGBoost":
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 50, 200),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
            "max_depth": trial.suggest_int("max_depth", 3, 20),
        }
    elif model_name == "LightGBM":
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 50, 200),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
            "num_leaves": trial.suggest_int("num_leaves", 20, 150),
        }
    else:
        raise ValueError(f"Модель {model_name} не поддерживается.")
    return params


def objective(trial, model_name, base_model, X_train, y_train, task_type):
    params = get_hyperparameters(model_name, trial, task_type)
    model = base_model.set_params(**params)
    pipeline = create_pipeline(model)

    if task_type == "classification":
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scoring = "accuracy"
    else:
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        scoring = "neg_root_mean_squared_error"

    scores = cross_val_score(
        pipeline, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1
    )
    mean_score = scores.mean()

    if task_type == "classification":
        return -mean_score
    else:
        return mean_score


def train_with_mlflow(
    pipeline,
    X_train,
    y_train,
    X_val,
    y_val,
    params,
    task_type,
    model_name,
    dataset_name,
    report_id,
    db
):
    mlflow.set_tracking_uri("http://mlflow:5000")

    with mlflow.start_run() as run:
        run_id = run.info.run_id
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_val)

        if task_type == "classification":
            accuracy = accuracy_score(y_val, y_pred)
            precision = precision_score(
                y_val, y_pred, average="weighted", zero_division=0
            )
            recall = recall_score(y_val, y_pred, average="weighted", zero_division=0)
            f1 = f1_score(y_val, y_pred, average="weighted", zero_division=0)

            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            mlflow.log_metric("f1_score", f1)

            cm = confusion_matrix(y_val, y_pred)
            disp = ConfusionMatrixDisplay(confusion_matrix=cm)
            disp.plot()
            plt.title(f"Confusion Matrix - {model_name}")
            cm_filename = f"confusion_matrix_{dataset_name}_{model_name}.png"
            plt.savefig(cm_filename)
            plt.close()
            mlflow.log_artifact(cm_filename)
            os.remove(cm_filename)

        else:
            rmse = mean_squared_error(y_val, y_pred, squared=False)
            r2 = r2_score(y_val, y_pred)

            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("r2_score", r2)

        mlflow.log_params(params)
        mlflow.log_param("model_name", model_name)
        mlflow.log_param("dataset_name", dataset_name)

        if hasattr(pipeline.named_steps["model"], "feature_importances_"):
            importances = pipeline.named_steps["model"].feature_importances_
            feature_names = X_train.columns
            importance_df = pd.DataFrame(
                {"feature": feature_names, "importance": importances}
            )
            importance_df = importance_df.sort_values(by="importance", ascending=False)
            importance_filename = f"feature_importances_{dataset_name}_{model_name}.csv"
            importance_df.to_csv(importance_filename, index=False)
            mlflow.log_artifact(importance_filename)
            os.remove(importance_filename)

        mlflow.sklearn.log_model(pipeline, "model")

        model_path = f"models/{dataset_name}_{model_name}"

        if os.path.exists(model_path):
            try:
                shutil.rmtree(model_path)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise

        mlflow.sklearn.save_model(pipeline, model_path)

        print(f"Model: {model_name}, saved at {model_path}")
        mlflow_report_data = {
        'run_id': run_id,
        'metrics': mlflow.tracking.MlflowClient().get_run(run_id).data.metrics,
        'params': mlflow.tracking.MlflowClient().get_run(run_id).data.params,
        'tags': mlflow.tracking.MlflowClient().get_run(run_id).data.tags
        }

        report_entry = db.query(Report).filter(Report.report_id == report_id).first()
        if report_entry:
            report_entry.mlflow_data = mlflow_report_data
            db.commit()


def run_pipeline(
    data_path,
    column_names,
    target_column,
    task_type="classification",
    sep=",",
    dataset_name="dataset",
    report_id=None,
    db=None
):
    if report_id is None:
        report_id = str(uuid.uuid4())
    data = load_data(data_path, column_names=column_names, sep=sep)
    data.replace("?", pd.NA, inplace=True)
    data.dropna(inplace=True)

    X_train, X_val, y_train, y_val = preprocess_data(data, target_column)

    models = get_models(task_type)

    report = {}

    model_scores = {}
    for model_name, base_model in models.items():
        print(f"Evaluating {model_name}...")
        pipeline = create_pipeline(base_model)

        if task_type == "classification":
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            scoring = "accuracy"
        else:
            cv = KFold(n_splits=5, shuffle=True, random_state=42)
            scoring = "neg_root_mean_squared_error"

        scores = cross_val_score(
            pipeline, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1
        )
        mean_score = scores.mean()
        model_scores[model_name] = mean_score
        print(f"{model_name} CV Score: {mean_score}")

        report[model_name] = {"cv_scores": scores.tolist(), "mean_cv_score": mean_score}

    if task_type == "classification":
        best_model_name = max(model_scores, key=model_scores.get)
    else:
        best_model_name = min(model_scores, key=model_scores.get)

    print(f"Best model: {best_model_name}")

    best_base_model = models[best_model_name]

    print(f"Optimizing hyperparameters for {best_model_name}...")

    if task_type == "classification":
        direction = "minimize"
    else:
        direction = "minimize"

    study = optuna.create_study(direction=direction)
    study.optimize(
        lambda trial: objective(
            trial, best_model_name, best_base_model, X_train, y_train, task_type
        ),
        n_trials=50,
    )

    best_params = study.best_params
    report["best_params"] = best_params

    best_model = best_base_model.set_params(**best_params)

    best_pipeline = create_pipeline(best_model)

    best_pipeline.fit(X_train, y_train)

    y_pred = best_pipeline.predict(X_val)

    if task_type == "classification":
        accuracy = accuracy_score(y_val, y_pred)
        precision = precision_score(y_val, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_val, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_val, y_pred, average="weighted", zero_division=0)
        print(f"Validation Accuracy: {accuracy}")
        print(f"Validation Precision: {precision}")
        print(f"Validation Recall: {recall}")
        print(f"Validation F1 Score: {f1}")

        report["validation_metrics"] = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        }

    else:
        rmse = mean_squared_error(y_val, y_pred, squared=False)
        r2 = r2_score(y_val, y_pred)
        print(f"Validation RMSE: {rmse}")
        print(f"Validation R2 Score: {r2}")

        report["validation_metrics"] = {"rmse": rmse, "r2_score": r2}

    report_entry = db.query(Report).filter(Report.report_id == report_id).first()
    if report_entry:
        report_entry.dataset_name = dataset_name
        report_entry.model_name = best_model_name
        report_entry.report_data = report
        db.commit()

    train_with_mlflow(
        best_pipeline,
        X_train,
        y_train,
        X_val,
        y_val,
        best_params,
        task_type,
        best_model_name,
        dataset_name,
        report_id,
        db
    )
